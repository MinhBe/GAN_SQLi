# Phân Tích Bài Báo Khoa Học: SQLova (Hwang et al., 2019)

---

## Core Question
**Làm thế nào để chuyển đổi ngôn ngữ tự nhiên thành câu lệnh SQL (Text-to-SQL) một cách chính xác trên tập dữ liệu WikiSQL bằng cách tận dụng sức mạnh của các mô hình ngôn ngữ tiền huấn luyện (như BERT) kết hợp với cơ chế nắm bắt ngữ cảnh của bảng (table-aware context)?**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | A Comprehensive Exploration on WikiSQL with Table-Aware Word Contextualization |
| **Tác giả** | Wonseok Hwang, Jinyeung Bin, Yangsuk Yang, Jiyuo Oh |
| **Năm** | 2019 |
| **Conference / Journal** | arXiv (Clova AI, NAVER Corp) |
| **Link** | https://arxiv.org/abs/1902.01069 |

### A1. Phân Loại Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **Task Type** | Text-to-SQL (Semantic Parsing) |
| **Model Family** | BERT-based + Sketch-based Decoding |
| **Dataset** | WikiSQL |
| **Approach** | Discriminative (Slot-filling) |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | WikiSQL |
| **Quy mô** | 80,654 câu hỏi tự nhiên và câu lệnh SQL tương ứng trên 24,241 bảng từ Wikipedia. |
| **Đặc điểm** | Mỗi câu hỏi chỉ tương ứng với một bảng duy nhất. SQL đơn giản (SELECT, FROM, WHERE). |

### B2. Data Characteristics
- **Input**: Câu hỏi bằng tiếng Anh + Tên các cột của bảng.
- **Output**: Câu lệnh SQL (được biểu diễn dưới dạng sketch/template).

### B3. Preprocessing (Table-Aware)
- Thay vì chỉ đưa câu hỏi vào BERT, SQLova đưa cả câu hỏi và danh sách tên cột vào cùng một lúc, phân tách bởi các token đặc biệt (`[SEP]`). Điều này giúp mô hình hiểu được mối quan hệ giữa các từ trong câu hỏi và các cột trong bảng.

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
SQLova sử dụng kiến trúc **Encoder-Decoder** nhưng phần Decoder không sinh tự do mà dựa trên một **SQL Sketch**.

1. **Encoder (BERT)**: Trích xuất đặc trưng ngữ cảnh cho từng từ trong câu hỏi và từng cột trong bảng.
2. **Table-Aware Contextualization**: Sử dụng lớp Bi-LSTM chồng lên sau BERT để làm mịn thông tin.
3. **Execution-Guided Decoding (EG)**: Một kỹ thuật quan trọng giúp loại bỏ các câu lệnh SQL không hợp lệ về mặt logic (ví dụ: so sánh cột kiểu chuỗi với giá trị số) bằng cách thử thực thi trên database.

### C2. SQL Sketch
SQLova chia bài toán thành 6 nhiệm vụ con (sub-tasks):
- **SELECT column**
- **SELECT aggregator** (MAX, MIN, COUNT, v.v.)
- **WHERE number** (số lượng điều kiện)
- **WHERE column**
- **WHERE operator** (=, >, <)
- **WHERE value** (trích xuất thực thể từ câu hỏi)

---

## Phần D: Training Configuration

### D1. Optimization
- **Pre-trained model**: BERT-Base hoặc BERT-Large (Uncased).
- **Fine-tuning**: Cập nhật trọng số của BERT cùng với các lớp phía trên.
- **Loss function**: Cross-entropy cho từng sub-task.

---

## Phần E: So Sánh Với Baselines

| Feature | SQLova | Seq2SQL / SQLNet |
|---------|--------|------------------|
| Encoder | BERT (Pre-trained) | LSTM (Train from scratch) |
| Context | Table-Aware (Joint) | Separate Question/Column |
| Execution | Execution-Guided | No Execution Check |

---

## Phần F: Kết Quả & Đánh Giá

### H1. Quantitative Results (WikiSQL)
- **Logical Accuracy**: 84.2% (với BERT-Large + EG).
- **Execution Accuracy**: 90.2% (vượt qua mốc 90% đầu tiên trên WikiSQL).

