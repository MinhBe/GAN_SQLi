# 01 — Data Reality Check Và Slot/Action Audit

> Mục tiêu: quyết định dữ liệu hiện tại có đủ tín hiệu để làm masked/action surgery hay không. Đây là gate G0, đứng trước mọi train GAN.

---

## 1. Vấn đề cần giải quyết

Phản biện quan trọng nhất của nhánh là: slot hiện tại gần như toàn literal; nếu generator chỉ điền literal, adversarial signal có thể rỗng và mô hình hội tụ về anchor-only. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:33-40`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

Phase 4 hiện đã có delex template và literal pools lớn, nhưng điều đó chưa chứng minh có đủ slot non-literal như operator, comment, function-choice, encoding hoặc tamper action. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-22`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:42-44`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

---

## 2. Input

```text
Guiding/Phase 4 outputs
payload canonical/delex/template artifacts
Phase 5 labels nếu đã đủ subset
Asset/Total_OCR1/Le_2024_GSQLi.md
```

---

## 3. Audit bắt buộc

Tạo `slot_action_audit.py` hoặc report tương đương.

Các thống kê phải có:

```text
literal_slot_count
operator_slot_count
comment_slot_count
encoding_slot_count
function_slot_count
keyword_variant_slot_count
tamper_action_candidate_count
coverage theo technique_primary
coverage theo db_hint
payload_length_bucket coverage
```

Không chỉ báo tổng số. Phải báo theo:

```text
technique × db_hint
template_family × action_type
train/dev/test split
```

---

## 4. Libinjection/action taxonomy

GSQLi cung cấp taxonomy phi-literal gồm keyword, operation, expression, string, comment, function, bareword; đây là bằng chứng để dùng Libinjection hoặc parser tương tự nhằm tạo action space có nghĩa. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:56-62`](..\03_Phan_Tich_Sau_Tu_Paper.md)

Action set ban đầu:

```text
case_swap
inline_comment
whitespace_swap
logical_operator_swap
compare_operator_swap
number_encoding
string_encoding
keyword_split
function_variant
logic_constant_insert
```

---

## 5. Gate G0

Pass nếu:

```text
non_literal_action coverage đủ để tạo tối thiểu 3-5 action family chính
mỗi action family có đủ mẫu train/dev/test cluster-safe
round-trip trên action giữ payload parse/relex được
condition distribution không bị một class thống trị hoàn toàn
```

Fail nếu:

```text
slot chỉ là literal STR/NUM/ID/TABLE
action taxonomy không map được về payload gốc
db/technique hiếm không có đủ mẫu
round-trip action phá payload quá nhiều
```

---

## 6. Output

```text
reports/gumbel/01_slot_action_audit.md
data/gumbel/action_taxonomy.json
data/gumbel/action_candidates.parquet
data/gumbel/g0_decision.json
```

Nội dung `g0_decision.json`:

```json
{
  "decision": "S1_MASKED_SLOT | S2_TAMPER_ACTION | STOP",
  "reason": "...",
  "coverage": {},
  "risks": []
}
```

---

## 7. Kết luận

Không được train Phase 08 nếu G0 chưa pass. Nếu slot audit cho thấy "literal-only", chuyển S2 tamper-action thành đường chính, không gọi đó là tinh chỉnh nhỏ.
