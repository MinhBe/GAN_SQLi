# 03 — Decision Gate

> Mục tiêu: khóa cổng quyết định cho pure-VAE, MI controllability và adversarial VAE-GAN.

---

## 1. Ba quyết định riêng

```text
G0: Pure-VAE có dùng latent thật không?
G1: MI/condition có tạo controllability đo được không?
G2: Adversarial VAE-GAN có thắng pure-VAE không?
```

Không gộp ba câu hỏi này thành một composite.

---

## 2. Gate G0 — Pure-VAE

Pass nếu:

```text
reconstruction pass
validity pass
KL/active dims không collapse
near-copy không tăng bất thường
latent interpolation còn hợp lệ
```

Fail thì dừng nhánh adversarial.

---

## 3. Gate G1 — Controllability/MI

Có hai đường:

```text
A supervised: c = technique/db verified labels
B unsupervised: c tự khám phá factor, map post-hoc
```

InfoGAN cho phép học factor không giám sát, nên đường B có thể né nhãn yếu; nhưng factor có thể chỉ là length/keyword density, không phải technique. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:41-48`](..\03_Phan_Tich_Sau_Tu_Paper.md)

Pass nếu:

```text
latent traversal thay đổi output có kiểm soát
post-hoc alignment với verified labels vượt baseline
condition_ignore_rate thấp
factor không chỉ là length/template shortcut
```

---

## 4. Gate G2 — Adversarial

VAE-GAN pass nếu:

```text
VAE-GAN > pure-VAE trên frontier đã đăng ký
không giảm validity/reconstruction dưới floor
không tăng near-copy
không làm KL/latent usage collapse
multi-seed mean/CI ủng hộ kết luận
```

Tie-break:

```text
VAE-GAN hòa pure-VAE -> chọn pure-VAE.
```

Xu 2019 là cơ sở giữ gate này vì TVAE có thể outperform CTGAN ở nhiều dataset. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:8-13`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 5. Output

```text
eval/vae_gan/phase03/pure_vae_gate.json
eval/vae_gan/phase03/mi_gate.json
eval/vae_gan/phase03/adversarial_gate.json
reports/vae_gan/03_decision_gate.md
```

---

## 6. Kết luận

VAE-GAN chỉ được gọi là thành công nếu cả latent và adversarial đều chứng minh giá trị. Nếu chỉ pure-VAE/MI tốt, kết luận đúng là **controllable VAE**, không phải VAE-GAN thắng.
