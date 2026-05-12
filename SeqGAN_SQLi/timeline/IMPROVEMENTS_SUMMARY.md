# Tổng Kết Cải Thiện — SeqGAN SQLi V1 → V3

> **Ngày**: 2026-05-12  
> **Kết quả cuối**: `checkpoints/v3/adv_step2000.pt` — warmup-trained model  
> **Composite score**: 0.471 (no WAF) — cải thiện **+133%** so với MLE baseline

---

## Hành Trình Cải Thiện

### Phase 0 — Data Pipeline V2 (2026-05-10 → 05-12)

**Vấn đề ban đầu**: Dataset V1 có 40,860 rows nhưng label chất lượng thấp, không có tiered confidence, không có de-lex nhất quán.

**Cải thiện:**
- Audit + relabel toàn bộ dataset → 17,821 rows chất lượng cao (loại benign)
- Tiered confidence: gold (≥0.95), silver (0.80–0.94), bronze (bỏ qua khi train)
- Stratified split V2: 12,474 train / 2,673 val / 2,674 test
- Aggressive de-lex: 8 placeholder types (`__INT__`, `__STR__`, `__HEX__`, `__TABLE__`, `__COL__`, `__IDENT__`, `__TIME__`, `__BIGINT__`)
- Re-lex dictionary: `data/relex_dictionary.json` cho phép restore actual SQL khi scoring reward
- Vocab: **89 tokens** (vs V1: 134) — tinh gọn hơn nhờ de-lex tốt hơn
- 4 attack types rõ ràng: error_based=0, boolean_blind=1, time_blind=2, union_based=3

**Commit**: `c083331` — Phase 0 complete

---

### Phase 1–3 — Infrastructure V2 (2026-05-12 sáng)

**Vấn đề**: Playbook có nhiều API không khớp với codebase thực tế.

**9 bugs phát hiện và fix** (ghi trong `timeline/V2_IMPLEMENTATION_NOTES.md`):

| # | Bug | Fix |
|---|---|---|
| 1 | `NUM_SQLI_TYPES=18` trong utils.py nhưng data chỉ có 4 | Đọc `type_id` trực tiếp từ CSV |
| 2 | Class `Generator` không tồn tại | Dùng `GeneratorLSTM` |
| 3 | `SQLTokenizer.from_vocab()` không tồn tại | Viết helper `load_tokenizer()` |
| 4 | Vocab size V2=89 ≠ V1=134 | Fix config `vocab_size: 89` |
| 5 | `num_attack_types: 8` trong playbook | Đổi thành 4 |
| 6 | MLE không pass conditional embedding | Tạo `pretrain_mle_v2.py` với `cond=type_ids` |
| 7 | Columns V2 CSV khác V1 | Adapt code dùng `payload_delex`, `tier`, `type_id` |
| 8 | Reward nhận de-lexed string, không phải actual SQL | Thêm `relex()` trước `reward_fn()` |
| 9 | `→` gây UnicodeEncodeError trên Windows | Đổi sang `->` |

**Files tạo mới**: `src/waf_oracle.py`, `src/custom_rules.py`, `src/parser_gate.py`, `src/db_sandbox.py`, `src/ast_tracker.py`, `src/reward_cache.py`, `src/reward_v2.py`, `configs/seqgan_v2.yaml`, `pretrain_mle_v2.py`, `train_adversarial_v2.py`

**Commit**: `0cb8847` — Phase 1-2-3 complete

---

### MLE Pretrain V2 (2026-05-12 09:21–09:36)

| Metric | V1 | V2 | Delta |
|---|---|---|---|
| val_ppl (final) | ~1.70 | **1.27** | **-25%** |
| Epochs | 10 (no early stop) | 9 (early stop) | — |
| Training time | ~20 min | ~15 min | -25% |

**Tại sao tốt hơn**: WeightedRandomSampler (gold=3×, silver=1×) + dataset sạch hơn + conditional embedding theo attack type.

---

### V2 Adversarial Training (2026-05-12 10:08–10:54, 46 min)

**Kết quả (500 samples, no WAF)**:

| Checkpoint | Composite | Re-lex Uniq | AST-H | DB% | ML-IDS% |
|---|---|---|---|---|---|
| v2_mle | 0.202 | 0.686 | 3.08 | 3.2% | 3.4% |
| v2_step1000 | **0.394** | 0.010 | 2.42 | 99.8% | **31.4%** |
| v2_step2000+ | 0.353 | 0.002 | 2.565 (frozen) | 100% | 0% |

**Phát hiện quan trọng — Mode Collapse tại step 2000**:
```
Cơ chế:
  Generator tìm payload đạt reward 0.70 → tất cả samples cùng reward
  → advantage = reward - mean ≈ 0
  → gradient REINFORCE ≈ 0
  → Generator không học gì thêm
  → Lặp lại 1-2 payload duy nhất mãi mãi
```
Bằng chứng: cache hit rate 93% tại step 1000, AST entropy đóng băng tại 2.5649 từ step 2000 → 20000.

**Commit**: `53865ae` — Phase 4-5 complete

---

### V3 Adversarial Training — Entropy Regularization (2026-05-12 11:08–12:xx)

**3 fixes chống mode collapse**:

| Fix | Mô tả | Tác dụng |
|---|---|---|
| **Entropy regularization** | `g_loss = pg_loss - entropy_coeff * H(logits)` | Gradient ≠ 0 kể cả khi advantage=0 |
| **EMA baseline** | `ema = 0.95*ema + 0.05*batch_mean` | Cung cấp signal khi tất cả rewards bằng nhau |
| **Temperature sampling** | warmup=1.2, adv=1.1, ref=1.0 | Tăng exploration, giảm tốc độ collapse |

