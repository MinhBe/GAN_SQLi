# Timeline Update 2 — 2026-05-16 (Chiều)

> **Phiên bản**: V4 MLE Pretrain + Adversarial attempt
> **Ngày**: 2026-05-16 (chiều sau buổi gặp thầy)
> **Trạng thái**: Data pipeline hoàn tất. MLE BiLSTM done. V4 adversarial partial (crashed).
> **Người báo cáo**: Sinh viên (via opencode)

---

## 1. TÓM TẮT PHIÊN LÀM VIỆC

Đã triển khai toàn bộ pipeline từ label data → MLE pretrain → V4 adversarial:

| Bước | Việc | Kết quả |
|------|------|---------|
| 1 | Option C: Phase 2→3→4 full (subagent helper) | 40,545 rows labeled, 13,100 balanced |
| 2 | Tier split: gold/silver/bronze | gold 662, silver 3,250, bronze 9,188 |
| 3 | Nhận ra gold quá ít → quyết định relabel ALL | Từ bỏ Option C, chạy lại toàn bộ |
| 4 | Pre-label A+C (chat_queue) trên 40,545 rows | 25.8% rows có A≠C |
| 5 | Batch label 203 chunks × 200 rows | 0 errors, all 40,545 labeled |
| 6 | Strip wrapper → Delex v2 | 16.42% wrapper, collision 55.43% |
| 7 | Resample (cap 50/2000) → 13,100 rows | Balanced |
| 8 | Tier split (adjusted: sources_agree≥2) | gold 662, silver 3,250, bronze 9,188 |
| 9 | **MLE pretrain (LSTM)** | val_ppl=1.74 @ epoch 24, 34 epochs |
| 10 | Phát hiện LSTM≠BiLSTM → sửa pretrain_mle.py | Thêm GeneratorBiLSTMEncoder support |
| 11 | **MLE pretrain (BiLSTM)** | val_ppl=1.74 @ epoch 20, 30 epochs |
| 12 | **V4 adversarial start** | Crashed step 750 (UnicodeEncodeError⚠) |
| 13 | Fix encoding + restart | User aborted |

---

## 2. DATA PIPELINE — KẾT QUẢ CUỐI CÙNG

### 2.1 Dataset sizes
| Tier | Rows | Điều kiện |
|------|------|-----------|
| **Gold** | 662 | confidence ≥ 0.90 AND sources_agree ≥ 2 |
| **Silver** | 3,250 | confidence ≥ 0.70 AND sources_agree ≥ 1 |
| **Bronze** | 9,188 | còn lại |
| **Total balanced** | 13,100 | |

### 2.2 Gold quality
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Collision rate | 40.18% | < 15% | ❌ FAIL (nhưng cải thiện 1.8x từ 71.89%) |
| Top-10 coverage | 17.37% | < 10% | ❌ FAIL |
| Type entropy | 1.76 bits | > 2.0 bits | ❌ FAIL |
| Mean reasoning | 63.7 chars | > 60 chars | ✅ PASS |
| Type×DB holes | 4 | < 5 cells | ✅ PASS |

### 2.3 Gold type distribution
```
time_blind:      296 (44.7%)
benign:          213 (32.2%)
boolean_blind:   110 (16.6%)
union_based:      39 ( 5.9%)
out_of_band:       4 ( 0.6%)
```

### 2.4 Source agreement (balanced)
```
0/3 agree:   7,209 (55.0%)  — A≠C (no Haiku source)
1/3 agree:   2,387 (18.2%)
2/3 agree:   3,504 (26.7%)
```
**Lưu ý**: Hệ thống chỉ có 2 nguồn A (Rule) + C (Heuristic), không có Haiku API → max agreement = 2.

---

## 3. MLE PRETRAIN (BiLSTM Generator)

