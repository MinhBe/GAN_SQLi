# 06 — Evaluator And Model Separation

> Mục tiêu: định nghĩa evaluator cho latent/reconstruction/controllability, tách khỏi discriminator.

---

## 1. Metric groups

### 1.1. Reconstruction/Validity

```text
reconstruction_exact
canonical_reconstruction
round_trip_success
parse_success
slot_relex_success
```

### 1.2. Latent usage

```text
KL mean/std
active dimensions
latent mutual information proxy
interpolation validity
posterior collapse indicator
```

### 1.3. Controllability

```text
conditional accuracy
post-hoc alignment
latent traversal consistency
condition_ignore_rate
factor shortcut diagnostic
```

### 1.4. Diversity/Novelty

```text
unique_ratio
self_bleu3
template_entropy
exact_copy_rate
near_copy_rate
cluster_novelty
```

---

## 2. Adversarial evaluator policy

Discriminator/critic không được là evaluator cuối.

```text
D chỉ là training signal hoặc feature-matching source.
Final decision dựa trên evaluator frozen.
```

Không dùng WGAN-GP vòng đầu, kể cả trên embedding, vì ràng buộc 6GB và vì phản biện đã chọn feature-matching/critic nhẹ. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:60-62`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 3. Output

```text
eval/vae_gan/evaluator_config.json
eval/vae_gan/latent_metric_protocol.md
reports/vae_gan/06_evaluator_model_separation.md
```

---

## 4. Kết luận

Evaluator của VAE-GAN phải đo thứ mà nhánh tuyên bố: latent có được dùng không, điều khiển được không, và payload decoded có còn hợp lệ không.
