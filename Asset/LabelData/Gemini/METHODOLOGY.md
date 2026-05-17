# PHƯƠNG PHÁP CẢI THIỆN DATASET SQL INJECTION (V3)

Tài liệu này chi tiết hóa kiến trúc, quy tắc và quy trình đánh nhãn dữ liệu để khắc phục tình trạng Mode Collapse trong dự án SeqGAN-SQLi.

---

## 1. TỔNG QUAN KIẾN TRÚC (4-PHASE WORKFLOW)

Quy trình được thiết kế theo mô hình **Curator-Critic**, tập trung vào việc bảo tồn tín hiệu đặc trưng (features) của SQL Injection.

### Phase 1: TRIAGE (Sàng lọc)
- **Mục tiêu**: Loại bỏ dữ liệu rác và xác định các row cần đánh nhãn lại.
- **Dựa vào đâu**: Script `critique_labels.py` kiểm tra:
    - Độ dài reasoning (phải > 20 chars).
    - Sự thống nhất giữa label cũ và Rule-based engine.
    - Confidence score hiện tại.
- **Kết quả**: Chia dataset thành `KEEP` (giữ), `RELABEL` (đánh lại), và `DROP` (bỏ).

### Phase 2: PREPARATION & RELABEL (Chuẩn bị & Đánh nhãn)
- **Strip Wrapper**: Bóc tách các thành phần SQL bao quanh (ví dụ: `SELECT * FROM users WHERE id='...'`) để chỉ giữ lại phần payload lõi.
- **Multi-Source Labeling**: Sử dụng 3 nguồn để xác thực chéo:
    - **Source A (Rule-based)**: Dùng Regex và từ khóa để nhận diện chính xác các hàm SQL.
    - **Source B (LLM - Claude)**: Phân tích ngữ cảnh, logic tấn công và cung cấp reasoning.
    - **Source C (Heuristic)**: Dùng các dấu hiệu bề mặt (surface signals) và fingerprinting.

### Phase 3: TRANSFORMATION (Chuyển đổi)
- **Delexicalization V2**: Thay vì xóa sạch (Delex V1), V2 sử dụng một **Whitelist** để giữ lại ~30 hàm quan trọng (ví dụ: `xmltype`, `pg_sleep`, `extractvalue`).
- **Mục tiêu**: Giảm collision rate từ 71% xuống < 15% trong khi vẫn giữ được sự đa dạng của các loại tấn công.

### Phase 4: TIERING & BALANCING (Phân tầng & Cân bằng)
- **Tier Splitting**: Chia dữ liệu thành 3 tầng dựa trên độ tin cậy:
    - **Gold**: Confidence ≥ 0.90 & 3 nguồn thống nhất (Dùng để pre-train MLE).
    - **Silver**: Confidence ≥ 0.70 & 2 nguồn thống nhất (Dùng để RL).
    - **Bronze**: Còn lại (Dùng làm negative samples cho Discriminator).
- **Resampling**: Giới hạn số lượng dòng cho mỗi "Signature" (mã hash của delex payload) để tránh model bị thiên kiến (bias) vào một vài pattern quá phổ biến.

---

## 2. QUY TẮC ĐÁNH NHÃN (LABELING RULES)

### Taxonomy (Phân loại)
Chúng ta tập trung vào 10 loại SQLi chính (dựa trên OWASP và thực tế WAF):
1. `error_based`: Khai thác thông báo lỗi (Oracle, MySQL, v.v.)
2. `boolean_blind`: Tấn công đúng/sai.
3. `time_blind`: Tấn công dựa trên thời gian phản hồi (sleep, benchmark).
4. `union_based`: Dùng từ khóa UNION để lấy dữ liệu.
5. `auth_bypass`: Vượt qua đăng nhập.
6. `heavy_query`: Gây tải nặng cho DB.
7. `stacked_queries`: Chạy nhiều lệnh SQL cùng lúc.
8. `out_of_band`: Đẩy dữ liệu ra ngoài qua DNS/HTTP.
9. `polyglot`: Payload chạy được trên nhiều ngữ cảnh.
10. `benign`: Dữ liệu sạch (để dạy model phân biệt).

### Priority Rules (Thứ tự ưu tiên)
Nếu một payload có nhiều dấu hiệu, ưu tiên theo thứ tự:
`stacked_queries` > `union_based` > `error_based` > `time_blind` > `boolean_blind`.

---

## 3. CÁCH THỨC HOẠT ĐỘNG CỦA SUBAGENT
Khi đánh nhãn, subagent phải tuân thủ:
1. **Trích xuất Token**: Reasoning phải chỉ ra được token cụ thể (ví dụ: "Sử dụng `pg_sleep(5)` nên là Time-based").
2. **Xác định DB**: Phải chỉ ra được loại cơ sở dữ liệu (MySQL, Oracle, PostgreSQL, v.v.).
3. **Độ tự tin**: Gán `confidence` từ 0.5 đến 1.0.

---

## 4. TIẾN TRÌNH THỰC HIỆN (TIMELINE)
1. **Giai đoạn 1**: Triage 40k rows (Đã xong).
2. **Giai đoạn 2**: Tạo queue gợi ý A+C (Đã xong).
3. **Giai đoạn 3**: Chia chunk và gọi Subagents (Tiếp theo).
4. **Giai đoạn 4**: Hợp nhất, Transform và Tiering (Cuối cùng).
