# 10 Hướng Cải Thiện SeqGAN-SQLi — Phân Tích Phản Biện Sâu

> **Bối cảnh thực tế (đọc kỹ trước khi đọc tiếp):**
> Mô hình hiện tại đạt ASR=100% / Syntax=100% nhưng **Self-BLEU-3 = 0.9894** — nghĩa là 1,000 payload sinh ra tương đương ~5–10 mẫu unique. WGAN-GP đã thử và **thất bại** (reward phân kỳ về -84.6, phải set λ_D=0). Vocab=134, MLE val_ppl=1.70, train 5,000 adv steps trong 4h56m.
>
> **Phản biện thẳng vào PAPER_ANALYSIS_REPORT.md hiện tại:**
> Báo cáo cũ kết luận "WGAN-GP nên thử", "self-attention nên thử", "core approach correct" — đây là kết luận **dựa trên paper** chứ không dựa trên kết quả thực nghiệm của bạn. Thực tế:
> 1. Bạn đã thử WGAN-GP rồi → fail (vì Wasserstein không bounded khi G chưa fit).
> 2. ASR=100% với Self-BLEU=0.99 là **dấu hiệu reward hacking kinh điển**, không phải "thành công".
> 3. MLE đã đạt ASR 69.7% với Self-BLEU 0.98 → adversarial training **không cải thiện diversity** mà chỉ "vắt" thêm 30pp ASR bằng cách thu hẹp distribution.
>
> Tức là vấn đề cốt lõi **không phải kiến trúc D**, mà là: **reward signal quá đơn điệu + dataset quá đồng nhất + không có cơ chế ép diversity**.

---

## Tóm tắt 10 hướng (xếp theo ROI ước tính)

| # | Hướng | Chi phí | Kỳ vọng | Mức độ phản biện |
|---|-------|---------|---------|------------------|
| 1 | Diversity-aware reward (penalize Self-BLEU trong batch) | Thấp | **Cao** | Bắt buộc, không tranh luận |
| 2 | Multi-WAF reward ensemble + curriculum | Trung | **Cao** | Phá reward hacking |
| 3 | Maximum-Entropy / KL-to-prior regularization | Thấp | **Cao** | Lý thuyết vững |
| 4 | Token-level / dense reward (không chỉ terminal) | Trung | Trung-Cao | Sửa sparse reward gốc |
| 5 | Conditional generation (CGAN-style, conditioned on attack class) | Trung | Trung-Cao | Ép phân nhánh mode |
| 6 | Replay buffer + experience prioritization (RankGAN/LeakGAN style) | Trung | Trung | Ổn định variance |
| 7 | Mixture-of-Experts Generator hoặc Population-based G | Cao | Trung | Đắt, chưa chắc thắng |
| 8 | Latent-variable G (VAE-SeqGAN) thay vì pure autoregressive | Cao | Trung | Học từ Dasari, có rủi ro |
| 9 | Bỏ adversarial — thay bằng RL-fine-tuning trực tiếp trên reward (RLHF style) | Trung | **Cao** | **Phản biện táo bạo** |
| 10 | Đánh giá lại pipeline ASR — ModSecurity oracle có "rò rỉ" không? | Thấp | Cao (về integrity) | Có thể vô hiệu hóa toàn bộ kết quả |

---

## Hướng 1 — Diversity-Aware Reward (Self-BLEU Penalty trong batch)

### Vấn đề thực tế
Reward hiện tại = `λ_bypass * R_bypass + λ_syntax * R_syntax (+ λ_D * D_score)`. Không có thành phần nào **trừng phạt việc sinh giống nhau**. Generator học được rằng: "tìm 1 payload bypass được rồi spam nó" là chiến lược tối ưu reward → Self-BLEU=0.99 là kết cục **toán học tất yếu**.

### Đề xuất kỹ thuật
Trong mỗi batch B sequences `{s_1, ..., s_B}`, tính:

```
R_div(s_i) = 1 - mean_{j != i} BLEU-3(s_i, s_j)
R_total(s_i) = α·R_bypass(s_i) + β·R_syntax(s_i) + γ·R_div(s_i)
```

