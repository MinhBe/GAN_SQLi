# 07 — Pure-VAE Warmup Và MI

> Mục tiêu: xây baseline chính của nhánh: pure-VAE có latent dùng được, sau đó thêm MI controllability nếu pass.

---

## 1. Model

```text
Encoder: LSTM/Transformer nhỏ
z_dim: 64 trước, 128 nếu pass
Decoder: nhỏ hơn anchor MLE
Condition embedding: optional, tùy label readiness
```

Dasari dùng latent `448`, nhưng analysis ghi compute cost cao; với 6GB, không bắt đầu bằng cấu hình lớn. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16`](..\..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md)

---

## 2. Warm-up loss

```text
L = reconstruction + beta_KL * KL
```

Kỹ thuật như KL annealing/free-bits chỉ đưa vào claim chính thức sau khi bổ sung paper nền còn thiếu. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:58`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 3. MI head

Sau khi VAE pass G0:

```text
Q-head dự đoán c từ output/latent
MI lower-bound loss
lambda_MI khoảng 1 cho discrete code nếu dùng InfoGAN-style
```

InfoGAN cho thấy generator có thể bỏ qua code c nếu không cưỡng chế MI. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:34-36`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 4. Training order

```text
07A pure-VAE no MI
07B pure-VAE + supervised condition nếu label đủ sạch
07C pure-VAE + unsupervised MI
07D post-hoc alignment report
```

---

## 5. Gate

Pass nếu:

```text
KL/active dims không collapse
reconstruction/validity pass
latent traversal validity pass
MI/post-hoc alignment vượt baseline
near-copy không tăng bất thường
```

---

## 6. Output

```text
models/vae_gan/pure_vae_seed_*/best.pt
models/vae_gan/pure_vae_mi_seed_*/best.pt
eval/vae_gan/pure_vae_frontier.json
reports/vae_gan/07_pure_vae_warmup_and_mi.md
```

---

## 7. Kết luận

Nếu Phase 07 pass, luận văn đã có một đóng góp hợp lệ: controllable/reconstructive latent model. Adversarial chỉ là bước thử thêm.
