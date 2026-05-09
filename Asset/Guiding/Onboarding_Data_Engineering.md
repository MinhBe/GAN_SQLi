# Onboarding — Data Engineering của Dự án

> **Đối tượng đọc**: Thành viên mới của team (vd bạn phụ trách giới thiệu sản phẩm/marketing) **chưa có background về code, AI, hay bảo mật**. File này dùng analogy đời thường, không công thức toán, có glossary cuối file.
>
> **Mục tiêu sau khi đọc xong**: Bạn có thể (1) trả lời "team đang làm cái gì" với khách hàng/đồng nghiệp, (2) biết "dữ liệu của team nằm ở đâu" nếu cần demo, (3) hiểu vì sao có 13 loại tấn công khác nhau và mỗi loại nguy hiểm thế nào.
>
> **Không cần đọc xong toàn file trong 1 lần.** Đọc 4 mục đầu trước (mục 1-4) là đủ để giới thiệu sản phẩm. Mục 5-7 đọc khi rảnh.

> **Cập nhật**: 2026-05-04

---

## Mục lục

1. [SQL Injection là gì? (giải thích bằng câu chuyện)](#1-sql-injection-là-gì)
2. [Vì sao team cần một dataset SQL Injection?](#2-vì-sao-team-cần-dataset-sqli)
3. [Data Engineering là gì? (giải thích bằng nhà bếp)](#3-data-engineering-là-gì)
4. [Pipeline của dự án — 5 bước kể chuyện](#4-pipeline-của-dự-án)
5. [13 loại tấn công SQL Injection — giải thích đời thường](#5-13-loại-tấn-công)
6. [Bản đồ thư mục — file gì nằm đâu](#6-bản-đồ-thư-mục)
7. [Glossary — từ điển từ chuyên môn](#7-glossary)

---

## 1. SQL Injection là gì?

### Câu chuyện đầu tiên

Hình dung một **quán nước trà sữa**. Bên ngoài có ô cửa sổ, khách viết tên đồ uống vào tờ giấy rồi đẩy vào trong cho nhân viên pha. Quy trình bình thường:

> Khách viết: `"trà sữa trân châu"` → Nhân viên pha → Trao cho khách.

Bây giờ có một khách lừa đảo. Anh ta viết:

> `"trà sữa trân châu, và mở luôn két tiền cho tôi xem có gì"`

Nếu nhân viên không tỉnh táo, anh ta sẽ pha trà sữa **VÀ** mở két tiền. Hai hành động riêng biệt, nhưng vì khách viết liền vào 1 tờ giấy, nhân viên hiểu nhầm thành 1 yêu cầu.

**SQL Injection** chính xác là điều đó, nhưng với website. Khách = kẻ tấn công. Tờ giấy = ô tìm kiếm/login trên web. Nhân viên = database. Két tiền = dữ liệu nhạy cảm (mật khẩu, thông tin khách hàng, sổ sách).

### Ví dụ kỹ thuật (chỉ để bạn nhận diện)

Trên một website có ô đăng nhập:
- Username: `admin`
- Password: `12345`

Bình thường: website hỏi database "có tài khoản admin với mật khẩu 12345 không?". Database trả lời "có" hoặc "không".

Với SQL Injection, kẻ tấn công gõ:
- Username: `admin' OR '1'='1`
- Password: bất kỳ

Câu hỏi gửi đến database biến thành: "có tài khoản admin **HOẶC** điều kiện 1=1 đúng không?". Vì 1=1 luôn đúng, database luôn trả "có" → kẻ tấn công vào được tài khoản admin mà **không cần biết mật khẩu**.

### Vì sao nguy hiểm?

- Mất dữ liệu khách hàng (gây kiện cáo, mất uy tín).
- Mất tiền (chuyển khoản trái phép).
- Mất kiểm soát hệ thống.
- Theo OWASP, SQL Injection nằm trong top 10 lỗ hổng web nguy hiểm nhất suốt 20 năm qua.

---

## 2. Vì sao team cần dataset SQLi?

Team đang làm dự án **AI sinh ra SQL Injection**. Nghe lạ — sao lại tạo ra cái nguy hiểm?

### Hai lý do (giải thích đơn giản)

**Lý do 1 — Để dạy AI phòng thủ giỏi hơn.**
Hình dung trong môn võ thuật. Để dạy võ sĩ phòng thủ, cần có võ sĩ tấn công đa dạng. Nếu chỉ có 100 đòn tấn công đã biết, võ sĩ phòng thủ chỉ giỏi đỡ 100 đòn đó. Khi gặp đòn mới, anh ta thua.

→ Team xây AI **sinh ra hàng nghìn đòn tấn công SQLi mới chưa từng có**. Đem những "đòn tấn công ảo" đó cho hệ thống phòng thủ luyện tập. Phòng thủ luyện được càng đa dạng → bảo vệ website thật càng tốt.

**Lý do 2 — Để kiểm tra chất lượng "tường lửa" (WAF).**
Mỗi website có một **bức tường** chặn các yêu cầu nguy hiểm (gọi là Web Application Firewall — WAF). Tường này có thể tốt hay tệ. Để biết tường có tốt không, cần liên tục thử "ném" payload mới vào. Nếu tường chặn được hết → tường tốt. Tường lọt nhiều → cần vá.

→ AI của team sinh ra payload "khó", dùng để **chấm điểm tường lửa của khách hàng** một cách khoa học.

### Vậy "dataset" để làm gì?

AI muốn "sinh" ra payload mới thì trước tiên phải **học từ payload thật**. Giống như trẻ con học vẽ, phải có nhiều tranh mẫu để xem. Dataset = bộ sưu tập 41,460 mẫu SQL Injection thật từ 5 nguồn khác nhau, mỗi mẫu được dán nhãn ("loại tấn công gì, dùng cho database loại nào, mức độ tinh vi").

Khi AI đã học xong, nó sẽ tự sinh ra payload mới — tương tự cách trẻ học nhiều tranh con vật, sau biết tự vẽ con vật mới chưa từng thấy.

---

## 3. Data Engineering là gì?

### Câu chuyện nhà bếp

Hình dung bạn mở **nhà hàng phở**. Có 3 vai trò:

- **Đầu bếp** = AI model (người nấu phở)
- **Người đi chợ + sơ chế** = **Data Engineer** (người chuẩn bị nguyên liệu)
- **Khách hàng** = User cuối (người ăn phở)

Đầu bếp giỏi đến mấy mà nguyên liệu bẩn, thịt ôi, rau úa thì phở vẫn dở. **Data Engineer** = người đảm bảo nguyên liệu đến tay đầu bếp luôn sạch, đủ, đúng loại.

### Công việc cụ thể của Data Engineer

1. **Đi chợ** (data collection): biết mua thịt ở chợ A (rẻ), rau ở chợ B (tươi), gia vị ở chợ C (gốc).
2. **Rửa** (cleaning): rau có sạn, thịt có lông, phải rửa.
3. **Cắt** (transformation): thịt cắt mỏng, rau xé nhỏ.
4. **Phân loại** (classification): thịt bò vào hộp 1, thịt gà vào hộp 2, không lẫn lộn.
5. **Loại trùng** (deduplication): nếu có 5 bó hành giống nhau bị nhân đôi do sai sót → bỏ 4, giữ 1.
6. **Đóng gói** (storage): cho vào tủ lạnh đúng nhiệt độ, dán nhãn ngày, dễ tìm.

Trong dự án này, "nguyên liệu" là **payload SQL Injection**, "đầu bếp" là **AI GAN**.

### Vai trò của bạn (member mới) trong nhà bếp này?

Bạn là **người giới thiệu phở cho khách**. Không cần biết nấu, nhưng cần biết:
- Phở của nhà hàng có gì đặc biệt? (= dataset có 41,460 mẫu, 13 loại, từ 5 nguồn — to và đa dạng).
- Nguyên liệu sạch sao? (= dữ liệu đã được lọc, đánh nhãn, kiểm chứng).
- So với hàng xóm thế nào? (= so với dataset public khác, dataset của team có thêm nhãn "loại tấn công" và "DB engine" mà ít nơi có).

---

## 4. Pipeline của dự án — 5 bước kể chuyện

> *Pipeline = "dây chuyền sản xuất". Như nhà máy, nguyên liệu đi qua các trạm, mỗi trạm xử lý 1 chuyện.*

### Bước 1 — Đi chợ (lấy data từ 5 nguồn)

Team đi 5 "chợ" khác nhau để gom mẫu SQLi:

| Chợ (nguồn) | Đặc điểm |
|---|---|
| **SQLiV5 Dataset** | Chợ lớn nhất, ~162,000 mẫu, công khai trên GitHub |
| **sqlmap payloads** | Của một công cụ pentest nổi tiếng, mẫu chuyên nghiệp ~2,000 |
| **SecLists** | Danh sách "fuzzing" cho hacker, chuyên sâu theo từng database, ~594 mẫu |
| **ExploitDB** | Bảo tàng các lỗ hổng đã được công bố (CVE), 8,696 vụ |
| **BCCC-SFU 2023** | Dataset học thuật từ Đại học Simon Fraser (Canada), 11,011 mẫu |

Tổng: gần **195,000 mẫu thô**.

### Bước 2 — Rửa rau (normalization)

Mẫu đến từ chợ thường "bẩn":
- Có mẫu viết hoa, có mẫu viết thường (`UNION` vs `union`).
- Có mẫu dùng mã URL (`%27` thay cho dấu nháy).
- Có mẫu thừa khoảng trắng dư thừa (`UNION    SELECT`).

→ "Rửa" = đưa tất cả về **một dạng chuẩn**. Sau khi rửa, `UNION SELECT`, `union select`, `%55nion%20select` đều thành cùng một dạng. Lý do: nếu không, AI nghĩ chúng là 3 thứ khác nhau.

### Bước 3 — Cắt nhỏ (de-lexicalization)

Trong các mẫu có những "tên cụ thể" — tên bảng, tên cột, số ID, chuỗi cụ thể. Ví dụ:
- `SELECT * FROM users WHERE id = 42`
- `SELECT * FROM products WHERE name = 'apple'`

Hai câu trên có **cùng cấu trúc** nhưng khác tên. Để AI học cấu trúc chứ không phải học từng tên, ta thay bằng nhãn chung:
- `SELECT * FROM <BẢNG> WHERE <CỘT> = <SỐ>`
- `SELECT * FROM <BẢNG> WHERE <CỘT> = <CHUỖI>`

Sau bước này, AI sẽ hiểu "cấu trúc tấn công" thay vì memorize tên bảng "users" hay "products".

### Bước 4 — Loại trùng (deduplication)

Trong 195,000 mẫu thô có rất nhiều mẫu **giống hệt nhau** (do 5 nguồn cùng có 1 payload phổ biến) hoặc **gần giống** (chỉ khác đúng 1 số). 

Loại trùng có 3 cấp:
- **Cấp 1** — giống y hệt → bỏ luôn.
- **Cấp 2** — giống cấu trúc, khác tên cụ thể → bỏ.
- **Cấp 3** — giống ~85% → bỏ.

Sau lọc trùng: còn **41,460 mẫu** — đây là con số "sạch" cuối cùng.

### Bước 5 — Phân loại (classification — AI dán nhãn)

41,460 mẫu sạch nhưng chưa biết "đây là loại tấn công gì". Team dùng **AI** (GPT-4o-mini) để dán nhãn từng mẫu:
- `sqli_type`: 1 trong 13 loại (xem mục 5).
- `db_engine`: nhắm vào loại database nào (MySQL, Oracle, PostgreSQL...).
- `confidence`: AI tự tin bao nhiêu (từ 0 đến 1).
- `reasoning`: AI giải thích vì sao gán nhãn đó.

Vì 41,460 mẫu là số lớn, AI không gọi 1 lần được — phải chia thành **1,382 batch (mỗi batch 30 mẫu)** rồi gọi liên tục. Tổng có 1,382 file kết quả.

**Quan trọng**: bạn (researcher) đã **review tay** những mẫu AI không tự tin (confidence 0.6-0.85) để chắc chắn nhãn đúng. Mẫu < 0.6 thì gán "unknown" (chưa biết).

---

## 5. 13 loại tấn công SQLi (giải thích đời thường)

Mỗi loại = một "kiểu lừa" khác nhau. Hình dung như 13 chiêu thức kiếm pháp.

| # | Loại | Giải thích đời thường |
|---|---|---|
| 1 | **union_based** | "Ghép câu hỏi" — kẻ tấn công ghép câu hỏi của mình vào câu hỏi của website, hỏi cùng lúc. Như viết thêm 1 dòng vào tờ giấy đặt hàng để lén đặt thêm món. |
| 2 | **error_based** | "Cố ý gây lỗi để đọc bí mật" — như cố ý làm rơi cốc để nhân viên la lên "cốc đắt 500k", từ đó biết giá. Kẻ tấn công cố ý hỏi sai để website báo lỗi, trong lỗi có thông tin nội bộ. |
| 3 | **boolean_blind** | "Hỏi yes/no kiểu mò" — như chơi 20 câu hỏi: "có phải con vật?", "có phải động vật có vú?". Kẻ tấn công hỏi từng bit dữ liệu, "đúng/sai", từ đó dò ra mật khẩu/data. Chậm nhưng chắc. |
| 4 | **time_blind** | "Hỏi yes/no qua thời gian chờ" — kẻ tấn công nói: "nếu chữ đầu của mật khẩu là 'A', bạn ngủ 5 giây rồi trả lời". Nếu phản hồi sau 5 giây → đúng là 'A'. Nếu trả lời ngay → là chữ khác. Mò chậm hơn nữa nhưng vô hình. |
| 5 | **heavy_query** | "Câu hỏi nặng làm server đứng" — như đặt 1 đơn hàng yêu cầu nhân viên đếm từng hạt gạo trong kho. Server bận đếm → các khách khác phải chờ → DoS gián tiếp. |
| 6 | **stacked_queries** | "Đặt nhiều việc cùng lúc" — như viết "pha trà sữa; mở két tiền; xóa camera". Database thực hiện cả 3 lệnh nếu cấu hình lỏng. Cực nguy hiểm. |
| 7 | **lateral** | "Tấn công qua bảng kế bên" — qua một bảng phụ (vd JOIN) để chui vào bảng chính. Như vào nhà bằng cửa sau qua nhà hàng xóm. |
| 8 | **second_order** | "Bom hẹn giờ" — kẻ tấn công gửi 1 mẫu vào hệ thống, không nguy hiểm ngay. Sau đó lúc admin xem báo cáo, mẫu đó kích hoạt. Lừa kiểu trễ. |
| 9 | **auth_bypass** | "Vượt cổng đăng nhập" — chiêu kinh điển `' OR '1'='1` — đăng nhập admin mà không cần mật khẩu. |
| 10 | **out_of_band** | "Gửi tin ra ngoài" — kẻ tấn công bắt database "gọi điện" đến server của hắn (qua DNS/HTTP) kèm dữ liệu. Server hắn bắt được → đọc được dữ liệu. |
| 11 | **rce** | "Chiếm máy chủ" — Remote Code Execution — không chỉ đọc data mà còn chạy lệnh hệ điều hành. Đỉnh nguy hiểm. |
| 12 | **polyglot** | "Đa năng" — payload vừa là SQL Injection vừa là XSS vừa là LDAP injection. Đánh nhiều mặt cùng lúc. Hiếm. |
| 13 | **unknown** | "Chưa phân loại" — AI không đủ tự tin, chờ pass sau hoặc người expert review. |

### Phân phối (con số nhớ)

- **76%** corpus là `unknown` — ai mới đọc tưởng "tệ" nhưng thực ra do nguồn data thô có nhiều mẫu khó phân loại tự động. AI đã làm tối đa, phần còn lại cần expert.
- Top 4 loại có nhãn rõ: `union_based` (6.8%), `boolean_blind` (5.9%), `error_based` (4.3%), `time_blind` (4.1%).
- Loại hiếm: `rce`, `polyglot`, `out_of_band` mỗi loại < 0.1% — quý hiếm, mỗi mẫu phải giữ kỹ.

---

## 6. Bản đồ thư mục

> *Khi cần demo cho khách hoặc tự tìm hiểu, bạn có thể mở các thư mục sau bằng File Explorer.*

```
C:\Users\Admin\Documents\GAN\
│
├── Asset\
│   ├── Guiding\               ← TÀI LIỆU (bạn đang đọc 1 file ở đây)
│   │   ├── Onboarding_Data_Engineering.md       ← FILE NÀY (cho người mới)
│   │   ├── Data_Engineering_Recap.md            ← Bản kỹ thuật cho researcher
│   │   ├── Data_Engineering_Foundation.md       ← Bản nền tảng cho team
│   │   ├── Onboarding_AI_Knowledge_*.md         ← 4 file giáo dục AI cho người mới
│   │   ├── AI_Foundations_For_Team_*.md         ← 4 file giáo dục AI cho team
│   │   └── SQLi-{VAE-GAN, SeqGAN, Gumbel}-Roadmap.md   ← Lộ trình kỹ thuật từng hướng AI
│   │
│   ├── Data\                  ← DỮ LIỆU
│   │   ├── batches\           ← 1,382 file input đầu vào AI dán nhãn
│   │   ├── results\           ← 1,382 file output sau khi AI đã dán nhãn
│   │   ├── sqliv5_dataset\    ← Nguồn 1
│   │   ├── sqlmap_payloads\   ← Nguồn 2
│   │   ├── seclists_sqli\     ← Nguồn 3
│   │   ├── exploitdb_sqli\    ← Nguồn 4
│   │   └── BCCC-SFU-...csv    ← Nguồn 5
│   │
│   └── Opencode\              ← MÃ NGUỒN TỰ ĐỘNG ĐÁNH NHÃN
│       ├── classify*.py       ← Script gọi AI dán nhãn
│       ├── KE_HOACH.md        ← Kế hoạch chi tiết workflow
│       └── progress.json      ← Trạng thái: 1382/1382 đã xong ✅
│
├── data_engine\               ← MÃ NGUỒN PIPELINE CHÍNH
│   ├── normalizer.py          ← Bước "rửa rau"
│   ├── deduplicator.py        ← Bước "loại trùng"
│   ├── classifier.py          ← Bước "phân loại bằng quy tắc"
│   └── ...
│
├── VAE-GAN_SQLi\              ← THƯ MỤC ĐỂ CHỨA AI HƯỚNG 1 (đang trống)
├── SeqGAN_SQLi\               ← THƯ MỤC ĐỂ CHỨA AI HƯỚNG 2 (đang trống)
└── Gumbel-Softmax_SQLi\       ← THƯ MỤC ĐỂ CHỨA AI HƯỚNG 3 (đang trống)
```

### Khi giới thiệu cho khách, bạn có thể nói

> *"Team chúng tôi có 41,460 mẫu SQL Injection chất lượng cao, được tổ chức trong thư mục `Asset/Data/`. Mỗi mẫu được AI dán nhãn vào 1 trong 13 loại tấn công, với độ tin cậy có thể audit được qua trường `reasoning`. Ngoài ra, có 3 hướng AI khác nhau (VAE-GAN, SeqGAN, Gumbel-Softmax) đang được chuẩn bị triển khai trong `VAE-GAN_SQLi/`, `SeqGAN_SQLi/`, `Gumbel-Softmax_SQLi/` — mỗi hướng có trade-off riêng phù hợp với use case khác nhau."*

---

## 7. Glossary — Từ điển từ chuyên môn

> *Tra từ này khi gặp trong file khác hoặc trong cuộc họp.*

| Từ | Nghĩa đơn giản |
|---|---|
| **AI / Model** | Chương trình máy tính tự học từ dữ liệu — không cần lập trình quy tắc thủ công. |
| **Annotation / Label** | Nhãn gán cho 1 mẫu dữ liệu, vd "đây là `union_based`". |
| **Batch** | Nhóm nhỏ dữ liệu xử lý cùng lúc (ở đây 30 mẫu/batch). |
| **Benign SQL** | SQL hợp pháp, không phải tấn công (vd query bình thường của ứng dụng). |
| **Confidence** | Độ tự tin của AI khi gán nhãn, từ 0 (không chắc) đến 1 (rất chắc). |
| **Corpus** | Bộ sưu tập dữ liệu lớn — đồng nghĩa "dataset". |
| **CSV** | Định dạng file bảng đơn giản, mỗi dòng 1 hàng, các cột phân cách bằng dấu phẩy. Mở được bằng Excel. |
| **Database / DB** | Hệ thống lưu trữ dữ liệu của website (vd MySQL, PostgreSQL). |
| **Dataset** | Bộ dữ liệu — nhiều mẫu đi cùng nhau. |
| **DB Engine** | Loại database cụ thể (MySQL, Oracle, PostgreSQL, MSSQL, SQLite, NoSQL). |
| **De-lexicalization** | Bước thay tên cụ thể bằng nhãn chung (xem mục 4 bước 3). |
| **Deduplication / Dedup** | Loại bỏ các mẫu trùng lặp. |
| **Discriminator (D)** | Phần của GAN — "thẩm phán" phân biệt thật/giả. |
| **Embedding** | Cách biến token text thành vector số để AI xử lý. |
| **Evasion** | Kỹ thuật ngụy trang để tránh bị tường lửa phát hiện. |
| **Exploit** | Việc khai thác lỗ hổng. |
| **GAN** | Generative Adversarial Network — kiểu AI gồm 2 phần (G và D) đối kháng nhau để học sinh dữ liệu thật. |
| **Generator (G)** | Phần của GAN — "thợ giả mạo" sinh ra dữ liệu mới. |
| **Gumbel-Softmax** | Một kỹ thuật toán học giúp AI sinh chuỗi rời rạc (như SQL). Đây là 1 trong 3 hướng AI của dự án. |
| **Label / Nhãn** | Đồng nghĩa "annotation". |
| **Master_unlabeled.csv** | File chính chứa 41,460 mẫu input. |
| **ModSecurity** | Một tường lửa web (WAF) phổ biến, mã nguồn mở. |
| **Normalization / Chuẩn hóa** | Đưa các biến thể bề mặt về 1 dạng chuẩn (xem mục 4 bước 2). |
| **OWASP** | Tổ chức bảo mật web nổi tiếng — duy trì danh sách top 10 lỗ hổng nguy hiểm. |
| **Pa load** | Đoạn dữ liệu kẻ tấn công gửi đi (= "đạn"). Trong dự án này, mỗi payload = 1 chuỗi SQLi cụ thể. |
| **Pipeline** | Dây chuyền xử lý dữ liệu — nhiều bước nối tiếp. |
| **PostgreSQL / MySQL / Oracle / MSSQL / SQLite** | Các loại database phổ biến. |
| **Preprocessing** | Tiền xử lý dữ liệu — chính là data engineering. |
| **Result_batch_*.csv** | File kết quả AI dán nhãn. |
| **Schema** | Cấu trúc bảng dữ liệu — cột nào, kiểu gì. |
| **SeqGAN** | Một biến thể GAN dùng học tăng cường (RL). 1 trong 3 hướng AI của dự án. |
| **SQL** | Ngôn ngữ truy vấn database. |
| **SQL Injection / SQLi** | Loại tấn công web nhắm vào database (xem mục 1). |
| **Test set** | Phần dataset giữ riêng để đánh giá cuối cùng — không cho model thấy lúc train. |
| **Token** | Đơn vị nhỏ nhất của text sau khi cắt — vd `UNION`, `SELECT`, `--`. |
| **Tokenization** | Bước cắt chuỗi text thành tokens. |
| **Train set** | Phần dataset cho AI học. |
| **VAE / VAE-GAN** | Variational Autoencoder — kiến trúc AI có "không gian ẩn". 1 trong 3 hướng của dự án. |
| **Validation / Val set** | Phần dataset để chỉnh tinh hyperparameter. |
| **Vocabulary / Vocab** | Tập tất cả các token có thể có. |
| **WAF** | Web Application Firewall — tường lửa web — chương trình chặn các yêu cầu nguy hiểm. |

---

## 8. Câu hỏi thường gặp (FAQ)

**Q: Em có cần biết code không?**
A: Không. Bạn cần biết "team đang làm gì" và "dữ liệu/sản phẩm trông thế nào". Nếu cần biết sâu hơn, đọc 4 file `Onboarding_AI_Knowledge_*.md` (giải thích AI bằng analogy đời thường).

**Q: Dataset của team có cạnh tranh được với dataset public không?**
A: Có 2 điểm mạnh: (1) đã được dán nhãn 13 loại + DB engine + confidence (ít dataset public có) — sẵn sàng dùng cho conditional generation. (2) Đã được lọc trùng 3 cấp, chất lượng cao — không như nhiều dataset public còn duplicate.

**Q: Pipeline đã chạy xong chưa?**
A: 100% xong. File `Asset/Opencode/progress.json` cho thấy 1382/1382 batches đã được xử lý. Bước tiếp theo là gộp 1,382 file kết quả thành 1 file lớn `master_sqli.csv`.

**Q: Có phải toàn bộ payload đều "nguy hiểm" không?**
A: Có và không. Đứng riêng, mỗi payload là 1 chuỗi text vô hại. Chỉ khi gửi vào website không vá lỗi, payload mới gây hại. Team không tấn công ai — chỉ thử nghiệm với hệ thống được phép (như tường lửa của khách hàng đã ký hợp đồng pentest, hoặc môi trường sandbox).

**Q: Em có thể demo dataset không?**
A: Có thể. Mở Excel, kéo thả file `Asset/Data/results/result_batch_0001.csv` vào → thấy 30 dòng × 5 cột. Mỗi dòng 1 mẫu với loại + DB + confidence + reasoning. Đây là "demo nhanh" cho khách thấy chất lượng nhãn.

**Q: Khi nào team xong dự án?**
A: Hiện tại pha **data engineering** xong. Pha tiếp theo là **AI training** trên 3 hướng (VAE-GAN, SeqGAN, Gumbel-Softmax). Mỗi hướng cần ~1-3 tháng nghiên cứu+training+evaluation. Sau đó là **paper writing** và **đóng gói API**.

---

## 9. Liên kết tới các file khác

Khi đọc xong file này, gợi ý đọc tiếp theo thứ tự độ khó tăng dần:

1. **`Onboarding_AI_Knowledge_01_Neural_Net_And_Training.md`** — AI cơ bản nhất (mạng neural là gì) — giải thích bằng analogy.
2. **`Onboarding_AI_Knowledge_02-04_*`** — các loại model phức tạp hơn (CNN, RNN, Transformer, GAN, VAE) — vẫn analogy đời thường.
3. **`Data_Engineering_Foundation.md`** — concepts data engineering có thêm tầng toán học (đọc nếu muốn lên level junior data engineer).
4. **`Data_Engineering_Recap.md`** — bản kỹ thuật cho researcher (đọc nếu rảnh và muốn challenge).
5. **`SQLi-{VAE-GAN,SeqGAN,Gumbel-SoftmaxGAN}-Roadmap.md`** — chi tiết kỹ thuật từng hướng AI (chỉ đọc khi đã quen).

> **Lời khuyên**: Đừng cố hiểu hết trong 1 ngày. Mỗi tuần đọc 1 file, hỏi team khi gặp đoạn khó. Sau 1-2 tháng bạn sẽ tự tin giới thiệu sản phẩm như 1 thành viên kỹ thuật thực thụ.
