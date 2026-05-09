# Evidence Pattern Checklist — sqli-label-critic

Dùng file này trong Phase 1 Check C3: "Primary signal có trong payload?"
Mỗi type cần ít nhất 1 signal từ danh sách Required Signals của nó.

---

## rce (priority 1) — Required Signals (≥ 1)
```
✓ xp_cmdshell(
✓ xp_cmdshell '
✓ EXEC xp_cmdshell
✓ certutil
✓ powershell -e
✓ powershell -enc
✓ /bin/bash
✓ /bin/sh
✓ cmd /c
✓ cmd.exe
```

## out_of_band (priority 2) — Required Signals (≥ 1)
```
✓ LOAD_FILE(
✓ UTL_HTTP.request
✓ UTL_HTTP.begin_request
✓ utl_inaddr.get_host_address       ← cũng là error_based signal, priority wins
✓ xp_dirtree
✓ xp_fileexist
✓ OPENROWSET(
✓ dns(
```

## stacked_queries (priority 3) — Required Signals
```
✓ ;        ← dấu chấm phẩy PHẢI đi kèm SQL statement mới
✓ Phải có: ; + (CREATE|DROP|INSERT|UPDATE|DELETE|EXEC|SELECT) sau dấu ;
✗ Chỉ có ; mà không có statement → không phải stacked_queries
```

## error_based (priority 4) — Required Signals (≥ 1)
```
✓ EXTRACTVALUE(
✓ extractvalue(
✓ UPDATEXML(
✓ updatexml(
✓ utl_inaddr.get_host_address(
✓ ctxsys.drithsx
✓ ctxsys.ctx_ddl
✓ exp(~(SELECT
✓ geometrycollection(
✓ multipoint(
```

## time_blind (priority 5) — Required Signals (≥ 1)
```
✓ SLEEP(       ← MySQL
✓ sleep(
✓ pg_sleep(    ← PostgreSQL (exclusive)
✓ PG_SLEEP(
✓ WAITFOR DELAY ← MSSQL (exclusive)
✓ waitfor delay
✓ BENCHMARK(   ← MySQL
✓ benchmark(
✓ randomblob(  ← SQLite (exclusive)
✓ RANDOMBLOB(
```

## heavy_query (priority 6) — Required Signals
```
✓ COUNT(*) FROM [table] , [table] , [table]    ← ≥ 3 tables trong cross-join
✓ SELECT ... FROM A, B, C WHERE               ← ≥ 3 tables
✗ COUNT(*) FROM A, B   → chỉ 2 tables → KHÔNG phải heavy_query
```

## union_based (priority 7) — Required Signals (≥ 1)
```
✓ UNION SELECT
✓ UNION ALL SELECT
✓ UNION (SELECT
✓ union select
✓ UNION%20SELECT           (URL-encoded)
✓ UN/**/ION/**/SEL/**/ECT  (obfuscated — cần decode trước)
✓ UNiOn SeLeCt             (case variation)
```

## boolean_blind (priority 8) — Required Signals (≥ 1)
```
✓ AND 1=1
✓ AND 1=2
✓ OR 1=1
✓ OR 1=0
✓ AND 'a'='a'
✓ AND 'a'='b'
✓ OR '1'='1'
✓ AND (SELECT ... ) = 'x'   ← character-by-character inference
✓ AND ASCII(SUBSTR(         ← binary search pattern
```
Perhatikan: TIDAK ada "admin" prefix. Jika ada → auth_bypass.

## auth_bypass (priority 9) — Required Signals (≥ 1 + admin context)
```
✓ admin'--
✓ admin'#
✓ admin' OR
✓ ' OR '1'='1   PLUS login/auth context
✓ " OR "1"="1
✓ admin" OR
✗ Chỉ "OR 1=1" không có username/admin context → boolean_blind
```

## second_order (priority 10) — Required Signals
```
✓ INSERT INTO ... VALUES (...attack payload...)
✓ Context: payload được store rồi execute sau
✗ Nếu không rõ context → dùng boolean_blind thay vì second_order
```

## polyglot (priority 11) — Required Signals
```
✓ Payload có syntax hoạt động trên ≥ 2 DB engines đồng thời
✓ Ví dụ: '/**/OR/**/1=1--  (works MySQL, MSSQL, PostgreSQL)
✓ Comment bypass kết hợp với generic boolean
```

## lateral (priority 12) — Required Signals (≥ 1)
```
✓ JOIN ... ON ... OR 1=1
✓ LATERAL JOIN
✓ JOIN table ON condition OR 1=1
```

## benign — Điều kiện
```
✓ Không có BẤT KỲ signal nào từ priority 1-12
✓ Plain text, legitimate SQL (SELECT id FROM users WHERE id=1)
✓ Single keyword không có attack context
```

## unknown — Khi nào dùng
```
✓ Payload quá ngắn (< 3 tokens) và không có signal rõ
✓ Payload bị obfuscation nặng không decode được
✓ Confidence ≤ 0.50 sau khi không match category nào
```

---

## DB Engine Signal Map (Quick Reference)

| Signal trong payload | DB Engine đúng |
|---------------------|----------------|
| `pg_sleep(` | `postgresql` |
| `WAITFOR DELAY` | `mssql` |
| `utl_inaddr` | `oracle` |
| `ctxsys` | `oracle` |
| `dual` + Oracle functions | `oracle` |
| `randomblob(` | `sqlite` |
| `sqlite_master` | `sqlite` |
| `rdb$` | `firebird` |
| `sysibm.systables` | `db2` |
| `SLEEP(` only | `mysql` (hoặc `generic` nếu không chắc) |
| `@@VERSION` only | `generic` (tồn tại MySQL lẫn MSSQL) |
| Không có DB-specific signal | `generic` |