- Bắt đầu γ=0.3, scan {0.1, 0.3, 0.5, 1.0}.
- Hoặc dùng **n-gram novelty** so với buffer 5,000 payload đã sinh trước đó (intra-batch dễ bị G "lách" bằng cách sinh batch đa dạng nhưng giữa các batch vẫn lặp).

### Phản biện gay gắt
- **Bẫy 1**: Nếu γ quá cao, G sẽ sinh **rác có ngữ pháp lạ nhưng không bypass** để tối đa diversity → ASR tụt. Phải monitor Pareto front (ASR × Diversity).
- **Bẫy 2**: BLEU không phải metric tốt cho SQL — `' OR 1=1--` và `' OR 2=2--` BLEU thấp nhưng **semantically identical**. Cần thêm **AST-level diversity** (parse bằng sqlparse, so cây).
- **Không phải free lunch**: Paper SeqGAN gốc thừa nhận diversity-reward là known trick (Lin et al. 2017 — RankGAN), nhưng kết quả mixed.

### ROI: ★★★★★ — đây là hướng số 1 vì nó **trực tiếp đánh vào failure mode bạn đang có**.

---

## Hướng 2 — Multi-WAF Reward Ensemble + Curriculum

### Vấn đề thực tế
Bạn train trên ModSecurity với CRS rules. ASR=100% trên ModSecurity **không có nghĩa gì** — có thể chỉ vì G học được 1 lỗ hổng cụ thể của CRS (ví dụ: comment injection `/*!50000...*/` mà CRS pre-version không catch). Đây là **WAF overfitting** đúng như báo cáo cũ đã cảnh báo nhưng chưa giải quyết.

### Đề xuất kỹ thuật
- **Ensemble reward**: `R_bypass = mean(bypass_modsec, bypass_libinjection, bypass_naxsi, bypass_owasp_coraza)`.
- **Curriculum**: Tuần 1 chỉ ModSec; tuần 2 thêm libinjection (chặt hơn); tuần 3 ensemble đầy đủ. Tránh G bị stuck ngay từ đầu vì tất cả WAF reject.
- **Held-out WAF**: Giữ 1 WAF (ví dụ Cloudflare ruleset offline copy) **không bao giờ** dùng trong training, chỉ để eval generalization.

### Phản biện gay gắt
- **Bẫy chính**: Nếu các WAF có rules trùng nhau ~80%, ensemble không tăng difficulty đáng kể, chỉ tăng compute 4×.
- **Không giải quyết mode collapse** — chỉ giải quyết overfitting. Phải combine với hướng 1.
- **Reward latency**: Mỗi rollout giờ phải call 4 WAF → I/O bottleneck. Phải batch + cache.

### ROI: ★★★★☆ — bắt buộc nếu muốn claim "bypass WAF" thay vì "bypass ModSecurity CRS v3".

---

## Hướng 3 — Maximum Entropy Regularization (KL-to-prior)

### Cơ sở lý thuyết
RLHF (InstructGPT, Ouyang 2022) dùng `R - β·KL(π || π_ref)` để **giữ G gần MLE policy**, tránh distribution collapse. SeqGAN gốc không có cơ chế này → đây là lỗi thiết kế mà cộng đồng RL-LM đã giải quyết từ 2022.

### Đề xuất kỹ thuật
```
loss_G = -E[R(s) - β · log(π_θ(s) / π_MLE(s))]
       = -E[R(s)] + β · KL(π_θ || π_MLE)
```

- `π_MLE` = generator sau pre-training, **freeze**.
- β scan {0.01, 0.05, 0.1, 0.5}.
- Tương đương về mặt toán học với entropy bonus khi prior là uniform.

### Phản biện gay gắt
- **Tại sao paper SeqGAN gốc không làm?** Vì 2017 chưa có RLHF. Nhưng giờ đã 2026, không có lý do gì không dùng.
- **Bẫy**: Nếu MLE policy đã collapse (Self-BLEU 0.98 ngay sau pre-training), KL constraint không cứu được — bạn cần **diverse pre-training data** trước.
- **Tốt nhất kết hợp** với hướng 1: KL giữ G không drift xa, diversity reward đẩy G ra khỏi mode.

