# Recovery 2 — MLE Pretrain Pipeline (Gold + Silver → Generator)

> **Mục đích**: MLE pretrain Generator LSTM trên gold + silver tiers, làm bước 1 trước khi chạy adversarial training V4.
> **Trạng thái**: ✅ Hoàn thành

---

## 1. MỤC TIÊU

- Pretrain `GeneratorLSTM` bằng MLE loss + Scheduled Sampling
- Dữ liệu: gold (662 rows) + silver (3,250 rows) = ~3,912 rows
- Output: `mle_best.pt` (best val perplexity) + `mle_final.pt`

## 2. CHUẨN BỊ DỮ LIỆU

### 2.1 Nguồn
| File | Rows | Tier |
|------|------|------|
| `gold.csv` | 662 | confidence ≥ 0.90, sources_agree ≥ 2 |
| `silver.csv` | 3,250 | confidence ≥ 0.70, sources_agree ≥ 1 |
| **Tổng** | **3,912** | |

### 2.2 Column mapping
- `payload_delex_v2` → `payload_delex` (rename)
- Tokenizer built từ `payload_delex` text

### 2.3 Output structure
```
Asset/LabelData/OpenCode/mle_data/
├── train.csv              # 90% = ~3,521 rows, cột payload_delex
├── val.csv                # 10% = ~391 rows, cột payload_delex
├── expert_demos.csv       # Empty (no expert data)
└── tokenizer_vocab.json   # Vocab built từ train+val delex text
```

## 3. CONFIG

### 3.1 MLE-specific config (`seqgan_v4_mle.yaml`)
```yaml
model:
  embed_dim: 256
  hidden_dim: 512
  num_layers: 2
  dropout: 0.2
  max_len: 80

pretrain:
  epochs: 50
  lr: 1.0e-3
  batch_size: 64
  expert_weight: 3.0
  scheduled_sampling_steps: 5000
  grad_clip: 1.0
  patience: 10
  seed: 42
```

## 4. COMMAND

```powershell
python SeqGAN_SQLi/pretrain_mle.py `
  --config SeqGAN_SQLi/configs/seqgan_v4_mle.yaml `
  --data_dir Asset/LabelData/OpenCode/mle_data `
  --epochs 50 `
  --save_dir SeqGAN_SQLi/checkpoints/v4
```

## 5. KẾT QUẢ

| Metric | Value |
|--------|-------|
| Vocab size | 434 |
| Best val perplexity | **1.74** (epoch 24) |
| Final val perplexity | 1.76 (epoch 34 — early stop) |
| Epochs run | 34 / 50 (early stop, patience=10) |
| Loss curve | 3.26 → 0.91 (epoch 1 → epoch 34) |
| Best checkpoint | `SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/v4/mle_best.pt` (48MB) |
| Final checkpoint | `SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/v4/mle_final.pt` (48MB) |

> **Note**: Checkpoints saved at `SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/v4/` due to `pretrain_mle.py` path resolution (joins `--ckpt_dir` with script dir). Copy to `SeqGAN_SQLi/checkpoints/v4/` if needed by adversarial trainer.

## 6. NEXT STEPS

1. ✅ MLE pretrain (this)
2. ⬜ V4 adversarial training (warmup 2000 + adversarial 12000 + refinement 6000)
3. ⬜ Evaluation + slide
