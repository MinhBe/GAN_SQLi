# 05 — Label Condition Calibration

> Mục tiêu: làm sạch hoặc hạ rủi ro nhãn trước khi dùng condition/MI.

---

## 1. Vấn đề

Controllability theo `technique_primary` hoặc `db_hint` sẽ hỏng nếu label nhiễu. Phase 5 hiện có verified split nhỏ và review queue lớn. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\..\Guiding\Phase%205\reports\05_full_label_system_report.md)

---

## 2. Hai đường condition

### A. Supervised condition

```text
c = technique/db label
chỉ dùng verified/gold-silver
Q-head hoặc classifier phụ đo lại c
```

Ưu:

```text
semantic rõ
metric dễ giải thích
```

Rủi ro:

```text
nhãn yếu -> MI học shortcut sai
```

### B. Unsupervised MI

```text
c = latent discrete code tự học
map post-hoc với technique/db/template
```

Ưu:

```text
không bị chặn bởi label yếu
```

Rủi ro:

```text
factor học được có thể là length/template/keyword density
```

Đường B được đề xuất thử trước trong phân tích mới. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:39-48`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 3. Calibration tasks

```text
label confidence table
condition grouping 3-4 class chính
unknown removal/downweight
Snorkel-style LF calibration nếu đủ labeling functions
verified subset for post-hoc alignment
```

---

## 4. Output

```text
data/vae_gan/full/condition_calibrated.parquet
data/vae_gan/full/verified_alignment_set.parquet
reports/vae_gan/05_label_condition_calibration.md
```

---

## 5. Gate

Pass nếu:

```text
supervised labels đủ sạch cho ít nhất một RQ
hoặc unsupervised MI có verified alignment protocol
```

Fail nếu:

```text
condition chủ yếu là unknown/noisy
không có cách đo post-hoc alignment
```

---

## 6. Kết luận

Không có label calibration thì VAE-GAN vẫn có thể học latent, nhưng không được claim controllability theo attack technique.