### ROI: ★★★★☆ — rẻ, nguyên tắc, nên làm song song với hướng 1.

---

## Hướng 4 — Dense / Token-Level Reward

### Vấn đề thực tế
SeqGAN gốc chỉ có reward tại terminal state, dùng MC Rollout K=16 để propagate ngược. Bạn đang chạy K=16 → 16× chi phí inference. Với SQL, **mỗi token có semantics rõ ràng** (keyword, operator, literal) — có thể dùng dense reward trực tiếp.

### Đề xuất kỹ thuật
- **Per-token bypass probability**: Sau mỗi token, parse partial query bằng sqlparse, hỏi WAF "if I terminate now, do you block?". Tốn — chỉ làm mỗi N=5 token.
- **Hoặc**: Train value network V(s_t) làm baseline (đã có trong plan) + GAE (Generalized Advantage Estimation) thay MC Rollout.
- GAE: `A_t = δ_t + (γλ)δ_{t+1} + ... ` với `δ_t = r_t + γV(s_{t+1}) - V(s_t)`.

### Phản biện gay gắt
- **Bẫy lớn nhất**: WAF không thiết kế để eval partial queries → kết quả noisy, có thể tệ hơn MC Rollout.
- **GAE thay MC Rollout**: Đây là upgrade chuẩn, **rẻ hơn 16× và variance thấp hơn**, nhưng yêu cầu value network ổn định — và bạn báo cáo giá trị V chưa converge tốt trong run trước (cần verify).
- **Không giải quyết mode collapse** — chỉ giảm variance.

### ROI: ★★★☆☆ — nên làm GAE thay MC Rollout (rõ ràng có lợi); per-token reward thì thử nghiệm.

---

## Hướng 5 — Conditional Generation (CGAN-style)

### Cơ sở
Dasari (2025) dùng CWGAN-GP. SQL injection có **các họ tấn công riêng biệt**: UNION-based, Boolean-blind, Time-blind, Stacked, Out-of-band. G hiện tại học hỗn hợp → collapse về 1 họ "dễ" nhất (thường là UNION với comment).

### Đề xuất kỹ thuật
- Label dataset thành C={UNION, BOOLEAN, TIME, STACKED, OOB, OBFUSCATED} (semi-auto bằng regex + manual verify).
- G(z, c) — embed class label vào hidden state ban đầu.
- D(s, c) — discriminator phân biệt cả real/fake và class.
- Sample c uniform khi inference → **ép G phải biết tất cả họ**.

### Phản biện gay gắt
- **Bẫy 1**: Labeling không chính xác → noise label làm hỏng cả G và D.
- **Bẫy 2**: Nếu 1 họ chiếm 80% dataset (thường UNION-based), CGAN vẫn collapse trong từng họ.
- **Bẫy 3**: Đây là **giả định cấu trúc** — nếu attacker thật không nghĩ theo "class", model bị bias.
- So với hướng 1: CGAN ép diversity **giữa các class**, hướng 1 ép diversity **trong class**. Hai cái bổ sung nhau.

### ROI: ★★★★☆ — nên làm sau khi hướng 1 cho ra Pareto curve để biết base diversity.

---

## Hướng 6 — Replay Buffer + Prioritized Experience

### Vấn đề
On-policy REINFORCE: mỗi batch sample mới → **vứt đi** sau 1 update. Lãng phí.

### Đề xuất kỹ thuật
- Buffer 10k payload tốt nhất (high R, low pairwise BLEU).
- D học từ mix `(real, recent_fake, buffer_fake)` — D không quên các mode cũ.
- G học với importance sampling từ buffer.
- Inspired by RankGAN (Lin 2017), LeakGAN (Guo 2018).

