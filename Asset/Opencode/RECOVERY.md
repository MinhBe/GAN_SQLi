# RECOVERY PROMPT - SQLi CLASSIFY

## HIỆN TRẠNG HIỆN TẠI (Cập nhật khi bị mất điện)

### Progress File
- File: `C:\Users\Admin\Documents\GAN\Asset\Opencode\progress.json`
- Đọc trước để biết tiến trình đang dừng ở đâu

### Thông số cần kiểm tra
- `last_completed`: Batch cuối cùng đã hoàn thành
- `completed_batches`: Mảng danh sách các batch đã xong
- `rows_completed`: Tổng số rows đã classify
- `status`: "in_progress" hoặc "completed"

---

## NHIỆM VỤ: TIẾP TỤC SQLi CLASSIFY

### Bước 1: Xác định tiến trình
```bash
Đọc file progress.json để lấy last_completed
```
- Batch tiếp theo = last_completed + 1

### Bước 2: Đọc 10 batch files
Thư mục: `C:\Users\Admin\Documents\GAN\Asset\Data\batches\`
- batch_XXXX.csv (XXXX = batch number, pad 4 digits)
- Mỗi batch = 30 rows
- Columns: row_index,payload_norm,label,sqli_type_hint

### Bước 3: Classify 300 rows
Input: 10 batch × 30 rows = 300 payloads

Yêu cầu classify mỗi payload:
1. **sqli_type**: union_based | error_based | boolean_blind | time_blind | heavy_query | stacked_queries | out_of_band | auth_bypass | second_order | rce | polyglot | lateral | benign | unknown

2. **db_engine**: mysql | mssql | oracle | postgresql | sqlite | firebird | db2 | generic | unknown

3. **confidence**: 1.0=certain, 0.7=likely, 0.5=unsure, 0.3=guessing

4. **reasoning**: 1-2 words về key indicator

Classification rules:
- `label=1` → sqli_type KHÔNG phải "benign"
- `label=0` → sqli_type = "benign"
- Plain English text với no SQL structure = "benign"
- Focus on TECHNIQUE, không chỉ keywords

### Bước 4: Xuất kết quả JSON
Format output (300 objects):
```json
[
  {"row_index": 3300, "sqli_type": "...", "db_engine": "...", "confidence": 0.xx, "reasoning": "..."},
  {"row_index": 3301, "sqli_type": "...", "db_engine": "...", "confidence": 0.xx, "reasoning": "..."},
  ... (300 total)
]
```

### Bước 5: Split và lưu 10 file riêng
Thư mục: `C:\Users\Admin\Documents\GAN\Asset\Data\results\`
- result_batch_XXXX.csv (mỗi file 30 rows)
- Header: row_index,sqli_type,db_engine,confidence,reasoning

### Bước 6: Cập nhật progress.json
```json
{
  "last_completed": <batch_number>,
  "completed_batches": [<danh sách>]",
  "rows_completed": <tổng rows>,
  "status": "in_progress"
}
```

### Bước 7: Lặp lại
Tiếp tục với 10 batch tiếp theo cho đến batch 1382

---

## VÍ DỤ RECOVERY

### Khi bị mất điện ở batch 0110:
1. Đọc progress.json → `last_completed: 110`
2. Tiếp tục từ batch 0111
3. Đọc batch_0111.csv → batch_0120.csv (10 files)
4. Classify 300 rows
5. Xuất JSON kết quả
6. Split thành 10 file:
   - result_batch_0111.csv
   - result_batch_0112.csv
   - ...
   - result_batch_0120.csv
7. Cập nhật progress.json: `last_completed: 120`
8. Lặp lại

---

## CẤU TRÚC THƯ MỤC

```
C:\Users\Admin\Documents\GAN\Asset\
├── Data\
│   ├── batches\
│   │   ├── batch_0001.csv   (Input)
│   │   ├── batch_0002.csv
│   │   └── ...batch_1382.csv
│   └── results\
│       ├── result_batch_0001.csv  (Output)
│       └── ...result_batch_1382.csv
└── Opencode\
    └── progress.json   (Tracking)
```

---

## CHẠY RECOVERY

### Lệnh bắt đầu:
```
Tiếp tục SQLi classify từ batch [last_completed + 1].
Đọc progress.json trước.
Chạy 10 batch mỗi lần.
Auto-continue cho đến batch 1382.
Cập nhật progress.json sau mỗi 10 batch.
```

### Rules tái lập:
- 10 batch/lần = 300 rows
- Auto-continue (không cần xác nhận từng lần)
- Cập nhật progress sau mỗi batch

---

## CHECKLIST KHI RECOVERY

- [ ] Đọc progress.json → lấy last_completed
- [ ] Xác định batch bắt đầu = last_completed + 1
- [ ] Đọc 10 batch files
- [ ] Classify 300 rows
- [ ] Xuất JSON kết quả
- [ ] Split thành 10 file result
- [ ] Cập nhật progress.json
- [ ] Lặp lại hoặc dừng nếu hoàn thành batch 1382