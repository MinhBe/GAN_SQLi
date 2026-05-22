# 10 — Literature And Implementation Roadmap

> Mục tiêu: khóa danh sách paper còn thiếu và thứ tự triển khai tiếp theo cho nhánh VAE-GAN.

---

## 1. Paper nền bắt buộc

Phản biện đã chỉ ra corpus hiện thiếu các paper nền quan trọng:

```text
Larsen 2016 — VAE-GAN gốc
Kingma & Welling 2014 — VAE gốc
Bowman 2016 — text VAE / posterior collapse / KL annealing
Higgins 2017 — beta-VAE / disentanglement
```

Thiếu các paper này thì claim về posterior collapse, KL/free-bits và disentanglement chưa đủ nguồn. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:21-34`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 2. Paper đã dùng được hiện tại

```text
Xu 2019 CTGAN/TVAE: gate VAE-GAN > pure-VAE, conditional sampling
InfoGAN: MI controllability, trivial code risk
ARAE/text latent survey: adversarial trong latent space
Dasari 2025: SQLi augmentation pipeline, nhưng không phải VAE-GAN payload generator trực tiếp
Lee dedup: novelty/memorization guard
Ratner Snorkel: label calibration
```

---

## 3. Việc phải làm ngay

```text
1. Bổ sung 4 paper nền và tạo analysis/OCR.
2. Chốt partial-delex dataset.
3. Chạy label readiness và verified alignment set.
4. Chạy pure-VAE slice.
5. Chỉ thêm MI nếu pure-VAE dùng latent.
6. Chỉ thêm adversarial nếu pure-VAE+MI có evaluator ổn.
```

---

## 4. Việc không làm vòng đầu

```text
full Transformer VAE-GAN lớn
latent 448 chiều như Dasari ngay từ đầu
WGAN-GP
claim privacy nếu chưa có privacy/memorization test
claim controllability nếu chỉ có latent visualization
```

---

## 5. Deliverables research

```text
paper foundation pack
pure-VAE posterior-collapse report
MI/post-hoc alignment report
VAE-GAN vs pure-VAE ablation
negative result nếu adversarial không thắng
```

---

## 6. Câu chốt

```text
Nhánh VAE-GAN đáng nghiên cứu vì latent controllability là novelty cao nhất.
Nhưng phải xây từ nền: paper, label, pure-VAE, MI.
Adversarial là bước cuối có gate, không phải mặc định.
```
