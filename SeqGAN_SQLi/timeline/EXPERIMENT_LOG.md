# Nhật Ký Thực Nghiệm — Per-Type Training & Entropy Regularization

> **Ngày**: 2026-05-10  
> **Tiếp nối từ**: `ANALYSIS_REPORT.md` (kết quả mixed model)  
> **Mục tiêu**: Kiểm tra 2 hướng giải quyết mode collapse — per-type training và entropy regularization

---

## Bối Cảnh

Sau khi mixed SeqGAN đạt Self-BLEU-3 = 0.9894 (FAIL, target < 0.60), hai câu hỏi được đặt ra:

1. **Per-type training** — train riêng từng loại tấn công có giảm mode collapse không?
2. **Entropy regularization** — thêm bonus entropy vào G loss có buộc model đa dạng hóa không?

---

## Thực Nghiệm 1: Phân Tích Dataset theo Loại Tấn Công

**Mục tiêu**: Kiểm tra tính khả thi của per-type training.

**Kết quả phân phối** (`combined_labeled_data.csv`, N=40,860):

| sqli_type | Số mẫu | Train (~70%) | Đánh giá |
|-----------|--------|-------------|---------|
| benign | 19,669 | - | Không dùng để generate |
| error_based | 8,663 | ~6,064 | ✅ OK |
| boolean_blind | 4,531 | ~3,171 | ✅ OK |
| time_blind | 2,391 | ~1,673 | ⚠ Marginal |
| union_based | 2,236 | ~1,565 | ⚠ Marginal |
| heavy_query | 1,296 | ~907 | ❌ Quá nhỏ |
| auth_bypass | 1,193 | ~835 | ❌ Quá nhỏ |
| out_of_band | 610 | ~427 | ❌ Quá nhỏ |
| (10 loại còn lại) | < 130 mỗi loại | — | ❌ Vô nghĩa |

**Phân tích error_based cụ thể**: 88.6% payload target `users`/`accounts` table, 60.6% dùng Oracle XMLTYPE. Đây là **data exfiltration trực tiếp qua error message** — không phải blind, không phải chỉ tiết lộ cấu trúc DB.

**Quyết định**: Bắt đầu với `error_based` (8,663 mẫu, đủ data, hoàn thành nhanh ~25 phút/run để iterate).

---

## Thực Nghiệm 2: Per-Type Training — error_based

### Thay đổi code

Thêm `--sqli_type` vào `data/prepare_seqgan_data.py` — filter dataset theo loại, lưu vào `data/{sqli_type}/` với tokenizer riêng.

Thêm `--data_dir` và `--ckpt_dir` vào `pretrain_mle.py`, `train_adversarial.py`, `generate.py` — cho phép chỉ định thư mục data và checkpoint độc lập.

### Kết quả Data Prep

```
Filter: sqli_type='error_based' → 8,663 rows
Split: Train=6,063 | Val=1,300 | Test=1,300
Vocab: 63 tokens  (vs 134 của mixed model — giảm 53%)
Expert demos: 3,020 mẫu (confidence >= 0.95)
```

### Kết quả MLE Pretrain

| Epoch | val_ppl |
|-------|---------|
| 1 | 3.04 |
| 5 | 1.31 |
| 10 | **1.24** ← best |

**So sánh**: Mixed model best val_ppl = **1.70** (early stop epoch 5). Per-type model học tốt hơn rõ rệt — vocab nhỏ hơn, data thuần nhất hơn.

### Kết quả Adversarial Training

- **Thời gian**: 5,000 steps / **25 phút** (so với 4h 56m của mixed model — nhanh hơn ~12×)
- Step 5000: reward=0.51, syntax=100%

### Kết quả Evaluate (1,000 samples)

| Model | ASR | Syntax | Self-BLEU-3 | Avg Length |
|-------|-----|--------|-------------|------------|
| EB SeqGAN (adv) | 100.0% | 100% | **0.9922** | 79.9 ±0.3 |
| EB MLE | 98.9% | 100% | **0.9929** | 61.5 ±18.5 |

**Nhận xét**: Self-BLEU-3 = 0.9922 — **tệ hơn** mixed model (0.9894). Avg length 79.9 ±0.3 nghĩa là gần như toàn bộ 1,000 payload đều dài tối đa 80 token, độ lệch chuẩn chỉ 0.3 — **mode collapse hoàn toàn về một pattern duy nhất**.

**Kết luận Thực Nghiệm 2**: Per-type training không cải thiện Self-BLEU-3. Thậm chí tệ hơn một chút.

---

## Thực Nghiệm 3: Entropy Regularization (entropy_coef=0.05)

### Lý thuyết

Thêm bonus entropy vào G loss:
```
g_loss = -(log_probs * advantages).mean()   [REINFORCE]
       - 0.05 * H(π)                        [Entropy bonus]
```

Trong đó H(π) = -Σ p(a|s) × log p(a|s) tính trên toàn bộ vocab tại mỗi token position. Entropy cao → distribution đều hơn → model không bị kẹt ở một pattern duy nhất.

### Thay đổi code

- `configs/seqgan_fast.yaml`: thêm `entropy_coef: 0.05`
- `train_adversarial.py`: thêm forward pass lấy logits → tính H(π) → cộng vào g_loss
- Import `torch.nn.functional as F`
- Log `entropy` ở mỗi bước

