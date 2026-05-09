# RECOVERY PLAN — SQLi Label Validator Skill

> **Ngày tạo:** 2026-05-09  
> **Mục đích:** Khôi phục và validate toàn bộ dữ liệu labeled trong `combined_labeled_data.csv`  
> **Trạng thái:** Phase 2 (AI Labeling) hoàn thành — 40,860 rows labeled  
> **Phase 3 (GAN Training):** Chưa bắt đầu

---

## 1. Tổng quan dữ liệu hiện tại

### 1.1 File duy nhất cần xử lý

| File | Path | Rows | Columns |
|------|------|------|---------|
| `combined_labeled_data.csv` | `Asset/LabelData/` | **40,860** | `payload_norm`, `sqli_type`, `db_engine`, `confidence`, `reasoning` |

### 1.2 Phân bố SQLi Types

| Type | Count | % | Trạng thái |
|------|-------|---|------------|
| `benign` | 19,669 | 48.1% | ✅ OK (cần verify) |
| `error_based` | 8,663 | 21.2% | ✅ OK |
| `boolean_blind` | 2,711 | 6.6% | ✅ OK |
| `time_blind` | 2,391 | 5.9% | ✅ OK |
| `union_based` | 2,236 | 5.5% | ✅ OK |
| `boolean_based` | 1,820 | 4.5% | ❌ **Cần normalize → `boolean_blind`** |
| `heavy_query` | 1,296 | 3.2% | ✅ OK |
| `auth_bypass` | 1,193 | 2.9% | ✅ OK |
| `out_of_band` | 610 | 1.5% | ✅ OK |
| `unknown` | 124 | 0.3% | ✅ OK (có thể review thêm) |
| `polyglot` | 51 | 0.1% | ✅ OK |
| `stacked_queries` | 41 | 0.1% | ✅ OK |
| `generic` | 19 | <0.1% | ❌ **Out-of-taxonomy — cần map về type đúng** |
| `rce` | 10 | <0.1% | ✅ OK |
| `comment_based` | 10 | <0.1% | ❌ **Out-of-taxonomy — cần map** |
| `inline_query` | 8 | <0.1% | ❌ **Out-of-taxonomy — cần map** |
| `second_order` | 3 | <0.1% | ✅ OK |
| `stacked_query` | 2 | <0.1% | ❌ **Typo — cần normalize → `stacked_queries`** |
| `ldap_injection` | 2 | <0.1% | ❌ **Out-of-taxonomy — cần map → `unknown`** |
| `command_injection` | 1 | <0.1% | ❌ **Out-of-taxonomy — cần map → `rce`** |

### 1.3 Phân bố DB Engines

| DB Engine | Count | % |
|-----------|-------|---|
| `generic` | 23,024 | 56.3% |
| `oracle` | 9,141 | 22.4% |
| `mysql` | 4,840 | 11.8% |
| `postgresql` | 1,896 | 4.6% |
| `mssql` | 1,081 | 2.6% |
| `firebird` | 396 | 1.0% |
| `sqlite` | 275 | 0.7% |
| `db2` | 204 | 0.5% |
| `unknown` | 3 | <0.1% |

### 1.4 Phân bố Confidence

| Range | Count | % |
|-------|-------|---|
| 1.0 | 10,198 | 25.0% |
| 0.9 - <1.0 | 19,437 | 47.6% |
| 0.8 - <0.9 | 4,631 | 11.3% |
| 0.7 - <0.8 | 4,221 | 10.3% |
| 0.6 - <0.7 | 654 | 1.6% |
| 0.5 - <0.6 | 1,717 | 4.2% |
| 0.3 - <0.4 | 2 | <0.1% |
| **< 0.7:** | **2,373** | **5.8%** |

---

## 2. Các vấn đề cần xử lý (Prioritized)

### 🔴 P0 — Label Inconsistencies (1,822 rows)

Hai type bị labeling lỗi hệ thống:

| Vấn đề | Số rows | Nguyên nhân | Hành động |
|--------|---------|-------------|-----------|
| `boolean_based` (1,820) | 1,820 | AI dùng 2 tên khác nhau cho cùng 1 type | **Normalize** → `boolean_blind` |
| `stacked_query` (2) | 2 | Typo thiếu "s" | **Normalize** → `stacked_queries` |

### 🟡 P1 — Out-of-Taxonomy Types (40 rows)

