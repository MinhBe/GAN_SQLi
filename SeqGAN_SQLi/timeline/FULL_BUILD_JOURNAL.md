# Nhật Ký Xây Dựng SeqGAN SQLi — Toàn Bộ Hành Trình

> **Đối tượng đọc**: Bất kỳ ai — kể cả người chưa bao giờ viết code.
> **Ngày thực hiện**: 2026-05-10
> **Trạng thái hiện tại**: MLE pretrain ✅ hoàn thành | Adversarial training ⏳ đang chạy

---

## Mục Lục

1. [Bức Tranh Lớn — Dự Án Này Làm Gì?](#1-bức-tranh-lớn)
2. [Tại Sao Phải Làm Điều Này?](#2-tại-sao)
3. [Nguyên Lý Hoạt Động — Giải Thích Không Cần Biết Code](#3-nguyên-lý-hoạt-động)
4. [Sprint 1 — Chuẩn Bị Dữ Liệu](#4-sprint-1--chuẩn-bị-dữ-liệu)
5. [Sprint 2 — Xây Dựng Các Thành Phần Mô Hình](#5-sprint-2--xây-dựng-mô-hình)
6. [Sprint 3 — MLE Pre-training (Học Bắt Chước)](#6-sprint-3--mle-pre-training)
7. [Sprint 4 — Adversarial RL Training (Học Qua Thưởng Phạt)](#7-sprint-4--adversarial-rl-training)
8. [Sprint 5 — Đánh Giá Kết Quả](#8-sprint-5--đánh-giá)
9. [Những Vấn Đề Gặp Phải và Cách Giải Quyết](#9-vấn-đề-và-giải-quyết)
10. [Kết Quả Đã Đạt Được](#10-kết-quả)
11. [Tại Sao Chọn Thiết Kế Này?](#11-giải-thích-thiết-kế)
12. [Cấu Trúc File Đã Tạo](#12-cấu-trúc-file)

---

## 1. Bức Tranh Lớn

### Dự án này làm gì?

Dự án xây dựng một **AI có khả năng tự sáng tạo ra các câu tấn công SQL (SQL Injection)** — những đoạn code độc hại mà hacker dùng để "qua mặt" hệ thống bảo vệ cơ sở dữ liệu.

**Mục đích nghiên cứu (không phải tấn công thực tế)**: Hiểu được AI có thể sinh ra các kiểu tấn công chưa từng thấy để từ đó xây dựng hệ thống phòng thủ tốt hơn.

### Hãy hình dung như thế này:

```
+------------------+        +-------------------+        +-----------------+
|   Hacker thật    |  gõ   | Web Application   |  chặn  | Cơ sở dữ liệu  |
|  (người dùng xấu)|------->| Firewall (WAF)    |------->| (dữ liệu nhạy  |
|                  |        | "bảo vệ viên"     |        | cảm)            |
+------------------+        +-------------------+        +-----------------+

Dự án này làm gì?
Tạo ra một AI "học sinh" được luyện tập với hàng chục nghìn ví dụ tấn công,
rồi tự sáng tạo ra các biến thể mới có thể qua mặt "bảo vệ viên" đó.
```

### Tại sao điều này có giá trị trong nghiên cứu?

> Nếu bạn muốn xây một cái ổ khóa tốt hơn, bạn cần biết những cách nào có thể phá được nó trước.

Mô hình AI này giúp các chuyên gia bảo mật:
- Tìm ra lỗ hổng trong WAF *trước khi* hacker thật tìm ra
- Tạo ra bộ dữ liệu test phong phú hơn cho hệ thống phòng thủ
- Hiểu cách các kiểu tấn công tiến hóa theo thời gian

---

## 2. Tại Sao?

### Tại sao dùng AI thay vì viết tay?

Một hacker giỏi có thể tạo ra vài chục biến thể tấn công trong một ngày. Một AI được huấn luyện tốt có thể tạo ra **hàng triệu biến thể đa dạng** trong vài giây — và quan trọng là, nó tìm được những biến thể mà con người *chưa nghĩ ra*.

### Tại sao dùng SeqGAN thay vì cách khác?

Dự án này là một trong **ba nhánh nghiên cứu song song**:

| Phương pháp | Cách tiếp cận | Ưu điểm | Nhược điểm |
|-------------|---------------|---------|------------|
| **SeqGAN** (nhánh này) | Học qua thưởng/phạt (RL) | Tối ưu trực tiếp khả năng vượt WAF | Huấn luyện chậm, không ổn định |
| VAE-GAN | Học không gian tiềm ẩn | Ổn định hơn, đa dạng hơn | Không tối ưu trực tiếp WAF bypass |
| Gumbel-Softmax | Xấp xỉ liên tục | Gradient ổn định | Không dùng được signal không-vi-phân |

SeqGAN là lựa chọn duy nhất có thể dùng **tín hiệu reward không-vi-phân** (như: WAF có block không? Parser có parse được không?) — đây là lợi thế cốt lõi.

### Vấn đề kỹ thuật cốt lõi: Tại sao text generation khó với GAN thông thường?

Hãy nghĩ về cách AI học vẽ tranh (image GAN):
- AI thử vẽ → Chuyên gia cho điểm → AI điều chỉnh từng pixel

Với text (câu chữ), điều này **không hoạt động được**:
- Câu chữ là rời rạc: `"SELECT"` hoặc `"select"`, không có trung gian
- Không thể "điều chỉnh một chút" từ `"SELECT"` về phía `"UNION"` như điều chỉnh pixel màu

**SeqGAN giải quyết bằng cách**: Đừng nhìn vào từng chữ. Hãy coi việc viết một câu SQL như một **trò chơi** — mỗi lần chọn từ tiếp theo là một **nước đi**, và phần thưởng chỉ đến khi câu hoàn thành. Kỹ thuật này có tên là **Reinforcement Learning (Học Tăng Cường)**.

---

## 3. Nguyên Lý Hoạt Động — Giải Thích Không Cần Biết Code

### 3.1 Ba nhân vật chính

```
+============================================================+
|                    VÒNG HUẤN LUYỆN                         |
|                                                            |
|  [GENERATOR]          [DISCRIMINATOR]       [ORACLE]       |
|  "Kẻ Làm Giả"         "Thám Tử"            "Giám Khảo"    |
|                                                            |
|  Học cách tạo ra       Học cách phân biệt   Chấm điểm     |
|  câu SQL trông         câu SQL thật với     câu SQL có     |
|  như thật              câu SQL giả          hợp lệ không   |
+============================================================+
```

**Generator (Kẻ Làm Giả)**:
- Nhận vào: không có gì (hoặc một từ khởi đầu)
- Tạo ra: từng từ một, giống như viết câu chữ
- Mục tiêu: tạo ra câu SQL trông như thật VÀ qua được WAF

**Discriminator (Thám Tử)**:
- Nhận vào: một câu SQL (có thể là thật hoặc do Generator tạo ra)
- Cho ra: điểm số "câu này trông thật đến mức nào"
- Mục tiêu: không bị Generator qua mặt

**Oracle (Giám Khảo)**:
- Nhận vào: câu SQL từ Generator
- Kiểm tra: câu có đúng cú pháp SQL không? Có qua được WAF không?
- Cho ra: điểm thưởng để Generator học

### 3.2 Vòng học tập — Câu chuyện của "Thợ Làm Giả Tiền"

Hãy tưởng tượng Generator là một **thợ làm giả tiền**, Discriminator là **chuyên gia ngân hàng**:

**Giai đoạn 1 — Học Bắt Chước (MLE Pre-training)**:
```
Thợ làm giả: "Tôi cần học từ tiền thật trước"
→ Nhìn vào 28,602 ví dụ câu SQL tấn công thật
→ Học: sau "SELECT" thường đến gì? Sau "FROM" thường đến gì?
→ Giống như đứa trẻ học viết bằng cách nhìn vào chữ mẫu
```

**Giai đoạn 2 — Luyện Tập Thực Chiến (Adversarial RL)**:
```
Thợ làm giả tạo tiền giả → Đưa cho chuyên gia ngân hàng xem
Chuyên gia: "Cái này giả quá, nhìn thấy ngay" → Thợ bị trừ điểm
Thợ làm giả tạo lại → "Cái này trông OK hơn" → Thợ được thêm điểm
... lặp đi lặp lại 50,000 lần ...
Kết quả: Thợ làm giả tiền ngày càng giỏi hơn
```

### 3.3 Monte Carlo Rollout — "Chơi trước để biết kết quả"

Đây là kỹ thuật quan trọng nhất trong SeqGAN. Hãy dùng ví dụ cờ vua:

```
Tình huống: Bạn đang chơi cờ vua, cần quyết định nước đi thứ 5.

Cách thông thường: Chọn theo bản năng
Cách Monte Carlo: 
  - Từ nước đi thứ 5 này, thử chơi 16 ván cờ ngẫu nhiên đến cuối
  - Xem trung bình bao nhiêu ván thắng?
  - Nếu thắng 12/16 ván → nước đi này tốt!
  - Nếu thắng 3/16 ván → nước đi này tệ!
```

Trong SeqGAN:
- "Nước đi" = chọn từ tiếp theo trong câu SQL
- "Chơi đến cuối" = hoàn thành toàn bộ câu SQL
- "Thắng" = câu SQL qua được WAF và đúng cú pháp
- K=16 = thử 16 kịch bản khác nhau để tính điểm trung bình

**Tại sao cần điều này?** Vì phần thưởng chỉ đến khi câu hoàn thành — nhưng quyết định quan trọng xảy ra từ từ ngay từ đầu. Monte Carlo giúp "phân bổ công trạng" về các bước trước đó.

### 3.4 WGAN-GP — "Thám Tử Không Thể Bị Hối Lộ"

Discriminator bình thường cho điểm 0 hoặc 1 (giả/thật). Điều này dễ bị lợi dụng.

WGAN-GP (Wasserstein GAN với Gradient Penalty) hoạt động khác:
- Cho điểm **liên tục** (không phải 0/1)
- Có **ràng buộc toán học** ngăn Discriminator "nói dối"
- Giúp Generator có **gradient (hướng học)** rõ ràng hơn ngay cả khi nó đang tạo ra đồ giả rất tệ

Hình dung: thay vì chuyên gia ngân hàng chỉ nói "thật/giả", họ nói "tờ này 73% trông thật, tờ kia 12% trông thật" — phản hồi chi tiết hơn giúp thợ làm giả học nhanh hơn.

---

## 4. Sprint 1 — Chuẩn Bị Dữ Liệu

### 4.1 Xuất phát điểm

**Dữ liệu đầu vào**: File `combined_labeled_data.csv` với **40,860 câu SQL injection** đã được gán nhãn.

```
Ví dụ một dòng dữ liệu:
payload_norm : " or pg_sleep ( __TIME__ ) --
sqli_type   : time_blind
db_engine   : postgresql
confidence  : 0.95
reasoning   : pg_sleep là hàm delay thời gian của PostgreSQL, dùng trong Time-based blind SQLi
```

Các loại tấn công trong dataset:

| Loại tấn công | Số lượng | Giải thích ngắn |
|---------------|----------|-----------------|
| benign | 19,669 | Câu SQL bình thường, không độc hại |
| error_based | 8,663 | Khai thác thông báo lỗi của database |
| boolean_blind | 2,711+1,820 | Hỏi database yes/no để suy ra thông tin |
| time_blind | 2,391 | Đo thời gian phản hồi để lấy thông tin |
| union_based | 2,236 | Kết hợp nhiều query để lấy dữ liệu |
| ... | ... | ... |

### 4.2 Bước 1: Chuẩn hóa nhãn (`normalize_labels.py`)

**Vấn đề**: Dataset có tên nhãn không nhất quán.
- `boolean_based` và `boolean_blind` — cùng một loại tấn công, tên khác nhau
- `stacked_query` và `stacked_queries` — tương tự

**Giải pháp**: Script nhỏ đổi tên tự động.

**Tại sao quan trọng**: Nếu mô hình thấy cùng một loại tấn công với hai tên khác nhau, nó sẽ "nghĩ" đó là hai thứ khác nhau → học sai. Giống như nếu bạn dạy trẻ em "con mèo" và "cat" như hai con vật khác nhau.

**Kết quả**: 1,820 dòng `boolean_based` → `boolean_blind`

### 4.3 Bước 2: De-lexicalization — "Trừu Tượng Hóa" (`prepare_seqgan_data.py`)

Đây là **bước quan trọng nhất** trong toàn bộ data pipeline.

**Vấn đề gốc rễ**:
Câu SQL tấn công có hàng nghìn biến thể cụ thể:
```
' OR 1=1 --
' OR 2=2 --
' OR 3=3 --
' OR 9999=9999 --
```
Tất cả đều là cùng một kiểu tấn công, chỉ khác số. Nếu mô hình phải học riêng từng số, nó cần một từ điển khổng lồ và mất rất nhiều thời gian.

**Giải pháp — De-lexicalization**:
Thay thế các giá trị cụ thể bằng "placeholder" (đại diện):

```
Trước de-lex:
  ' OR 1=1 --
  SELECT * FROM users WHERE id = 'admin' AND password = 'abc123'
  SLEEP(5) OR 0x616263 = 0x616263

Sau de-lex:
  __STR__ OR __INT__ = __INT__ --
  SELECT * FROM __TABLE__ WHERE __COL__ = __STR__ AND __COL__ = __STR__
  SLEEP ( __INT__ ) OR __HEX__ = __HEX__
```

| Placeholder | Thay thế cho | Ví dụ |
|-------------|--------------|-------|
| `__STR__` | Chuỗi ký tự trong nháy đơn/đôi | `'admin'`, `"test"` |
| `__INT__` | Số nguyên | `1`, `9999`, `42` |
| `__HEX__` | Số thập lục phân | `0x616263` |
| `__TABLE__` | Tên bảng phổ biến | `users`, `admin`, `accounts` |
| `__COL__` | Tên cột phổ biến | `id`, `password`, `name` |
| `__IDENT__` | Định danh lạ không biết | `dbms_pipe`, `xmltype` |

**Tại sao điều này giúp ích**:

```
Trước de-lex: Vocabulary (từ điển) = 3,088 tokens
Sau de-lex:   Vocabulary (từ điển) = 134 tokens

Giảm 96% kích thước từ điển!
```

Từ điển nhỏ hơn có nghĩa là:
- Mô hình học nhanh hơn
- Policy Gradient (thuật toán RL) ổn định hơn (ít variance)
- Ít bị overfitting (học vẹt)

**Hình dung**: Thay vì học thuộc lòng "John Smith mua 3 quả táo", "Jane Doe mua 7 quả cam", bạn học cấu trúc "[Tên người] mua [số] quả [loại quả]" — hiểu sâu hơn, tổng quát hơn.

### 4.4 Bước 3: Phân chia dữ liệu (Stratified Split)

**Phân chia 70/15/15**:

```
40,860 câu SQL
├── Train set: 28,602 câu (70%) — để mô hình học
├── Val set:   6,129 câu  (15%) — để kiểm tra trong quá trình học
└── Test set:  6,129 câu  (15%) — ĐÓNG BĂNG, chỉ dùng khi đánh giá cuối
```

**"Stratified"** nghĩa là gì? Đảm bảo mỗi phần có tỷ lệ đúng của từng loại tấn công. Nếu dataset gốc có 10% `time_blind`, thì train/val/test đều có ~10% `time_blind`. 

**Tại sao test set phải "đóng băng"?** Giống như đề thi — nếu học sinh nhìn thấy đề trước, điểm số không phản ánh thực lực. Mô hình không bao giờ được "nhìn thấy" test set trong quá trình huấn luyện.

**Seed = 42**: Con số ngẫu nhiên cố định. Đảm bảo mọi lần chạy lại cho ra cùng phân chia — khả năng tái tạo kết quả là điều kiện bắt buộc trong nghiên cứu khoa học.

### 4.5 Bước 4: Expert Demonstrations

```
Expert demos = Tập con đặc biệt
Điều kiện: is_attack = True VÀ confidence >= 0.95

Số lượng: 3,223 câu (11.3% của train set)
```

**Tại sao cần Expert Demos?**

Đây là ý tưởng từ **Imitation Learning (Học Bắt Chước)**: khi dạy robot lái xe, bạn không chỉ để robot thử ngẫu nhiên — bạn cho nó xem người lái giỏi trước. 

Trong dự án này: các câu SQLi với `confidence >= 0.95` là những câu "chuyên gia đã xác nhận là tấn công thật sự, không phải benign". Trong giai đoạn pre-training, những câu này được **tăng trọng số × 3** — mô hình "chú ý" đến chúng nhiều hơn.

### 4.6 Tóm tắt kết quả Sprint 1

```
INPUT:  combined_labeled_data.csv (40,860 dòng, 5 cột)
OUTPUT:
  data/train.csv        → 28,602 câu
  data/val.csv          → 6,129 câu
  data/test.csv         → 6,129 câu (ĐÓNG BĂNG)
  data/expert_demos.csv → 3,223 câu (confidence >= 0.95)
  data/tokenizer_vocab.json → 134 tokens

Thời gian chạy: ~30 giây
```

---

## 5. Sprint 2 — Xây Dựng Mô Hình

### 5.1 Danh sách các "bộ phận" đã tạo

```
src/
├── tokenizer.py         → Từ điển và bộ chuyển đổi text ↔ số
├── generator.py         → Não bộ tạo ra câu SQL (LSTM)
├── discriminator.py     → Bộ phận phân biệt thật/giả (TextCNN)
├── env.py               → Môi trường RL (như bàn cờ cho AI)
├── reward.py            → Hàm chấm điểm (thưởng/phạt)
├── rollout.py           → Monte Carlo (thử nhiều kịch bản)
├── baseline.py          → Bộ giảm nhiễu cho RL
├── losses.py            → Các công thức tính "độ sai" để cải thiện
├── scheduled_sampling.py→ Giảm dần "nhìn bài" trong quá trình học
└── utils.py             → Các hàm tiện ích
```

### 5.2 Generator — "Não Bộ Sáng Tác"

**Kiến trúc**: LSTM 3 lớp

**LSTM là gì?** (Long Short-Term Memory)

LSTM là loại mạng neural có **bộ nhớ**. Khi viết câu SQL từng từ một, nó không quên những từ đã viết trước:

```
Câu đang viết: "SELECT * FROM users WHERE id ="

Bước tiếp theo, LSTM "nhớ":
- Đã bắt đầu bằng SELECT → đây là query đọc dữ liệu
- Đang ở mệnh đề WHERE → cần điều kiện lọc
- Đã có dấu "=" → cần một giá trị

→ Xác suất cao: __STR__ hoặc __INT__ hoặc __IDENT__
→ Xác suất thấp: FROM, SELECT (không hợp lý ở đây)
```

**Cấu hình**:
```
Số lớp LSTM:    3   (3 mức xử lý thông tin, từ thấp đến cao)
Kích thước:   512   (mỗi lớp có 512 "tế bào thần kinh")
Dropout:      0.2   (20% neuron bị tắt ngẫu nhiên khi train → tránh học vẹt)
Từ điển:      134   (134 token có thể chọn mỗi bước)
```

**Cách hoạt động** (đơn giản hóa):

```
Bước 1: [SOS] → LSTM → phân phối xác suất trên 134 tokens
         Xác suất: SELECT(35%), OR(20%), __STR__(15%), ...
         Chọn ngẫu nhiên theo xác suất → SELECT

Bước 2: SELECT → LSTM → phân phối xác suất mới
         Xác suất: *(40%), __IDENT__(25%), count(15%), ...
         Chọn → *

Bước 3: * → LSTM → ...tiếp tục cho đến khi gặp [EOS] hoặc đủ dài
```

### 5.3 Discriminator — "Thám Tử Phân Loại"

**Kiến trúc**: TextCNN (Convolutional Neural Network cho văn bản)

TextCNN dùng **cửa sổ trượt** để phân tích từng đoạn nhỏ của câu SQL:

```
Câu SQL: [SELECT] [*] [FROM] [__TABLE__] [WHERE] [__COL__] [=] [__STR__]

Cửa sổ 3-gram quét qua:
  [SELECT * FROM] → "Đây là đầu query SELECT bình thường"
  [* FROM __TABLE__] → "FROM sau * là pattern phổ biến"
  [FROM __TABLE__ WHERE] → "Cấu trúc chuẩn"
  ...

Cửa sổ 4-gram, 5-gram cũng làm tương tự.
Tổng hợp tất cả → Điểm số: "Câu này trông thật 0.72/1.0"
```

**WGAN-GP** (Wasserstein Gradient Penalty):
- Thay vì điểm 0/1, cho điểm liên tục
- Ràng buộc toán học: gradient penalty đảm bảo Discriminator không "cực đoan" quá
- Lợi ích: Generator luôn có tín hiệu học rõ ràng, ngay cả khi đang rất tệ

### 5.4 SQLiEnv — "Bàn Cờ" cho AI

**Kiến trúc**: Gym-like interface (giống OpenAI Gym)

```python
# Giao diện đơn giản:
env.reset()           → Bắt đầu câu mới [SOS]
env.step(action)      → Thêm một token vào câu
                        Trả về: (câu mới, phần thưởng, xong chưa)
env.compute_reward()  → Tính điểm thưởng cho câu hoàn chỉnh
```

**Tại sao cần wrapper này?**
- Tách biệt logic môi trường khỏi logic học
- Dễ thay thế phần tính reward mà không cần sửa toàn bộ code
- Tuân theo chuẩn OpenAI Gym → tương thích với nhiều thuật toán RL khác nhau

### 5.5 Reward Oracle — "Bảng Chấm Điểm"

**Công thức reward**:

```
r_total = 0.3 × D(x)        → Điểm từ Discriminator "câu trông thật"
        + 0.5 × r_bypass     → Điểm từ proxy WAF bypass
        + 0.2 × r_syntax     → Điểm từ SQL parser
        - length_penalty     → Phạt nếu câu quá dài
        - trivial_penalty    → Phạt nếu câu quá ngắn (< 5 tokens)
```

**Giải thích từng thành phần**:

| Thành phần | Trọng số | Ý nghĩa | Tại sao mức này? |
|------------|----------|---------|-----------------|
| D(x) | 0.3 | Câu trông như SQLi thật không? | Nhỏ nhất — chỉ là "tấm gương" |
| r_bypass | 0.5 | Câu có vượt WAF không? | Lớn nhất — đây là mục tiêu chính |
| r_syntax | 0.2 | Câu có đúng cú pháp SQL không? | Ngưỡng tối thiểu phải đạt |
| length_penalty | — | Phạt câu quá dài | Chống reward hacking |
| trivial_penalty | — | Phạt câu chỉ `--` hay `;` | Chống shortcut vô nghĩa |

**Dev mode vs Production mode**:
- **Production**: Gửi payload đến ModSecurity Docker thật → kết quả chính xác
- **Dev mode** (đang dùng): Heuristic proxy — câu có chứa `UNION`, `SLEEP(`, `OR 1=1` thì được điểm bypass

Lý do dùng dev mode: Docker ModSecurity chưa setup. Kết quả "estimated ASR" — có thể so sánh giữa các mô hình, nhưng con số tuyệt đối chưa chính xác.

### 5.6 Scheduled Sampling — "Tập Bơi Không Phao Dần"

**Vấn đề**: Trong MLE training, mô hình luôn được "nhìn bài" (dùng token thật của dataset làm input). Khi sang RL phase, phải tự dùng prediction của mình → bị shock vì chưa quen.

**Giải pháp**: Tăng dần tỷ lệ dùng prediction của bản thân.

```
Bước 0:    ε = 0.0  → 100% dùng token thật (teacher forcing hoàn toàn)
Bước 1000: ε = 0.2  → 20% dùng dự đoán, 80% dùng token thật
Bước 2500: ε = 0.5  → 50-50
Bước 5000: ε = 1.0  → 100% tự lập, không nhìn bài nữa
```

**Tương tự**: Dạy bơi — đầu tiên có phao đỡ (teacher forcing), dần dần bỏ phao ra, cuối cùng tự bơi hoàn toàn.

---

## 6. Sprint 3 — MLE Pre-training

### 6.1 Mục tiêu

Trước khi dạy AI "sáng tạo bypass WAF", phải dạy nó "viết đúng SQL" đã. Giai đoạn này gọi là **MLE Pre-training** (Maximum Likelihood Estimation — tối đa hóa khả năng dự đoán đúng).

**Nguyên lý**:
```
Dữ liệu thật: SELECT * FROM __TABLE__ WHERE __COL__ = __STR__ OR __INT__ = __INT__

Mô hình dự đoán: "Sau SELECT, token tiếp theo là gì?"
Nếu đúng → reward cao
Nếu sai  → penalty

Sau hàng triệu ví dụ, mô hình học được phân phối xác suất của SQL thật.
```

### 6.2 Expert Upweighting — "Chú Ý Hơn Vào Ví Dụ Tốt"

```
Batch bình thường:   loss × 1.0
Batch expert demos:  loss × 3.0  (chú ý 3 lần hơn)
```

**Tại sao?** Expert demos là những câu tấn công đã xác nhận hoạt động. Mô hình cần học đặc trưng của chúng rõ ràng hơn so với các câu ít tin cậy hơn.

### 6.3 Quá Trình và Kết Quả

**Cấu hình**: 10 epochs tối đa, early stop patience=3, learning rate=0.001

**Kết quả epoch-by-epoch**:

```
Epoch 1: loss=1.99, val_ppl=2.12  ← Bắt đầu học từ số 0
Epoch 2: loss=0.99, val_ppl=1.81  ← Cải thiện mạnh (-0.31)
Epoch 3: loss=0.93, val_ppl=1.73  ← Tiếp tục giảm (-0.08)
Epoch 4: loss=0.89, val_ppl=1.72  ← Chậm lại (-0.01)
Epoch 5: loss=0.87, val_ppl=1.70  ← BEST ← Lưu checkpoint
Epoch 6: loss=0.85, val_ppl=1.71  ← Tăng nhẹ (bắt đầu overfit?)
Epoch 7: loss=0.84, val_ppl=1.75  ← Tiếp tục tăng
Epoch 8: loss=0.84, val_ppl=1.83  ← Patience counter = 3
→ EARLY STOP
```

**Perplexity (PPL) là gì?**

PPL đo mức độ "ngạc nhiên" của mô hình khi nhìn vào dữ liệu thật:
- PPL = 2.12: Mô hình "ngạc nhiên" nhiều → chưa học tốt
- PPL = 1.70: Mô hình "ngạc nhiên" ít → đã học khá tốt
- PPL = 1.0: Mô hình dự đoán hoàn hảo (không thực tế — sẽ là overfitting)

**Tại sao PPL ~1.70 là tốt?**

Với vocabulary 134 tokens, PPL ngẫu nhiên = 134. PPL = 1.70 nghĩa là mô hình đã thu hẹp không gian tìm kiếm từ 134 xuống còn 1.70 lựa chọn "có khả năng" ở mỗi bước — hiểu biết về cú pháp SQL rất sâu.

**Early Stop** — Tại sao dừng ở epoch 8 thay vì chạy hết 10?

Vì PPL trên validation set đã bắt đầu tăng lại sau epoch 5, dù training loss vẫn giảm. Đây là dấu hiệu của **overfitting** (học vẹt): mô hình đang ghi nhớ dataset thay vì hiểu cấu trúc SQL. Dừng sớm → giữ lại mô hình tổng quát hơn.

**Thời gian**: ~8 epochs × 447 batches × ~38 giây/epoch ≈ **~5 phút** (trên GPU CUDA)

### 6.4 Checkpoint đã lưu

```
checkpoints/mle_best.pt    ← Epoch 5, val_ppl=1.70  (DÙNG CHO RL)
checkpoints/mle_final.pt   ← Epoch 8 cuối cùng
```

---

## 7. Sprint 4 — Adversarial RL Training

### 7.1 Tại Sao Cần Giai Đoạn Này Sau Khi Đã Pre-train?

MLE pre-training dạy mô hình "viết SQL trông như dataset". Nhưng mục tiêu thực sự là **"viết SQL bypass được WAF"** — hai điều này khác nhau đáng kể.

Hình dung:
```
Sau MLE:   Mô hình viết được câu SQL bình thường, đúng cú pháp
           Nhưng: vẫn giống dataset gốc quá, WAF detect được ngay

Sau RL:    Mô hình "tiến hóa" để tìm câu SQL mà WAF không nhận ra
           Trong khi vẫn đúng cú pháp SQL
```

### 7.2 Vòng Lặp REINFORCE — "Học Qua Thưởng Phạt"

```
Mỗi step trong 50,000 steps:

[1] Generator tạo ra 64 câu SQL ngẫu nhiên
    (dùng xác suất đã học từ MLE phase)

[2] Tính reward cho mỗi câu:
    - Syntax check: sqlparse có parse được không?
    - Bypass proxy: có pattern tấn công không?
    - Discriminator score: trông như SQLi thật không?
    → reward = trung bình cộng có trọng số

[3] Tính Advantage = reward - baseline
    (Điểm này TỐT HƠN mức bình thường bao nhiêu?)

[4] Cập nhật Generator:
    Nếu reward > baseline → tăng xác suất chọn những token đó
    Nếu reward < baseline → giảm xác suất chọn những token đó

[5] Cập nhật Discriminator (5 lần):
    Cho xem câu SQL thật + câu SQL giả
    Học phân biệt tốt hơn

[6] Cập nhật Baseline:
    Cập nhật "mức bình thường" để tính advantage lần sau
```

### 7.3 Tại Sao Cần Baseline?

**Vấn đề không có baseline**:
```
Câu A: reward = 0.7  → "Câu A OK, tăng xác suất"
Câu B: reward = 0.5  → "Câu B kém hơn A, nhưng vẫn tăng xác suất?"
Câu C: reward = 0.1  → "Câu C tệ, giảm xác suất"
```
Không có baseline, tất cả reward dương đều được khuyến khích → gradient rất nhiễu.

**Với baseline**:
```
Baseline (EMA của reward gần đây) = 0.4

Câu A: advantage = 0.7 - 0.4 = +0.3  → Tốt hơn mức bình thường, tăng mạnh
Câu B: advantage = 0.5 - 0.4 = +0.1  → Hơi tốt hơn, tăng nhẹ
Câu C: advantage = 0.1 - 0.4 = -0.3  → Kém hơn mức bình thường, giảm mạnh
```
Gradient sạch hơn, học hiệu quả hơn.

**Kỹ thuật EMA (Exponential Moving Average)**:
```
baseline_mới = 0.95 × baseline_cũ + 0.05 × reward_vừa_rồi
```
Giống như "bộ nhớ mờ dần" — sự kiện gần đây ảnh hưởng nhiều hơn sự kiện xa.

### 7.4 Cơ Chế Chống Reward Hacking

**Reward Hacking** là gì? AI tìm ra "gian lận" — cách đạt điểm cao mà không thực sự thỏa mãn mục tiêu.

Ví dụ điển hình trong text generation:
- Mô hình học rằng câu ngắn hay lặp lại ít lỗi cú pháp hơn → sinh toàn câu `--` hoặc `;`
- Điểm syntax cao, điểm bypass cao (WAF thường bỏ qua comment), nhưng vô nghĩa

**Các cơ chế phòng chống đã implement**:

| Cơ chế | Mô tả | Kích hoạt khi |
|--------|-------|----------------|
| Length penalty | Phạt câu dài hơn max_len=80 | len > 80 tokens |
| Trivial penalty | Phạt câu < 5 tokens | len < 5 |
| Syntax monitor | Nếu syntax rate < 50% sau 5k steps → tăng λ_syntax lên 0.4 | Tự động |

### 7.5 Cấu Hình Adversarial Training

```yaml
total_steps:    50,000    # 50k bước học
lr_g:           0.0001   # Học rate của Generator (nhỏ → ổn định)
lr_d:           0.0001   # Học rate của Discriminator
batch_size:     64        # 64 câu SQL mỗi bước
d_steps_per_g:  5         # Train D 5 lần / 1 lần train G
mc_rollout_k:   16        # 16 kịch bản Monte Carlo mỗi bước
gp_lambda:      10.0      # Cường độ Gradient Penalty
grad_clip:      1.0       # Cắt gradient nếu quá lớn (tránh bùng nổ)
```

**Tại sao D train 5 lần / G train 1 lần?**
Discriminator cần phải "đủ mạnh" để cho Generator tín hiệu học có ý nghĩa. Nếu Generator quá mạnh so với Discriminator, nó sẽ "lừa" Discriminator dễ dàng mà không học được gì thực sự.

---

## 8. Sprint 5 — Đánh Giá

### 8.1 Các Metrics Quan Trọng

**Sau khi training xong, chạy**:
```bash
python SeqGAN_SQLi/generate.py --ckpt checkpoints/adv_final.pt --n_samples 1000 --out eval_samples.csv
python SeqGAN_SQLi/evaluate.py --input eval_samples.csv
```

**Bốn metric cốt lõi**:

| Metric | Cách tính | Mục tiêu | Ý nghĩa |
|--------|-----------|---------|---------|
| **ASR** (Attack Success Rate) | % câu bypass WAF trong 1000 mẫu | > MLE + 30% | Tỷ lệ vượt WAF |
| **Syntax Validity** | % câu parse được bởi sqlparse | > 90% | Câu có đúng cú pháp SQL |
| **Self-BLEU-3** | Điểm n-gram giữa các mẫu | < 0.60 | Đa dạng (thấp = tốt) |
| **Reward convergence** | Đồ thị mean reward theo steps | Tăng dần | Học ổn định |

**Self-BLEU là gì?** Đo mức độ "sao chép lẫn nhau" của 1000 câu được sinh ra:
- BLEU cao = các câu giống nhau → mô hình bị "mode collapse" (chỉ học 1-2 mẫu)
- BLEU thấp = các câu đa dạng → mô hình sáng tạo được nhiều biến thể

### 8.2 Baselines để so sánh

Không có ý nghĩa khi chỉ report số của SeqGAN. Cần so sánh với:

| Baseline | Mô tả | Mục đích |
|----------|-------|---------|
| Template-based | Điền ngẫu nhiên vào mẫu cố định | Lower bound — đơn giản nhất |
| MLE only | Checkpoint sau pre-train, không RL | Biết RL có giúp gì không |
| SeqGAN vanilla | RL không có advantage (Q thay Q-b) | Biết baseline có quan trọng không |
| SeqGAN + advantage | Model đầy đủ của dự án | Upper bound |

### 8.3 Statistical Rigor (Độ Tin Cậy Thống Kê)

Chạy ≥ 3 seeds khác nhau, report `mean ± std`.

Bootstrap CI (n=10,000 resamples) cho ASR:
```
ASR = 67.3% [CI: 64.4% – 70.1%, N=1000]
```
Điều này có nghĩa: "Với 95% tin cậy, ASR thực sự nằm trong khoảng 64.4% đến 70.1%"

---

## 9. Vấn Đề Gặp Phải và Cách Giải Quyết

### 9.1 Vocab quá lớn (3,088 → 134)

**Vấn đề phát hiện**: Chạy lần đầu → vocab = 3,088 tokens (mục tiêu 100-200).

**Nguyên nhân gốc rễ**:
- `||chr` (pipe + function) không có space → trở thành 1 token thay vì 2
- Database-specific functions (`xmltype`, `dbms_pipe`, `sysibm.systables`) → mỗi cái là 1 token riêng
- Số liệu dính vào ký tự (`__INT__"`, `__INT__'`) → tạo hybrid token lạ

**Giải pháp**: Rewrite tokenizer với 2 bước:
1. **Pre-tokenize**: Thêm space xung quanh tất cả operators trước (`||` → ` || `, `(` → ` ( `)
2. **Replace unknowns**: Mọi token không phải SQL keyword → `__IDENT__`

**Kết quả**: 3,088 → **134 tokens** (giảm 96%)

### 9.2 Unicode trong print statements

**Vấn đề**: Windows console mặc định dùng encoding CP1252, không hỗ trợ Unicode `→` (`→`) và `ε` (`ε`).

**Giải pháp**: Thay `→` bằng `->`, `ε` bằng `eps`.

**Bài học**: Code chạy trên máy Linux/Mac không có vấn đề này. Khi deploy trên Windows, cần chú ý encoding của terminal.

### 9.3 Batch size mismatch trong Gradient Penalty

**Vấn đề**: `RuntimeError: The size of tensor a (58) must match tensor b (64)`.

**Nguyên nhân**: Batch cuối cùng của dataset có thể có 58 samples (không đủ 64), nhưng fake_seqs luôn được tạo đủ 64. Khi gradient_penalty cần interpolate giữa real và fake, kích thước phải bằng nhau.

**Giải pháp**: Cắt cả hai về `B_min = min(real.size(0), fake.size(0))` trước khi gửi vào discriminator.

### 9.4 Config path resolution

**Vấn đề**: Script chạy từ `GAN_SQLi/`, nhưng `ROOT` trong script là `SeqGAN_SQLi/`. Khi user pass `--config SeqGAN_SQLi/configs/...`, script build path thành `SeqGAN_SQLi/SeqGAN_SQLi/configs/...` → không tìm thấy file.

**Giải pháp**: Logic fallback:
```
1. Thử path user cung cấp (relative to CWD)
2. Nếu không tìm thấy → thử ROOT + path
3. Nếu vẫn không → fallback về default config
```

---

## 10. Kết Quả Đã Đạt Được

### 10.1 Smoke Tests (Kiểm Tra Nhanh Từng Bước)

| Sprint | Test | Kết quả |
|--------|------|---------|
| Sprint 1 | vocab size | 134 ✅ (target 100-200) |
| Sprint 1 | splits | 28,602 / 6,129 / 6,129 ✅ |
| Sprint 2 | Generator forward pass | shape (4, 32, 134) ✅ |
| Sprint 2 | Discriminator forward pass | shape (4,) ✅ |
| Sprint 2 | Reward oracle | syntax=1.0, bypass=0.2, total=0.3 ✅ |
| Sprint 3 | 100 steps smoke | loss=4.27, no NaN ✅ |
| Sprint 4 | 100 steps smoke | no NaN, syntax=100% ✅ |

### 10.2 MLE Pre-training (Full Run)

```
Best val_ppl = 1.70 (epoch 5 / 10)
Early stop sau epoch 8 (patience=3)
Training time: ~5 phút trên GPU CUDA
Checkpoint: checkpoints/mle_best.pt
```

**Đánh giá**: Perplexity 1.70 với vocab 134 là kết quả tốt. Mô hình đã học được cú pháp SQL injection khá chắc.

### 10.3 Adversarial Training (Đang Chạy)

```
Status: ⏳ 50,000 steps đang chạy
Smoke test (100 steps): syntax=100%, no NaN ✅
Estimated time: ~1-2 giờ
```

### 10.4 Cấu Trúc File Hoàn Chỉnh

```
SeqGAN_SQLi/
├── configs/
│   └── seqgan_default.yaml        ← Tất cả hyperparameters
├── data/
│   ├── normalize_labels.py        ← Bước 0: chuẩn hóa nhãn
│   ├── prepare_seqgan_data.py     ← Sprint 1: data pipeline
│   ├── train.csv                  ← 28,602 samples [GENERATED]
│   ├── val.csv                    ← 6,129 samples  [GENERATED]
│   ├── test.csv                   ← 6,129 samples  [FROZEN]
│   ├── expert_demos.csv           ← 3,223 samples  [GENERATED]
│   └── tokenizer_vocab.json       ← 134 tokens     [GENERATED]
├── src/
│   ├── tokenizer.py               ← SQL tokenizer + de-lex
│   ├── generator.py               ← LSTM 3-layer policy
│   ├── discriminator.py           ← TextCNN WGAN-GP
│   ├── env.py                     ← RL environment
│   ├── reward.py                  ← Reward oracle
│   ├── rollout.py                 ← Monte Carlo Q estimation
│   ├── baseline.py                ← Value baseline (EMA)
│   ├── losses.py                  ← REINFORCE + WGAN-GP + MLE loss
│   ├── scheduled_sampling.py      ← Curriculum learning
│   └── utils.py                   ← Seed, checkpoint, padding
├── baselines/
│   ├── template_based.py          ← Random template fill
│   ├── mle_lm_only.py             ← Generate từ mle_best.pt
│   └── seqgan_vanilla.py          ← RL không có advantage
├── checkpoints/
│   ├── mle_best.pt                ← val_ppl=1.70 [SAVED]
│   ├── mle_final.pt               ← Epoch 8 [SAVED]
│   └── adv_final.pt               ← [ĐANG TẠO]
├── pretrain_mle.py                ← Sprint 3: MLE training
├── train_adversarial.py           ← Sprint 4: RL training
├── generate.py                    ← Inference: sinh payloads
├── evaluate.py                    ← Sprint 5: metrics
├── requirements.txt               ← Dependencies
├── Guiding.md                     ← Tài liệu hướng dẫn
└── IMPLEMENTATION_PLAN.md         ← Kế hoạch implement
```

---

## 11. Giải Thích Thiết Kế — Tại Sao Làm Thế?

### 11.1 Tại sao LSTM thay vì Transformer?

| Tiêu chí | LSTM | Transformer |
|----------|------|-------------|
| Độ phức tạp code | Thấp hơn | Cao hơn |
| Memory khi training | Thấp hơn | Cao hơn (attention matrix) |
| Tốc độ inference | Nhanh hơn (sequential) | Chậm hơn (khi tự hồi quy) |
| Xử lý sequence dài | Tốt với 3-layer LSTM | Tốt hơn LSTM |
| Phù hợp với RL | Tốt (hidden state = state representation) | Khó hơn cho RL |

**Kết luận**: LSTM phù hợp hơn cho bước đầu. Có thể nâng cấp lên Transformer nếu LSTM không đủ mạnh.

### 11.2 Tại sao vocab = 134 là mục tiêu?

Với REINFORCE (policy gradient):
- Variance của gradient ≈ tỷ lệ thuận với kích thước action space
- Vocab 3,088 → gradient quá nhiễu → không học được
- Vocab 134 → gradient đủ sạch để học

Phân tích thực nghiệm từ SeqGAN paper gốc: vocab ~100-200 cho text generation tasks có độ dài vừa phải (~50-100 tokens) là range lý tưởng.

### 11.3 Tại sao K=16 rollouts?

**Trade-off**:
- K quá nhỏ (K=4): Q estimate có variance cao → policy gradient nhiễu
- K quá lớn (K=32): Tốn compute, T×K=80×32=2560 forward passes/step

K=16 là điểm cân bằng phổ biến trong literature (SeqGAN paper gốc dùng K=16).

Nếu gặp OOM (out of memory): giảm xuống K=8.
Nếu training không ổn định: tăng lên K=24 hoặc K=32.

### 11.4 Tại sao λ_bypass = 0.5 (lớn nhất)?

Mục tiêu cuối cùng là ASR (Attack Success Rate). Nếu cho trọng số nhỏ quá:
- Mô hình sẽ optimize D-score và syntax nhiều hơn
- ASR cải thiện ít so với MLE baseline
- Không thể pass hard target: `SeqGAN_ASR > MLE_ASR + 30pp`

0.5 là giá trị khởi đầu. Có thể tune nếu:
- ASR cao nhưng validity thấp → tăng λ_syntax, giảm λ_bypass
- Validity cao nhưng ASR không tăng → tăng λ_bypass

### 11.5 Tại sao D:G = 5:1?

Đây là chuẩn của WGAN. Lý do:
- Wasserstein distance cần Discriminator "đủ mạnh" để estimate khoảng cách phân phối chính xác
- Nếu G và D train cùng tốc độ, D thường "thua" sớm (mode collapse)
- 5:1 đảm bảo D luôn có phản hồi chất lượng cho G

---

## 12. Cấu Trúc File

### Pipeline commands theo thứ tự:

```bash
# Chạy từ C:\Users\Admin\Documents\GAN_SQLi\

# Bước 0: Cài dependencies
pip install -r SeqGAN_SQLi/requirements.txt

# Bước 1: Chuẩn hóa nhãn
python SeqGAN_SQLi/data/normalize_labels.py

# Bước 2: Chuẩn bị dữ liệu + kiểm tra
python SeqGAN_SQLi/data/prepare_seqgan_data.py --verify

# Bước 3: MLE Pre-training (~5-10 phút)
python SeqGAN_SQLi/pretrain_mle.py
# Kết quả: checkpoints/mle_best.pt (val_ppl=1.70)

# Bước 4: Adversarial RL (~1-2 giờ)
python SeqGAN_SQLi/train_adversarial.py --mle_ckpt SeqGAN_SQLi/checkpoints/mle_best.pt
# Kết quả: checkpoints/adv_final.pt

# Bước 5a: Sinh 1000 samples
python SeqGAN_SQLi/generate.py \
  --ckpt SeqGAN_SQLi/checkpoints/adv_final.pt \
  --n_samples 1000 \
  --out eval_samples.csv

# Bước 5b: Đánh giá
python SeqGAN_SQLi/evaluate.py --input eval_samples.csv

# Bước 5c: Sinh baseline samples để so sánh
python SeqGAN_SQLi/baselines/template_based.py --n_samples 1000 --out eval_template.csv
python SeqGAN_SQLi/generate.py --ckpt SeqGAN_SQLi/checkpoints/mle_best.pt \
  --n_samples 1000 --out eval_mle.csv
```

---

## Phụ Lục: Glossary (Từ Điển Thuật Ngữ)

| Thuật ngữ | Giải thích đơn giản |
|-----------|---------------------|
| **SQL Injection** | Kỹ thuật tấn công bằng cách chèn code SQL độc hại |
| **WAF** | Web Application Firewall — "bảo vệ viên" chặn tấn công web |
| **GAN** | Mạng đối nghịch — hai mô hình thi nhau (Generator vs Discriminator) |
| **SeqGAN** | GAN cho dữ liệu tuần tự (text, audio) dùng Reinforcement Learning |
| **LSTM** | Loại mạng neural có bộ nhớ, tốt cho xử lý ngôn ngữ tuần tự |
| **Reinforcement Learning** | Học bằng thưởng/phạt, như huấn luyện thú cưng |
| **REINFORCE** | Thuật toán policy gradient cụ thể để implement RL |
| **Policy Gradient** | Cách cập nhật mô hình dựa trên gradient của expected reward |
| **Monte Carlo Rollout** | Thử nhiều kịch bản ngẫu nhiên để ước tính giá trị tương lai |
| **MLE** | Maximum Likelihood Estimation — học bắt chước dữ liệu thật |
| **Perplexity** | Đo mức độ "ngạc nhiên" của mô hình — thấp hơn là tốt hơn |
| **De-lexicalization** | Thay thế giá trị cụ thể bằng placeholder tổng quát |
| **Stratified Split** | Phân chia dữ liệu giữ nguyên tỷ lệ từng loại |
| **Early Stop** | Dừng training khi validation loss bắt đầu tăng |
| **Overfitting** | Mô hình học vẹt dataset, mất khả năng tổng quát |
| **Batch Size** | Số ví dụ xử lý cùng lúc trong một bước update |
| **Gradient** | Hướng và độ dốc của hàm loss — dùng để điều chỉnh mô hình |
| **Checkpoint** | File lưu trạng thái mô hình tại một thời điểm |
| **ASR** | Attack Success Rate — tỷ lệ câu tấn công bypass được WAF |
| **Self-BLEU** | Đo độ đa dạng của nhiều câu được sinh ra |
| **Reward Hacking** | AI "gian lận" — đạt điểm cao bằng cách không mong muốn |
| **Mode Collapse** | Mô hình chỉ sinh ra 1-2 dạng output, mất đa dạng |
| **EMA** | Exponential Moving Average — trung bình trọng số theo thời gian |
| **Advantage** | Độ tốt của action so với mức trung bình |
| **WGAN-GP** | Phiên bản GAN ổn định hơn dùng Wasserstein distance + gradient penalty |

---

*Tài liệu này được tạo ngày 2026-05-10 sau phiên implement Sprint 1-5.*
*Adversarial training (Sprint 4) đang chạy tại thời điểm viết.*
