# 08 — VAE-GAN Adversarial Challenger

> Mục tiêu: kiểm tra adversarial/feature-matching có cải thiện pure-VAE hay không.

---

## 1. Điều kiện mở Phase 08

Chỉ mở nếu:

```text
pure-VAE pass G0
MI/condition protocol đã định nghĩa
evaluator frozen
paper nền tối thiểu đã bổ sung hoặc claim được hạ cấp rõ
```

---

## 2. Kiến trúc

```text
Encoder/Decoder từ Phase 07
Discriminator/critic nhẹ trên latent hoặc decoder hidden features
Feature matching loss
Không WGAN-GP vòng đầu
```

Text GAN survey/ARAE direction ủng hộ làm adversarial trong latent/continuous space thay vì token rời rạc. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:52-58`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 3. Loss

```text
L_total =
  L_reconstruction
+ beta_KL * KL
+ lambda_MI * L_MI
+ lambda_fm * L_feature_matching
+ lambda_adv * L_adv
```

Nguyên tắc:

```text
lambda_adv nhỏ
reconstruction không tắt
KL/active dims vẫn phải log
```

---

## 4. Ablation bắt buộc

```text
A0 Conditional MLE
A1 pure-VAE
A2 pure-VAE + MI
A3 VAE + feature matching
A4 VAE-GAN full
```

Không claim adversarial nếu A4 không hơn A1/A2.

---

## 5. Stop rule

Dừng nếu:

```text
validity/reconstruction giảm dưới floor
KL collapse sau khi thêm D
latent traversal mất ý nghĩa
near-copy tăng
adversarial chỉ cải thiện D score nhưng không cải thiện evaluator
```

---

## 6. Output

```text
models/vae_gan/adversarial_seed_*/best.pt
eval/vae_gan/adversarial_comparison.json
reports/vae_gan/08_vae_gan_adversarial_challenger.md
```

---

## 7. Kết luận

VAE-GAN chỉ là challenger của pure-VAE. Nếu adversarial không thắng, kết luận đúng là pure-VAE/MI là hướng chính, VAE-GAN là negative result.
