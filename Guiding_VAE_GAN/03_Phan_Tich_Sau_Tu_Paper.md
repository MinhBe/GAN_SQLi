# 03 — Phân tích sâu từ paper (nhánh VAE-GAN)

> **Ngày:** 2026-05-22 · **Vai trò:** đọc *sau* `00/01/02`. Trích **nội dung OCR gốc** trong `Asset/Total_OCR1` để chốt quyết định kỹ thuật bằng dòng cụ thể.
> Trục paper cho nhánh này: **TVAE/CTGAN** (Xu 2019 — pure-VAE vs VAE+adversarial trên dữ liệu rời rạc-có-điều-kiện), **InfoGAN** (Chen 2016 — cơ chế controllability/disentanglement), và nhắc lại lỗ hổng paper nền (PB1 của `02`).

---

## 1. TVAE vs CTGAN (Xu 2019): bằng chứng mạnh cho gate "VAE-GAN phải thắng pure-VAE"

Đây là so sánh trực tiếp nhất ta có giữa **VAE thuần** (TVAE) và **GAN có điều kiện** (CTGAN) trên cùng dữ liệu rời rạc/hỗn hợp:

- **TVAE thắng CTGAN ở nhiều dataset:** "TVAE outperforms CTGAN in several cases". [`Asset\Total_OCR1\Xu_2019_CTGAN.md:651`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) Bảng benchmark real-data: **TVAE clf = 0.519 > CTGAN = 0.469** (và TVAE reg −0.20 > CTGAN −0.43). [`Asset\Total_OCR1\Xu_2019_CTGAN.md:616-629`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) ⇒ **bằng chứng paper khách quan** rằng thêm adversarial *không tự động* tốt hơn VAE thuần. Củng cố trực tiếp gate G1 của `00` (full VAE-GAN phải thắng pure-VAE) và lựa chọn "tie → pure-VAE".
- **Nhưng GAN có giá trị khác (không phải chất lượng):** ưu thế của GAN là **privacy** — generator không nhìn dữ liệu thật suốt train nên đạt differential privacy dễ hơn TVAE. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:651-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) ⇒ nếu adversarial không thắng về chất lượng, vẫn có thể claim **privacy/anti-memorization** — một góc đóng góp trung thực cho phần adversarial.

### 1.1 Conditional generator + training-by-sampling = chìa khóa cho class hiếm (rất hợp ô hiếm của ta)

CTGAN xử lý mất cân bằng bằng **conditional vector + training-by-sampling theo log-tần suất**. Ablation:
- Bỏ training-by-sampling (`w/o S.`) → **F1 về 0%** trên dataset cực lệch (credit). [`Asset\Total_OCR1\Xu_2019_CTGAN.md:669-675`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)
- Bỏ luôn conditional vector (`w/o C.`) → **−36.5%** hiệu năng. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:700`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

⇒ Với corpus ta cực lệch (`error_based`=405, `db_hint` 78% unknown — `00` D.3), đây là **bằng chứng định lượng** rằng conditional sampling theo log-tần suất là *bắt buộc*, không phải tùy chọn (khớp hướng #6/#7 của `02`).

### 1.2 Hai cảnh báo khi mượn TVAE/CTGAN

- **Đây là dữ liệu TABULAR, không phải chuỗi token.** Continuous column được chuẩn hóa mode-specific (VGM) rồi mới sinh; MinMax norm làm tệ −25.7%. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:664-698`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) WGAN-GP "+1.75%" mà CTGAN báo là trên **không gian liên tục đã chuẩn hóa**, *không* phải token rời rạc → **không** dùng điều này để biện minh WGAN-GP cho payload (giữ PB5 của `02`).
- **TVAE/CTGAN cần xử lý biến rời rạc bằng relaxation có đạo hàm.** CTGAN dùng cơ chế relaxation cho cột rời rạc, còn TVAE encoder/decoder chỉ 128-128 FC, Adam 1e-3. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:371-373`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:422-464`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

---

