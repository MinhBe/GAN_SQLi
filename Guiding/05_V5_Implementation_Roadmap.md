# V5 Implementation Roadmap

> File tổng hợp thứ tự triển khai thực tế từ 16 CSV shard `payload_norm` đến Conditional Gumbel-SeqGAN V5.

---

## 1. Nguyên tắc làm lại từ đầu

Không reuse checkpoint V3/V4 làm nền chính.

Có thể reuse ý tưởng:

```text
entropy regularization
WGAN-GP
delex_v2
strip wrapper trước delex
composite evaluation
```

Nhưng không nên reuse trực tiếp:

```text
old labels
old gold/silver split
old train/val split
old final checkpoint
```

---

# 2. Roadmap tổng thể

```text
Phase 1 — Data Foundation
  16 CSV shards
  → normalize
  → decode
  → dedup
  → canonicalize
  → near-dedup
  → strip wrapper
  → delex_v2

Phase 2 — Labeling System
  → is_sqli
  → technique_primary
  → intent_secondary
  → db_engine
  → syntax_validity
  → confidence
  → review priority
  → gold/silver/bronze

Phase 3 — Model Separation
  → Label Quality Model
  → SQLi Type/DB Classifier
  → Evaluator Suite

Phase 4 — Conditional Gumbel-SeqGAN
  → MLE warmup
  → adversarial WGAN-GP
  → controlled reward fine-tune
  → checkpoint selection
```

---

# 3. Deliverables theo phase

## Phase 1 deliverables

```text
data/processed/phase1_payload_foundation.parquet
data/processed/exact_dedup_map.parquet
data/processed/near_dup_clusters.parquet
reports/phase1_data_foundation_report.md
```

## Phase 2 deliverables

```text
data/labeled/phase2_labeled_payloads.parquet
data/labeled/gold.parquet
data/labeled/silver.parquet
data/labeled/bronze.parquet
data/labeled/review_queue.parquet
reports/phase2_gold_quality_report.md
```

## Phase 3 deliverables

```text
models/label_quality/label_quality_model.pkl
models/sql_classifier/classifier_best.pt
models/evaluators/
reports/phase3_classifier_eval_report.md
```

## Phase 4 deliverables

```text
checkpoints/v5/mle_best.pt
checkpoints/v5/adv_stepXXXX.pt
eval/results_v5/*.json
eval/samples_v5/*.csv
reports/phase4_v5_eval_report.md
```

---

# 4. Thứ tự code nên build

## Nhóm A — Data

```text
01_load_shards.py
02_normalize_decode.py
03_exact_dedup.py
04_canonicalize.py
05_near_dedup.py
06_strip_wrapper.py
07_delex_v2.py
08_phase1_report.py
```

## Nhóm B — Label

```text
09_sql_signal_detector.py
10_technique_detector.py
11_intent_detector.py
12_db_engine_detector.py
13_syntax_context_checker.py
14_conflict_resolver.py
15_confidence_calibrator.py
16_tier_split.py
17_phase2_report.py
```

## Nhóm C — Model separation

```text
18_train_label_quality.py
19_train_multitask_classifier.py
20_eval_classifier.py
21_build_evaluator_suite.py
```

## Nhóm D — Gumbel-SeqGAN

```text
22_tokenizer.py
23_generator_gumbel.py
24_discriminator_wgan_gp.py
25_losses.py
26_train_mle.py
27_train_adversarial.py
28_evaluate_checkpoint.py
29_generate_samples.py
30_phase4_report.py
```

---

# 5. Minimal viable V5

Nếu cần làm bản nhỏ trước, chọn scope:

```text
Input:
  16 CSV shards

Phase 1:
  normalize
  exact dedup
  strip wrapper
  delex_v2

Phase 2:
  rule labeler cho:
    is_sqli
    technique_primary
    db_engine
    confidence

Phase 3:
  train one multi-task classifier

Phase 4:
  train ConditionalGumbelGenerator + WGAN-GP
  evaluate type/db/uniqueness/AST
```

Không cần làm ngay:

```text
WAF fine-tune
IDS evasion
LLM relabel toàn bộ
LeakGAN/RelGAN
complex mutation engine
```

---

# 6. Success criteria V5

## Data

| Metric | Target |
|---|---:|
| Cluster leakage | 0 |
| Delex collision gold | < 10% |
| Top-10 coverage gold | < 10% |
| Technique entropy | > 2.0 bits |
| Gold size | càng lớn càng tốt, target tối thiểu 10k |

## Classifier

| Metric | Target |
|---|---:|
| is_sqli F1 | > 0.95 nếu gold sạch |
| technique macro F1 | > 0.75 ban đầu |
| db_engine macro F1 | > 0.75 trên known engine |
| syntax macro F1 | > 0.80 |

## Generator

| Metric | Target |
|---|---:|
| unique ratio | > 0.70 |
| self-BLEU-3 | < 0.85 |
| type accuracy | > 0.70 |
| db consistency | > 0.70 |
| AST entropy | tăng so với V3 |
| train exact-copy rate | thấp, report rõ |

---

# 7. Best checkpoint rule

Không chọn checkpoint cuối mặc định.

Chọn checkpoint theo rule:

```text
score = weighted composite
nhưng reject nếu:
  unique ratio thấp
  self-BLEU quá cao
  type accuracy thấp
  db consistency thấp
  exact-copy rate cao
```

Ví dụ:

```text
Nếu WAF bypass = 40%
nhưng uniqueness = 0.01
→ reject
```

---

# 8. Rủi ro chính và cách giảm

| Rủi ro | Cách giảm |
|---|---|
| Labeler bias | multi-module + confidence calibration |
| Gold set nhỏ | dùng silver có kiểm soát + review queue |
| DB engine unknown quá nhiều | train generic riêng, engine-specific riêng |
| Mode collapse | Gumbel-Softmax + entropy + novelty |
| Reward hacking | multi-metric gate |
| Val metric đẹp giả | split theo near_dup_cluster |
| Generator ignore condition | type/db consistency loss |

---

# 9. Kết luận roadmap

V5 nên được triển khai như một hệ thống AIOps/ML pipeline, không phải một script GAN.

Câu triển khai cốt lõi:

```text
Build data observability trước.
Build label observability sau.
Build evaluator trước generator.
Sau cùng mới train Conditional Gumbel-SeqGAN.
```
