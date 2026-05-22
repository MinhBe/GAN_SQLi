# 04 — Full Data Foundation Và Partial Delex

> Mục tiêu: tạo dataset reconstruct/latent-friendly cho VAE, không để vocabulary raw phá training.

---

## 1. Nền hiện có

Phase 4 đã xử lý `12,753,953` dòng và có split cluster leakage `0`; VAE phải giữ split này để tránh reconstruction/memorization giả. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

---

## 2. Partial delex policy

Giữ:

```text
SQLi keywords chính
structural punctuation
whitelisted functions khoảng 30-50
operator quan trọng
attack skeleton
```

Mask:

```text
identifier
table/column
string literal
numeric literal
comment literal nếu không phải tamper marker
```

Mục tiêu:

```text
vocab frozen khoảng 200-500
round-trip/relex kiểm được
decoder không phải học raw vocabulary quá lớn
```

---

## 3. Dataset schema

```text
payload_canonical
payload_partial_delex
token_ids
slot_map
condition_label
condition_confidence
template_id
cluster_id
split
round_trip_status
```

---

## 4. Novelty/memorization guard

Lee dedup cho thấy near-duplicate overlap làm tăng memorization; do đó VAE reconstruction phải báo exact/near-copy theo cluster. [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:775`](..\..\Asset\Total_OCR1\Lee_2022_Deduplicating.md)

---

## 5. Output

```text
data/vae_gan/full/partial_delex_train.parquet
data/vae_gan/full/partial_delex_dev.parquet
data/vae_gan/full/partial_delex_test.parquet
data/vae_gan/full/vocab.json
data/vae_gan/full/slot_map.parquet
reports/vae_gan/04_full_data_foundation_partial_delex.md
```

---

## 6. Gate

Pass nếu:

```text
round_trip_success >= ngưỡng đăng ký
cluster leakage = 0
vocab không phình vượt budget
template/condition coverage đủ cho pure-VAE slice
```

---

## 7. Kết luận

Partial delex là phần sống còn của VAE-GAN trên SQLi. Nếu dataset không reconstruct/relex được, latent model đẹp cũng không có giá trị sản phẩm.
