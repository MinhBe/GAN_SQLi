# 00 — Tổng Quan Kiến Trúc VAE-GAN

> Mục tiêu: viết lại nhánh VAE-GAN thành bộ kế hoạch modular giống `Guiding/Mục lục`, nhưng cập nhật theo phản biện mới: **pure-VAE và controllability là lõi; adversarial chỉ là thí nghiệm có gate**.

---

## 1. Định hướng đã chốt

Nhánh VAE-GAN không nên bắt đầu bằng full VAE-GAN.

Kiến trúc chốt:

```text
Partial delex / span-preserving dataset
→ pure conditional VAE warm-up
→ posterior-collapse gate
→ MI controllability head
→ adversarial/feature-matching chỉ khi pure-VAE pass
→ final ablation pure-VAE vs VAE-GAN vs MLE
```

Lý do: TVAE có thể thắng CTGAN ở nhiều dataset; vì vậy adversarial không tự động tốt hơn VAE thuần. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:8-13`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 2. Luồng tổng thể

```text
01 Data Reality + Label Readiness
        ↓
02 De-risk Pure-VAE Slice
        ↓
03 Decision Gate
        ↓
04 Full Data Foundation + Partial Delex
        ↓
05 Label/Condition Calibration
        ↓
06 Evaluator & Model Separation
        ↓
07 Pure-VAE Warm-up + MI
        ↓
08 VAE-GAN / Adversarial Challenger
        ↓
09 Final Evaluation & Delivery
        ↑
10 Literature/Implementation Roadmap
```

---

## 3. Danh sách phase

| Số | Phase | Vai trò |
|---:|---|---|
| 01 | Data Reality + Label Readiness | xác định dữ liệu/nhãn đã đủ cho controllability chưa |
| 02 | De-risk Pure-VAE Slice | kiểm tra posterior collapse sớm |
| 03 | Decision Gate | pure-VAE gate, MI gate, adversarial gate |
| 04 | Full Data Foundation + Partial Delex | dataset latent/reconstruct được |
| 05 | Label/Condition Calibration | giảm rủi ro MI học shortcut |
| 06 | Evaluator & Model Separation | metric controllability/novelty/validity |
| 07 | Pure-VAE Warm-up + MI | main baseline của nhánh |
| 08 | VAE-GAN / Adversarial Challenger | chỉ mở nếu Phase 07 pass |
| 09 | Final Evaluation & Delivery | kết luận pure-VAE, MI, adversarial |
| 10 | Literature/Implementation Roadmap | bổ sung paper nền còn thiếu |

---

## 4. Nguyên tắc bất biến

```text
1. Tải paper nền VAE-GAN/VAE/posterior collapse trước khi viết claim học thuật.
2. Pure-VAE phải pass gate trước khi thêm discriminator.
3. VAE-GAN phải thắng pure-VAE mới claim adversarial có ích.
4. Controllability phải đo được, không chỉ nhìn latent traversal.
5. Nếu dùng unsupervised MI, phải map post-hoc với verified labels.
6. Không WGAN-GP vòng đầu; dùng feature matching/critic nhẹ trên latent/embedding.
7. Decoder không được quá mạnh đến mức bỏ qua z.
8. Tie với pure-VAE hoặc MLE thì chọn baseline đơn giản hơn.
```

---

## 5. Kết luận kiến trúc

VAE-GAN có trần novelty cao nhất vì có latent interpolation/disentanglement, nhưng rủi ro nền cũng cao nhất: thiếu paper nền, nhãn yếu, posterior collapse. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:118-127`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

Vì vậy nhánh này nên đi theo thứ tự:

```text
paper nền → label calibration → pure-VAE pass → MI controllability → adversarial gate
```
