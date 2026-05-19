# MASTER PROBLEM-SOLUTION MATRIX — SeqGAN SQLi

> Tài liệu tổng hợp toàn bộ vấn đề kỹ thuật của bài toán SeqGAN SQLi và paper giải quyết tương ứng.
> Cập nhật: 2026-05-18 | Dựa trên phân tích 51 bài báo

---

## PHẦN 1 — BẢNG VẤN ĐỀ → GIẢI PHÁP

| # | Vấn Đề SeqGAN SQLi | Paper Giải Quyết | Kỹ Thuật Cụ Thể | Priority | Implemented? |
|---|---|---|---|---|---|
| 1 | **Mode collapse (REINFORCE reward ceiling)** — advantage→0, G freeze | Jang_2017_Gumbel; Maddison_2017_Concrete | Gumbel-Softmax STE: gradient luôn tồn tại dù reward ổn định | **P0** | Đang build (V5) |
| 2 | **Sparse reward (chỉ có ở end-of-sequence)** — early tokens không nhận gradient | Guo_2018_LeakGAN | Manager nhận D intermediate features mỗi step, không chỉ cuối | P1 | ✗ |
| 3 | **Monte Carlo roll-out cost O(N×T)** — prohibitive với T=80, N=16 | Jang_2017_Gumbel; Bengio_2013_STE | Gumbel-Softmax: không cần MC roll-out, backprop trực tiếp | **P0** | Đang build (V5) |
| 4 | **Conditional generation bị ignore** — type_accuracy ~45% sau 1000 steps | Chen_2016_InfoGAN | Q-network mutual information loss: phạt G nếu ignore condition | P1 | Xem xét (Guideline Phần 12) |
| 5 | **WAF bypass rate thấp (2%)** — G sinh payload không bypass OWASP CRS | Demetrio_2020_WAF_A_MoLE | 6 mutation operators post-processing: space, comment, case, URLencode | P1 | Guideline Phần 11 |
| 6 | **Dataset collision 71.89%** — delex V1 xóa 100% function names | Own pipeline | delex_v2 với function whitelist 50 tokens (proven: →4.33%) | **P0** | Build ngày 17/05 |
| 7 | **Wrapper bias 53.64%** — inner payload bị nuốt trong STR placeholder | Own pipeline | strip_wrapper.py trước delex | **P0** | Build ngày 17/05 |
| 8 | **Discriminator instability** — D loss oscillates, no Lipschitz constraint | Gulrajani_2017_WGAN_GP | Gradient Penalty λ=10, không dùng BatchNorm trong D | **P0** | Đã có (V3/V4) |
| 9 | **IDS evasion = 0% tại best checkpoint** — G không học evasion pattern | Lin_2018_IDSGAN | Adversarial perturbation nhắm vào IDS feature space | P2 | ✗ (Phase 3 reward) |
| 10 | **Long sequence quality drop** — SQL >30 tokens mất cấu trúc | Guo_2018_LeakGAN; Nie_2019_RelGAN | LeakGAN: Manager-Worker hierarchy; RelGAN: relational memory | P2 | ✗ |
| 11 | **Discriminator "winner-takes-all"** — D quá mạnh → G không học | Yu_2017_SeqGAN; Gulrajani_2017 | n_critic=5 (WGAN standard), TTUR learning rate asymmetry | **P0** | Đã có (V4) |
| 12 | **Tokenization mất SQL semantics** — character-level quá sparse | Sennrich_2016_BPE; Lu_2022_GAN_SQLi | BPE hoặc SQLParse keyword-level tokenization | P1 | delex_v2 vocab=434 |
| 13 | **Reproducibility thấp** — 1 seed, không CI, không fixed test set | Williams_1992_REINFORCE | Thêm: 3 seeds minimum, confidence intervals, fixed test set | P1 | Test set fixed, seeds TBD |
| 14 | **Exposure bias** — train với real tokens, inference với generated tokens | Yu_2017_SeqGAN (MLE pretrain) | MLE pretrain 2000 steps trước adversarial (V5 giữ nguyên) | **P0** | Đã có (Phase 1 warmup) |
| 15 | **Reward function không có semantics** — D score không phản ánh SQL validity | Lu_2022_GAN_SQLi; Chowdhary_2023 | Composite reward: WAF(0.30) + DB_exec(0.25) + AST(0.20) + IDS(0.15) + Novelty(0.10) | **P0** | Đã có (V3) |
| 16 | **Benign SQL thiếu trong D training** — D không phân biệt attack vs benign | Rahman_2025_GANs_IDS; thầy Lâm #5 | generate_benign_sql.py ~2000 benign queries | P1 | Build ngày 17/05 |
| 17 | **Spectral norm vs BatchNorm trong D** — BatchNorm vi phạm WGAN-GP independence | Miyato_2018_Spectral_Norm; Gulrajani_2017 | SpectralNorm thay BatchNorm trong D CNN layers | P2 | ✗ (potential V5 add) |

---

## PHẦN 2 — PHÂN NHÓM THEO COMPONENT

### 2.1. Generator Issues → Gradient Estimator Papers

| Vấn đề | P | Paper | Kỹ thuật |
|--------|---|-------|----------|
| Mode collapse | P0 | Jang_2017 | Gumbel-Softmax τ∈[0.5,1.0] |
| Exposure bias | P0 | Yu_2017 | MLE warmup 2000 steps |
| Conditional drift | P1 | Chen_2016 | InfoGAN Q-loss: CE(q_atk, condition) |
| Long sequence | P2 | Guo_2018 | Manager-Worker hierarchy |

