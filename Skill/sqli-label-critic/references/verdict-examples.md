# Verdict Examples — sqli-label-critic

Dùng file này để calibrate verdict khi không chắc. Mỗi ví dụ gồm payload, label được review,
và verdict có dẫn chứng đầy đủ.

---

## PASS Examples

### PASS-1: time_blind / postgresql — Signal rõ ràng
```
payload:    """ or pg_sleep ( __TIME__ ) --"
sqli_type:  time_blind
db_engine:  postgresql
confidence: 0.95
reasoning:  "pg_sleep() is PostgreSQL-specific time-delay function — time-based blind inference"

verdict:    PASS
evidence:   "Signal confirmed: pg_sleep() — PostgreSQL-exclusive time-delay function"
note:       "Correct: priority 5, DB confirmed by pg_sleep() signature"
```

### PASS-2: error_based / oracle — utl_inaddr
```
payload:    "AND 1 = utl_inaddr.get_host_address((SELECT name FROM users))"
sqli_type:  error_based
db_engine:  oracle
confidence: 0.95
reasoning:  "utl_inaddr.get_host_address with subquery is Oracle error-based exfiltration"

verdict:    PASS
evidence:   "Signal confirmed: utl_inaddr.get_host_address — Oracle error-based primary signal"
note:       "Correct: priority 4, DB confirmed by utl_inaddr (Oracle-exclusive)"
```

### PASS-3: auth_bypass / generic
```
payload:    "admin' OR '1'='1"
sqli_type:  auth_bypass
db_engine:  generic
confidence: 0.95
reasoning:  "admin'-- with OR 1=1 pattern terminates password check in login query"

verdict:    PASS
evidence:   "Signal confirmed: admin' + OR '1'='1 — classic auth bypass with username prefix"
note:       "Correct: priority 9, generic DB correct (no DB-specific signature)"
```

### PASS-4: benign — No attack signals
```
payload:    "distinct"
sqli_type:  benign
db_engine:  unknown
confidence: 0.70
reasoning:  "Single SQL keyword 'distinct' without injection context — legitimate use"

verdict:    PASS
evidence:   "No attack signals found. Single keyword with no injection pattern."
note:       "Correct benign. Confidence 0.70 appropriate for single-token payload."
```

---

## FLAG Examples

### FLAG-1: Reasoning quá ngắn
```
payload:    "or 1 = 1 --"
sqli_type:  boolean_blind
db_engine:  generic
confidence: 0.80
reasoning:  "boolean"

verdict:    FLAG
evidence:   "Reasoning insufficient: 7 chars, no signal cited"
note:       "Type may be correct (OR 1=1 present) but reasoning must cite specific pattern. Expected: 'OR 1=1 -- comparison pattern for boolean-based blind inference'"
```

### FLAG-2: Confidence không khớp
```
payload:    "SELECT 1"
sqli_type:  boolean_blind
db_engine:  mysql
confidence: 0.95
reasoning:  "SELECT 1 can be used in boolean blind injection"

verdict:    FLAG
evidence:   "Confidence 0.95 unjustified: no boolean signal (AND/OR 1=1) found. SELECT 1 alone is weak evidence."
note:       "Should be confidence 0.50, type unknown or benign. DB=mysql unsupported by any mysql-specific signal."
```

### FLAG-3: DB engine generic nhưng có clear signature
```
payload:    "' AND SLEEP(5)--"
sqli_type:  time_blind
db_engine:  generic
confidence: 0.80
reasoning:  "SLEEP() is time-based blind injection function"

verdict:    FLAG
evidence:   "DB engine improvable: SLEEP() is MySQL-specific, db_engine should be mysql not generic"
note:       "Type correct. DB should be mysql. Confidence 0.95 appropriate given SLEEP() is primary signal."
```

### FLAG-4: boolean_blind nhưng có admin prefix (cần check auth_bypass)
```
payload:    "admin' AND 1=1--"
sqli_type:  boolean_blind
db_engine:  generic
confidence: 0.85
reasoning:  "AND 1=1 pattern is boolean blind injection"

verdict:    FLAG
evidence:   "admin prefix detected — consider auth_bypass (P9) vs boolean_blind (P8). Both are valid interpretations but auth_bypass more specific for admin+OR/AND pattern."
note:       "Ambiguous case. If login context confirmed → REJECT and change to auth_bypass."
```