### Phản biện gay gắt
- **Bẫy**: Importance sampling với policy gradient có variance cực cao khi buffer cũ → policy hiện tại khác xa policy lúc sample. Cần KL clip (giống PPO) — và bạn vừa đọc paper Rodriguez nói **PPO kém hơn REINFORCE**. Nguy cơ thật.
- **Phức tạp**: LeakGAN có 3,000+ dòng code, debug khó. Cost/benefit không rõ.

### ROI: ★★★☆☆ — chỉ làm khi 1-3 đã hết dư địa.

---

## Hướng 7 — Mixture-of-Experts hoặc Population-based G

### Ý tưởng
Train K=4 generators song song, mỗi G được đẩy vào 1 mode khác nhau bằng **diversity-between-G reward** (G_i bị phạt nếu sinh giống G_j). Inference: round-robin hoặc weighted sample.

### Phản biện gay gắt
- **Cost 4×**, kết quả không đảm bảo. Đây là "brute force diversity".
- **Mode collapse trong mỗi G vẫn xảy ra**. Bạn có thể có 4 mode thay vì 1, nhưng vẫn rất xa target Self-BLEU<0.6.
- **Đề xuất rẻ hơn**: Dùng **temperature sampling** + **nucleus (top-p) sampling** lúc inference. Có thể đẩy diversity miễn phí mà không train lại. **Hãy thử cái này trước khi nghĩ tới MoE.**

### ROI: ★★☆☆☆ — không khuyến nghị. Thử nucleus sampling trước.

---

## Hướng 8 — Latent-Variable G (VAE-SeqGAN)

### Ý tưởng
G(z) với z ~ N(0, I) latent → encoder ép payload vào latent space → decoder sinh. Latent z cung cấp "noise multiplier" cho diversity (giống StyleGAN cho image).

### Phản biện gay gắt
- **Posterior collapse** là vấn đề kinh điển của VAE-text — z bị decoder ignore. Cần KL annealing, free-bits, BoW loss... — thêm 1 zoo hyperparameter mới.
- Dasari (2025) đã làm và **CWGAN-GP của họ R²=-1.7253** — chính paper bạn cite cũng struggle.
- **Lý thuyết hấp dẫn, thực hành đầy mìn**.

### ROI: ★★☆☆☆ — research direction, không phải engineering direction.

---

## Hướng 9 — Bỏ Adversarial, Chuyển sang RL-Fine-tuning Trực Tiếp

### Phản biện táo bạo nhất
**Câu hỏi gay gắt: tại sao bạn cần Discriminator?**

Trong setup gốc của Yu 2017, D cần thiết vì **không có ground-truth reward** cho text quality. Nhưng bạn **CÓ** reward thật: ModSecurity bypass + sqlparse syntax. **D chỉ là proxy nhiễu cho cái bạn đã có.**

Bằng chứng từ chính experiment của bạn:
- λ_D phải set = 0 vì WGAN-GP phân kỳ
- Tức là **thực tế bạn đã chạy không có D**, vẫn đạt ASR=100%
- Vậy "SeqGAN" của bạn thực chất là **REINFORCE thuần với reward = bypass + syntax** — không phải GAN.

### Đề xuất
- **Loại bỏ D hoàn toàn**, gọi đúng tên: **RL-fine-tuned LSTM** (giống RLHF nhưng reward = WAF oracle).
- Tập trung vào: reward shaping (hướng 1, 3), value function (hướng 4), curriculum (hướng 2).
- Tiết kiệm 50% compute (không train D), 50% complexity (không tune g_steps/d_steps/k).

### Phản biện ngược (devil's advocate)
- D có thể giúp **regularize**: G không thể sinh "rác bypass được" vì D phân biệt được với real payloads.
- Nhưng bạn có thể đạt regularization tương đương bằng **KL-to-MLE** (hướng 3) — rẻ hơn và ổn định hơn.

### ROI: ★★★★★ — **đây là hướng có ý nghĩa khoa học cao nhất**: thừa nhận bản chất thật của hệ thống và đặt câu hỏi đúng.

---

## Hướng 10 — Audit Lại Reward Oracle (Critical Integrity Check)

