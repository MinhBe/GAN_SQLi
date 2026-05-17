# Tổng Kết Cải Thiện — SeqGAN SQLi V1 → V4

> **Ngày**: 2026-05-16  
> **Trạng thái hiện tại**: Data pipeline V3 hoàn tất (13,100 balanced), MLE BiLSTM pretrain done (val_ppl=1.74), V4 adversarial partial (crashed step 750, cần chạy lại)  
> **Model tốt nhất đến nay**: `checkpoints/v3/adv_step2000.pt` (composite 0.471 no-WAF)

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

### Phase 5 — Root Cause Discovery & Data Pipeline V3 (2026-05-16)

**Phát hiện chấn động**: Mode collapse KHÔNG do training dynamics — mà do **delex xóa sạch tín hiệu phân biệt**.

| Function | Trong data | Còn sau delex V1 | % Mất |
|----------|-----------|-----------------|-------|
| `xmltype` (Oracle error) | 5,793 | 0 | **100%** |
| `pg_sleep` (PostgreSQL time) | 225 | 0 | **100%** |
| `extractvalue` (MySQL error) | 250 | 0 | **100%** |
| `updatexml` (MySQL error) | 107 | 0 | **100%** |
| `dbms_pipe` (Oracle time) | 212 | 0 | **100%** |
| `randomblob` (SQLite time) | 190 | 0 | **100%** |
| `elt` (MySQL boolean) | 1,045 | 0 | **100%** |

**Thống kê dataset V1**:
- Delex collision: **71.89%** (17,821 unique -> 5,009 delex unique)
- Wrapper bias: **53.64%** payload bi boc `select * from users WHERE username = "..."`
- Top-100 patterns chiem **42.82%** dataset
- Reasoning < 20 chars: **40%** rows

**Giai phap**: Skill `sqli-data-curator` — 4-phase pipeline thay the 3 skills cu.

**4 Phase workflow**:

| Phase | Cong viec | Script |
|-------|-----------|--------|
| 1 TRIAGE | Critique label -> Keep/Relabel/Drop | `critique_labels.py` |
| 2 RELABEL | 3-source (rule + heuristic) + subagent chat | `label_payload.py`, `chat_label_coordinator.py` |
| 3 TRANSFORM | Strip wrapper + delex_v2 voi function whitelist | `strip_wrapper.py`, `delex_v2.py` |
| 4 TIER | Gold/Silver/Bronze split + resample | `tier_split.py`, `resample_balanced.py` |

**Ket qua prototype (1000 rows)**:

| Metric | Truoc (V1 delex) | Sau (Curator) | Target | Status |
|--------|------------------|---------------|--------|--------|
| Collision rate | 71.89% | **4.33%** | < 30% | PASS (16x) |
| Vocab size | 89 tokens | **147 tokens** | 100-180 | PASS |
| Top-100 coverage | 42.82% | **23.16%** | < 25% | PASS |
| xmltype preservation | 0% | **100%** | > 95% | PASS |

**Ket qua full pipeline (40,545 rows)**:

| Tier | Rows | Dieu kien |
|------|------|-----------|
| Gold | 662 | confidence >= 0.90 AND sources_agree >= 2 |
| Silver | 3,250 | confidence >= 0.70 AND sources_agree >= 1 |
| Bronze | 9,188 | con lai |
| **Total balanced** | **13,100** | resample cap 50/2000 |

**Gold quality**:
- Collision: 40.18% (cai thien 1.8x tu 71.89%, nhung chua dat target < 15%)
- Type entropy: 1.76 bits (target > 2.0)
- Mean reasoning: 63.7 chars
- Type x DB holes: 4 cells (< 5)

---

### Phase 6 — MLE BiLSTM Pretrain (2026-05-16)

**Van de**: V1-V3 dung LSTM thuan. Thay Lam goi y chuyen sang BiLSTM de capture context 2 chieu.

**Kien truc moi**:

| Thanh phan | Gia tri |
|-----------|---------|
| Model | `GeneratorBiLSTMEncoder` (2-layer BiLSTM encoder + 2-layer LSTM decoder) |
| Vocab | **434 tokens** (vs V3: 89 — nho giu function names) |
| embed_dim | 256 |
| hidden_dim | 512 |
| Data | Gold + Silver (3,520 train / 392 val) |

**Training curve**:

```
Epoch  1: val_ppl=6.84
Epoch 10: val_ppl=1.81
Epoch 20: val_ppl=1.74 <- BEST
Epoch 30: val_ppl=1.75 <- early stop (patience=10)
```

