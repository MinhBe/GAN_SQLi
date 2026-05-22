# 06 — Evaluator And Model Separation

> Mục tiêu: tách model sinh dữ liệu khỏi evaluator, tránh reward hacking và tránh proxy metric che lỗi thật.

---

## 1. Nguyên tắc

```text
Generator không được tự định nghĩa ground truth.
Discriminator không được dùng làm evaluator duy nhất.
Classifier/WAF proxy không được thay parse/relex/novelty/verified.
```

GSQLi dùng attack classifier trong vòng reward; khi mượn hướng này, phải bọc thêm evaluator thực thi/diversity vì bypass classifier không chứng minh payload còn hợp lệ. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:64-67`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 2. Evaluator groups

### 2.1. Structure/Validity

```text
round_trip_success
parse_success
slot_boundary_validity
dialect_soft_validity
template_preservation
```

### 2.2. Diversity

```text
unique_ratio
self_bleu3
template_entropy
action_entropy
AST_or_structure_entropy
```

### 2.3. Novelty

```text
exact_copy_rate
near_copy_rate
cluster_novelty
nearest_neighbor_similarity
```

### 2.4. Control

```text
condition_accuracy
db_hint_consistency
action_family_accuracy
condition_ignore_rate
```

### 2.5. Security lab

```text
WAF/IDS score
rule triggered
bypass after parse/relex pass only
```

---

## 3. Composite score policy

Composite chỉ dùng sau khi sub-metric floors pass.

```text
S = weighted score đã khóa trước
Nhưng S không được bù cho failure ở validity/diversity/novelty.
```

Phản biện đã chỉ rõ composite có thể tăng proxy trong khi verified giảm; vì vậy phải khóa trọng số trước train và thêm phủ quyết từng sub-metric. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:50-52`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 4. Output

```text
eval/gumbel/evaluator_config.json
eval/gumbel/evaluator_calibration.json
reports/gumbel/06_evaluator_model_separation.md
```

---

## 5. Kết luận

Evaluator là cổng đo lường, không phải phần trang trí. Nếu evaluator yếu, mọi kết luận GAN thắng đều yếu.
