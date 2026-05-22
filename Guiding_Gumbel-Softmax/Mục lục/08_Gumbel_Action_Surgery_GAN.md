# 08 — Gumbel Action-Surgery GAN

> Mục tiêu: train generator adversarial trên action/slot có kiểm soát, không sinh full sequence.

---

## 1. Giả thuyết

```text
Nếu giữ payload frame hợp lệ và chỉ dùng Gumbel để chọn action/slot,
thì adversarial signal có thể cải thiện action choice so với anchor-only
mà không lặp collapse full-sequence.
```

Giả thuyết này chỉ hợp lệ nếu Phase 01/04 chứng minh có action space phi-literal đủ tín hiệu.

---

## 2. Generator

Tên:

```text
GumbelActionGenerator
```

Input:

```text
payload_action_frame
mutation_vector
condition embedding
action history
```

Output:

```text
action family distribution
action argument distribution
stop/continue decision
```

Gumbel dùng cho:

```text
hard action forward
soft gradient backward
```

Không dùng cho:

```text
full token sequence generation
unbounded vocabulary softmax
```

---

## 3. Discriminator

Tên:

```text
PairedActionDiscriminator
```

Input:

```text
base_payload
mutated_payload
action_trace
condition
```

Loss vòng đầu:

```text
BCE hoặc hinge/RSGAN nhẹ
không WGAN-GP
```

RelGAN cho thấy Gumbel-text-GAN chạy được nhờ combo pretrain, loss phù hợp, D nhiều representation và lịch temperature; không phải nhờ Gumbel đơn lẻ. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:22-30`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 4. Loss

```text
L_G =
  L_anchor_action
+ lambda_adv * L_adv
+ lambda_entropy * L_action_entropy
+ lambda_validity * L_invalid_action
+ lambda_novelty * L_near_copy
```

Mặc định:

```text
lambda_adv nhỏ
anchor luôn bật
entropy floor không tắt
novelty theo cluster/action trace
```

---

## 5. Temperature policy

Không làm sắc phân phối quá nhanh.

Kế hoạch:

```text
tau_start = 1.0
tau_min = 0.5
anneal chậm theo entropy/validity gate
kill nếu action_entropy tụt đột ngột
```

Lưu ý: khi diễn giải RelGAN, không nên nói đơn giản "Phase 2 sai hướng"; diễn giải chính xác hơn là Phase 2 làm sắc phân phối khi chưa có action space/regularizer phù hợp, dẫn tới mất exploration.

---

## 6. Stop rule

Dừng nếu:

```text
action_entropy collapse
unique_ratio < 0.10
validity tụt dưới floor
D acc > 0.90 kéo dài
adv gain không vượt anchor-only
near_copy tăng bất thường
runtime không phù hợp multi-seed
```

---

## 7. Output

```text
models/gumbel/action_surgery_gan_seed_*/best.pt
eval/gumbel/action_gan_seed_*/metrics.json
eval/gumbel/action_gan_comparison.json
reports/gumbel/08_gumbel_action_surgery_gan.md
```

---

## 8. Kết luận

Phase 08 chỉ thành công nếu adversarial cải thiện action choice sau khi đã kiểm soát anchor, evaluator và seed variance. Nếu không, giữ D-as-scorer/MLE.
