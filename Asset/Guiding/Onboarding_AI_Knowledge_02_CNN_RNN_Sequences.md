# Onboarding AI — Bài 02: CNN, RNN, LSTM, GRU

> **Đối tượng**: Member mới không-tech, đã đọc bài 01. File này dạy 2 họ kiến trúc đặc biệt: **CNN** (cho dữ liệu có cấu trúc không gian, vd ảnh) và **RNN family** (cho chuỗi text/audio).
>
> **Phong cách**: dày tầng kid + practical, không công thức toán phức tạp. Bản chi tiết hơn: `AI_Foundations_For_Team_02_CNN_RNN_Sequences.md`.

> **Cập nhật**: 2026-05-04
> **Concepts**: CNN, kernels, dilated CNN, RNN, vanishing gradient, LSTM, GRU.

---

## 1. CNN — Convolutional Neural Network

### Câu chuyện

Bạn được đưa cho **kính lúp 3×3 ô**. Đặt lên ảnh, **trượt từ trái sang phải, từ trên xuống dưới**. Mỗi vị trí, kính lúp "nhìn" 1 vùng nhỏ:
- Vùng có **đường thẳng đứng**? → đánh dấu.
- Vùng có **góc nhọn**? → đánh dấu.
- Vùng có **đường cong**? → đánh dấu.

Kính lúp cho ra **bản đồ đánh dấu** (= feature map) — chỉ ra mỗi vị trí có "loại đường" gì.

**Cùng 1 kính lúp dùng khắp ảnh** → khuôn mặt nằm góc nào cũng được phát hiện. Đó là tính chất "translation-invariant" — quan trọng cho ảnh.

### Trong AI

- **CNN = neural network dùng kính lúp** (gọi là **kernel** hoặc **filter**).
- Mỗi kernel học detect 1 đặc trưng cụ thể.
- Stack nhiều layer → đặc trưng từ đơn giản (cạnh, góc) → phức tạp (mắt, tai, mặt).

### Vì sao mạnh hơn MLP cho ảnh?

- **MLP** xử lý từng pixel độc lập, không tận dụng "pixel kề nhau quan trọng".
- **CNN** chỉ xử lý vùng nhỏ, share cùng kernel khắp ảnh → ít tham số, hiệu quả hơn.

### Khi nào dùng?

| Loại dữ liệu | Dùng CNN không? |
|---|---|
| Ảnh | ✅ Mặc định |
| Audio (waveform) | ✅ 1D CNN |
| Text classification | ✅ TextCNN (1D) |
| Time series | ✅ Đôi khi |
| Tabular | ❌ MLP/Tree |

### Trong dự án

**Discriminator** của 3 approach đều dùng CNN:
- VAE-GAN, SeqGAN: TextCNN với kernel sizes [3, 4, 5] — bắt n-gram patterns.
- Gumbel-Softmax: Dilated CNN với kernel sizes [2, 3, 5, 8, 12, 16] — bắt patterns ở nhiều scales.

→ Discriminator có nhiệm vụ "phân biệt SQL thật vs SQL giả do Generator sinh ra". CNN giỏi nhận diện pattern → phù hợp.

### Ví dụ trông như thế nào?

Một câu SQLi: `SELECT * FROM users WHERE id = 1 OR 1=1`

- Sau tokenize: `[SELECT, *, FROM, users, WHERE, id, =, 1, OR, 1, =, 1]` (12 tokens).
- TextCNN với kernel size 3:
  - Nhìn `[SELECT, *, FROM]`, đánh giá "có pattern nguy hiểm?".
  - Trượt: `[*, FROM, users]`, đánh giá tiếp.
  - ... tổng 10 vị trí.
- TextCNN với kernel size 4, 5: tương tự nhưng nhìn 4-5 token cùng lúc.
- Tổng hợp tất cả → 1 con số "thật/giả".

---

## 2. Kernel & Stride & Padding & Pooling — Các thành phần CNN

