# Taxonomy Reference — sqli-labeler

## SQLi Type (14 categories) — theo thứ tự priority

| Priority | Type | Primary Signals |
|----------|------|----------------|
| 1 | `rce` | `xp_cmdshell`, `certutil`, `powershell`, `/bin/bash`, `cmd.exe` |
| 2 | `out_of_band` | `LOAD_FILE`, `UTL_HTTP`, `UTL_INADDR`, `xp_dirtree`, `OPENROWSET`, `dns` |
| 3 | `stacked_queries` | `;` + new SQL statement (CREATE/DROP/INSERT/EXEC) |
| 4 | `error_based` | `EXTRACTVALUE`, `UPDATEXML`, `utl_inaddr.get_host_address`, `ctxsys.drithsx` |
| 5 | `time_blind` | `SLEEP()`, `pg_sleep()`, `WAITFOR DELAY`, `BENCHMARK()`, `randomblob()` |
| 6 | `heavy_query` | `COUNT(*) FROM A, B, C` — cross-join **≥ 3** tables |
| 7 | `union_based` | `UNION SELECT`, `UNION ALL SELECT` |
| 8 | `boolean_blind` | `AND 1=1`, `OR 1=1`, `AND 'a'='a'`, `OR '1'='1'` |
| 9 | `auth_bypass` | `admin' OR`, `' OR '1'='1`, `admin'--`, `admin'#` |
| 10 | `second_order` | `INSERT INTO ... VALUES` với attack intent |
| 11 | `polyglot` | Hoạt động trên ≥ 2 DB engines đồng thời |
| 12 | `lateral` | `JOIN ... ON ... OR 1=1`, `LATERAL JOIN` |
| 13 | `benign` | Legitimate SQL, plain text, không có attack signal |
| 14 | `unknown` | Không đủ thông tin để classify |

**Quy tắc:** Payload match nhiều categories → chọn priority số **thấp nhất**.

---

## DB Engine (9 categories)

| DB | Primary Signatures |
|----|-------------------|
| `mysql` | `@@VERSION`, `SLEEP()`, `LOAD_FILE()`, `information_schema`, `/*!...*/` comment |
| `mssql` | `WAITFOR DELAY`, `sysobjects`, `xp_cmdshell`, `@@servername`, `sys.tables` |
| `oracle` | `utl_inaddr`, `ctxsys.drithsx`, `dual`, `all_tables`, `ROWNUM`, `v$version` |
| `postgresql` | `pg_sleep()`, `version()::`, `::` cast syntax, `pg_catalog`, `pg_tables` |
| `sqlite` | `sqlite_version()`, `sqlite_master`, `randomblob()`, `sqlite_sequence` |
| `firebird` | `rdb$functions`, `rdb$relations` |
| `db2` | `sysibm.systables`, `syscat.tables` |
| `generic` | Không có DB-specific signature rõ ràng |
| `unknown` | Payload quá ngắn / mơ hồ để xác định |

**Lưu ý**: `@@VERSION` xuất hiện ở cả MySQL lẫn MSSQL → nếu không có signal bổ sung → `generic`.

---

## Signal Chi Tiết Từng Type

### rce (priority 1)
- `xp_cmdshell('...')` — MSSQL stored proc chạy OS command
- `EXEC xp_cmdshell` — biến thể
- `certutil`, `powershell -e`, `/bin/bash -c`, `cmd /c`
- Nếu có xp_cmdshell → `rce` (không phải `out_of_band`)

### out_of_band (priority 2)
- `LOAD_FILE('/etc/passwd')` — MySQL
- `UTL_HTTP.request()` — Oracle HTTP exfil
- `UTL_INADDR.get_host_address()` — Oracle DNS exfil
- `xp_dirtree`, `xp_fileexist` — MSSQL file system
- `OPENROWSET(...)` — MSSQL external connection

### stacked_queries (priority 3)
- `;` theo sau bởi `CREATE`, `DROP`, `INSERT`, `UPDATE`, `DELETE`, `EXEC`
- Ví dụ: `'; DROP TABLE users--`, `'; INSERT INTO admin VALUES(...)`

### error_based (priority 4)
- `EXTRACTVALUE(1, concat(0x7e, (SELECT ...)))` — MySQL
- `UPDATEXML(1, concat(0x7e, (SELECT ...)), 1)` — MySQL
- `utl_inaddr.get_host_address((SELECT ...))` — Oracle
- `ctxsys.drithsx.sxifconfigp` — Oracle

### time_blind (priority 5)
- `SLEEP(5)` — MySQL
- `pg_sleep(5)` — PostgreSQL (exclusive)
- `WAITFOR DELAY '0:0:5'` — MSSQL (exclusive)
- `BENCHMARK(5000000, MD5(1))` — MySQL
- `randomblob(1000000000)` — SQLite

### heavy_query (priority 6)
- `SELECT COUNT(*) FROM information_schema.tables A, information_schema.tables B, information_schema.tables C`
- **≥ 3 tables** trong cross-join là điều kiện bắt buộc
- 2 tables → KHÔNG phải heavy_query

### union_based (priority 7)
- `UNION SELECT NULL,NULL,NULL--`
- `UNION ALL SELECT 1,2,3--`
- `ORDER BY N` (column count enumeration) thường đi kèm

### boolean_blind (priority 8)
- `AND 1=1`, `AND 1=2`
- `OR 'a'='a'`, `OR '1'='1'`
- `AND (SELECT SUBSTRING(username,1,1) FROM users)='a'`
- Phân biệt với auth_bypass: không có `admin` prefix

### auth_bypass (priority 9)
- `admin'--`, `admin'#` — comment terminates password check
- `' OR '1'='1` với context đăng nhập
- `admin' OR '1'='1'--`
- **Phân biệt**: có username/admin prefix → auth_bypass; không có → boolean_blind

### second_order (priority 10)
- `INSERT INTO users (name) VALUES ('admin'--')`
- Payload được store trước, execute sau khi retrieved
- Cần context của query — nếu không rõ, dùng boolean_blind

### polyglot (priority 11)
- Payload thiết kế để bypass multiple DB engines
- Ví dụ: `'/**/OR/**/1=1--` (works MySQL, MSSQL, PostgreSQL)

### lateral (priority 12)
- `... JOIN table2 ON table1.id = table2.id OR 1=1`
- `LATERAL JOIN` với subquery injection
