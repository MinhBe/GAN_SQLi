# Kế Hoạch Tổng Thể (All-in-One) — Nhánh VAE-GAN (Latent Controllable)

> **Ngày:** 2026-05-22 · **Phần cứng:** RTX 3050 6GB + 20GB RAM · **Repo:** `C:\Users\Admin\Documents\GAN_SQLi`
> **Nguồn:** `Guiding/Kịch bản/VAE-GAN_SQLi_Guiding.md` (bản gốc 05-04) + nền V5
> (`Guiding/Phase 1,2`, `Guiding/Mục lục/00–10`, `Kết luận 1.md`, kết quả Phase 3/3.5).
> Điều hướng nhanh: xem `Mục lục.md`.

---

## A. Mục lục

- **B.** Bối cảnh & phạm vi nhánh VAE-GAN
- **C.** Đính chính bản VAE-GAN gốc (giữ gì / bỏ gì / thay gì)
- **D.** Phân tích đa góc độ (7 góc)
- **E.** Kiến trúc chốt của nhánh
- **F.** Roadmap phase 00–10 (mục tiêu / deliverable / gate / files)
- **G.** Gate pre-registered + chống tự lừa
- **H.** Tài nguyên 6GB, timeline, cây deliverable

---

## B. Bối cảnh & phạm vi

Luận văn **bắt buộc có GAN trung tâm**. Trong thư mục này, nhánh được xét là VAE-GAN với một trục đóng góp riêng:
**điều khiển qua latent**.

| Trục đóng góp | Điểm mạnh | Điểm yếu chính |
|---|---|---|
| Điều khiển qua latent | controllability/disentanglement; interpolation; conditional generation | nặng trên 6GB; posterior collapse; phụ thuộc paper/label readiness |

**Vị thế nhánh này:** VAE-GAN là **GAN không thể chối cãi** (đúng nghĩa "có GAN trong luận văn") **cộng**
một năng lực mới mà các hướng kia không có: **sinh có điều khiển** — cho z điều khiển kiểu attack
(`technique_primary`) và độ ngụy trang, interpolate giữa 2 payload, tách cluster "SQL thuần" vs "ngụy
trang". Đây là novelty chính của nhánh — **nếu chạy được trên 6GB**.

Nhánh này tái dùng nền chung từ `Guiding` khi cần: data Phase 1/4, label Phase 5, evaluator Phase 6 và literature Phase 10.

---

## C. Đính chính bản VAE-GAN gốc

**Hai vấn đề phải bỏ:**
1. **Path/dữ liệu chết:** `C:\Users\Admin\Documents\GAN`, `master_sqli.csv`, data 41.460 dòng — không còn;
   thay bằng nền V5 (slice 38.906 dòng đã gán nhãn).
2. **WGAN-GP trên token rời rạc:** loss adversarial của bản gốc dùng WGAN-GP với nội suy
   `x̂ = εx + (1−ε)x̃` trên token rời rạc — **sai bản chất** và là một phần của RC1 (D bão hòa) đã thấy
   ở Phase 3/3.5. Phải thay bằng feature-matching (đã có sẵn trong doc) + critic hinge thận trọng, **không** GP.

**Phần giữ lại (giá trị thật):**
- **Encoder → latent z có cấu trúc** → controllability (đóng góp lõi).
- **Reconstruction loss** = **mỏ neo ground-truth mạnh nhất** trong 3 nhánh → chống RC2 (G trôi khỏi cú pháp).
- **Feature matching loss** = đòn bẩy chống D-saturation (so khớp thống kê đặc trưng thay vì để D thắng tuyệt đối) → giảm RC1.
- **KL annealing + free bits** → chống posterior collapse.
- **δ-correlation experiment** (constraint density) — thí nghiệm khoa học trung thực, "demonstrate
  tradeoff, không prove VAE-GAN luôn thắng".