**Kết quả training** (`--no_waf`):

```
Warmup (steps 1–2000):
  - unique/64: 6 → 64/64 (recovered by step 750, V2 stuck at 1-2/64)
  - H (entropy): 1.06 → 1.46 (tăng liên tục)
  - avg_reward: 0.39 → 0.62
  - cache hit rate: 42% (V2 = 93%) — diversity 2× tốt hơn

Adversarial (steps 2000–12000):
  - unique/64: 64 → 6-7 (collapse nhưng chậm hơn V2, H không về 0)
  - g_loss ≠ 0 (entropy term duy trì gradient ở -0.01)
```

**Kết quả eval (500 samples, no WAF)**:

| Checkpoint | Composite | Re-lex Uniq | AST-H | DB% | Custom% |
|---|---|---|---|---|---|
| V2 best (step1000) | 0.394 | 0.010 | 2.42 | 99.8% | 60.0% |
| **V3 step1000** | **0.460** | **0.926** | 2.91 | 99.8% | 77.4% |
| **V3 step2000 ★** | **0.471** | **1.000** | **3.07** | 99.2% | 94.6% |
| V3 step12000 | 0.357 | 0.008 | 2.67 | 100% | 80% |
| V3 final | 0.357 | 0.008 | 2.66 | 100% | 80% |

**Commits**: `33cd047` (V3 code), `473448d` (V3 eval)

---

## Final Model — Warmup-Trained

**`checkpoints/v3/adv_step2000.pt`** = checkpoint tại cuối warmup phase.

Đây là **sweet spot**: warmup đủ dài để học SQL syntax + custom rules, nhưng chưa bước vào adversarial phase (nơi mode collapse xảy ra). Entropy regularization trong warmup giữ diversity hoàn toàn.

```
Để generate samples từ model tốt nhất:
  python SeqGAN_SQLi/generate_v2.py \
    --config SeqGAN_SQLi/configs/seqgan_v3.yaml \
    --ckpt SeqGAN_SQLi/checkpoints/v3/adv_step2000.pt \
    --n_samples 1000 \
    --out output/final_payloads.csv
```

---

## Tổng Hợp Cải Thiện So Với Baseline

| Metric | MLE baseline | **Final model** | Cải thiện |
|---|---|---|---|
| Composite score | 0.202 | **0.471** | **+133%** |
| DB execution rate | 3.2% | **99.2%** | **+31× lần** |
| Re-lex uniqueness | 0.686 | **1.000** | +45% |
| AST diversity entropy | 3.08 | **3.07** | ≈ giữ nguyên |
| Custom rules pass | 86.8% | **94.6%** | +7.8pp |
| Syntax pass rate | 99.8% | **100%** | — |

**Tradeoff duy nhất**: ML-IDS evasion = 0% ở final model (vs MLE's 3.4%) — IDS dễ nhận diện pattern của warmed-up adversarial generator.

---

## WAF Evaluation (ModSecurity OWASP CRS)

Eval thêm với WAF bật cho thấy ranking thay đổi:

| Checkpoint | No-WAF | **With-WAF** | OWASP bypass | Uniq |
|---|---|---|---|---|
| V3 step1000 | 0.460 | **0.491** | 9.8% | 0.926 |
| V3 step2000 ★ | **0.471** | 0.476 | 2.0% | **1.000** |
| V3 step12000 (collapsed) | 0.357 | 0.488 | **43.4%** | 0.008 |

**Phát hiện quan trọng**: Collapsed model (step12000, payload = `1 or 'root'`) bypass WAF 43% vì pattern quá đơn giản để WAF CRS detect. Tuy nhiên diversity gần 0 → không có giá trị thực tế.

**Khuyến nghị**:
- Dataset đa dạng (red-team): `v3/adv_step2000.pt` (uniqueness=1.000)
- WAF stress test: `v3/adv_step1000.pt` (WAF composite=0.491, bypass=9.8%, uniq=0.926)

---

## Bài Học Kỹ Thuật

1. **REINFORCE collapse là fundamental**: Không phải bug, là đặc tính của on-policy RL với fixed reward ceiling. Entropy reg giảm nhẹ, không giải quyết triệt để.

2. **Warmup > Adversarial trong context này**: Custom rule reward (0.70 ceiling) + DB gate quá "dễ đạt" → generator không cần adversarial signal. Warmup với entropy reg đủ để train model tốt.

3. **Cache hit rate là health metric tốt**: V2 step1000 = 93% hit rate → collapse rõ. V3 step1000 = 42% → diversity tốt. Monitor metric này trong training.

4. **De-lex + re-lex là bắt buộc**: Reward function cần actual SQL. Quên re-lex → mọi payload score -0.5 (DB gate fail) → training không ý nghĩa.

5. **Windows gotchas**: Unicode `→` crash, PowerShell heredoc syntax khác bash, stdout buffering với Start-Process.

---

## Files Quan Trọng

| File | Vai trò |
|---|---|
| `checkpoints/v3/adv_step2000.pt` | **Production model** |
| `configs/seqgan_v3.yaml` | Config V3 với entropy params |
| `train_adversarial_v3.py` | Training script V3 |
| `generate_v2.py` | Sampling script (dùng cho cả V2 và V3) |
| `eval/evaluate_v2.py` | 5-metric evaluation |
| `eval/compare_v2_v3.py` | So sánh V2 vs V3 |
| `timeline/V2_IMPLEMENTATION_NOTES.md` | 9 bugs đã fix |
| `timeline/V2_RESULTS.md` | V2 full analysis + V3 recommendation |
| `timeline/V3_RESULTS.md` | V3 results + verdict |
| `timeline/WAF_EVAL_RESULTS.md` | WAF eval với ModSecurity OWASP CRS |