| Type hiện tại | Count | Hành động |
|---------------|-------|-----------|
| `generic` | 19 | **Review từng row** → map về type phù hợp dựa vào payload pattern |
| `comment_based` | 10 | **Normalize** → kiểm tra: nếu là `boolean_blind` với comment injection |
| `inline_query` | 8 | **Normalize** → kiểm tra: nếu có `UNION` → `union_based` |
| `ldap_injection` | 2 | **Chuyển** → `unknown` (LDAP injection không phải SQLi) |
| `command_injection` | 1 | **Chuyển** → `rce` (nếu liên quan đến DB command execution) |

### 🟡 P1 — Low Confidence Rows (2,373 rows)

| Confidence | Count | Type phổ biến nhất |
|------------|-------|-------------------|
| 0.5 - 0.6 | 1,717 | `boolean_based` (1,210) + `auth_bypass` (920) |
| 0.6 - 0.7 | 654 | `boolean_blind` (140) |
| 0.3 - 0.4 | 2 | `unknown` |

### 🟢 P2 — DB Engine Mở Rộng (600 rows)

| DB Engine | Count | Vấn đề |
|-----------|-------|--------|
| `firebird` | 396 | Không nằm trong 7-category taxonomy gốc, nhưng có vẻ hợp lý (boolean time-based) |
| `db2` | 204 | Hợp lý (heavy_query với `sysibm.systables`) |
| `unknown` | 3 | Cần review lại |

### 🟢 P2 — Reasoning Quality (27,997 rows)

- **27,997 rows (68.5%)** có `reasoning` < 30 ký tự
- Nhiều reasoning quá ngắn / chung chung (`"where_equality"`, `"or_arithmetic"`)
- Cần cải thiện để phục vụ cho việc debug GAN training sau này

### 🟢 P2 — Benign Ratio (19,669 rows)

- `benign` chiếm **48.1%** — rất cao
- Cần kiểm tra: đây là legitimate benign SQL (dùng cho discriminator training) hay là noise từ sqliv2 dataset?
- Gợi ý: verify 500 rows mẫu để đánh giá accuracy của benign labeling

---

## 3. Cấu trúc Skill phục hồi

Tất cả skill files nằm tại:

```
Skill/
└── sqli-label-validator/
    ├── SKILL.md                           # Core skill — gọi để chạy validate
    └── references/
        ├── taxonomy.md                    # 13 SQLi types + detection signals
        ├── label-normalization.md         # Mapping rules cho normalize
        └── validation-rules.md            # 7 rules kiểm tra chất lượng
```

### 3.1 Cách sử dụng skill

Khi cần validate lại dữ liệu, chạy lệnh:

> `/sqli-label-validator` — Validate toàn bộ `combined_labeled_data.csv`

Skill sẽ tự động:
1. Đọc file CSV
2. Chạy 7 validation rules
3. Tạo báo cáo quality
4. Đề xuất corrections

### 3.2 Output files (tự động sinh)

| File | Mô tả |
|------|-------|
| `combined_labeled_data_normalized.csv` | Dataset đã normalize labels |
| `label_corrections_report.csv` | Danh sách tất cả rows đã sửa |
| `data_quality_report.md` | Báo cáo quality chi tiết |
| `master_labeled_data.csv` | Dataset sẵn sàng cho GAN training |

---

## 4. Chi tiết 14-category Taxonomy

```
union_based       — UNION SELECT / UNION ALL SELECT / UNION (SELECT...)
error_based       — EXTRACTVALUE / updatexml / utl_inaddr / ctxsys / convert
boolean_blind     — AND/OR + so sánh (1=1, 'a'='a), True/False inference
time_blind        — SLEEP / pg_sleep / WAITFOR DELAY / BENCHMARK / randomblob
heavy_query       — COUNT(*) cross-join, CPU-intensive subqueries
stacked_queries   — Nhiều statements cách nhau bằng dấu ;
out_of_band       — LOAD_FILE / xp_cmdshell / UTL_HTTP / BULK INSERT / DNS exfil
auth_bypass       — ' OR '1'='1 / admin'-- / login bypass patterns
second_order      — Stored SQLi, INSERT → trigger-based exploitation
rce               — xp_cmdshell / certutil / powershell / OS command via DB
polyglot          — Cross-DBMS payloads (nhiều DB engines đồng thời)
lateral           — JOIN-based injection / LATERAL JOIN exploitation
benign            — Legitimate SQL, plain text, không phải attack
unknown           — Không đủ thông tin để xác định
```

Xem chi tiết tại `references/taxonomy.md`.

---

## 5. Mapping Rules chi tiết