### Câu hỏi "đáng sợ"
ASR=100% trên 1,000 payload là **bất thường nghi ngờ**. Trước khi cải thiện model, hãy verify:

1. **ModSecurity có thực sự được call không?** Check log file, count POST requests = 1,000.
2. **CRS rules có load đúng không?** Test sanity: gửi `' OR 1=1--` (payload sơ đẳng) — phải bị block. Nếu không bị, CRS không active.
3. **Paranoia level CRS đặt ở đâu?** PL=1 (default) cực kỳ permissive — nhiều payload trivial pass. PL=4 mới strict.
4. **HTTP transport có encoding issue?** Nếu gửi binary token `__IDENT__` literal, ModSec có thể trả 200 không phải vì bypass mà vì **request không parse được**.
5. **Status code mapping**: ASR=1 khi status=200? Thế còn 500, 503, connection-refused thì sao? Có bị count nhầm thành "bypass"?

### Phản biện gay gắt
- Đây không phải "improvement" theo nghĩa thông thường. Nhưng **nếu ASR=100% là artifact pipeline bug, mọi hướng 1-9 đều vô nghĩa**.
- Báo cáo cũ (PAPER_ANALYSIS_REPORT.md) **không đặt câu hỏi này** — đây là blind spot lớn.

### Action item cụ thể
```bash
# Sanity test
echo "' OR 1=1--" | curl -X POST -d @- http://localhost:8080/test
# Phải nhận 403. Nếu 200 → ModSec không hoạt động → ASR=100% là FAKE.

# Diversity check trên ground truth
python -c "from src.eval import waf_check; \
  payloads = open('data/test_real_payloads.txt').readlines(); \
  print('Real payload bypass rate:', sum(waf_check(p) for p in payloads)/len(payloads))"
# Nếu real payloads cũng ~100% bypass → CRS PL too low → meaningless eval.
```

### ROI: ★★★★★ — **làm trước tất cả các hướng khác**. Không có integrity, không có khoa học.

---

## Lộ Trình Đề Xuất (4-6 tuần)

### Tuần 1 — Audit & Foundation
- **Hướng 10**: Verify reward oracle integrity. **Không tiếp tục nếu fail.**
- **Hướng 1**: Implement Self-BLEU penalty + AST-diversity penalty.
- Re-train MLE với data đa dạng hơn (kiểm tra label balance giữa các attack class).

### Tuần 2-3 — Core Improvements
- **Hướng 9**: Loại bỏ D, chạy pure RL với reward = bypass + syntax + diversity (1) + KL (3).
- **Hướng 4**: GAE thay MC Rollout K=16 → giảm 10× compute.
- Đo Pareto front: ASR × Self-BLEU × WAF generalization.

### Tuần 4 — Generalization
- **Hướng 2**: Thêm libinjection + 1 WAF khác vào reward ensemble.
- **Hướng 5**: Conditional generation theo attack class (nếu hướng 1 chưa đủ).

### Tuần 5-6 — Advanced (optional)
- Hướng 6, 7, 8 chỉ làm nếu đã có baseline mới ổn định và còn budget.

---

## Tóm Tắt Phản Biện Cuối

1. **PAPER_ANALYSIS_REPORT.md cũ thiếu phản biện vào kết quả thực tế của bạn** — nó tổng kết lý thuyết tốt, nhưng không đặt câu hỏi "tại sao Self-BLEU 0.99?" và "ASR 100% có thật không?".
2. **WGAN-GP không phải silver bullet** — bạn đã thử và fail; đừng quay lại trừ khi diagnose được tại sao Wasserstein distance unbounded.
3. **D có thể không cần thiết** — đây là insight quan trọng nhất. Hệ thống của bạn đã thực chất là RL với differentiable reward, không phải GAN.
4. **Mode collapse là vấn đề SỐ 1**, không phải training stability. Mọi hướng phải hướng vào diversity.
5. **Integrity audit là bước 0** — không thương lượng.

> Nếu chỉ chọn **3 hướng**: làm **10 → 1 → 9** theo thứ tự. Đó là path từ "research có thể là artifact" đến "research có insight thật".
