# 01 — Data Reality And Label Readiness

> Mục tiêu: kiểm tra dữ liệu và nhãn có đủ để huấn luyện latent controllability hay không.

---

## 1. Vấn đề cần giải quyết

Novelty lớn nhất của VAE-GAN là controllability, nhưng controllability lại phụ thuộc vào nhãn yếu nhất của hệ thống. Phase 5 hiện mới detector-only, verified_dev/test còn nhỏ và full progress chưa hoàn tất. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:43-51`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 2. Input

```text
Phase 4 canonical/delex data
Phase 5 label tiers
verified_dev/test
Asset papers: Xu CTGAN/TVAE, InfoGAN, ARAE/text latent surveys
```

---

## 3. Readiness checks

```text
label coverage theo technique_primary
label confidence band
unknown ratio theo db_hint
rare class count
template coverage
payload length distribution
reconstruction feasibility by template family
```

Không dùng:

```text
unknown làm engine class thật
review_queue làm condition ground truth
downstream classifier accuracy làm bằng chứng generator tốt
```

---

## 4. Label readiness gate

Pass nếu:

```text
verified/gold-silver đủ cho tối thiểu 3-4 condition chính
class hiếm có sample test đủ tối thiểu
condition noise được report
unknown được loại hoặc hạ trọng số
```

Fail nếu:

```text
condition chính dựa trên detector-only nhiễu
verified split quá nhỏ để đo controllability
db_hint unknown thống trị và không có route post-hoc
```

---

## 5. Output

```text
reports/vae_gan/01_data_label_readiness.md
data/vae_gan/condition_readiness.json
data/vae_gan/verified_condition_subset.parquet
```

---

## 6. Kết luận

Nếu label readiness fail, nhánh vẫn có thể thử **unsupervised MI** trước rồi map post-hoc, nhưng không được claim controllability theo technique nếu chưa có verified alignment.
