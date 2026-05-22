# 09 — Final Evaluation And Delivery

> Mục tiêu: kết luận nhánh Gumbel/action-surgery bằng so sánh công bằng, không cherry-pick.

---

## 1. Models cần evaluate

```text
H1 Conditional MLE
H2 MLE + D-as-scorer
H3 anchor-only action infiller
H4 Gumbel action-surgery GAN
H5 rule/tamper baseline
```

---

## 2. Evaluation sets

```text
validation
verified_dev
verified_test
holdout_rare
dialect_lab_set nếu có
WAF_lab_set nếu relex pass
```

Verified_test chỉ dùng cuối.

---

## 3. Metric groups

```text
quality: round_trip, parse, slot boundary, dialect soft validity
control: condition/action accuracy, db consistency
diversity: unique, self-BLEU, template/action entropy
novelty: exact/near-copy, cluster novelty
security: WAF/IDS sau validity pass
robustness: mean/std/CI, worst seed
```

---

## 4. Kết luận hợp lệ

### Trường hợp 1 — MLE/D-scorer thắng

```text
MLE-first hoặc MLE + D-as-scorer là kiến trúc chính.
Action-GAN là negative/limited result.
```

### Trường hợp 2 — Action-GAN thắng rõ

```text
Gumbel action-surgery vượt anchor-only và D-scorer trong frontier đã đăng ký.
Có thể claim adversarial action selection tạo giá trị.
```

### Trường hợp 3 — Không rõ

```text
Tie-break chọn baseline đơn giản hơn.
Action-GAN giữ future work.
```

---

## 5. Artifacts

```text
eval/gumbel/final/frontier.json
eval/gumbel/final/statistical_summary.json
eval/gumbel/final/generated_samples.csv
eval/gumbel/final/verified_test_results.json
reports/gumbel/09_final_evaluation_and_delivery.md
```

---

## 6. Kết luận

Final evaluation không đi tìm con số đẹp nhất. Nó trả lời: action-surgery có đáng làm main result hơn MLE/D-scorer không.