### Kernel (Filter)

**Kính lúp** chính là kernel. Có thể có nhiều "kính lúp" khác nhau cùng lúc — vd 64 kính lúp khác nhau, mỗi cái detect 1 pattern.

### Stride

**Bước trượt** của kính lúp.
- Stride = 1: trượt từng pixel (kỹ).
- Stride = 2: nhảy 2 pixel (nhanh, nhưng có thể bỏ sót).

### Padding

**Đóng khung trắng** quanh ảnh trước khi áp kính lúp. Lý do: giữ kích thước output bằng input. Không pad → mỗi layer mất 1-2 pixel ở biên.

### Pooling

**Thu nhỏ** feature map. Vd: mỗi vùng 2×2, lấy giá trị **lớn nhất** (max pooling). Giúp:
- Giảm kích thước → nhanh hơn.
- Tăng "tầm nhìn" của neuron sau (tăng receptive field).

---

## 3. Dilated CNN — Kính lúp có lỗ

### Câu chuyện

Kính lúp 3 ô bình thường: ▮▮▮ — nhìn 3 pixel **kề nhau**.

**Dilated rate = 2**: kính lúp có **lỗ ở giữa** → ▮_▮_▮ — nhìn 3 pixel **cách 1 pixel**. Cùng số ô (3) nhưng phủ vùng to hơn (5 pixel).

**Dilated rate = 4**: ▮___▮___▮ — phủ 9 pixel.

### Vì sao hữu ích?

Cần "tầm nhìn" rộng (vd nhìn được toàn bộ câu dài 100 token) mà **không tăng số tham số**:
- CNN bình thường: phải stack 50 layer.
- Dilated CNN: stack 7-8 layer là đủ.

### Trong dự án — Gumbel-Softmax

SQL có cấu trúc phân tầng:
- Toán tử kép (`UNION SELECT`): cần kernel **nhỏ, chật** (size 2-3).
- Mệnh đề đơn (`WHERE id = <NUM>`): cần kernel **vừa** (size 5-8).
- Subquery lồng (`SELECT ... FROM (SELECT ...)`): cần kernel **rộng** (size 12-16).

Dilated CNN cho phép có cả 6 kernels này song song mà vẫn hiệu quả.

---

## 4. RNN — Recurrent Neural Network

### Câu chuyện

Đọc cuốn truyện. Mỗi trang đọc, bạn **nhớ** nội dung trang trước. Khi đến trang 100, hiểu chi tiết trang 100 vì nhớ 99 trang trước.

**RNN** làm điều tương tự với chuỗi text:
- Đọc token 1 → cập nhật "trí nhớ" $h_1$.
- Đọc token 2 → kết hợp token 2 với $h_1$ → cập nhật $h_2$.
- ...
- Đến token cuối → $h_T$ chứa "tổng hợp toàn bộ chuỗi".

### Vấn đề lớn của RNN

**Vanishing gradient** — trí nhớ dần "phai" qua thời gian.

Hình dung dây chuyền 100 người nhắn tin tai-mép. Mỗi lần truyền **mất 10% âm thanh**. Đến người 100, tin nhắn còn $0.9^{100} \approx 0$ → không nghe gì.

→ RNN bình thường **không học được dependency dài** (>20-50 tokens). Đó là lý do LSTM được phát minh.

### Khi nào dùng RNN?

- Hiện tại RNN bình thường ít dùng — thay bằng LSTM/GRU/Transformer.
- Vẫn dùng khi: low-resource device, real-time streaming, very small models.

---

## 5. LSTM — Long Short-Term Memory

### Câu chuyện

Cải tiến của RNN. Mỗi "người" trong dây chuyền có thêm **cuốn sổ nhỏ** (gọi là **cell state**). Họ có 3 quyền:

1. **Forget gate**: quyết định **xóa mục nào** trong sổ (không quan trọng nữa).
2. **Input gate**: quyết định **viết thêm thông tin gì** vào sổ.
3. **Output gate**: quyết định **đọc mục nào** ra ngoài cho người tiếp theo.

Nhờ cuốn sổ này, **thông tin quan trọng được giữ nguyên qua nhiều bước** → vanishing gradient ít xảy ra.

### Vì sao gọi là "Long Short-Term Memory"?

- **Short-term** = hidden state $h$ thay đổi nhanh.
- **Long-term** = cell state $c$ giữ thông tin lâu dài.

### Khi nào dùng LSTM?

- Trước 2017: dominant cho NLP.
- Sau 2017: bị Transformer thay thế cho hầu hết task lớn.
- Vẫn dùng cho: small/medium task, streaming, low-resource.

### Trong dự án

**SeqGAN Generator** có thể dùng LSTM hoặc Transformer Decoder. LSTM được khuyến nghị cho task này:
> "Kiến trúc: **LSTM** (phù hợp với sequence dài, tránh vanishing gradient) hoặc Transformer Decoder."

LSTM 3 layers, hidden 512 là config phổ biến.

---

## 6. GRU — Gated Recurrent Unit

### Câu chuyện

Phiên bản **gọn nhẹ** của LSTM. **Bỏ cuốn sổ riêng**, chỉ giữ 1 hidden state. **2 gate** thay 3:

1. **Reset gate**: nên **quên bao nhiêu** thông tin cũ.
2. **Update gate**: nên **đè thông tin mới** lên cũ bao nhiêu.

Đơn giản, nhanh hơn LSTM ~30%, hiệu quả gần tương đương trong nhiều task.

### LSTM vs GRU?

- **LSTM** mạnh hơn cho rất long sequence (> 200 tokens).
- **GRU** đủ cho hầu hết task, nhanh hơn.
- **Khuyến nghị**: thử GRU trước, không đủ thì lên LSTM.

### Trong dự án

SeqGAN có thể dùng GRU thay LSTM nếu muốn train nhanh hơn — quyết định lúc implement, dựa trên benchmark.

---

## 7. So sánh CNN vs RNN family

| Tiêu chí | CNN | RNN/LSTM/GRU |
|---|---|---|
| Ý tưởng chính | Kính lúp trượt | Bộ nhớ tuần tự |
| Phù hợp với | Ảnh, n-gram text | Sequence dài |
| Parallel? | ✅ Yes (nhanh) | ❌ No (sequential) |
| Long-range | Cần stack/dilated | LSTM/GRU OK |
| Tham số | Ít | Trung bình |

### Trong dự án (tóm tắt)

| Approach | Dùng cho Generator | Dùng cho Discriminator |
|---|---|---|
| VAE-GAN | Transformer | TextCNN |
| SeqGAN | LSTM/Transformer | TextCNN |
| Gumbel-Softmax | Transformer | Dilated CNN |

→ **CNN** chiếm vị trí Discriminator (phân loại). **RNN/Transformer** cho Generator (sinh sequence).

---

## 8. Bạn đã hiểu gì?

- ✅ CNN: kính lúp trượt qua ảnh/text, share cùng filter.
- ✅ Stride, padding, pooling: thông số kỹ thuật của CNN.
- ✅ Dilated CNN: kính lúp có "lỗ" để có tầm nhìn rộng.
- ✅ RNN: bộ nhớ tuần tự nhưng bị vanishing gradient.
- ✅ LSTM: RNN có "cuốn sổ" giữ thông tin lâu dài.
- ✅ GRU: phiên bản đơn giản hơn LSTM, comparable.
- ✅ Khi nào dùng cái nào trong dự án này.

---

## 9. Đọc tiếp

Bài 03: `Onboarding_AI_Knowledge_03_Attention_And_Transformer.md` — học về **attention** (cách model "chú ý" có chọn lọc) và **Transformer** (kiến trúc thay thế RNN cho hầu hết task NLP hiện đại).