**Phần thay/nâng cấp:**
- Validity đo bằng **evaluator thực thi** (parse + execute + injection-structure), không phải "có keyword".
- WAF Evasion Rate (WER) hạ xuống **metric phụ** (theo nguyên tắc V5: không tin WAF/DB khi relex chưa đủ tốt).
- Kiến trúc **thu nhỏ mạnh** cho 6GB (xem §D.4, §E).
- Kỷ luật: warm-up gate posterior-collapse, multi-seed, anti-cherry-pick, ablation pure-VAE.

---

## D. Phân tích đa góc độ

### D.1 Góc khoa học / phương pháp luận
Bản gốc đã có khung trung thực: **δ-correlation** (khi constraint density δ cao, baseline có cấu trúc
cạnh tranh VAE-GAN ở chi phí thấp hơn → đo *tradeoff*, không tuyên bố VAE-GAN luôn thắng) + sample
efficiency + main comparison. **RQ riêng của nhánh này** nên xoay quanh *controllability*:
- **RQ1**: latent z có tách được kiểu attack / độ ngụy trang không (disentanglement đo được)?
- **RQ2**: conditional generation `G(z, technique, db)` đạt độ chính xác điều kiện bao nhiêu?
- **RQ3**: thành phần adversarial (full VAE-GAN) có cải thiện gì so với **pure-VAE** trên chất lượng/đa
  dạng/controllability — hay recon+KL đã đủ?

### D.2 Góc kiến trúc
- **Recon anchor = ưu thế lớn nhất:** khác GAN thuần (chỉ có tín hiệu D), VAE-GAN buộc decoder tái tạo
  payload thật → neo chặt vào cú pháp hợp lệ ⇒ chống RC2 tốt nhất trong 3 nhánh.
- **Feature matching > WGAN-GP critic** ở đây: so khớp thống kê đặc trưng của D ổn định hơn, ít D-saturation (RC1).
- **Latent có cấu trúc** = nơi sinh ra controllability (interpolate, conditional, disentangle).
- **Failure mode MỚI: posterior collapse** (KL→0, encoder bị bỏ qua, z vô dụng) — không có ở 2 nhánh kia
  → phải có warm-up gate + KL annealing + free bits.

### D.3 Góc dữ liệu (đã xác minh trên `slice_labeled.parquet`, 38.906 dòng)
- Bản gốc giả định **partial de-lex** (giữ keyword + ~30 hàm tấn công + ký tự đặc biệt; mask `<TABLE>`,
  `<COL>`, `<NUM>`, `<STR>`). Nhưng delex hiện có **chỉ** có `__NUM__` (×36.876), `__STR__` (×33.744),
  `__TIME__` (×354); **không** mark `<TABLE>/<COL>` riêng, và `placeholder_types` 99,3% rỗng.
- ⇒ Phase 04 phải **dựng lại partial de-lex span-preserving** từ `delex_v2` (whitelist ~30 hàm + keywords
  giữ nguyên; mask identifier/literal), thống nhất token, vệ sinh rác.
- Encoder học cấu trúc từ `payload_delex` → chất lượng latent phụ thuộc độ đa dạng dữ liệu; mất cân bằng
  (`error_based`=405, `db_hint` 78% unknown) làm controllability ở ô hiếm yếu → gộp/thu hẹp điều kiện.

