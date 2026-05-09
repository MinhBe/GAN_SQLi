# Common Pitfalls & Fixes — SeqGAN SQLi

## Diagnostic Table

| Triệu chứng | Nguyên nhân | Hành động |
|-------------|-------------|-----------|
| MLE loss không giảm | LR / architecture | Tune LR, tăng capacity G |
| RL divergence / NaN | Variance gradient | Tăng baseline weight, K=24-32 |
| Reward plateau, ASR thấp | Reward hacking | Thêm length penalty, semantic check |
| Mode collapse | G collapse về 1 mode | Tăng dropout, diversity bonus |
| ASR cao, validity thấp | G học bypass trick không hợp lệ SQL | Tăng λ_syntax |
| Validity cao, ASR ngang baseline | G chỉ học MLE distribution | Tăng λ_bypass, train RL lâu hơn |
| OOM với MC rollout | K quá lớn | Giảm K=8, gradient checkpointing |
| WAF Oracle quá chậm | Docker overhead | Batch payloads, parallel containers |

## NaN Debugging Checklist

1. Kiểm tra reward scale — nên nằm trong [-2, 2]
2. Grad norm log — nếu `‖∇G‖ > 10` → clip chưa hoạt động
3. WGAN-GP: Wasserstein distance phải dương và ổn định
4. Baseline output — kiểm tra không bị saturate về 0 hoặc constant
5. Log_prob: `log π(a|s)` không được là -inf (vocab coverage issue)

## Reward Hacking Patterns

### Length reward hacking
G học sinh chuỗi rất ngắn hoặc rất dài để minimize length penalty. Fix:
```python
length_penalty = 0.01 * max(0, len(seq) - max_len)
# Thêm minimum length penalty nếu cần:
length_penalty += 0.005 * max(0, min_len - len(seq))
```

### Lexical repetition hacking
G lặp 1 token nhiều lần. Fix: thêm repetition penalty vào reward:
```python
unique_ratio = len(set(token_ids)) / len(token_ids)
repetition_penalty = -0.1 * (1 - unique_ratio)
```

### Discriminator saturation
D quá mạnh → G không học được signal. Fix:
- Giảm num_filters D
- Tạm dùng D:G ratio = 2:1 trong 5k steps đầu
- Label smoothing: real label = 0.9 thay vì 1.0

## Sprint-Specific Issues

### Sprint 1 — Data Pipeline
- Vocab size > 200: kiểm tra lại de-lex rules, có thể thiếu pattern
- Split imbalance: kiểm tra `sqli_type` distribution sau split

### Sprint 3 — MLE
- Perplexity không giảm sau epoch 3: LR có thể quá cao, thử 5e-4
- Expert demo loss không giảm riêng: kiểm tra upweight logic

### Sprint 4 — Adversarial RL
- Reward log toàn 0: kiểm tra dev mode bypass_proxy hoạt động đúng
- D_loss âm liên tục: WGAN-GP bình thường — chỉ lo nếu không ổn định