## 2. InfoGAN (Chen 2016): cơ chế controllability — và một ngã rẽ quan trọng cho nhánh

Controllability là novelty cốt lõi của nhánh (`00` B/D.6). InfoGAN cho cơ chế chính xác để đạt nó — kèm một lựa chọn thiết kế mà `00/01` đang **bỏ ngỏ**:

- **Vấn đề "trivial code" = bản sao của posterior collapse cho controllability:** trong GAN thường, generator **tự do bỏ qua** code c (`PG(x|c)=PG(x)`). [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:141-142`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:279`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) ⇒ "latent điều khiển được" **không tự nhiên có** — phải cưỡng chế. (Đây đúng là rủi ro `02` PB4 nói, nhìn từ phía code thay vì phía KL.)
- **Cưỡng chế bằng mutual information** `I(c;G(z,c))` qua cận dưới biến phân `LI(G,Q)`, Q là mạng phụ chia sẻ lớp với D → "comes for free", hội tụ nhanh hơn cả GAN objective. [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:143-160`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:191-218`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md)
- **Siêu tham số dễ chỉnh:** `λ=1` cho code rời rạc, λ nhỏ hơn cho liên tục. [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:222-225`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md)
- **Bằng chứng disentanglement đo được:** code phân loại c1 đạt **5% error như một classifier không giám sát** trên MNIST; c2/c3 điều khiển góc nghiêng/độ rộng. [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:285-291`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md)

### 2.1 Ngã rẽ mà nhánh phải chốt (NEW — chưa nói trong 00/01/02)

**InfoGAN học disentanglement KHÔNG cần nhãn** — nó *khám phá* factor một cách không giám sát. [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:139-140`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:304-306`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) Điều này tạo **hai con đường khác nhau** cho controllability của ta:

| Con đường | Cách làm | Ưu | Nhược |
|---|---|---|---|
| **(A) Có giám sát** — condition trên `technique_primary` | đưa nhãn vào làm c, ép G tái tạo nhãn (kiểu CTGAN cross-entropy) | semantic rõ ("đây là dim điều khiển kiểu attack") | **phụ thuộc nhãn yếu** (PB3: Phase 5 30.58%, verified 504/468) → MI học shortcut sai |
| **(B) Không giám sát** — InfoGAN MI thuần | để MI tự khám phá factor, **map sang technique post-hoc** | **né được nhãn yếu** — không cần label sạch khi train | factor khám phá có thể là độ dài/mật độ keyword, **không khớp** technique → controllability "có" nhưng không theo trục ta muốn |

