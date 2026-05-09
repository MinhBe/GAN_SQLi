# Hyperparameter Reference — SeqGAN SQLi

## Core Hyperparameters

| Param | Default | Range | Notes |
|-------|---------|-------|-------|
| embed_dim | 128 | 64-256 | |
| hidden_dim | 512 | 256-1024 | |
| num_layers (G) | 3 | 2-6 | |
| dropout (G) | 0.2 | 0.1-0.4 | |
| kernel_sizes (D) | [3,4,5] | TextCNN | |
| num_filters (D) | 128 | 64-256 | |
| MLE epochs | 10 | 5-30 | Đến val perplexity converge |
| MLE LR | 1e-3 | | |
| SS ramp | 5k steps | | linear 0→1 |
| K rollout | 16 | 4-32 | |
| λ_D, λ_bypass, λ_syntax | 0.3, 0.5, 0.2 | | reward shaping |
| α (bypass vs syntax) | 0.7 | 0.5-0.9 | |
| baseline EMA | 0.95 | | |
| D:G ratio | 5:1 | | WGAN-GP |
| GP lambda | 10 | | |
| adv G LR | 1e-4 | | |
| adv D LR | 1e-4 | | |
| grad clip | 1.0 | | REINFORCE stability |
| batch_size | 64 | 32-128 | |
| total adv steps | 50k | 30k-200k | |

## Config YAML — seqgan_default.yaml

```yaml
pretrain:
  epochs: 10
  lr: 1.0e-3
  batch_size: 64
  expert_weight: 3.0
  scheduled_sampling_steps: 5000
  grad_clip: 1.0

adversarial:
  total_steps: 50000
  lr_g: 1.0e-4
  lr_d: 1.0e-4
  batch_size: 64
  mc_rollout_k: 16
  d_steps_per_g: 5
  gp_lambda: 10.0
  baseline_ema_decay: 0.95
  grad_clip: 1.0
```

## Tuning Guide

### OOM với MC Rollout
Giảm K=8 trước, sau đó gradient checkpointing nếu vẫn OOM.

### RL không converge
- Tăng K từ 16 → 24-32 để giảm variance
- Tăng baseline EMA weight
- Kiểm tra reward scale (nên ~0.1-1.0)

### Mode collapse
- Tăng dropout G lên 0.3-0.4
- Thêm diversity bonus vào reward
- Giảm D:G ratio từ 5:1 xuống 3:1 tạm thời

### Reward hacking (ASR cao, validity thấp)
- Tăng λ_syntax lên 0.4 (từ 0.2)
- Auto-adjust trigger: `if syntax_rate < 0.5 after 5k steps`
