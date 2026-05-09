# Labeling Guidelines — sqli-labeler

## Edge Cases Quan Trọng

| Tình huống | Cách xử lý |
|------------|------------|
| Payload chỉ là 1 từ (`insert`, `distinct`, `select`) | `benign`, db=`unknown`, confidence=0.70 |
| `OR 1=1` không có username context | `boolean_blind`, db=`generic`, confidence=0.85 |
| `admin' OR '1'='1` | `auth_bypass` — có `admin` prefix, không phải `boolean_blind` |
| `UNION SELECT` + `SLEEP()` đồng thời | `time_blind` (priority 5) — không phải `union_based` (priority 7) |
| `@@VERSION` không có context bổ sung | db=`generic` — tồn tại ở cả MySQL lẫn MSSQL |
| `SELECT COUNT(*) FROM A, B` (2 tables) | `boolean_blind` hoặc `union_based` — KHÔNG phải `heavy_query` |
| Payload bị heavy obfuscation | Cố decode, nếu không được → confidence 0.60-0.70, ghi rõ "obfuscated" |
| `'; DROP TABLE` sau `' OR 1=1` | `stacked_queries` (priority 3) — không phải `boolean_blind` |
| `EXEC xp_cmdshell` có `WAITFOR` trước | `rce` (priority 1) — không phải `time_blind` |
| Payload toàn số/hex như `0x41414141` | `unknown` nếu không có SQL keyword, confidence=0.50 |

---

## Reasoning Quality Guide

### Format chuẩn
```
"[signal cụ thể] [→ / is / confirms] [tên type / hành vi] [context nếu ambiguous]"
```

### Ví dụ đúng theo từng type

| Type | Reasoning tốt |
|------|--------------|
| `time_blind` | `"pg_sleep() is PostgreSQL-specific time-delay function — time-based blind inference"` |
| `union_based` | `"UNION SELECT with @@VERSION confirms MySQL union-based data extraction"` |
| `error_based` | `"EXTRACTVALUE(1,concat(0x7e,(SELECT version()))) is MySQL error-based exfiltration"` |
| `rce` | `"xp_cmdshell('net user') executes OS command via MSSQL stored procedure"` |
| `auth_bypass` | `"admin'-- terminates password check in login query, classic auth bypass"` |
| `boolean_blind` | `"AND 1=1 / AND 1=2 pattern for boolean-based blind inference without output"` |
| `stacked_queries` | `"'; DROP TABLE users-- executes second statement after semicolon terminator"` |
| `benign` | `"Plain English text, no SQL keywords or injection patterns detected"` |
| `unknown` | `"Single token without SQL context, insufficient signal for classification"` |

### Reasoning không chấp nhận
```
"sql_injection"          ← quá generic
"boolean"                ← thiếu context
"boolean_blind"          ← chỉ lặp lại type
"not_sql_injection"      ← không giải thích
"injection detected"     ← không có signal cụ thể
```

---

## Re-label Mode (Mode B) — Quyết định giữ hay thay đổi

Khi sqli_type đã tồn tại, đánh giá:

1. **Giữ nguyên** nếu: type hiện tại đúng theo priority chain + có primary signal
2. **Thay đổi** nếu:
   - Type nằm ngoài taxonomy (boolean_based, stacked_query, comment_based, ...)
   - Type đúng nhưng confidence < 0.7 và có signal rõ hơn → update confidence + reasoning
   - Priority violation: payload match type cao priority hơn type hiện tại

**Mapping chuẩn cho out-of-taxonomy labels:**

| Label cũ | Label mới | Điều kiện |
|----------|-----------|-----------|
| `boolean_based` | `boolean_blind` | Auto — luôn rename |
| `stacked_query` | `stacked_queries` | Auto — luôn rename |
| `comment_based` | `boolean_blind` | Nếu payload có AND/OR pattern |
| `inline_query` | `union_based` | Nếu payload có UNION |
| `ldap_injection` | `unknown` | Không thuộc SQLi taxonomy |
| `command_injection` | `rce` | Nếu có xp_cmdshell |
| `generic` | Tra cứu payload | Xác định theo signal |

---

## Confidence Calibration

### 0.95 — Rất chắc chắn
- Có ít nhất 1 **primary signal rõ ràng** (function name, keyword đặc trưng)
- Không có signal mâu thuẫn với category khác
- Ví dụ: `pg_sleep(5)` → time_blind/postgresql/0.95

### 0.80 — Khá chắc chắn
- Có signal nhưng payload **ngắn** (< 20 tokens) hoặc **obfuscated nhẹ**
- Ví dụ: `OR 1=1--` → boolean_blind/generic/0.80

### 0.70 — Không chắc lắm
- Signal **yếu hoặc gián tiếp** — có thể là false positive
- Payload có thể thuộc 2 categories, chọn priority thấp hơn
- Ví dụ: `SELECT 1` → benign/unknown/0.70

### 0.50 — Ambiguous
- Không thể xác định rõ giữa 2 categories
- Payload bị obfuscation nặng, không decode được
- Dùng `unknown` khi confidence = 0.50

---

## Batch Processing Notes

### Xử lý theo batch 30 rows
- Process từng batch → append vào output CSV
- Checkpoint sau mỗi batch (không re-process nếu crash)
- Log progress: `Batch X/Y done (Z rows processed)`

### relabeling_diff.csv — chỉ rows thay đổi
```csv
row_index,field,old_value,new_value,reason
5,sqli_type,boolean_based,boolean_blind,"out-of-taxonomy rename"
12,confidence,0.60,0.95,"primary signal found: pg_sleep()"
```

### relabeling_summary.md — báo cáo distribution
```markdown
## Before
| sqli_type | count |
...

## After
| sqli_type | count |
...

## Changes
- Total rows changed: X / 40,860 (Y%)
- Confidence improved (< 0.7 → ≥ 0.7): Z rows
- Out-of-taxonomy fixed: N rows
```