### Diễn Biến Entropy trong Training

| Step | Entropy | Nhận xét |
|------|---------|---------|
| 50 | 0.419 | Model rất peaked (concentrated) |
| 150 | 2.340 | Tăng nhanh |
| 500 | 3.426 | Tiếp tục tăng |
| 1000 | 3.890 | Gần plateau |
| 2000 | 4.136 | Plateau |
| 5000 | **4.142** | ≈ log(63) = **4.143** = MAX ENTROPY |

Entropy đạt gần tối đa lý thuyết cho vocab=63 tokens. Model đang output gần như **uniform distribution** trên tất cả 63 token ở mỗi vị trí.

### Kết quả Evaluate

| Model | ASR | Syntax | Self-BLEU-3 | Avg Length |
|-------|-----|--------|-------------|------------|
| EB SeqGAN (entropy=0.05) | 100.0% | 100% | **0.9939** | 79.8 ±0.5 |

**Nhận xét**: Self-BLEU-3 = 0.9939 — **tệ nhất trong tất cả experiments**. Entropy bonus không giúp gì, thậm chí làm worse.

---

## Bảng Tổng Hợp Tất Cả Experiments

| Model | Self-BLEU-3 | Avg Length | ASR | Train time |
|-------|------------|-----------|-----|-----------|
| Mixed SeqGAN (adv) | 0.9894 | 68.1 ±20.6 | 100% | 4h 56m |
| Mixed MLE | 0.9833 | 55.1 ±13.5 | 69.7% | — |
| Mixed Template | 0.6836 | 4.0 ±1.2 | 67.9% | — |
| EB SeqGAN (no entropy) | 0.9922 | 79.9 ±0.3 | 100% | 25 min |
| EB MLE | 0.9929 | 61.5 ±18.5 | 98.9% | — |
| **EB SeqGAN (entropy=0.05)** | **0.9939** | 79.8 ±0.5 | 100% | 28 min |

---

## Phát Hiện Quan Trọng

### 1. Entropy token-level ≠ Diversity sequence-level

Dù model có entropy token gần maximum (4.142 ≈ log(63)), Self-BLEU-3 vẫn 0.9939. Lý do:

SQL structure constraints ép các vị trí nhất định phải có cùng token bất kể distribution. Trong không gian de-lex, error_based payload gần như luôn có dạng:

```
select * from __IDENT__ where __IDENT__ = ... (XMLTYPE / ctxsys.drithsx ...) ...
```

Dù sample uniform trên 63 token, các token "filler" thay đổi không làm cấu trúc câu khác đi.

### 2. Self-BLEU-3 là metric sai cho bài toán này

5 experiments liên tiếp đều cho Self-BLEU-3 ≥ 0.98. Không có intervention nào cải thiện được. Đây không phải do model tệ — mà do **de-lexicalization đã collapse diversity trong token space**:

- `' OR 1=1--` và `' OR 'x'='x` → cùng token sequence sau de-lex
- `SLEEP(5)` và `SLEEP(10)` → `SLEEP ( __INT__ )` → giống nhau
- 1,000 payload khác nhau về giá trị cụ thể → na ná nhau về cấu trúc token

### 3. Hướng đúng: Re-lexicalization

Self-BLEU-3 phải được tính **sau khi fill placeholder** với giá trị thực. Hai payload có cùng de-lex structure nhưng khác `__INT__` = 1 vs 999, `__STR__` = `'admin'` vs `'test'` là **hai payload khác nhau có ý nghĩa**.

---

## Thay Đổi File Trong Session Này

| File | Thay đổi |
|------|---------|
| `data/prepare_seqgan_data.py` | Thêm `--sqli_type` filter, output per-type dir |
| `pretrain_mle.py` | Thêm `--data_dir`, `--ckpt_dir` |
| `train_adversarial.py` | Thêm `--data_dir`, `--ckpt_dir`, entropy regularization |
| `generate.py` | Thêm `--data_dir` |
| `configs/seqgan_fast.yaml` | Thêm `entropy_coef: 0.05` |
| `data/error_based/` | New: train/val/test/expert/vocab cho error_based |
| `checkpoints/error_based/` | New: mle_best.pt, adv_final.pt, adv_step*.pt |
| `checkpoints/error_based_entropy/` | New: adv_final.pt với entropy bonus |
| `eval_eb_seqgan.csv`, `eval_eb_mle.csv`, `eval_eb_entropy.csv` | New: generated samples |
| `eval_eb_*_metrics.json` | New: evaluation results |

---

## Khuyến Nghị Tiếp Theo

**Implement Re-lexicalization** — đây là bước có chi phí thấp nhất (~1-2h code, không cần retrain) và sẽ trả lời câu hỏi: diversity thực sự sau khi fill giá trị là bao nhiêu?

Nếu Self-BLEU-3 sau re-lex giảm xuống < 0.60 → mọi experiment đều pass, bài toán đã được giải quyết về mặt measurement.

Nếu vẫn cao → mode collapse là thực sự ở structural level, cần Hướng 2 (Bounded D score) hoặc Hướng 4 (MMD penalty).

---

*Tạo: 2026-05-10 | Dựa trên kết quả từ `eval_report.json`, `eval_eb_*_metrics.json`*
