# RECOVERY 2 — QUY TRÌNH TÁI THỰC THI TOÀN BỘ PIPELINE DATA V3 & V4

> **Ngày cập nhật**: 2026-05-16
> **Mục tiêu**: Hướng dẫn chi tiết cách chạy lại toàn bộ quy trình từ đánh nhãn dataset (40,860 rows) đến huấn luyện model V4 sau khi bị ngắt quãng (do rate limit hoặc chuyển môi trường).

---

## 1. TRẠNG THÁI HIỆN TẠI (Trước khi reset)
- **Root Cause**: Mode collapse ở V3 do data bị delex quá đà (collision 71.89%, mất function name).
- **Giải pháp**: Skill `sqli-data-curator` đã build xong và smoke test thành công 1000 rows.
- **Tiến độ full pipeline**: Đã chạy Stage 1, 2 và đang ở Stage 3 (B4 - Labeling chunks). Mới hoàn thành 10/113 chunks (2,000/22,401 rows cần relabel).
- **Mã nguồn**: Các script Phase 1-4 đã được viết đầy đủ trong `Skill/sqli-data-curator/scripts/`.

---

## 2. QUY TRÌNH THỰC HIỆN CHI TIẾT (8 BƯỚC)

### BƯỚC 1: TRIAGE — Phân loại ban đầu
Dùng script `critique_labels.py` để lọc ra những row nào cần giữ, row nào cần đánh nhãn lại, row nào bỏ.
```bash
python Skill/sqli-data-curator/scripts/critique_labels.py \
    --input Asset/LabelData/combined_labeled_data.csv \
    --output Asset/LabelData/triaged.csv
```
Sau đó chia file:
```python
import pandas as pd
df = pd.read_csv('Asset/LabelData/triaged.csv')
df[df['verdict']=='KEEP'].to_csv('Asset/LabelData/keep.csv', index=False)
df[df['verdict']=='RELABEL'].to_csv('Asset/LabelData/to_relabel.csv', index=False)
```

### BƯỚC 2: PRE-LABEL & STRIP — Chuẩn bị cho RELABEL
Bóc tách wrapper (chống bias) và chạy rule-based + heuristic làm hint cho subagent.
```bash
# 1. Strip wrapper
python Skill/sqli-data-curator/scripts/strip_wrapper.py \
    --input Asset/LabelData/to_relabel.csv \
    --output Asset/LabelData/to_relabel_stripped.csv \
    --col_in payload_norm --col_out payload_inner

# 2. Sinh hint A+C
python Skill/sqli-data-curator/scripts/label_payload.py \
    --mode chat_queue \
    --input Asset/LabelData/to_relabel_stripped.csv \
    --output Asset/LabelData/chat_queue.csv
```

### BƯỚC 3: CHUNKING — Chia nhỏ công việc
Chia 22,401 rows thành các chunk 200 rows để subagent xử lý song song.
```bash
python Skill/sqli-data-curator/scripts/chat_label_coordinator.py \
    --input Asset/LabelData/chat_queue.csv \
    --chunk_size 200 \
    --temp_dir Asset/LabelData/_chunks/
```
*Lưu ý: Lệnh này sẽ sinh ra `_chunks/prompts.json` chứa các prompt cho subagent.*

### BƯỚC 4: SUBAGENT EXECUTION (Phần nặng nhất)
Yêu cầu Gemini CLI đọc `Asset/LabelData/_chunks/prompts.json` và spawn subagents.
- **Cách thực hiện**: "Hãy đọc prompts.json và dùng tool Agent (general-purpose) chạy song song ~10 subagents mỗi đợt."
- **Nhiệm vụ subagent**: Đọc `SKILL.md` của curator, đọc chunk CSV, đánh nhãn từng dòng (có reasoning > 50 chars), ghi file `chunk_NNN_labeled.csv`.

### BƯỚC 5: MERGE & CONCAT — Hợp nhất dữ liệu
Sau khi 113 chunks hoàn thành:
```bash
# 1. Merge các chunks đã relabel
python Skill/sqli-data-curator/scripts/merge_chunks.py \
    --temp_dir Asset/LabelData/_chunks/ \
    --output Asset/LabelData/relabeled_chat.csv

# 2. Hợp nhất với phần KEEP ban đầu
python -c "
import pandas as pd
keep = pd.read_csv('Asset/LabelData/keep.csv')
relab = pd.read_csv('Asset/LabelData/relabeled_chat.csv')
merged = pd.concat([keep, relab], ignore_index=True).drop_duplicates(subset='id')
merged.to_csv('Asset/LabelData/merged_final.csv', index=False)
"
```

### BƯỚC 6: TRANSFORM (DELEX V2) — Tăng cường tín hiệu
Áp dụng delex_v2 với whitelist để giữ lại các function SQLi quan trọng.
```bash
python Skill/sqli-data-curator/scripts/delex_v2.py \
    --input Asset/LabelData/merged_final.csv \
    --output Asset/LabelData/dataset_v3.csv \
    --col_in payload_inner --col_out payload_delex_v2 --stats
```

### BƯỚC 7: RESAMPLE & TIER SPLIT — Cân bằng dữ liệu
```bash
# 1. Chống bias signature và type
python Skill/sqli-data-curator/scripts/resample_balanced.py \
    --input Asset/LabelData/dataset_v3.csv \
    --output Asset/LabelData/dataset_v3_balanced.csv \
    --cap_signature 30 --cap_type_db 300

# 2. Chia Gold/Silver/Bronze
python Skill/sqli-data-curator/scripts/tier_split.py \
    --input Asset/LabelData/dataset_v3_balanced.csv \
    --output_dir SeqGAN_SQLi/data/v3/
```

### BƯỚC 8: TRAINING V4 (Định hướng mới)
1. **Pre-train MLE**: Huấn luyện Generator trên `gold.csv`.
2. **Adversarial Training**: Chạy `train_adversarial_v4.py` với các fixes (entropy, temperature, BiLSTM, benign data).

---

## 3. CHECKLIST KIỂM TRA CHẤT LƯỢNG (Acceptance Criteria)
- [ ] **Collision Rate (Gold)**: < 15% (V3 cũ là 71%).
- [ ] **Vocab Size**: 120-180 tokens (V3 cũ là 89).
- [ ] **Reasoning**: > 50 chars cho mỗi dòng relabel, không trùng lặp.
- [ ] **Structure**: Payload không còn bị wrapper `select * from...` bọc ngoài quá nhiều.
- [ ] **Function Whitelist**: Kiểm tra `xmltype`, `pg_sleep`, `extractvalue` còn tồn tại trong `payload_delex_v2`.

---

## 4. LƯU Ý KHI CHẠY TRÊN WINDOWS
- Luôn sử dụng `encoding='utf-8'` khi đọc/ghi file CSV.
- Nếu gặp lỗi hiển thị terminal, dùng `PYTHONIOENCODING=utf-8`.
- Cẩn thận với đường dẫn file (dùng `/` hoặc `\\`).

---
*File này được tạo để đảm bảo quy trình không bị thất lạc khi chuyển đổi session.*
