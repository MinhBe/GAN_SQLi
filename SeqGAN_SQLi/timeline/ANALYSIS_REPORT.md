# Báo Cáo Phân Tích Toàn Diện — SeqGAN SQLi

> **Ngày**: 2026-05-10  
> **Đối tượng**: Researcher — có nền tảng kỹ thuật, muốn hiểu sâu kết quả và hướng đi tiếp theo  
> **Phạm vi**: Toàn bộ pipeline từ raw data đến final evaluation  
> **Dữ liệu gốc**: `timeline/eval_report.json`, output từ 5000-step adversarial run

---

## Mục Lục

1. [Những Gì Đã Làm Được](#1-những-gì-đã-làm-được)
2. [Kết Quả Đo Lường Chính Thức](#2-kết-quả-đo-lường)
3. [Vấn Đề Được Phát Hiện — Dẫn Chứng & Thước Đo](#3-vấn-đề--dẫn-chứng--thước-đo)
4. [Nguyên Nhân Gốc Rễ](#4-nguyên-nhân-gốc-rễ)
5. [5 Hướng Giải Quyết Khả Thi](#5-5-hướng-giải-quyết)
6. [Khuyến Nghị & Thứ Tự Ưu Tiên](#6-khuyến-nghị)

---

## 1. Những Gì Đã Làm Được

### 1.1 Pipeline Hoàn Chỉnh Đã Chạy End-to-End

Toàn bộ hệ thống được xây từ con số không và đã chạy thành công qua 5 giai đoạn:

| Giai đoạn | File | Kết quả đo được |
|-----------|------|-----------------|
| Data pipeline | `data/prepare_seqgan_data.py` | train=28,602 / val=6,129 / test=6,129 |
| Vocab reduction | `src/tokenizer.py` | **3,088 → 134 tokens** (giảm 95.7%) |
| MLE pre-training | `pretrain_mle.py` | val_ppl = **1.70** tại epoch 5, early stop epoch 8 |
| Adversarial training | `train_adversarial.py` | 5,000 steps / 4h 56m, reward = **0.65** |
| Evaluation | `evaluate.py` | ASR=100%, Syntax=100%, Self-BLEU-3=0.9894 |

**Dẫn chứng cụ thể:**
- Checkpoint `checkpoints/mle_best.pt` — epoch 5, val_ppl=1.7034 (recorded in checkpoint metadata)
- Checkpoint `checkpoints/adv_final.pt` + `adv_step1000.pt` through `adv_step5000.pt` — 6 file tồn tại
- 3 file CSV: `eval_seqgan.csv`, `eval_mle.csv`, `eval_template.csv` — mỗi file 1,000 dòng

### 1.2 Các Bug Quan Trọng Đã Giải Quyết

Dưới đây là các vấn đề kỹ thuật không tầm thường đã được xử lý trong quá trình build:

**Bug 1 — Vocab explosion (3,088 token):**  
Nguyên nhân: `||chr` được tokenize thành 1 token duy nhất; các DB function như `xmltype`, `dbms_pipe` mỗi cái 1 token riêng. Với vocab 3,088, model LSTM 128-dim embedding không thể học tốt.  
Fix: Rewrite `src/tokenizer.py` — pre-tokenize bằng cách thêm space quanh tất cả operator (`||`, `(`, `)`, `=`, `--`, `/*`...) trước khi split, sau đó replace unknown identifier bằng `__IDENT__`.  
Kết quả: 3,088 → **134 tokens**.

**Bug 2 — Reward âm và phân kỳ:**  
Tại step 200, reward = **-84.6** (giảm từ -23.4 ở step 100). WGAN-GP discriminator trả về Wasserstein distance không giới hạn (ví dụ: -300), nhân với λ_D=0.3 → dominate toàn bộ reward signal.  
Fix: Tạo `configs/seqgan_fast.yaml` với `lambda_d = 0.0`.  
Kết quả: Reward hội tụ về **+0.65** tại step 5,000.

**Bug 3 — Tốc độ training (1.49s/step → 20 giờ cho 50k steps):**  
Nguyên nhân: `generator.sample()` được gọi **6 lần/step** (5 D-updates + 1 G-update), mỗi lần là 64×80 sequential LSTM forward pass.  
Fix: Generate fake sequences **1 lần/step**, reuse cho tất cả D-updates. Giảm xuống 5,000 steps.  
Kết quả: 5,000 steps hoàn thành trong **4h 56m** (ổn định ~3.5s/step do CUDA warmup, sau đó ~2s/step).

---

## 2. Kết Quả Đo Lường

### 2.1 Bảng So Sánh Chính Thức

| Model | ASR | ASR CI (95%) | Syntax% | Self-BLEU-3 | Avg Length | Trivial% |
|-------|-----|-------------|---------|-------------|------------|----------|
| **SeqGAN (adv)** | **100.0%** | 100.0%–100.0% | **100%** | 0.9894 | 68.1 ±20.6 | 0% |
| MLE only | 69.7% | 66.8%–72.5% | 100% | 0.9833 | 55.1 ±13.5 | 0% |
| Template | 67.9% | 64.9%–70.8% | 100% | 0.6836 | 4.0 ±1.2 | 6.7% ⚠ |

*CI = Bootstrap confidence interval, n_resamples=10,000*

### 2.2 Hard Target Evaluation

| Metric | Giá trị đo được | Ngưỡng | Kết quả |
|--------|----------------|--------|---------|
| ASR delta vs MLE | **+30.3pp** | ≥ +30pp | ✅ PASS (margin: 0.3pp) |
| Syntax validity | **100.0%** | ≥ 90% | ✅ PASS |
| Self-BLEU-3 | **0.9894** | < 0.60 | ❌ FAIL (cao hơn 65%) |

---

## 3. Vấn Đề — Dẫn Chứng — Thước Đo

### Vấn Đề 1: Mode Collapse (Nghiêm Trọng)

**Nhận định:** Generator đã hội tụ về một tập hẹp các pattern lặp lại, không tạo ra được sự đa dạng thực sự.

**Dẫn chứng định lượng:**
- Self-BLEU-3 của SeqGAN = **0.9894** → gần như tất cả 1,000 payload được tạo ra giống nhau đến 99%
- Self-BLEU-3 của MLE (không qua adversarial) = **0.9833** → không có cải thiện đa dạng sau 5,000 bước RL
- Để tham khảo: SeqGAN gốc trên text generation tasks thường đạt Self-BLEU-3 trong khoảng 0.6–0.8; target của ta là < 0.60

**Thước đo dùng để đánh giá:**  
Self-BLEU-3 (Zhu et al., 2018) — đo mức độ một tập mẫu tự "chép" lẫn nhau. Với mỗi câu, tính BLEU-3 của câu đó so với tất cả câu còn lại rồi lấy trung bình. Score 1.0 = tất cả câu giống hệt nhau; Score 0.0 = không có n-gram nào trùng nhau.

**Giải thích tại sao mức này nghiêm trọng:**  
Với Self-BLEU-3 = 0.9894, thực chất 1,000 payload SeqGAN generate ra **không thêm thông tin mới so với ~5–10 payload mẫu**. Trong bối cảnh nghiên cứu security, điều này vô nghĩa — attacker cần sự đa dạng để vượt qua nhiều WAF rule khác nhau.

**Một lưu ý quan trọng — Confounding Factor:**  
De-lexicalization thay thế giá trị cụ thể (`'admin'`, `1`, `users`) bằng placeholder (`__STR__`, `__INT__`, `__TABLE__`). Hai payload khác hoàn toàn về nội dung (`' OR 1=1--` vs `' OR 'x'='x`) có thể trở thành cùng token sequence sau de-lex. Self-BLEU-3 được tính trên token space đã de-lex nên **có thể phóng đại** mức độ mode collapse thực sự. Tuy nhiên, Self-BLEU-3 của MLE = 0.9833 xác nhận vấn đề tồn tại ngay cả trước adversarial training — de-lex là một phần nguyên nhân, nhưng không phải toàn bộ.

---

### Vấn Đề 2: Proxy Reward Quá Dễ Bị "Gian Lận" (Reward Hacking)

**Nhận định:** ASR = 100% với CI [100%, 100%] không phản ánh khả năng bypass WAF thực sự — nó chỉ phản ánh khả năng model qua mặt *heuristic proxy*.

**Dẫn chứng định lượng:**
- Template baseline (các pattern cố định đơn giản, length trung bình 4 token) đạt **ASR = 67.9%**
- Template có trivial_rate = 6.7% (nhiều payload quá ngắn để có ý nghĩa)
- SeqGAN đạt 100% nhưng MLE đã là 69.7% — khoảng cách chỉ +30.3pp, nằm đúng trên ngưỡng

**Thước đo dùng để đánh giá:**  
ASR (Attack Success Rate) ở đây được đo bằng *dev proxy* — một heuristic kiểm tra xem payload có chứa các pattern tấn công SQL điển hình không (`OR 1=1`, `UNION SELECT`, `; DROP`, v.v.). Đây **không phải** là WAF thực sự.

**Tại sao đây là vấn đề:**  
Proxy reward là signal mà model optimize trực tiếp. Khi proxy quá đơn giản, model học cách gian lận nó thay vì học cách thực sự bypass WAF. ASR = 100% với heuristic = model tìm được pattern nào đó *luôn trigger proxy*, chứ không có nghĩa là 100% payload sẽ bypass ModSecurity hay WAF thực.

**Bằng chứng gián tiếp:**  
Training reward tăng từ 0 → 0.65 sau 5,000 steps (tức là model đang optimize đúng hướng), nhưng đồng thời Self-BLEU-3 không giảm — model tăng reward bằng cách lặp lại pattern thành công thay vì khám phá.

---

### Vấn Đề 3: ASR Delta Chỉ Vượt Ngưỡng 0.3pp — Kết Quả Mong Manh

**Nhận định:** Margin +30.3pp so với threshold +30pp quá nhỏ để có thể khẳng định kết quả robust.

**Dẫn chứng định lượng:**
- SeqGAN ASR = 100.0%, CI = [100.0%, 100.0%]
- MLE ASR = 69.7%, CI = [66.8%, 72.5%]
- Delta = 30.3pp — nếu MLE thực sự là 72.5% (upper bound của CI) thì delta = 27.5pp → **FAIL**

**Thước đo dùng để đánh giá:**  
Bootstrap CI (n=10,000 resamples, percentile method). CI rộng 5.7pp của MLE (66.8%–72.5%) trong khi CI của SeqGAN bằng 0 (vì 100%) tạo ra bất cân xứng trong so sánh.

**Ý nghĩa thực tế:**  
Kết quả "PASS" không đủ mạnh về mặt thống kê. Nếu đánh giá với WAF thực hoặc thay đổi proxy, delta có thể dễ dàng thay đổi theo cả hai chiều.

---

## 4. Nguyên Nhân Gốc Rễ

Phân tích cause-effect cho Mode Collapse + Reward Hacking:

```
Nguyên nhân gốc #1: lambda_d = 0.0
    ↳ Discriminator không còn tạo áp lực diversity
    ↳ Generator không bị phạt khi output giống nhau liên tục
    ↳ Mode collapse

Nguyên nhân gốc #2: Proxy reward quá đơn giản (heuristic)
    ↳ Reward cao nhất đạt được bằng cách lặp pattern bypass đơn giản
    ↳ Generator hội tụ về pattern đó
    ↳ Reward hacking + Mode collapse

Nguyên nhân gốc #3: Không có entropy regularization
    ↳ REINFORCE thuần túy không có cơ chế ngăn distribution collapse
    ↳ Khi một action có reward cao, gradient push mạnh → collapse nhanh

Nguyên nhân gốc #4: De-lexicalization collapses diversity không gian
    ↳ Nhiều payload distinct → cùng token sequence
    ↳ Self-BLEU-3 đo trên de-lex space → phóng đại collapse
    ↳ (confounding, không phải root cause duy nhất)
```

Vấn đề #1 và #2 **synergistic**: nếu proxy dễ bị hack, model sẽ hack nó. Nếu đồng thời không có diversity pressure từ D, không có gì ngăn cản việc lặp lại mãi mãi.

---

## 5. 5 Hướng Giải Quyết Khả Thi

---

### Hướng 1: Entropy Regularization trên Generator

**Mô tả kỹ thuật:**  
Thêm một hạng tử entropy vào policy gradient loss để generator bị phạt khi phân phối của nó quá "nhọn" (peaked):

```
g_loss = -(log_probs * advantages).mean()  [hiện tại]
       - entropy_coef * H(π)               [thêm vào]
```

Trong đó H(π) = -Σ p(a|s) × log p(a|s) trên toàn bộ vocabulary. Khi entropy_coef = 0.01–0.05, model được thưởng nhẹ khi phân phối token đều hơn.

**Thay đổi code:** ~5 dòng trong `train_adversarial.py`, thêm vào vòng lặp G-update.

**Ưu điểm:**
- Đơn giản nhất trong 5 hướng — ít rủi ro phá vỡ training stability
- Không cần thêm data, model, hay infrastructure
- Có nền tảng lý thuyết vững (PPO, A3C đều dùng entropy bonus)
- Compute cost gần như bằng 0 (tính entropy từ logits đã có)
- Có thể tune nhanh: entropy_coef từ 0.001 → 0.1 trong vài runs ngắn

**Nhược điểm:**
- Chỉ giải quyết được **triệu chứng** của mode collapse, không giải quyết proxy reward hacking
- Entropy_coef quá cao → random payloads → syntax rate giảm, ASR giảm
- Entropy ở token level không đảm bảo diversity ở sequence level (model có thể sample token đa dạng nhưng vẫn ra cùng một cấu trúc câu)
- Không giải quyết vấn đề Self-BLEU-3 đo trên de-lex space (confounding)

**Phù hợp khi:** Muốn cải thiện nhanh với minimal code change, bước đầu verify xem diversity có tăng không trước khi đầu tư các hướng phức tạp hơn.

---

### Hướng 2: Bounded Discriminator Score — Khôi Phục lambda_d

**Mô tả kỹ thuật:**  
Vấn đề gốc là WGAN score không giới hạn (unbounded). Thay vì bỏ hoàn toàn (lambda_d=0), ta normalize/clip score về một range cố định rồi dùng lại làm reward:

**Option A — Sigmoid normalization:**
```python
r_d = torch.sigmoid(d_score)  # map (-∞,+∞) → (0,1)
```

**Option B — Running statistics normalization:**
```python
# Track running mean và std của D score qua EMA
d_score_normalized = (d_score - d_mean_ema) / (d_std_ema + 1e-8)
r_d = torch.clamp(d_score_normalized, -3, 3) / 3  # → [-1, 1]
```

Sau đó restore `lambda_d = 0.1` trong config và dùng r_d đã normalize thay vì raw score.

**Thay đổi code:** ~15 dòng trong `src/reward.py` + `train_adversarial.py`, thêm EMA tracking cho D score nếu dùng option B.

**Ưu điểm:**
- Giải quyết đúng nguyên nhân gốc rễ #1: khôi phục diversity pressure từ discriminator
- Discriminator phân biệt real/fake → nếu generator output quá giống nhau, D dễ phân biệt → penalty → generator buộc phải đa dạng hơn
- Lý luận nguyên lý hơn: adversarial training có diversity built-in qua minimax game
- Self-BLEU-3 có khả năng giảm rõ rệt

**Nhược điểm:**
- Khó tune hơn: cần chọn normalization method + lambda_d + warmup schedule cho D trước khi cho vào reward
- D score thay đổi scale trong suốt quá trình training → running stats cần warm-up period ổn định
- Nguy cơ training instability cao hơn (thêm 1 feedback loop vào hệ thống vốn đã phức tạp)
- Cần run adversarial training lại từ đầu (5h+ compute)

**Phù hợp khi:** Muốn fix diversity theo cách principled nhất, sẵn sàng đầu tư thêm compute và debugging.

---

### Hướng 3: Thay Thế Dev Proxy bằng Reward Mạnh Hơn

**Mô tả kỹ thuật:**  
Thay heuristic hiện tại bằng một trong các option sau, theo thứ tự khó tăng dần:

**Option A — ML Bypass Classifier:**  
Train một classifier (CNN/LSTM) trên dataset có label bypass/blocked, dùng P(bypass|payload) làm reward. Classifier có thể được train từ data thực hoặc augmented data.

**Option B — WAF Signature Matching Engine:**  
Dùng `py-modsecurity` hoặc port của ModSecurity rules để test payload locally, không cần Docker. Score = 1 nếu bypass, 0 nếu blocked.

**Option C — Actual WAF in Docker:**  
Setup ModSecurity + NGINX trong Docker container, gọi HTTP request với payload, đọc response code. Score = 1 nếu 200, 0 nếu 403.

**Ưu điểm:**
- Giải quyết nguyên nhân gốc rễ #2 — reward không còn bị hack dễ dàng
- ASR metric trở nên có ý nghĩa thực sự với security research
- Tự nhiên tạo ra selective pressure: chỉ những payload thực sự bypass WAF mới được reward cao → generator phải đa dạng hóa để tìm nhiều góc tấn công
- Đây là con đường dẫn đến **research publishable** — kết quả với WAF thực có giá trị hơn nhiều

**Nhược điểm:**
- **Compute cost cực kỳ cao**: gọi WAF thực cho mỗi token sequence trong mỗi batch (64 sequences × 5,000 steps = 320,000 HTTP calls)
- Cần giải quyết latency: nếu mỗi WAF call mất 50ms → 320,000 × 0.05s = 4.4 giờ chỉ cho reward computation
- Option A (classifier) có circular dependency: data để train classifier cũng cần WAF test
- Option C cần infrastructure setup (Docker, networking, port management)
- Kết quả phụ thuộc vào loại WAF chọn — ModSecurity khác AWSWAF khác Cloudflare

**Phù hợp khi:** Phase nghiên cứu chính thức, có thể đầu tư infrastructure, muốn kết quả có thể publish.

---

### Hướng 4: Self-BLEU Penalty trong Training Loop

**Mô tả kỹ thuật:**  
Đo pairwise similarity *trong batch* tại mỗi training step và thêm penalty vào reward:

```python
# Với mỗi batch fake_seqs (B, T):
# Tính intra-batch pairwise BLEU-2 trên 16 sample đầu
payloads_sample = [tok.decode(s.tolist()) for s in fake_seqs[:16]]
intra_bleu = compute_self_bleu(payloads_sample, n=2)  # nhanh hơn BLEU-3

# Penalty: nếu batch quá giống nhau → giảm reward
diversity_bonus = -diversity_coef * intra_bleu  # âm = penalty

# Cộng vào reward
rewards = terminal_rewards + diversity_bonus
```

Hoặc dùng embedding-based similarity (cosine similarity trong LSTM hidden space) thay vì n-gram BLEU để tránh discrete text issue.

**Ưu điểm:**
- Directly target metric bị fail (Self-BLEU) trong quá trình training
- Differentiable nếu dùng embedding similarity (không cần qua discrete text)
- Có thể tune riêng diversity_coef độc lập với các reward component khác
- Không cần thay đổi architecture, chỉ thêm vào reward computation

**Nhược điểm:**
- Tính BLEU trong training loop **chậm** nếu làm trên toàn batch — cần hạn chế số sample so sánh
- BLEU tính trên de-lexicalized text vẫn bị confounding bởi de-lex design
- Embedding similarity trong LSTM space có thể không align tốt với actual payload diversity (hai payload khác nhau có thể có similar hidden state)
- Thêm một hyperparameter nữa vào hệ thống đã nhiều hyperparameter

**Phù hợp khi:** Đã có entropy regularization (Hướng 1) nhưng Self-BLEU vẫn cao, cần giải quyết diversity trực tiếp hơn.

---

### Hướng 5: Re-lexicalization — Đo Diversity Đúng Chỗ

**Mô tả kỹ thuật:**  
Đây là hướng khác về bản chất — không thay đổi training, thay đổi cách đánh giá và thực tế có thể giải quyết "vấn đề" mà không cần fix gì cả.

De-lexicalization là quyết định thiết kế đúng đắn (giảm vocab từ 3,088 → 134) nhưng tạo ra measurement artifact: hai payload thực sự khác nhau bị coi là giống nhau vì chứa cùng placeholder.

**Giải pháp:**  
Xây dựng một **re-lexicalization step** trong `generate.py`: sau khi generate de-lexicalized payload, fill placeholder với giá trị thực ngẫu nhiên từ một từ điển:

```
__STR__  → random.choice(['admin', 'test', 'root', '1', "' OR '1'='1"])
__INT__  → random.choice(['1', '0', '-1', '999', '10'])  
__TABLE__ → random.choice(['users', 'accounts', 'employees', 'orders'])
__COL__  → random.choice(['id', 'username', 'password', 'email'])
```

Sau đó tính Self-BLEU-3 trên *payload thực* (sau re-lex) — đây mới là diversity metric có ý nghĩa.

**Ưu điểm:**
- Không cần chạy lại training — áp dụng được ngay trên checkpoint hiện có
- Có thể giải quyết FAIL của Self-BLEU-3 mà không tốn compute training
- Re-lexicalization cũng làm cho eval_seqgan.csv có ý nghĩa hơn cho downstream testing
- Diversity thực tế (sau re-lex) có thể cao hơn nhiều so với Self-BLEU-3 trên de-lex space

**Nhược điểm:**
- Không giải quyết vấn đề mode collapse **trong token space** — nếu generator chỉ biết 2-3 structure cơ bản, re-lex chỉ thêm "bề ngoài" đa dạng mà không có structural diversity
- Re-lex dictionary phải được curated cẩn thận — random string không đảm bảo valid SQL
- Self-BLEU-3 sau re-lex phụ thuộc nhiều vào kích thước từ điển re-lex hơn là quality của generator
- Có thể bị reviewer phản bác là "gaming the metric"

**Phù hợp khi:** Muốn verify nhanh xem Self-BLEU FAIL là do de-lex artifact hay do mode collapse thực sự, trước khi đầu tư fix training.

---

## 6. Khuyến Nghị & Thứ Tự Ưu Tiên

### Nếu mục tiêu là sửa nhanh, verify và move on:

```
Bước 1: Hướng 5 (Re-lexicalization)        — 1–2 giờ code
         → Xác định xem Self-BLEU FAIL là artifact hay real problem
         
Bước 2: Hướng 1 (Entropy Regularization)   — 2–3 giờ code + 5h training
         → Nếu FAIL là real: entropy bonus là fix đơn giản nhất để verify
```

### Nếu mục tiêu là research chất lượng cao, có thể publish:

```
Bước 1: Hướng 3 (Real WAF Reward)          — 1–2 ngày infrastructure
         → Không có ASR thực → không có paper
         
Bước 2: Hướng 2 (Bounded D Score)          — 5h training
         → Diversity từ GAN training, theoretically principled
         
Bước 3: Hướng 1 (Entropy Bonus)            — 5h training
         → Fine-tune diversity nếu vẫn còn mode collapse
```

### Ma trận quyết định nhanh:

| Tiêu chí | H1 Entropy | H2 Bounded-D | H3 Real WAF | H4 BLEU Penalty | H5 Re-lex |
|----------|-----------|-------------|------------|----------------|----------|
| Compute cost | Thấp | Trung bình | Cao | Trung bình | Rất thấp |
| Code complexity | Thấp | Trung bình | Cao | Trung bình | Thấp |
| Giải quyết root cause | Một phần | Có | Có | Một phần | Không |
| Risk phá vỡ training | Thấp | Trung bình | Không áp dụng | Thấp | Không |
| Giá trị research | Thấp | Trung bình | Cao | Thấp | Trung bình |

---

## Kết Luận

Thành tựu lớn nhất của sprint này là **pipeline end-to-end hoạt động hoàn chỉnh** — từ raw data đến evaluation — với MLE pre-training đạt val_ppl=1.70 (excellent) và adversarial training hội tụ reward về +0.65.

Vấn đề chính không phải là implementation sai, mà là **hai quyết định thiết kế được đưa ra vì lý do chính đáng nhưng có side effect**:

1. `lambda_d=0.0` — đúng khi fix unbounded reward, nhưng đồng thời xóa diversity pressure
2. Heuristic proxy — đúng cho dev environment không có Docker WAF, nhưng quá dễ bị gamed

Đây là loại tension phổ biến trong RL training: stability vs exploration, feasibility vs rigor. Bước tiếp theo hợp lý nhất là **Hướng 5** (15 phút) để phân loại vấn đề, rồi **Hướng 1** (5h) để fix nếu cần, trước khi đầu tư vào **Hướng 3** (infrastructure) cho research chất lượng cao.

---

*Report được tạo tự động từ `timeline/eval_report.json` và session logs — 2026-05-10*
