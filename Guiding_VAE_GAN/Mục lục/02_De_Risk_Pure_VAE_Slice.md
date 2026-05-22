# 02 — De-risk Pure-VAE Slice

> Mục tiêu: kiểm tra pure-VAE có reconstruct và dùng latent z thật sự hay không trước khi thêm adversarial.

---

## 1. Vì sao pure-VAE đứng trước

VAE-GAN chỉ có ý nghĩa nếu VAE không posterior-collapse. Phản biện đã nêu: trên 6GB, VAE text nhỏ + decoder tự hồi quy mạnh rất dễ làm `KL -> 0`, decoder bỏ qua z. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:53-58`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 2. Slice data

```text
5-10k train
1-2k dev
1-2k test
partial delex span-preserving
3-4 condition chính nếu đủ label
```

Nếu nhãn chưa sạch:

```text
train unsupervised/weakly conditional
đo post-hoc alignment trên verified subset
```

---

## 3. Model slice

```text
encoder: LSTM/Transformer nhỏ
z_dim: 64
decoder: cố tình nhỏ hơn anchor MLE
loss: reconstruction + KL annealing/free-bits nếu có nguồn
```

Lưu ý: các kỹ thuật KL/free-bits cần paper nền Bowman/Kingma trước khi viết claim chính thức. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:21-34`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 4. Metrics

```text
reconstruction_exact_or_canonical
syntax/parse success
round_trip_success
KL mean
active latent dimensions
latent traversal validity
condition/post-hoc alignment
near_copy_rate
```

---

## 5. Gate G0

Pure-VAE slice pass nếu:

```text
reconstruction >= ngưỡng đăng ký
syntax/parse không tụt dưới floor
KL không collapse về 0
active dims > ngưỡng tối thiểu
latent interpolation tạo payload còn hợp lệ ở tỷ lệ đáng kể
```

Fail nếu:

```text
decoder bỏ qua z
reconstruction chỉ là memorization
latent traversal invalid
condition/post-hoc alignment không đo được
```

---

## 6. Output

```text
models/vae_gan/slice/pure_vae.pt
eval/vae_gan/slice/pure_vae_metrics.json
reports/vae_gan/02_de_risk_pure_vae_slice.md
```

---

## 7. Kết luận

Không thêm discriminator nếu pure-VAE chưa qua gate. Nếu pure-VAE fail, VAE-GAN sẽ chỉ khuếch đại lỗi.