### 3.1 Config
| Param | Value |
|-------|-------|
| Model | GeneratorBiLSTMEncoder (Fix-8) |
| Vocab | 434 tokens |
| embed_dim | 256 |
| hidden_dim | 512 |
| enc_layers | 2, dec_layers = 2 |
| Batch size | 64 |
| LR | 1e-3 |
| Data | Gold + Silver (3,520 train / 392 val) |

### 3.2 Training curve
```
Epoch  1: loss=3.0975  val_ppl=6.84  ← best
Epoch  2: loss=1.7617  val_ppl=3.18  ← best
Epoch  5: loss=1.0910  val_ppl=1.99  ← best
Epoch 10: loss=0.9648  val_ppl=1.81
Epoch 15: loss=0.9280  val_ppl=1.77  ← best
Epoch 20: loss=0.9310  val_ppl=1.74  ← BEST (final best)
Epoch 25: loss=0.9164  val_ppl=1.74
Epoch 30: loss=0.9239  val_ppl=1.75  ← early stop (patience=10)
```
- **Best val_ppl: 1.74** (epoch 20)
- **Total epochs: 30/50** (early stop)

### 3.3 Bài học quan trọng
- `pretrain_mle.py` HARDCODE `GeneratorLSTM` — không thể load checkpoint vào `GeneratorBiLSTMEncoder`
- Đã sửa: thêm `use_bilstm` flag, import `GeneratorBiLSTMEncoder`
- Cần chạy MLE riêng nếu chuyển kiến trúc generator

---

## 4. V4 ADVERSARIAL — Attempt #1

### 4.1 Config
| Param | Value |
|-------|-------|
| Data dir | `Asset/LabelData/OpenCode/mle_data` |
| Checkpoint dir | `SeqGAN_SQLi/checkpoints/v4` |
| Steps | 2,000 warmup + 12,000 adv + 6,000 ref = 20,000 total |
| BiLSTM | Enabled (loaded MLE checkpoint, val_ppl=1.74) |
| WAF | Disabled (`--no_waf`) |

### 4.2 Progress before crash
```
Step   50: warmup  g=-0.5084  r=0.2694  unique=63/64
Step  100: warmup  g=-0.0348  r=0.3253  unique=62/64
Step  300: warmup  g=-0.5119  r=0.5403  unique=64/64
Step  500: warmup  g=-0.2471  r=0.6406  unique=64/64
Step  750: warmup  g=-0.2019  r=0.6847  unique=64/64 (CRASH)
```

### 4.3 Crash cause
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u26a0'
  at print(f"  ⚠ HEALTH [{step}]: ...")
  → Windows terminal cp1252 không hỗ trợ emoji
```
**Đã fix**: thay `⚠` bằng `[HEALTH]`.

### 4.4 Checkpoint đã lưu
| File | Size | Step |
|------|------|------|
| `adv_step1000.pt` | 61 MB | 1000 (auto-save) |

**Vấn đề**: `train_adversarial_v4.py` không có `--resume` flag → script chạy lại từ step 0.

---

## 5. LESSONS LEARNED (kỹ thuật)

| # | Bài học | Ảnh hưởng |
|---|---------|-----------|
| 1 | **pretrain_mle.py hardcode GeneratorLSTM** — không thể load vào BiLSTM | Phải sửa code + chạy lại MLE |
| 2 | **Chia sẻ checkpoint giữa MLE và adversarial** cần architecture match | Thêm BiLSTM support vào pretrain |
| 3 | **train_adversarial_v4.py không có resume** — crash = mất progress | Cần thêm resume logic |
| 4 | **Windows terminal cp1252** không hỗ trợ Unicode emoji | Dùng ASCII-safe characters |
| 5 | **`--save_dir` không tồn tại** trong pretrain_mle.py, dùng `--ckpt_dir` | Arg name khác nhau giữa scripts |
| 6 | **Path resolution double-nest** (SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/) | pretrain_mle.py line 104-106 join ROOT + path |
| 7 | **MLE training cực nhanh** trên CUDA (~25 it/s) → 30 epochs = 2 phút | Có thể retrain thoải mái |

---

## 6. FILE ĐÃ TẠO / SỬA

### Files mới
```
Asset/LabelData/OpenCode/
├── gold.csv                       (662 rows)
├── silver.csv                     (3,250 rows)
├── bronze.csv                     (9,188 rows)
├── dataset_v3_balanced.csv        (13,100 rows)
├── HOW_IT_WORKS.md                (pipeline guide)
├── RECOVERY_PLAN.md               (recovery instructions)
├── Recovery2.md                   (MLE pretrain plan + results)
├── eval_metrics.json              (quality metrics)
├── verification_report.txt        (verification output)
└── mle_data/
    ├── train.csv                  (3,520 rows, payload_delex + type_id)
    ├── val.csv                    (392 rows)
    ├── tokenizer_vocab.json       (434 tokens)
    └── expert_demos.csv           (empty)