### D.4 Góc tài nguyên (RTX 3050 6GB) — RỦI RO CHÍNH CỦA NHÁNH NÀY
VAE-GAN bản gốc là **nặng nhất**: Transformer encoder 4–6 lớp + decoder 4–6 lớp + 1D-CNN D + WGAN-GP
(`create_graph` nhân đôi bộ nhớ), latent 256, batch 64, 100k steps. **Khó/không chạy nổi full-spec trên
6GB.** Bắt buộc thu nhỏ:
```text
- Encoder/decoder: LSTM hoặc Transformer mini (2 lớp, d_model 128) thay 4–6 lớp/256.
- Latent z: 64–128 thay 256.
- Bỏ WGAN-GP GP → dùng feature-matching (+ critic hinge nhẹ) → tiết kiệm create_graph.
- Batch 16–32, gradient checkpointing nếu cần.
- Warm-up VAE (không D) rẻ; pha adversarial mới tốn.
```
Nếu sau khi thu nhỏ vẫn không đạt gate chất lượng → đó là **kết quả hợp lệ** ("VAE-GAN không khả thi ở
ngân sách 6GB cho domain này"), không phải thất bại cá nhân.

### D.5 Góc rủi ro & kết cục dễ xảy ra
- **Posterior collapse** (KL→0) — khả dĩ nếu decoder mạnh; mitigations: annealing, free bits, giảm capacity decoder.
- **4-loss khó cân** (recon/KL/adv/fm) → variance cao; theo dõi gradient norm.
- **Kết cục khả dĩ:** pure-VAE ≈ full VAE-GAN (adversarial thêm ít) HOẶC controllability yếu ở ô hiếm.
  → pre-commit khung: nếu vậy, đóng góp = *đặc tả δ-tradeoff + controllability có/không + recon-anchor chống collapse*.

### D.6 Góc đóng góp luận văn (GAN bắt buộc trung tâm)
Mạnh nhất 3 nhánh **về novelty**: VAE-GAN là GAN rõ ràng + **controllability là năng lực mới** (conditional
attack-type/obfuscation, latent walk, disentanglement). Kể cả nếu adversarial thêm ít so với pure-VAE,
luận văn vẫn có: latent controllable + δ-tradeoff + so sánh đa phương pháp + chẩn đoán posterior collapse.

### D.7 Góc định vị nhánh
```text
VAE-GAN (đây): "điều khiển qua latent" — controllability/disentanglement/interpolation.
Trục quyết định: pure-VAE + MI có dùng latent thật không; adversarial có thêm giá trị không.
```

---

## E. Kiến trúc chốt của nhánh (đã thu nhỏ cho 6GB)

```text
                    ┌──────────────────────────────┐
   x (payload) ────▶│  Encoder (LSTM/Transformer    │──▶ μ, log σ²  ∈ R^{64–128}
   delex slot       │  mini, 2 lớp)                 │
                    └───────────────┬──────────────┘
                                    ▼   z = μ + σ·ε  (reparameterization)
                    ┌──────────────────────────────┐
   condition ──────▶│  Decoder + cross-attn vào z   │──▶ logits → differentiable token relaxation
 (technique,db)     │  (LSTM/Transformer mini)      │      → token (giữ khung partial-delex)
                    └───────────────┬──────────────┘
                                    ▼
            ┌───────────────────────────────────────────────────────┐
   recon ◀──┤  4 loss: L_recon (CE teacher-forcing, MỎ NEO)          │
   KL    ◀──┤        + β·L_KL (annealing 0→1, free bits 2 nats)      │
            │        + λ_adv·L_adv  (KHÔNG WGAN-GP; critic hinge nhẹ) │
   fm    ◀──┤        + γ·L_fm  (feature matching — chống D-saturation)│
            └───────────────────────────┬───────────────────────────┘
                                         ▼
                    ┌──────────────────────────────┐
                    │  Discriminator 1D-CNN [3,4,5] │  (LayerNorm, KHÔNG BatchNorm)
                    │  + feature layer (L-2)        │  D:G điều tiết + freeze khi quá mạnh
                    └──────────────────────────────┘

[2 pha]  Warm-up: chỉ recon+KL (gate posterior-collapse)  →  Adversarial: thêm D + fm
[Inference] z ~ N(0,I) hoặc z điều khiển → decoder → relex → Syntax-Filter → payload
```

**Composite Score (điều chỉnh):** `S = w1·Validity_exec + w2·(1−SelfBLEU3) + w3·(1−Ŵ1) + w4·Controllability`,
trong đó **Validity_exec** = parse + execute (sqlite) + giữ cấu trúc injection; **Controllability** =
độ chính xác conditional gen + điểm disentanglement. WER là cột phụ, chỉ báo cáo khi relex đủ tin.

---

## F. Roadmap phase 00–10

### F.00 — Tổng quan kiến trúc VAE-GAN
Chốt định hướng (§E), khóa giả thuyết & gate (§G). Deliverable: file này + `Mục lục.md`.

### F.01 — Nền dữ liệu *(tái dùng)*
`Guiding/Phase 1/phase01_data_reality.parquet` + kế hoạch `Guiding/Mục lục/04` (canonical, dedup,
near-dup, lane-aware strip, cluster-safe split). Gate: cluster leakage = 0.

### F.02 — Label & verified split *(tái dùng)*
Theo `Guiding/Mục lục/05`: `technique_primary` (điều kiện chính cho controllability), verified_dev/test.

### F.03 — Evaluator thực thi + Composite Score **(mới — cổng mọi đo lường)**
`evaluator_exec.py` (parse + execute sqlite + injection-structure + novelty + diversity) + thêm
**Controllability evaluator** (conditional accuracy theo `technique_primary`, disentanglement). WER = phụ.
Gate: phân biệt đúng known-valid/broken; oracle không treo. Deliverable: `eval/phase03/*`, `reports/03_*`.

### F.04 — Partial de-lex + VAE-GAN dataset **(mới)**
`partial_delex.py` (span-preserving: giữ keyword + ~30 hàm whitelist + ký tự đặc biệt; mask
identifier/literal; round-trip check) + `vae_dataset.py` (tuple `(x_delex, condition)`; vệ sinh rác; gộp
ô hiếm). Gate: round-trip ≥99% mẫu sạch; vocab ~200–300 frozen. Deliverable: `data/phase04/*` + hash.

### F.05 — Baseline: Conditional MLE + pure-VAE *(tái dùng + thêm)*
Tái dùng MLE (`Guiding/Phase 2,7`, frontier khóa: unique 0.803/self_bleu3 0.013/syntax 0.712). Thêm
**pure-VAE** (recon+KL, không adversarial) làm baseline ablation bắt buộc + KN-5/template/LSTM (nhẹ).
Deliverable: `eval/phase05/baselines_frontier.json`.

### F.06 — Warm-up VAE **(mới — gate posterior collapse)**
Train encoder+decoder chỉ với `L_recon + β·L_KL` (β annealing 0→1, free bits 2 nats). **Gate bắt buộc
trước khi sang F.07:** `KL ∈ [5,50] nats` VÀ `recon accuracy ≥ 70%` VÀ gradient norm ổn định. Nếu KL<5 →
tăng free bits / giảm capacity decoder. Deliverable: `models/vae_warmup/seed_*/`, `eval/phase06/warmup.json`.

### F.07 — Adversarial VAE-GAN **(centerpiece)**
Thêm D 1D-CNN + feature matching; `L = recon + β·KL + λ_adv·L_adv + γ·L_fm`; **KHÔNG GP** (critic hinge);
D:G điều tiết + freeze khi acc(D) quá cao. Pilot 1 seed → confirmatory ≥5 seed nếu qua gate. **Gate:**
full VAE-GAN phải thắng **pure-VAE (F.05)** trên Composite mới được claim adversarial có giá trị.
Deliverable: `models/vae_gan/seed_*/`, `eval/phase07/*`.

### F.08 — Controllability + Benchmark + δ-correlation **(mới)**
- **Controllability:** latent walk (interpolate 2 payload), conditional gen `G(z, technique, db)` đo
  accuracy, disentanglement (mỗi dim z điều khiển attribute gì).
- **Benchmark đa phương pháp** trên cùng frozen test + evaluator F.03: KN-5/template · LSTM · MLE ·
  pure-VAE · **VAE-GAN(mới)**.
- **δ-correlation** (thí nghiệm quan trọng nhất): vary constraint density → plot WER/Composite gap baseline vs VAE-GAN.
- **Sample efficiency:** {1k,5k,10k,50k} samples → learning curve.
Deliverable: `eval/phase08/{controllability,benchmark,delta_correlation,sample_efficiency}.json` + PNG.

### F.09 — Final evaluation & kết luận
Kết luận pre-committed, một trong ba:
```text
(a) Controllability + adversarial có giá trị rõ qua gate → đóng góp VAE-GAN trung tâm dương.
(b) Pure-VAE ≈ VAE-GAN / controllability yếu → đóng góp = latent + δ-tradeoff + recon-anchor (limited result có kiểm soát).
(c) Không khả thi trên 6GB sau thu nhỏ → ghi rõ ngân sách compute là rào cản; future work.
```
Deliverable: `eval/final/*`, `reports/09_final_evaluation_report.md`.

### F.10 — Literature mapping *(tái dùng + nhấn)*
`Guiding/Mục lục/10`; nhấn: `Larsen_2016_VAE_GAN` (gốc kiến trúc), Kingma VAE, `Bowman_2016` (KL
annealing/posterior collapse), β-VAE (disentanglement), InfoGAN/MI controllability, `Lu_2022_GAN_SQLi`.

---

## G. Gate pre-registered + chống tự lừa

```text
GATE CHÍNH (khóa trước khi train):
  G0  Warm-up: KL ∈ [5,50] nats VÀ recon ≥ 70% → mới được thêm D (chống posterior collapse).
  G1  Full VAE-GAN PHẢI thắng pure-VAE trên Composite → mới claim thành phần adversarial tạo giá trị.
  G2  Controllability đo được (conditional accuracy > chance + disentanglement có ý nghĩa).
  G3  Validity_exec(VAE-GAN) ≥ MLE×0.95 VÀ diversity ≥ baseline → mới tính "phá tradeoff".
  G4  no posterior-collapse & no mode-collapse trên ≥4/5 seed.
  G5  CI theo seed; tie → baseline đơn giản hơn (pure-VAE/MLE).

KHÔNG chấp nhận:
  - latent walk "nhìn đẹp" mà không có metric controllability.
  - WGAN-GP GP trên token rời rạc.
  - WER tăng nhưng Validity_exec/diversity verified giảm.
  - cherry-pick seed/checkpoint; metric keyword cũ.
```

---

## H. Tài nguyên 6GB, timeline, cây deliverable

**6GB (rủi ro chính):** model thu nhỏ (LSTM/Transformer mini 2 lớp, latent 64–128), bỏ GP, batch 16–32,
gradient checkpointing, warm-up rẻ → adversarial mới tốn. Smoke test phải xác nhận VRAM < 6GB trước khi train thật.

**Timeline ước lượng (tương đối):**
```text
F.03 evaluator + F.04 partial-delex data .... nặng (cổng đo lường)
F.05 baselines (MLE tái dùng + pure-VAE) .... vừa
F.06 warm-up VAE ............................ rẻ, nhưng phải qua gate posterior-collapse
F.07 adversarial pilot → multi-seed ......... PHA TỐN NHẤT trên 6GB; pilot 1 seed trước
F.08 controllability + benchmark + δ ........ sau khi pilot qua gate
```

**Cây deliverable:**
```text
Guiding_VAE_GAN/
  Mục lục.md
  00_Ke_Hoach_Tong_The.md            ← file này
data/phase04/vae_{train,dev,frozen_test}.parquet (+ .md5, vocab.json frozen)
data/phase05/{labeled,verified_dev,verified_test}.parquet
models/{mle_generator, vae_warmup/seed_*, vae_gan/seed_*}/
eval/{phase03,phase05,phase06,phase07,phase08,final}/*.json + *.png
reports/{03_evaluator, 04_partial_delex, 06_warmup, 09_final_evaluation}_report.md
```

---

> **Kết luận khung:** VAE-GAN là nhánh **GAN-trung-tâm có novelty cao nhất** (điều khiển qua latent) và
> **mỏ neo recon mạnh nhất** chống RC2 — nhưng cũng **nặng nhất trên 6GB** và có thêm rủi ro posterior
> collapse. Đi theo nhánh này nếu ưu tiên *năng lực điều khiển* và chấp nhận rủi ro compute; warm-up gate
> + ablation pure-VAE + δ-correlation giữ cho kết luận trung thực dù VAE-GAN thắng hay thua. Không lặp lại
> WGAN-GP/full-sequence đã fail; để evaluator và ablation quyết định, đúng kỷ luật `Guiding/Mục lục`.