⇒ **Khuyến nghị mới:** thử **(B) trước** (vì nó không bị chặn bởi nhãn yếu — điểm nghẽn lớn nhất của nhánh theo `02` PB3), đo xem factor khám phá có *tình cờ* khớp technique/db không; nếu cần đúng trục technique thì mới chuyển sang (A) trên *verified split* sạch. Đây là cách dùng InfoGAN để **vòng tránh** điểm yếu nhãn, thay vì đâm thẳng vào nó. Lưu ý chính InfoGAN ghi: "core idea... can be applied to other methods like **VAE**, a promising area of future work" [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:376-377`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) → tức MI-regularized VAE chính là một dạng VAE-GAN-controllable hợp lệ.

---

## 3. Xương sống lý thuyết cho "GAN trên text rời rạc qua latent" — và lỗ hổng còn nguyên

Survey và related-work xác nhận hướng đi latent của nhánh là một *trường phái chính thống*:
- VAE = encoder nén input vào **latent space**, generator sinh từ latent. [`Asset\Total_OCR1\Zhang_2020_Adversarial_Text_Survey.md:396-397`](..\Asset\Total_OCR1\Zhang_2020_Adversarial_Text_Survey.md)
- **ARAE** (Adversarially Regularized Autoencoder) "applies an additional autoencoder to embed the discrete data into a **continuous latent space in which GANs can be trained properly**". [`Asset\Total_OCR1\Nie_2019_RelGAN.md:702-704`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) → đây **chính là** ý tưởng VAE-GAN cho text rời rạc: tránh token rời rạc bằng cách adversarial *trong latent*. Củng cố lựa chọn "critic trên latent/embedding" của `00`.

**Nhưng PB1 của `02` vẫn đứng nguyên:** ARAE/TVAE/InfoGAN là *họ hàng*, không phải paper định danh **VAE-GAN của Larsen 2016**, cũng không có **Kingma (VAE)**, **Bowman 2016 (KL-annealing/posterior collapse)**, **β-VAE (disentanglement)** trong `Asset/Total_OCR1` (55 file). [`Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md:9-12`](..\Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md) Mọi mệnh đề về *free-bits, KL-annealing schedule, β-disentanglement metric* của `00` (F.06, F.10) hiện **chưa có nguồn gốc trong corpus** → vẫn phải tải (skill `sci-paper-downloader`) trước khi viết, nếu không là citation rỗng.

---

## 4. Tổng hợp: paper thay đổi gì trong kế hoạch nhánh VAE-GAN

| Vấn đề trong `00/02` | Paper | Hành động |
|---|---|---|
| Gate "VAE-GAN > pure-VAE" có cơ sở không? | TVAE > CTGAN nhiều dataset (0.519>0.469) | **Giữ gate G1 cứng**; nếu adversarial thua, claim privacy/anti-memorization (ưu thế GAN theo Xu) |
| Controllability bị chặn bởi nhãn yếu (PB3) | InfoGAN disentangle **không cần nhãn** | Thử **đường (B) unsupervised-MI trước**, map technique post-hoc; (A) chỉ trên verified split |
| Class hiếm (error_based=405) | CTGAN ablation: bỏ sampling → F1 0% | conditional + log-frequency training-by-sampling **bắt buộc** |
| WGAN-GP có dùng được không? | CTGAN "+1.75%" là trên continuous tabular, không phải token | **Không** WGAN-GP token; feature-matching/critic-trên-latent (ARAE) |
| Posterior/trivial-code collapse | InfoGAN: G tự do bỏ qua c; cần MI cưỡng chế | MI head (λ=1 rời rạc) + free-bits; gate KL của `00` F.06 giữ nguyên |
| Paper nền thiếu (PB1) | Larsen/Kingma/Bowman/β-VAE **vẫn vắng** | **Tải trước khi viết**; tạm dùng ARAE/TVAE/InfoGAN làm chỗ dựa lý thuyết |

## 5. Cập nhật đánh giá khả thi (sau paper)

| Mục tiêu | `02` | `03` | Lý do |
|---|---:|---:|---|
| Pure-VAE qua gate posterior-collapse (6GB) | 0.55 | **0.55** | TVAE nhỏ (128-128) khả thi; collapse vẫn là rủi ro thật. |
| Adversarial thắng pure-VAE (G1) | 0.40 | **0.35** | TVAE>CTGAN nhiều case → adversarial khó thắng. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:651`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| Controllability đo được | 0.45 | **0.55** | InfoGAN MI **không cần nhãn** → né được PB3; có metric disentanglement rõ. |
| Độ sẵn sàng học thuật (paper nền) | 0.40 | **0.40** | PB1 chưa được giải; phải tải paper. |

> **Kết luận nhánh (cập nhật):** đọc paper **không nâng nhiều** độ khả thi *adversarial thắng* (TVAE>CTGAN là phản chứng mạnh), nhưng **mở một lối thoát cho novelty controllability**: dùng **InfoGAN-MI không giám sát** để né điểm nghẽn nhãn (PB3), rồi map sang technique post-hoc. Đường an toàn nhất của nhánh vẫn là **pure-VAE + conditional + training-by-sampling + MI head**, với adversarial là *thí nghiệm có gate* (G1) chứ không phải mặc định. Và việc cần làm *trước tiên* không đổi: **tải Larsen/Kingma/Bowman/β-VAE** (PB1) — đây là điều kiện sống còn để các claim của nhánh có nguồn.
