# OWASP Canonical SQLi Patterns

Source: OWASP Testing Guide v4.2 — OTG-INPVAL-005
and OWASP SQL Injection Prevention Cheat Sheet

These patterns are used by `owasp_scorer.py` for conservative, high-precision classification.
OWASP patterns are STRICT: they MISS obfuscated variants → lower recall, higher precision.

---

## Time-Blind Patterns

```
sleep\s*\(\s*\d+\s*\)          # MySQL: SLEEP(5)
benchmark\s*\(\s*\d+\s*,       # MySQL: BENCHMARK(10000000,MD5(1))
pg_sleep\s*\(\s*\d+            # PostgreSQL: pg_sleep(5)
waitfor\s+delay\s+'\d+:\d+:\d+'  # MSSQL: WAITFOR DELAY '0:0:5'
dbms_pipe\.receive_message     # Oracle: DBMS_PIPE.RECEIVE_MESSAGE
```

---

## Boolean-Blind Patterns

```
'\s+or\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+   # ' OR 1=1, ' OR '1'='1
'\s+and\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+  # ' AND 1=1
or\s+1\s*=\s*1\s*--                         # or 1=1--
or\s+1\s*=\s*1\s*#                          # or 1=1#
'\s+or\s+'[^']+'\s*=\s*'[^']+              # ' OR 'a'='a
```

---

## Union-Based Patterns

```
union\s+(?:all\s+)?select\b    # UNION SELECT, UNION ALL SELECT
union\s*/\*.*?\*/\s*select     # UNION/**/SELECT (with comment)
order\s+by\s+\d+\s*--         # ORDER BY 1-- (column count probing)
```

---

## Error-Based Patterns

```
extractvalue\s*\(              # MySQL: extractvalue(1,concat(0x7e,version()))
updatexml\s*\(                 # MySQL: updatexml(1,concat(0x7e,version()),1)
xmltype\s*\(                   # Oracle: xmltype((select version from v$instance))
floor\s*\(\s*rand\s*\(        # MySQL: SELECT count(*),floor(rand(0)*2)x FROM...GROUP BY x
exp\s*\(\s*~                   # MySQL: exp(~(SELECT * FROM(SELECT version())a))
```

---

## OWASP Injection Context Rule

OWASP scorer applies a 0.60x penalty to all scores if `has_injection_context()` is False.

**Reasoning**: Standalone SQL like `SELECT sleep(5)` is NOT an injection payload.
Only penalizes when NO injection signal (leading quote, OR/AND context, trailing comment).

```python
if not has_injection_context(payload):
    type_vector = {k: round(v * 0.60, 4) for k, v in type_vector.items()}
```

---

## OWASP Bonus Rule

Each OWASP pattern match beyond the base detector adds +0.05 confidence (max +0.10).

```python
bonus = min(0.10, matches * 0.05)
final_score = min(1.0, base_score + bonus)
```

---

## Why OWASP is Conservative

1. Patterns are explicit OWASP documented vectors — well-known but not exhaustive
2. Obfuscated payloads (`UN/**/ION SEL/**/ECT`) are NOT matched
3. Case-variation (`SeLeCt`) is NOT normalized before matching
4. Missing: structural signals, empirical patterns from real datasets

**Consequence**: OWASP has high precision but misses ~30-40% of real-world obfuscated attacks.
Heuristic scorer compensates for this gap.

---

*For heuristic extensions, see heuristic_patterns.md*