### 5.1 Normalize labels (rename thuần túy — không mất thông tin)

| Label cũ | Label mới | Type | Lý do |
|----------|-----------|------|-------|
| `boolean_based` | `boolean_blind` | Rename | Cùng technique, chỉ khác tên |
| `stacked_query` | `stacked_queries` | Rename | Typo thiếu "s" |

### 5.2 Re-classify (cần review payload để map)

| Label cũ | Label mới | Hướng dẫn |
|----------|-----------|-----------|
| `generic` | Tra theo payload | Nếu có AND/OR + so sánh → `boolean_blind`, nếu có UNION → `union_based`, v.v. |
| `comment_based` | `boolean_blind` | Hầu hết là boolean blind với comment injection (`/**/`, `#`, `--`) |
| `inline_query` | `union_based` | Nếu có UNION/UNION ALL → map về union_based |
| `ldap_injection` | `unknown` | LDAP injection không phải SQLi |
| `command_injection` | `rce` | Nếu có `xp_cmdshell` hoặc DB-to-OS command execution |

Xem chi tiết tại `references/label-normalization.md`.

---

## 6. 7 Validation Rules

| Rule | Mô tả | Target | Priority |
|------|-------|--------|----------|
| R1 | Out-of-taxonomy check | 40 rows | P1 |
| R2 | Label inconsistency (duplicate types) | 1,822 rows | P0 |
| R3 | Low confidence (< 0.7) | 2,373 rows | P1 |
| R4 | Benign với SQL keywords mạnh | 19,669 rows | P2 |
| R5 | DB engine không chuẩn | 600 rows | P2 |
| R6 | Reasoning quá ngắn (< 30 chars) | 27,997 rows | P2 |
| R7 | Duplicates theo payload_norm | Cần kiểm tra | P2 |

Xem chi tiết tại `references/validation-rules.md`.

---

## 7. Hướng dẫn Recovery từng bước

### Bước 1: Chạy skill validate

Gọi `/sqli-label-validator` với đường dẫn:

```
Input: C:\Projects\GAN_SQLi\Asset\LabelData\combined_labeled_data.csv
```

Skill sẽ đọc CSV và chạy 7 rules.

### Bước 2: Xem báo cáo

Mở `data_quality_report.md` để xem tổng quan:
- Số rows lỗi theo từng rule
- Danh sách cụ thể rows cần sửa
- Đề xuất correction

### Bước 3: Apply corrections

Skill sẽ tạo `label_corrections_report.csv` với:
- `row_index`: vị trí trong CSV gốc (0-based)
- `field`: cột cần sửa (`sqli_type` hoặc `db_engine`)
- `old_value`: giá trị cũ
- `new_value`: giá trị mới
- `reason`: lý do sửa
- `rule`: rule phát hiện (R1-R7)

### Bước 4: Generate master dataset

Sau khi apply corrections, chạy tiếp để tạo:
- `combined_labeled_data_normalized.csv` — dataset đã sạch
- `master_labeled_data.csv` — dataset sẵn sàng cho GAN training

### Bước 5: Verify (recommended)

Kiểm tra thủ công 100 rows ngẫu nhiên từ master dataset để đảm bảo chất lượng trước khi GAN training.

---

## 8. Ước tính tác động sau normalize

| Metric | Trước | Sau (dự kiến) |
|--------|-------|---------------|
| Tổng rows | 40,860 | 40,860 (không đổi) |
| Số type labels | 20 | 14 (chuẩn hóa) |
| Out-of-taxonomy rows | 40 | 0 |
| Inconsistent labels | 1,822 | 0 |
| Low confidence rows | 2,373 | 2,373 (giữ nguyên, flagged) |
| DB engines | 9 | 9 (giữ nguyên — thêm firebird, db2 vào taxonomy) |

---

## 9. Phụ lục: Data Backup

Trước khi chạy bất kỳ correction nào, skill sẽ tự động backup:

```
Asset/LabelData/
├── combined_labeled_data.csv                    ← Original (giữ nguyên)
├── combined_labeled_data_normalized.csv         ← Sau normalize
├── master_labeled_data.csv                      ← Final (sẵn sàng cho GAN training)
├── label_corrections_report.csv                 ← Chi tiết mọi thay đổi
├── data_quality_report.md                       ← Báo cáo chất lượng
└── RECOVERY_PLAN.md                             ← THIS FILE
```

**Không có dữ liệu nào bị ghi đè.** File gốc luôn được giữ nguyên.
