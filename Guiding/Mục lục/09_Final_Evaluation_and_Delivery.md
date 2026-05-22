# 09 — Final Evaluation & Delivery

> Mục tiêu: đánh giá cuối cùng toàn bộ hệ thống V5 một cách nhất quán, không cherry-pick, không chỉ báo cáo best checkpoint, và đưa ra kết luận kiến trúc rõ ràng.

---

## 1. Vấn đề cần giải quyết

Các version cũ có rủi ro:

```text
chọn checkpoint theo metric đẹp nhất
WAF score cao nhưng diversity thấp
final checkpoint collapse
DB execution bị thổi phồng
không so công bằng với baseline
```

Phase này đảm bảo kết luận cuối cùng đáng tin.

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| Frozen evaluation | Dùng verified_test không tune |
| Multi-metric | Không phụ thuộc một score |
| Baseline-comparative | So MLE-first và GAN nếu có |
| Relex-aware | DB/WAF đo trên payload literal |
| Reproducible | Có seed/config/checkpoint rõ |

---

## 3. Models cần evaluate

Tối thiểu:

```text
Conditional MLE Generator
MLE + evaluator-guided search
MLE + D-as-scorer/rerank nếu Phase 08B được chạy
anchor-only masked infiller nếu Phase 08C được chạy
paired masked payload-surgery GAN nếu pilot pass
```

Có thể thêm:

```text
random/template baseline
rule-based mutation baseline
old V3 checkpoint nếu chỉ để tham khảo lịch sử
```

---

## 4. Evaluation sets

```text
validation set
verified_dev
verified_test
holdout_rare
WAF lab set
DB execution set
```

Verified_test chỉ dùng cuối.

---

## 5. Metric groups

### 5.1. Quality

```text
syntax_validity
parse_success
DB_exec_success nếu applicable
valid_fragment_rate
```

### 5.2. Control

```text
type_accuracy
db_consistency
intent_consistency nếu dùng intent
condition_ignore_rate
```

### 5.3. Diversity

```text
unique_ratio
self-BLEU-3
template_entropy
AST_entropy
top-k coverage relative to train
```

### 5.4. Novelty

```text
exact_copy_rate
near_copy_rate
nearest_neighbor_similarity
cluster_novelty
```

### 5.5. Security lab

Chỉ dùng khi relex đủ tốt:

```text
WAF pass/bypass
WAF rule triggered
IDS evasion nếu có
```

Không dùng WAF score nếu:

```text
relex chưa đủ literal diversity
payload không phải literal thật
```

### 5.6. Robustness

```text
mean/std across seeds
confidence interval
worst-seed performance
training stability
```

---

## 6. Checkpoint selection

Không chọn final mặc định.

Reject checkpoint nếu:

```text
unique_ratio thấp
self-BLEU quá cao
exact-copy cao
type accuracy thấp
db consistency thấp
D shortcut fail
proxy_true_gap tăng bất thường
WAF cao nhưng diversity thấp
```

---

## 7. Báo cáo MLE frontier

MLE phải có frontier:

```text
temperature
top-k
top-p
repetition penalty
best-of-n size
```

Report:

```text
quality-diversity curve
best configs theo từng vùng
```

---

## 8. Báo cáo GAN

Nếu có GAN:

```text
3+ seeds
mean/std/CI
collapse curve
D shortcut diagnostic
proxy_true_gap
comparison với MLE frontier
```

Không báo cáo best seed như kết luận.

---

## 9. Kết quả đầu ra

```text
reports/09_final_evaluation_report.md
eval/final/mle_frontier.json
eval/final/gan_comparison.json
eval/final/generated_samples_mle.csv
eval/final/generated_samples_gan.csv
eval/final/verified_test_results.json
```

---

## 10. Kết luận kiến trúc

Báo cáo cuối phải kết luận rõ một trong ba trường hợp:

### Trường hợp 1 — MLE-first thắng

```text
Conditional MLE + evaluator-guided search là kiến trúc chính.
GAN không đủ lợi thế để full-scale/main.
```

### Trường hợp 2 — GAN thắng rõ

```text
Paired masked payload-surgery GAN vượt MLE frontier và anchor-only theo protocol.
GAN có thể trở thành đóng góp trung tâm hoặc co-main research result.
```

### Trường hợp 3 — Kết quả không rõ

```text
MLE-first là main do tie-break.
GAN giữ ở future work hoặc cần pilot thêm.
```

---

## 11. Cách evaluate phase này

Phase này pass nếu:

```text
có verified_test frozen
có so sánh MLE vs GAN công bằng
có multi-seed report
có relex-aware metrics
không cherry-pick
có quyết định kiến trúc rõ
```

---

## 12. Kết luận

Final evaluation không phải để tìm con số đẹp nhất. Nó để trả lời:

```text
Kiến trúc nào nên là kết quả chính của V5?
MLE-first, MLE+D-scorer, hay paired masked payload-surgery GAN?
Vì sao?
```
