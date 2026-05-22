# 07 — Main Generator: Conditional MLE + Evaluator-guided Search

> Mục tiêu: xây nhánh generation chính, ổn định và thực dụng hơn GAN: Conditional MLE Generator kết hợp sampling/search có dẫn hướng bởi evaluator.

---

## 1. Vấn đề cần giải quyết

Mục tiêu dự án không chỉ là sinh payload giống dữ liệu thật.

Mục tiêu thực tế:

```text
valid
đúng technique
đúng syntax/context
đa dạng
novel
có khả năng stress-test WAF/IDS trong lab
```

GAN học phân phối dữ liệu thật, nhưng red-team/WAF-stress có thể cần vượt ngoài phân phối thật. Vì vậy MLE + evaluator-guided sampling/search là hướng chính hợp lý.

---

## 2. Tính chất của nhánh này

| Tính chất | Diễn giải |
|---|---|
| Stable | MLE ổn định hơn adversarial training |
| Reproducible | Dễ chạy nhiều seed |
| Search-oriented | Có thể sinh nhiều candidate rồi chọn |
| Evaluator-guided | Tối ưu theo mục tiêu thực tế |
| Baseline/main | Đây là nhánh mặc định nếu GAN không thắng rõ |

---

## 3. Kiến trúc Generator

### 3.1. Input condition

Ban đầu:

```text
technique_primary
```

Sau đó thêm:

```text
db_family
syntax_validity
intent_secondary nếu đủ tin cậy
```

Không dùng db_engine chi tiết nếu ô dữ liệu thưa.

### 3.2. Backbone

Có thể chọn:

```text
LSTM decoder
hoặc Transformer decoder nhỏ
```

Khuyến nghị:

```text
Transformer decoder nhỏ nếu tài nguyên đủ
LSTM nếu muốn đơn giản và gần SeqGAN baseline
```

### 3.3. Output

```text
payload_delex_v5 tokens
```

Sau đó:

```text
payload_delex_v5
→ relex engine
→ payload literal
→ evaluator suite
```

---

## 4. Training method

Dùng Maximum Likelihood Estimation:

```text
teacher forcing
cross-entropy next-token prediction
```

Loss:

```text
L_MLE = CE(next_token_pred, next_token_true)
```

Có thể thêm nhẹ:

```text
label smoothing
dropout
class-balanced sampling
```

---

## 5. Sampling methods

Phải quét:

```text
temperature
top-k
top-p / nucleus
repetition penalty
max length
condition-balanced sampling
```

Không chọn một setting tùy ý. Tạo frontier.

---

## 6. Evaluator-guided generation

Quy trình:

```text
1. Chọn condition.
2. MLE sinh N candidates.
3. Relex candidates.
4. Evaluator chấm điểm.
5. Rerank hoặc reject.
6. Giữ top candidates.
```

Các phương pháp:

| Phương pháp | Mô tả |
|---|---|
| Best-of-N | Sinh N, chọn candidate score cao |
| Rejection sampling | Loại candidate không đạt rule |
| Reranking | Xếp hạng theo evaluator composite |
| Mutation after generation | Biến đổi nhẹ literal/comment/case |
| Diversity-aware selection | Không chọn nhiều candidate quá giống nhau |

---

## 7. Score function

Không dùng một score duy nhất thiếu kiểm soát.

Composite có thể gồm:

```text
syntax_score
type_consistency
db_consistency nếu known
novelty_score
diversity_bonus
DB_exec_score nếu applicable
WAF_score nếu relex/eval đủ tốt
```

Nhưng phải có guard:

```text
reject nếu exact-copy cao
reject nếu uniqueness thấp
reject nếu syntax invalid
reject nếu type sai
```

---

## 8. Relex-aware evaluation

Nếu relex chưa đủ tốt:

```text
không dùng WAF/IDS làm metric chính
```

Khi relex đủ tốt, đo:

```text
DB execution
WAF pass/bypass
literal-level uniqueness
literal-level novelty
```

---

## 9. Kết quả đầu ra

```text
models/phase07/mle_generator.pt
eval/phase07/mle_sampling_frontier.json
eval/phase07/generated_candidates.csv
reports/07_mle_first_generator_report.md
```

Generated CSV:

```csv
condition,
payload_delex,
payload_relex,
sampling_config,
syntax_score,
type_score,
db_score,
novelty_score,
diversity_group,
waf_score,
db_exec_score
```

---

## 10. Cách evaluate phase này

| Metric | Mục tiêu |
|---|---|
| Syntax validity | Cao |
| Type accuracy | Cao |
| Unique ratio | Không collapse |
| Self-BLEU | Không quá cao |
| Novelty | Không copy train |
| DB consistency | Tốt khi db known |
| DB execution | Chỉ khi relex/context đủ |
| WAF score | Chỉ dùng khi relex đủ tốt |
| Frontier | Quality-diversity trade-off rõ |

---

## 11. Kết luận

Nhánh này là default production/research path. Nếu GAN không thắng rõ, đây là kiến trúc chính của V5.
