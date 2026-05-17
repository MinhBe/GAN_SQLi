# RECOVERY PLAN — KỊCH BẢN KHÔI PHỤC KHI CÓ SỰ CỐ

Tài liệu này dành cho việc tái triển khai quy trình đánh nhãn dữ liệu SQLi trong trường hợp mất điện, mất kết nối hoặc lỗi hệ thống giữa chừng.

---

## 1. CÁCH KIỂM TRA ĐIỂM DỪNG (CHECKPOINT)

Hãy kiểm tra thư mục `Asset/LabelData/Gemini/` để biết mình đang ở bước nào:
1. Nếu thấy `chat_queue.csv`: Bạn đã xong Giai đoạn 1 & 2.
2. Nếu thấy các file `_chunks/chunk_NNN.csv`: Bạn đã xong bước chia nhỏ dữ liệu.
3. Nếu thấy `chunk_NNN_labeled.csv`: Bạn đã bắt đầu giai đoạn đánh nhãn LLM.
4. Nếu thấy `relabeled_chat.csv`: Bạn đã xong giai đoạn đánh nhãn LLM.

---

## 2. KỊCH BẢN KHÔI PHỤC CHI TIẾT

### Trường hợp A: Mất điện khi đang chạy Subagent (BƯỚC 4)
Đây là trường hợp dễ xảy ra nhất. Không cần chạy lại từ đầu.
1. **Kiểm tra**: Xem trong thư mục `_chunks/`, file `chunk_NNN_labeled.csv` cuối cùng là số bao nhiêu.
2. **Hành động**: Chỉ spawn subagent cho các chunk còn thiếu. 
   - Ví dụ: Nếu đã có đến `chunk_050_labeled.csv`, hãy yêu cầu: *"Hãy tiếp tục chạy subagent cho các chunk từ 051 đến hết dựa trên prompts.json"*.

### Trường hợp B: Lỗi khi Merge hoặc Transform (BƯỚC 5-7)
1. **Hành động**: Chỉ cần chạy lại các script đơn lẻ vì dữ liệu đầu vào (`_chunks/` và `keep.csv`) vẫn còn đó.
2. **Lệnh Merge**:
   ```bash
   python Skill/sqli-data-curator/scripts/merge_chunks.py --temp_dir Asset/LabelData/Gemini/_chunks/ --output Asset/LabelData/Gemini/relabeled_chat.csv
   ```
3. **Lệnh Transform (Delex V2)**:
   ```bash
   python Skill/sqli-data-curator/scripts/delex_v2.py --input Asset/LabelData/Gemini/merged_final.csv --output Asset/LabelData/Gemini/dataset_v3.csv --col_in payload_inner --col_out payload_delex_v2
   ```

### Trường hợp C: Mất toàn bộ file tạm (Tmp files)
Nếu thư mục `Gemini` bị xóa, hãy chạy lại theo đúng thứ tự trong `METHODOLOGY.md` hoặc `RECOVERY2.md` tại `SeqGAN_SQLi/timeline/`.

---

## 3. CÁC FILE QUAN TRỌNG CẦN LƯU TRỮ
- **`keep.csv`**: Chứa ~18k dòng dữ liệu tốt đã có.
- **`chat_queue.csv`**: Đầu vào cho toàn bộ quá trình đánh nhãn LLM.
- **`prompts.json`**: "Bản đồ" để subagent biết phải làm gì.

---
**Ghi chú**: Luôn sử dụng Gemini CLI để quản lý các subagent song song nhằm tối ưu hóa thời gian và tránh lỗi thủ công.