---

## REJECT Examples

### REJECT-1: Priority conflict — SLEEP beats UNION
```
payload:    "' UNION SELECT 1, SLEEP(5) --"
sqli_type:  union_based
db_engine:  oracle
confidence: 0.95
reasoning:  "UNION SELECT extracts data from database"

verdict:    REJECT
evidence:   "Priority conflict: SLEEP() (P5=time_blind) overrides UNION SELECT (P7=union_based). DB mismatch: SLEEP() is MySQL-specific, not Oracle."
correction: "sqli_type=time_blind, db_engine=mysql, confidence=0.95"
```

### REJECT-2: Signal absent — không có time_blind signal
```
payload:    "' OR '1'='1"
sqli_type:  time_blind
db_engine:  mysql
confidence: 0.80
reasoning:  "time based injection"

verdict:    REJECT
evidence:   "Signal absent: no SLEEP()/pg_sleep()/WAITFOR DELAY/BENCHMARK()/randomblob() in payload. Cannot be time_blind."
correction: "sqli_type=boolean_blind (OR '1'='1 present), db_engine=generic, confidence=0.85"
```

### REJECT-3: Benign có attack keyword
```
payload:    "1 UNION SELECT NULL, username, password FROM users--"
sqli_type:  benign
db_engine:  unknown
confidence: 0.70
reasoning:  "looks like a benign query"

verdict:    REJECT
evidence:   "Benign violated: UNION SELECT found (priority 7=union_based). 'FROM users--' confirms attack intent."
correction: "sqli_type=union_based, db_engine=generic, confidence=0.95"
```

### REJECT-4: Wrong DB engine — pg_sleep là PostgreSQL
```
payload:    "'; SELECT pg_sleep(10)--"
sqli_type:  time_blind
db_engine:  mysql
confidence: 0.90
reasoning:  "pg_sleep is time blind"

verdict:    REJECT
evidence:   "DB mismatch: pg_sleep() is PostgreSQL-exclusive function. db_engine=mysql is wrong. Also: stacked_queries (P3) via ';' may override time_blind (P5) — verify."
correction: "db_engine=postgresql. Check priority: '; SELECT' = stacked_queries (P3) → if confirmed, sqli_type=stacked_queries"
```

### REJECT-5: unknown với clear signal
```
payload:    "' UNION ALL SELECT table_name FROM information_schema.tables--"
sqli_type:  unknown
db_engine:  unknown
confidence: 0.50
reasoning:  "unclear injection type"

verdict:    REJECT
evidence:   "Signal present: UNION ALL SELECT (P7=union_based), information_schema (MySQL signature). Sufficient evidence for classification."
correction: "sqli_type=union_based, db_engine=mysql, confidence=0.95"
```

### REJECT-6: Priority conflict — xp_cmdshell beats union_based
```
payload:    "'; EXEC xp_cmdshell('net user')--"
sqli_type:  union_based
db_engine:  mssql
confidence: 0.80
reasoning:  "SQL injection"

verdict:    REJECT
evidence:   "Priority conflict: xp_cmdshell (P1=rce) found but labeled union_based (P7). Reasoning: 'SQL injection' is generic (< meaningful threshold)."
correction: "sqli_type=rce, db_engine=mssql, confidence=0.95, reasoning='xp_cmdshell executes OS command via MSSQL stored procedure — RCE via stacked query'"
```

---

## Conflict Duplicate Examples

### Conflict-1: Cùng payload, khác type
```
Row 1502: payload="' OR '1'='1", sqli_type=boolean_blind, confidence=0.85
Row 8741: payload="' OR '1'='1", sqli_type=auth_bypass,   confidence=0.90

verdict (both): FLAG — Conflict duplicate
note: "Same payload_norm, different sqli_type. Ambiguous case: auth_bypass requires username context. Without context, boolean_blind (P8) is safer. Recommend: boolean_blind for both."
```

### Conflict-2: Cùng payload, cùng type — redundant
```
Row 233:  payload="SELECT 1", sqli_type=benign
Row 9012: payload="SELECT 1", sqli_type=benign

verdict: FLAG (Row 9012)
note: "Exact duplicate. Keep Row 233 (lower index). Mark Row 9012 as redundant."
```