| Metric | V3 MLE (LSTM) | V4 MLE (BiLSTM) | Delta |
|--------|--------------|-----------------|-------|
| val_ppl | 1.70 | **1.74** | ~tuong duong |
| Vocab | 89 | **434** | +388% |
| Epochs | 5 (early stop) | 20 (early stop) | — |
| Training time | ~5 min | ~2 min (CUDA 25 it/s) | — |

**Luu y**: val_ppl 1.74 voi vocab 434 la tuong duong hoac tot hon V3 (1.70 voi vocab 89). Model co khong gian bieu dien rong hon nhieu.

---

### Phase 7 — V4 Adversarial Attempt (2026-05-16)

**8 anti-collapse fixes dong thoi** (dap ung 6 nhan xet thay Lam):

| Fix | Mo ta | Dap ung |
|-----|-------|---------|
| 1. Entropy boost | `entropy_coeff` 0.03 -> 0.10 | Anti-collapse |
| 2. Temperature boost | 1.1 -> 1.30 | Anti-collapse |
| 3. EMA faster | alpha 0.05 -> 0.20 | Anti-collapse |
| 4. Type-balanced batch | Stratified 14 attack types | Anti-collapse |
| 5. Diversity reward | Jaccard novelty vs buffer 256 | Anti-collapse |
| 6. Dynamic D steps | Giam khi G collapse | Anti-collapse |
| 7. **Benign SQL in D** | 5000 benign queries vao fake pile | Thay #5 |
| 8. **BiLSTM encoder** | GeneratorBiLSTMEncoder | Thay #4 |

**Ket qua training (crashed)**:

```
Step   50: warmup  g=-0.5084  r=0.2694  unique=63/64
Step  100: warmup  g=-0.0348  r=0.3253  unique=62/64
Step  300: warmup  g=-0.5119  r=0.5403  unique=64/64
Step  500: warmup  g=-0.2471  r=0.6406  unique=64/64
Step  750: CRASH — UnicodeEncodeError (emoji)
```

**Da fix**: emoji -> ASCII. Checkpoint luu tai `adv_step1000.pt` (61MB). Can chay lai tu step 0 do chua co resume flag.

---

## Bai Hoc Ky Thuat

1. **REINFORCE collapse la fundamental**: Khong phai bug, la dac tinh cua on-policy RL voi fixed reward ceiling. Entropy reg giam nhe, khong giai quyet triet de.

2. **Warmup > Adversarial trong context nay**: Custom rule reward (0.70 ceiling) + DB gate qua "de dat" -> generator khong can adversarial signal. Warmup voi entropy reg du de train model tot.

3. **Cache hit rate la health metric tot**: V2 step1000 = 93% hit rate -> collapse ro. V3 step1000 = 42% -> diversity tot. Monitor metric nay trong training.

4. **De-lex + re-lex la bat buoc**: Reward function can actual SQL. Quen re-lex -> moi payload score -0.5 (DB gate fail) -> training khong y nghia.

5. **Root cause collapse la data, khong phai training**: 71.89% collision do delex xoa function name. 8 training fixes khong cuu duoc neu data garbage.

6. **Function whitelist la gate**: Chi can giu ~30 SQLi-significant functions (xmltype, pg_sleep, extractvalue...) la collision rate giam tu 71.89% -> 4.33%.

7. **Wrapper bias la bay hidden**: 53.64% payload bi boc trong wrapper query -> delex bien inner payload thanh `__STR__` -> mat het thong tin. Strip wrapper la buoc bat buoc.

8. **BiLSTM vs LSTM**: val_ppl tuong duong (~1.74) nhung BiLSTM co vocab lon hon 5x (434 vs 89) -> model hoc duoc nhieu function names hon.

9. **Windows gotchas**: Unicode `->` crash, emoji crash terminal cp1252, PowerShell heredoc syntax khac bash, path resolution double-nest.

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
| `timeline/V3_RESULTS.md` | V3 results + verdict |
| `timeline/WAF_EVAL_RESULTS.md` | WAF eval với ModSecurity OWASP CRS |
| `configs/seqgan_v4.yaml` | V4 config với 8 anti-collapse params |
| `train_adversarial_v4.py` | V4 training script (BiLSTM + diversity) |
| `checkpoints/v4/mle_best.pt` | MLE BiLSTM pretrain (val_ppl=1.74) |
| `Skill/sqli-data-curator/SKILL.md` | 4-phase data curation workflow |
| `Asset/LabelData/OpenCode/dataset_v3_balanced.csv` | Final balanced dataset (13,100 rows) |
| `Asset/LabelData/OpenCode/gold.csv` | Gold tier (662 rows) for MLE training |