SeqGAN_SQLi/
├── configs/
│   ├── seqgan_v4_mle.yaml         (MLE config với BiLSTM)
│   └── seqgan_v4_adv.yaml         (Adversarial config trỏ mle_data)
├── checkpoints/v4/
│   ├── mle_best.pt                (BiLSTM, val_ppl=1.74, 87MB)
│   ├── mle_final.pt               (BiLSTM, val_ppl=1.74, 87MB)
│   └── adv_step1000.pt            (adversarial step 1000, 61MB)
├── logs/v4/adversarial_v4/        (TensorBoard logs)
└── pretrain_mle.py                (sửa: thêm BiLSTM support)
```

### Files sửa
```
SeqGAN_SQLi/pretrain_mle.py        (thêm import + instantiate BiLSTM)
SeqGAN_SQLi/train_adversarial_v4.py (fix emoji + thêm MLE checkpoint path)
```

---

## 7. TRẠNG THÁI HIỆN TẠI

```
Phase 1 Triage:       ✅ (40,545 rows → keep + relabel)
Phase 2 Relabel:      ✅ (40,545 rows labeled via helper)
Phase 3 Transform:    ✅ (strip + delex v2)
Phase 4 Tier:         ✅ (gold 662 + silver 3,250 + bronze 9,188)
MLE Pretrain (BiLSTM): ✅ (val_ppl=1.74)
V4 Warmup (0-2000):   ⏳ Partially done (750/2000 steps, crashed)
V4 Adversarial:       ❌ Not started
V4 Refinement:        ❌ Not started
```

---

## 8. VIỆC CẦN LÀM TIẾP THEO

| # | Việc | Ưu tiên | Ghi chú |
|---|------|---------|---------|
| 1 | Chạy lại V4 adversarial từ step 0 | **Critical** | ~15-20 phút warmup, ~2h adv, ~1h ref |
| 2 | Thêm resume logic vào train_adversarial_v4.py | Medium | Tránh mất progress nếu crash lại |
| 3 | Cân nhắc thêm more benign data (Fix-7) | Low | Cần file benign_sql.csv |
| 4 | Setup Docker WAF cho adversarial phase | Low | Chỉ cho final eval |
| 5 | V4 evaluation + slide | Medium | Sau khi V4 training hoàn tất |

---

## 9. RISK UPDATE

| Rủi ro | Trạng thái | Mitigation |
|--------|-----------|------------|
| V4 warmup chưa hoàn tất (crashed 750/2000) | ⚠ Open | Chạy lại từ step 0 |
| No resume → mất progress nếu crash | ⚠ Open | Thêm resume flag |
| Collision 40% vẫn trên target 15% | ⚠ Open | Cần cải thiện delex hoặc chấp nhận |
| Type entropy 1.76 < 2.0 target | ⚠ Open | Cần balanced hơn trong data |
| Gold chỉ 662 rows (target ≥ 5,000) | ❌ FAIL | Giảm threshold hoặc augment |