### 2.2. Discriminator Issues → Training Stability Papers

| Vấn đề | P | Paper | Kỹ thuật |
|--------|---|-------|----------|
| Gradient vanish | P0 | Gulrajani_2017 | WGAN-GP λ=10 |
| BatchNorm violation | P2 | Miyato_2018 | SpectralNorm |
| Winner-takes-all | P0 | Yu_2017; Gulrajani_2017 | n_critic=5, TTUR |
| Benign vs attack confusion | P1 | Rahman_2025 | Include benign in training |

### 2.3. Reward/Signal Issues → SQLi + RL Papers

| Vấn đề | P | Paper | Kỹ thuật |
|--------|---|-------|----------|
| Reward ceiling | P0 | Jang_2017 | Replace REINFORCE với Gumbel gradient |
| WAF bypass low | P1 | Demetrio_2020 | 6 mutation operators |
| IDS evasion | P2 | Lin_2018 | Adversarial gradient reversal |
| DB execution | P0 | Lu_2022 | SQLite sandbox execution check |

### 2.4. Data Pipeline Issues → Data Papers

| Vấn đề | P | Paper | Kỹ thuật |
|--------|---|-------|----------|
| Collision 71.89% | P0 | Own | delex_v2 whitelist |
| Wrapper bias | P0 | Own | strip_wrapper.py |
| Label quality | P1 | Ratner_2017 | Weak supervision + confidence scoring |
| Dataset size | P0 | RbSQLi + Zenodo | 14.6M raw → 50K gold |

---

## PHẦN 3 — IMPLEMENTATION ROADMAP từ Papers

```
TUẦN NÀY (trước 20/05):
  [P0] Jang_2017 → generator.py: thay REINFORCE bằng Gumbel-Softmax STE
  [P0] Gulrajani_2017 → discriminator.py: WGAN-GP λ=10, no BatchNorm
  [P0] delex_v2 → data/pipeline/delex_v2.py (proven: collision 71.89%→4.33%)
  [P0] strip_wrapper → data/pipeline/strip_wrapper.py

SAU 20/05:
  [P1] Chen_2016 → src/reward.py: thêm InfoGAN Q-loss (type_accuracy →80%)
  [P1] Demetrio_2020 → post_process/mutate.py: 6 mutation operators
  [P1] Sennrich_2016 → tokenizer: xem xét BPE nếu vocab_size >500

SAU KHI V5 STABLE:
  [P2] Guo_2018 → generator.py: LeakGAN Manager-Worker variant
  [P2] Miyato_2018 → discriminator.py: SpectralNorm thay LayerNorm
  [P2] Lin_2018 → reward.py: IDS adversarial gradient
```

---

## PHẦN 4 — BẢNG TRẠNG THÁI THỰC HIỆN (Version Tracking)

| Kỹ thuật | V1 | V2 | V3 | V4 | V5 (target) |
|----------|----|----|----|----|------------|
| SeqGAN framework | ✓ | ✓ | ✓ | ✓ | ✓ |
| MLE warmup | ✓ | ✓ | ✓ | ✓ | ✓ |
| REINFORCE | ✓ | ✓ | ✓ | ✓ | **✗ → Gumbel** |
| WGAN-GP | ✗ | ✗ | ✓ | ✓ | ✓ |
| Entropy regularization | ✗ | ✗ | ✓ | ✓ | ✓ |
| Gumbel-Softmax STE | ✗ | ✗ | ✗ | ✗ | **✓** |
| delex_v2 function whitelist | ✗ | ✗ | ✗ | ✓ | ✓ |
| BiLSTM encoder | ✗ | ✗ | ✗ | ✓ | ✓ |
| Benign SQL in D training | ✗ | ✗ | ✗ | ✓ | ✓ |
| InfoGAN conditional loss | ✗ | ✗ | ✗ | ✗ | P1 |
| WAF mutation post-processing | ✗ | ✗ | ✗ | ✗ | P1 |
| SpectralNorm | ✗ | ✗ | ✗ | ✗ | P2 |

---

## PHẦN 5 — BẢNG ĐÁP LẠI CÂU HỎI THẦY LÂM

| Câu hỏi thầy | Trả lời dựa trên papers | Paper tham chiếu |
|---|---|---|
| "5 điểm WAF đó dùng làm gì?" | Phase 2: WAF score là mixed reward (weight 0.10). Phase 3: WAF score là primary reward (D bị freeze). | Composite reward: Gulrajani_2017 (D signal) + Demetrio_2020 (WAF oracle) |
| "3 khối phải có kết nối" | G→soft tokens→D (Gumbel backprop), G→hard tokens→reward→G_loss | Jang_2017 (STE), Gulrajani_2017 (WGAN-GP) |
| "Em vẫn bị collapse" | Root cause: REINFORCE advantage→0. Fix: Gumbel-Softmax gradient không cần advantage | Jang_2017 (Section 3.2 của paper) |
| "Thay LSTM bằng BiLSTM" | Đã implement BiLSTM encoder trong V4, giữ trong V5 | Yu_2017 (LSTM baseline) → our BiLSTM |
| "Huấn luyện cả dữ liệu benign" | generate_benign_sql.py: ~2000 benign queries, dùng trong D training | Rahman_2025, thầy confirm |
| "Dùng WGAN-GP đúng không?" | Đúng. Gradient Penalty λ=10, không BatchNorm trong D | Gulrajani_2017 (confirmed) |
| "So sánh với CTGAN" | CTGAN = tabular baseline. CTGAN không có sequence structure → khác V5 fundamentally | Xu_2019_CTGAN |