### H2. Ablation Study
- Việc sử dụng **Execution Guidance** giúp tăng độ chính xác thêm khoảng 2-5%.
- **BERT** đóng vai trò quan trọng nhất, mang lại bước nhảy vọt so với các mô hình dựa trên LSTM thuần túy.

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh
- Cách tiếp cận **Table-Aware** rất thực tế và hiệu quả cho các bài toán SQL đơn giản.
- Việc tích hợp **Execution Guidance** là một ý tưởng thông minh để tận dụng môi trường thực thi nhằm sửa lỗi cho mô hình học máy.

### I2. Hạn Chế
- Sketch-based decoding khiến mô hình khó mở rộng sang các câu lệnh SQL phức tạp (JOIN, sub-query, GROUP BY) - vốn là đặc điểm của tập dữ liệu Spider.

---

## 3-Tier Explanation

### 1. Cấp độ Đứa trẻ (Child)
Hãy tưởng tượng bạn có một chiếc máy thần kỳ. Bạn đưa cho nó một tờ giấy ghi câu hỏi (ví dụ: "Ai là người cao nhất trong lớp?") và một danh sách tên các cột trong sổ điểm (Tên, Chiều cao, Cân nặng). Chiếc máy sẽ nhìn vào cả hai và biết ngay cần tìm ở cột "Chiều cao" và chọn người có số lớn nhất. Để chắc chắn không làm sai, chiếc máy còn thử chạy lệnh đó trên máy tính xem có ra kết quả không trước khi trả lời bạn (**Execution Guidance**).

### 2. Cấp độ Sinh viên (Student)
**SQLova** là một mô hình **Text-to-SQL** tiên phong ứng dụng **BERT**. Nó mã hóa đồng thời câu hỏi và cấu trúc bảng (schema) để tạo ra các biểu diễn vector giàu ngữ cảnh. Thay vì sinh câu lệnh SQL từng từ một, nó sử dụng một **phác thảo (sketch)** có sẵn và điền các giá trị vào các vị trí trống (như tên cột, toán tử so sánh). Điểm nhấn là cơ chế **Execution-Guided Decoding**, giúp lọc bỏ các kết quả sai về kiểu dữ liệu bằng cách thực thi thử câu lệnh SQL trên database thực tế.

### 3. Cấp độ Chuyên gia (Expert)
**SQLova** tối ưu hóa bài toán chuyển đổi ngôn ngữ tự nhiên sang SQL trên tập **WikiSQL** thông qua việc kết hợp **Pre-trained Language Models (BERT)** với cơ chế **Slot-filling** dựa trên sketch. Mô hình thực hiện **Schema Linking** ngầm định thông qua việc mã hóa chuỗi liên kết (Question + Column Names). Kiến trúc này giải quyết vấn đề trích xuất giá trị trong mệnh đề WHERE bằng cơ chế **Pointer Network**. Việc áp dụng **Execution Guidance** đóng vai trò như một bộ lọc hậu xử lý mạnh mẽ, loại bỏ các không gian tìm kiếm không khả thi về mặt ngữ nghĩa thực thi, từ đó đẩy độ chính xác vượt qua các giới hạn trước đó của các mô hình dựa trên RL hoặc Seq2Seq thuần túy.

---

## Misconception Seeds
1. **Lầm tưởng**: SQLova có thể viết được mọi loại câu lệnh SQL phức tạp.
   - **Sự thật**: Nó được thiết kế tối ưu cho WikiSQL (truy vấn trên 1 bảng đơn lẻ), không hỗ trợ JOIN hoặc các cấu trúc lồng nhau phức tạp.
2. **Lầm tưởng**: Mô hình này tự học ngôn ngữ SQL từ đầu.
   - **Sự thật**: Nó dựa vào một "khung" (sketch) cố định và chỉ học cách điền các thành phần vào khung đó.

---

## Transfer Question
**Làm thế nào để áp dụng tư tưởng "Execution Guidance" của SQLova vào việc sinh mã độc SQL Injection, cụ thể là để tự động kiểm tra xem một payload được sinh ra có gây ra lỗi cú pháp (Syntax Error) trên server mục tiêu hay không trước khi gửi đi?**
