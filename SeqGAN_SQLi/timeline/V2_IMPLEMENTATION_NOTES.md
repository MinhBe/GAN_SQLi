# V2 Implementation Notes — Phát hiện & Fix khi triển khai Phase 1-3

> **Cập nhật**: 2026-05-12
> **Mục đích**: Ghi lại các vấn đề phát hiện khi đọc playbook vs. codebase thực tế, và cách fix.

---

## Vấn đề 1: `NUM_SQLI_TYPES` mismatch (utils.py vs data thực tế)

**Phát hiện:** `src/utils.py` định nghĩa `NUM_SQLI_TYPES = 18` (list 18 attack types), nhưng dataset V2 chỉ có 4 types: `error_based, boolean_blind, time_blind, union_based`.

**Mapping thực tế (từ `data/v2/type_mapping.json`):**
```json
{"error_based": 0, "boolean_blind": 1, "time_blind": 2, "union_based": 3}
```

**Mapping trong utils.py (sai):**
- benign=0, error_based=1, boolean_blind=2, time_blind=3, union_based=4, ...

**Fix:** Các script V2 (`pretrain_mle_v2.py`, `train_adversarial_v2.py`) đọc `type_id` **trực tiếp từ CSV** (cột `type_id` đã có sẵn, giá trị 0-3). Không dùng `utils.sqli_type_to_idx()`. Generator khởi tạo với `num_conditions=4`.

**Không sửa utils.py** vì V1 vẫn dùng.

---

## Vấn đề 2: Class name mismatch — `Generator` vs `GeneratorLSTM`

**Phát hiện:** Playbook STEP 3.1 và 3.2 import `from src.generator import Generator` nhưng `src/generator.py` chỉ có class `GeneratorLSTM`.

**Fix:** Tất cả V2 scripts dùng `from src.generator import GeneratorLSTM`.

---

## Vấn đề 3: Tokenizer API — `from_vocab()` vs `load()`

**Phát hiện:** Playbook dùng `SQLTokenizer.from_vocab(path)` nhưng `src/tokenizer.py` chỉ có classmethod `SQLTokenizer.load(path)`.

**Fix:** Dùng `SQLTokenizer.load(path)` trong tất cả V2 scripts.

---

## Vấn đề 4: Vocab size V2 ≠ V1

**Phát hiện:**
- V1 vocab (`data/tokenizer_vocab.json`): 134 tokens
- V2 vocab (`data/v2/tokenizer_vocab.json`): **89 tokens** (dataset mới nhỏ hơn, de-lex aggressive hơn)

**Fix:** `configs/seqgan_v2.yaml` set `vocab_size: 89`. V2 scripts load vocab từ `data/v2/tokenizer_vocab.json`.

---

## Vấn đề 5: `num_attack_types` trong config

**Phát hiện:** Playbook spec trong Guiding_V2.md dùng 8 attack types, nhưng dataset thực tế chỉ có 4.

**Fix:** `seqgan_v2.yaml` set `num_attack_types: 4`.

---

## Vấn đề 6: `pretrain_mle.py` không pass conditional embedding

**Phát hiện:** `pretrain_mle.py` (V1 updated) gọi `model(inp_ss)` không có `cond` argument — generator chạy không điều kiện.

**Fix:** Tạo mới `pretrain_mle_v2.py` load `type_id` từ CSV và pass `cond=type_ids` trong forward pass.

---

## Vấn đề 7: Columns trong V2 train.csv

**Thực tế:** `data/v2/train.csv` có columns: `id, payload_norm, payload_delex, sqli_type, db_engine, confidence, source, tier, type_id`

Quan trọng:
- `payload_delex`: token sequence đã de-lex (dùng cho training)
- `type_id`: integer 0-3 (dùng cho conditional embedding)
- `tier`: gold/silver/bronze (dùng cho WeightedRandomSampler)

---

---

## Vấn đề 8: Reward function nhận de-lexed strings, không phải actual SQL

**Phát hiện:** Generator được train trên de-lexed sequences (`payload_delex` column). Khi decode, output có dạng `__INT__ OR __INT__=__INT__--`. Nhưng `CompositeRewardV2` (custom_rules, db_sandbox, parser_gate) expect actual SQL strings như `1 OR 1=1--`.

**Hậu quả:**
- `DBSandbox.evaluate("__INT__ OR __INT__=__INT__")` → 0 (fail SQL syntax) → reward = -0.5 cho mọi payload
- `CustomRuleEngine.score("__INT__ OR __INT__=__INT__")` → thấp vì không nhận ra keywords
- Warmup phase bị disabled hoàn toàn: mọi reward = -0.5

**Fix:** Thêm quick re-lex step trong `train_adversarial_v2.py` trước khi gọi `reward_fn`. Mỗi placeholder được thay bằng 1 random value từ `relex_dictionary.json`.

```python
# Trước khi gọi reward:
payloads = [relex(p, relex_dict) for p in decode_batch(fake_seqs, tok)]
```

**Đã fix trong:** `train_adversarial_v2.py` (re-lex step added).

---

## Vấn đề 9: UnicodeEncodeError khi phase transition (Windows)

**Phát hiện:** `train_adversarial_v2.py` có print statement:
```python
print(f"\n[Step {step}] Phase → {current_phase} | lr_g={new_lr}")
```
Ký tự `→` (U+2192) gây crash `UnicodeEncodeError: 'charmap' codec can't encode character '→'` trên Windows console (mặc định dùng cp1252).

**Hậu quả:** Training crash ở step 2000 (phase warmup → adversarial transition). Không có checkpoint nào sau step 1000.

**Fix:** Thay `→` bằng `->` trong print statement.

**Cũng fix trong:** `generate_v2.py` có cùng vấn đề trong output message.

---

## Summary của fixes áp dụng

| File | Fix |
|---|---|
| `configs/seqgan_v2.yaml` | `vocab_size: 89`, `num_attack_types: 4` |
| `pretrain_mle_v2.py` | `GeneratorLSTM`, `SQLTokenizer.load()`, load `type_id`, pass `cond` |
| `train_adversarial_v2.py` | `GeneratorLSTM`, `SQLTokenizer.load()`, load `type_id`, `→` → `->` |
| `generate_v2.py` | `→` → `->` in output message |
| `src/reward_v2.py` | Giữ nguyên playbook (không có V2-specific issue) |
