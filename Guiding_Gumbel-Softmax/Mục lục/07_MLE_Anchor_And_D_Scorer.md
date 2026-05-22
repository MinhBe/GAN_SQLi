# 07 — MLE Anchor Và D-as-scorer

> Mục tiêu: xây baseline chính và deliverable GAN an toàn trước khi train generator adversarial.

---

## 1. Vì sao Phase 07 đứng trước GAN

MLE hiện là baseline mạnh: Phase 3 chọn `MLE_MAIN`, với MLE frontier tốt hơn GAN cũ về unique/self-BLEU/frontier. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\..\Guiding\Phase%203\eval\phase03\decision.json)

Do đó mọi adversarial result phải so với:

```text
MLE candidate
anchor-only action infiller
MLE + D-as-scorer
```

---

## 2. H1 — MLE anchor

Vai trò:

```text
candidate source
syntax anchor
teacher forcing target
baseline frontier
```

Artifacts:

```text
models/gumbel/mle_anchor.pt
eval/gumbel/mle_anchor_frontier.json
```

---

## 3. H2 — D-as-scorer

D-as-scorer phải là đóng góp độc lập, không chỉ là lưới an toàn; phản biện đã chốt đây là kết quả GAN dương dễ đạt nhất. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:54-56`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

Quy trình:

```text
1. MLE sinh N candidates/action variants.
2. Paired-D học real vs generated trong cùng frame/condition.
3. Freeze D.
4. D rerank/reject candidate.
5. Final score = D + evaluator floors + novelty.
```

Không claim:

```text
D-as-scorer là GAN generator mới
```

Claim hợp lệ:

```text
Adversarial discriminator improves candidate selection/reranking.
```

---

## 4. Diagnostic cho D

```text
template shortcut test
length shortcut test
condition imbalance test
soft/hard representation shortcut test
paired swap test
```

D pass nếu vẫn phân biệt được chất lượng action khi template/length/condition đã được kiểm soát.

---

## 5. Output

```text
models/gumbel/paired_d_scorer.pt
eval/gumbel/d_scorer_frontier.json
reports/gumbel/07_mle_anchor_and_d_scorer.md
```

---

## 6. Gate

D-as-scorer pass nếu:

```text
rerank cải thiện frontier so với MLE raw candidates
không tăng near-copy
không giảm validity
shortcut diagnostic pass
```

---

## 7. Kết luận

Chạy H2 trước H4 giúp luận văn có kết quả dương ngay cả khi generator adversarial không thắng.
