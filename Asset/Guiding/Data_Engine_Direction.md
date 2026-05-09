# Định hướng Data Engineering Thực chiến cho SQLi-GAN (Final Blueprint)

Tài liệu này là bản thiết kế kiến trúc cuối cùng (v3) để xây dựng Data Engine, giải quyết triệt để các mâu thuẫn về Pipeline, Tokenization, chiến lược thu thập Benign SQL và đính chính các khái niệm GAN.

---

## 1. CHIẾN LƯỢC BÙ ĐẮP DỮ LIỆU & BÓC TÁCH (DATA INGESTION)

| Nguồn dữ liệu | Vấn đề / Khuyết điểm | Quyết định Kỹ thuật (Technical Decision) |
| :--- | :--- | :--- |
| **sqliv5** | Sạch, có nhãn 0/1 | Giữ nguyên làm Base Dataset. |
| **BCCC-SFU** | Nhãn cột 1 toàn `0` bất thường | **Drop cột nhãn hiện tại**. Dùng heuristic scan lại: nếu chứa SQL keywords + syntax break $\rightarrow$ gán nhãn `1` (SQLi). |
| **exploitdb** | Payload kẹt trong 8k file code (.py, .txt, .pl) | **Chọn Option B (Parse theo định dạng):** <br>- **Với .txt:** Quét từng dòng tìm URL parameters/SQL keywords (Coverage ~40-60%).<br>- **Với .py/.pl:** Dùng AST parser / String Scan để trích xuất biến chuỗi (string variable/f-string) chứa câu lệnh SQL. Ưu tiên độ chính xác tuyệt đối (Coverage target: 70-80%). |
| **Benign SQL** | **ĐANG THIẾU** <br>*(Faker sinh SQL sai ngữ pháp)* | **Chiến lược Thu thập (Theo mức độ ưu tiên):**<br>1. Download **Spider/WikiSQL benchmark (Yale NLP)**, lọc ra các câu SELECT/INSERT/UPDATE thật.<br>2. Export query logs từ **Chinook/Northwind sample DB**.<br>3. Dùng Template-based generation với ngữ pháp SQL chuẩn, **Faker CHỈ được dùng để điền giá trị (fill values)**, tuyệt đối không dùng để sinh cấu trúc câu. |

---

## 2. QUY TRÌNH XỬ LÝ 4 LỚP TÁCH BIỆT (PIPELINE)

Schema bắt buộc của `master_sqli.csv` để tránh ghi đè dữ liệu sai mục đích:
`payload_raw` | `payload_norm` | `payload_delex` | `label` | `sqli_type` | `is_obfuscated`

### Lớp 1: Chuẩn hóa & Giải mã (Normalization)
*   **Input:** `payload_raw`
*   **Output:** `payload_norm` (**Dùng làm target để train Generator**).
*   **Action:** Decode URL (`%27` $\rightarrow$ `'`), HTML decode, collapse comment (`/**/` $\rightarrow$ ` `), normalize case (`SeLeCt` $\rightarrow$ `SELECT`). KHÔNG đụng đến tên bảng/cột/giá trị.

### Lớp 2: Đánh dấu kỹ thuật lẩn tránh (Evasion Flagging)
*   **Input:** `payload_raw` (Phải kiểm tra TRƯỚC KHI decode để không mất dấu vết).
*   **Output:** Cột `is_obfuscated` (Boolean)
*   **Action:** Gán `True` nếu match **BẤT KỲ** pattern nào sau đây:
    *   `url_encoding`: `r"%[0-9a-fA-F]{2}"`
    *   `whitespace_subst`: `r"%09|%0a|%0d|\+"`
    *   `mysql_versioned`: `r"/\*![0-9]{5}"`
    *   `comment_obfuscation`: `r"/\*.*?\*/"`
    *   `case_mixing`: `r"(?i)(Se|sE|SE)(Le|lE|LE)"`
    *   `hex_encoding`: `r"0x[0-9a-fA-F]+"`

### Lớp 3: Ẩn danh hóa Cấu trúc (De-lexicalization)
*   **Input:** `payload_norm`
*   **Output:** `payload_delex` (**CHỈ DÙNG CHO EDA**, phân tích Vocabulary và đo Constraint Density. **TUYỆT ĐỐI KHÔNG** dùng làm target để train Generator).
*   **Action:** Đổi chuỗi thành `<STR>`, số thành `<NUM>`, tên bảng thành `<TABLE>`.

### Lớp 4: Phân loại đa tầng (Categorization)
*   **Input:** `payload_norm` (Regex chạy trên chuỗi đã giải mã/chuẩn hóa để match chính xác các keyword/pattern tấn công).
*   **Output:** Cột `sqli_type`
*   **Action:** Gán nhãn theo Regex ưu tiên (Time-based $\rightarrow$ Error-based $\rightarrow$ Union $\rightarrow$ Boolean).

---

## 3. QUYẾT ĐỊNH KỸ THUẬT: TOKENIZATION

Việc cắt từ (Tokenization) là quyết định sống còn. Dùng `sqlparse` hay Regex Tokenizer sẽ thất bại hoàn toàn với Evasion payload.

*   **Quyết định:** Sử dụng **BPE (Byte-Pair Encoding) / Subword Tokenization** được train *from scratch* trên chính tập `payload_norm`.
*   **Lý do:** BPE tự động giữ nguyên các keyword phổ biến (như `SELECT`) nhưng sẽ tách thành Character-level đối với các evasion payload (`S`, `e`, `L`, `e`, `C`, `t`).
*   **Vocabulary Size Target:** **$200 - 500$ tokens**. 
    *   *Justification (Biện luận):*
        *   **Quá nhỏ (< 100):** Buộc model phải sinh từng ký tự (char-level) ngay cả với các keyword phổ biến, làm sequence quá dài và khó hội tụ.
        *   **200-500:** Điểm cân bằng lý tưởng — chứa ~100 SQL keywords cơ bản + các subword units để lắp ghép evasion patterns + special tokens.
        *   **Quá lớn (> 1000):** Model dễ bị overfit (học vẹt) vào các tên bảng, tên cột, hoặc giá trị cụ thể trong tập training, làm mất tính tổng quát hóa.

---

## 4. ĐÍNH CHÍNH KHÁI NIỆM CHO 3 MÔ HÌNH GAN

*   **SeqGAN:** Dùng `payload_norm` để thực hiện **Maximum Likelihood Estimation (MLE) Pre-training** (học thuộc phân phối cơ bản của toàn bộ corpus). *Tuyệt đối không gọi đây là Expert Demonstrations / Imitation Learning* vì toàn bộ tập dữ liệu không phải là trajectory tối ưu đã bypass WAF thành công.
*   **Gumbel-Softmax:** Sử dụng `payload_delex` để đo lường Reference Entropy ban đầu. Generator huấn luyện trên `payload_norm` bằng phân phối soft-continuous để truyền gradient mượt mà.
*   **VAE-GAN:** Tận dụng triệt để cột `is_obfuscated` và `sqli_type` làm thông tin điều kiện (Condition) để ép không gian ẩn (Latent Space) phân tách ranh giới rõ ràng giữa cấu trúc SQL thuần túy và cấu trúc bị ngụy trang.
