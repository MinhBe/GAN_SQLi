# Onboarding AI — Bài 01: Mạng Nơ-ron và Cách Nó Học

> **Đối tượng**: Thành viên mới không có background code/AI/toán cao cấp. File này tập trung vào **tầng 1 (analogy đời thường)** và **tầng 4 (data trông như thế nào)**, **lược bớt toán hàn lâm**.
>
> **Khi nào đọc file này thay file Foundations?** Nếu công thức làm bạn nản, đọc file này. Khi đã quen, có thể đọc file `AI_Foundations_For_Team_01_Neural_Net_And_Training.md` cho sâu hơn.

> **Cập nhật**: 2026-05-04
> **Concepts trong bài**: Neural Network, MLP, Forward Pass, Weight & Bias, Loss Function, Gradient, Backpropagation, Learning Rate, Optimizer.

---

## Mục lục

1. [Neural Network — Mạng nơ-ron là gì?](#1-neural-network)
2. [MLP — Mạng nơ-ron nhiều tầng](#2-mlp)
3. [Forward Pass — "Chạy thử" model](#3-forward-pass)
4. [Weight & Bias — "Trí nhớ" của model](#4-weight--bias)
5. [Loss Function — "Chấm điểm" model](#5-loss-function)
6. [Gradient — "La bàn" để học](#6-gradient)
7. [Backpropagation — "Truy ngược" lỗi](#7-backpropagation)
8. [Learning Rate — Bước nhảy mỗi lần học](#8-learning-rate)
9. [Optimizer — Chiến lược học](#9-optimizer)

---

## 1. Neural Network

### Câu chuyện

Hình dung một **dây chuyền nhà máy** sản xuất kẹo. Nguyên liệu (đường, sữa, bột) đi vào đầu dây chuyền. Mỗi công nhân (= 1 nơ-ron) đứng ở 1 vị trí, làm 1 việc nhỏ:
- Công nhân 1: đong đường.
- Công nhân 2: trộn sữa.
- Công nhân 3: nướng nhẹ.
- ...
- Công nhân 50: đóng gói.

Sau 50 công nhân, ra được hộp kẹo hoàn chỉnh. **Mỗi công nhân riêng lẻ không "thông minh"** — chỉ làm 1 thao tác. Nhưng toàn dây chuyền cùng phối hợp → sản phẩm phức tạp.

**Neural Network** = dây chuyền đó, nhưng làm bằng phần mềm. Mỗi "công nhân" tính 1 phép toán nhỏ (cộng + nhân vài số). Nối hàng triệu "công nhân" lại → có thể nhận diện khuôn mặt, viết thơ, lái xe.

### Ví dụ cụ thể

**Bài toán**: phân biệt ảnh chó vs mèo.

- **Đầu vào**: ảnh = bảng số (mỗi pixel có giá trị 0-255).
- **Lớp 1** (ví dụ): các nơ-ron detect "có cạnh dọc?", "có cạnh ngang?", "có vệt cong?".
- **Lớp 2**: kết hợp → "có 2 mắt tròn?", "có tai nhọn?".
- **Lớp 3**: kết hợp → "có đặc điểm mặt mèo?", "có đặc điểm mặt chó?".
- **Đầu ra**: 2 con số: P(mèo)=0.85, P(chó)=0.15 → kết luận "mèo".

Mỗi lớp tự động học các "đặc điểm" — không cần con người dạy "mắt tròn = mèo". Đó là điểm thần kỳ của AI.

### Trong dự án này

3 hướng AI (VAE-GAN, SeqGAN, Gumbel-Softmax) đều là Neural Network — nhưng **input là chuỗi text SQL** thay vì ảnh, **output là chuỗi text SQL mới**. Network học được cấu trúc SQL Injection, sau đó tự sinh ra payload mới.

### Trông như thế nào trong code?

```python
# Một neural network siêu đơn giản (PyTorch)
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 256),  # Lớp 1: nhận 784 số (ảnh 28x28), output 256
    nn.ReLU(),            # "Bật/tắt" tín hiệu
    nn.Linear(256, 10)    # Lớp 2: output 10 (10 con số 0-9)
)
```

3 dòng code = 1 neural network có thể nhận diện chữ số viết tay với accuracy ~98%.

---

## 2. MLP — Multilayer Perceptron

### Câu chuyện

**MLP = "trường tiểu học có 5 lớp"**. Mỗi lớp 30 học sinh:
- Mỗi học sinh lớp 1 viết thư cho **mọi** học sinh lớp 2.
- Mỗi học sinh lớp 2 nhận 30 thư, đọc, tổng hợp, viết thư mới gửi mọi học sinh lớp 3.
- Cứ thế đến lớp 5.

Càng đi sâu, thông tin được lọc và tổng hợp. Lớp 5 đưa ra kết luận cuối.

### Đặc điểm

- **Fully connected**: mỗi nơ-ron nối với mọi nơ-ron lớp sau (như "viết thư cho mọi người").
- **Đơn giản nhất**: là dạng "vanilla" của NN, baseline cho mọi bài toán.
- **Hạn chế**: không tận dụng được cấu trúc đặc biệt (vd ảnh có pixel kề nhau quan trọng → cần CNN; text có thứ tự → cần RNN/Transformer).

### Khi nào dùng MLP?

- Khi đầu vào là **vector cố định** (vd thông tin khách hàng: 20 con số mô tả).
- Khi không có cấu trúc không gian/thời gian rõ ràng.
- Là một thành phần nhỏ trong network lớn (vd cuối CNN, FFN trong Transformer).

### Trong dự án

Discriminator của 3 approach **không phải MLP** (dùng CNN). Nhưng MLP xuất hiện trong: 
- "Output projection" cuối Generator (chuyển hidden state → vocab logits).
- Có thể làm baseline đơn giản để kiểm tra pipeline.

---

## 3. Forward Pass

### Câu chuyện

Quay lại nhà máy. **Forward pass** = đẩy nguyên liệu vào, chờ ra sản phẩm.
- Không sửa máy lúc này.
- Không sa thải công nhân.
- Chỉ chạy thuần.

Đây là cách model "trả lời câu hỏi" — đưa input vào, nhận output ra.

### Khi nào dùng?

- **Lúc train**: chạy forward để tính output, so với label thật → tính loss.
- **Lúc inference (deploy)**: chạy forward để predict.

### Ví dụ trong dự án

Lúc deploy AI sinh SQLi:
1. Bạn cho noise vector (random) vào Generator.
2. Forward pass qua Generator → ra chuỗi token SQLi.
3. Decode → payload string.

Toàn quá trình chỉ là 1 forward pass — vài mili-giây trên GPU.

### Trông như thế nào?

```python
output = model(input)   # 1 dòng, đó là forward pass
```

---

## 4. Weight & Bias

### Câu chuyện

Bạn đứng trước cửa hàng tiện lợi, quyết định **có mua bánh không**? Bạn cân nhắc 3 yếu tố:
- $x_1$ = "đói hay không?" (1/0).
- $x_2$ = "bánh có ngon không?" (1/0).
- $x_3$ = "có tiền hay không?" (1/0).

Mỗi yếu tố có **mức độ quan trọng** với bạn:
- $w_1 = 5$ (đói rất quan trọng).
- $w_2 = 2$ (ngon vừa thôi).
- $w_3 = 8$ (không có tiền là không mua dù gì).

Bạn cũng có **xu hướng cá nhân** $b$ — nếu cả 3 yếu tố trung tính, bạn nghiêng về "có mua" hay "không mua"? Nếu bạn là người tiết kiệm, $b = -3$ (xu hướng "không").

Quyết định: $w_1 x_1 + w_2 x_2 + w_3 x_3 + b > 0$ → mua.

**Weight ($w$)** = mức độ quan trọng. **Bias ($b$)** = xu hướng cố hữu.

### Trong neural network

- Mỗi kết nối giữa 2 nơ-ron có 1 weight.
- Mỗi nơ-ron có 1 bias.
- Mạng có hàng triệu weight + bias.
- **Train = điều chỉnh weight + bias** sao cho output gần label thật.

### Số tham số

- Mạng nhỏ: vài triệu params.
- BERT: 110 triệu.
- GPT-3: 175 tỷ.

Mỗi param là 1 số float (4 bytes). 1 model 100M params = 400MB checkpoint file.

### Trong dự án

3 approach ước lượng:
- VAE-GAN: ~10-50 triệu params.
- SeqGAN: ~5-20 triệu.
- Gumbel-Softmax: ~10-30 triệu.

Sau train, weight + bias được lưu thành file `.pt` trong `<Approach>_SQLi/checkpoints/` để load lại khi cần.

---

## 5. Loss Function

### Câu chuyện

Bạn ném phi tiêu vào bia. **Loss** = khoảng cách từ phi tiêu đến tâm bia.
- Loss = 0: trúng tâm. 
- Loss lớn: rơi ngoài bia.

Mục tiêu: **giảm loss** qua nhiều lần ném.

### Ý nghĩa

- Loss là **số đo lỗi** của model.
- Càng thấp = model càng giỏi.
- **Train = thay đổi weight để giảm loss**.

### Các loại loss phổ biến

| Bài toán | Loss | Ý nghĩa |
|---|---|---|
| Đoán giá nhà (số) | MSE (Mean Squared Error) | Bình phương khoảng cách dự đoán vs thật |
| Phân biệt mèo/chó | Binary Cross-Entropy | Đo độ tự tin sai lệch |
| Phân loại 10 chữ số | Cross-Entropy | Tương tự binary, nhưng nhiều class |
| GAN | Adversarial Loss | G và D cạnh tranh |

### Trong dự án

Mỗi approach có loss khác nhau:
- **VAE-GAN**: 4 loss kết hợp (recon + KL + adversarial + feature matching).
- **SeqGAN**: MLE pretrain + REINFORCE (policy gradient).
- **Gumbel-Softmax**: Wasserstein loss + Gradient Penalty.

Đừng lo nhớ — chỉ cần biết "loss = số đo độ sai".

---

## 6. Gradient

### Câu chuyện

Bạn đứng trên đồi, **bịt mắt**. Muốn đi xuống thung lũng (= giảm loss). Bạn không thấy toàn cảnh, nhưng cảm nhận dưới chân **dốc bên nào nhất** — đó là **gradient**.

- Gradient lớn: dốc đứng → biết đi đâu.
- Gradient = 0: đất phẳng → đã ở đáy hoặc lạc đỉnh.
- **Đi ngược chiều gradient** = đi xuống dốc = giảm loss.

### Ý nghĩa

- Gradient = "**hướng tăng nhanh nhất** của loss" theo từng weight.
- Để **giảm loss**, model dịch chuyển weight **ngược chiều gradient**.
- Lặp đi lặp lại → loss giảm dần → model học được.

### Vấn đề thường gặp

- **Vanishing gradient**: gradient nhỏ dần qua các lớp → không đi xuống được. Như tai-mép qua 100 người, mỗi lần mất 10% âm thanh → đến cuối còn 0.
- **Exploding gradient**: gradient phình quá → lệch lắc. Như kẻ say đi xuống dốc nhảy đại.

→ Cần kỹ thuật ổn định (ReLU, gradient clipping, LSTM thay RNN).

### Trong dự án

Khi train, mỗi step model tính gradient → cập nhật weight. Gradient được tính tự động bởi PyTorch (gọi là **autograd**). Bạn chỉ cần viết:
```python
loss.backward()        # Tính gradient tự động
optimizer.step()       # Cập nhật weight ngược chiều gradient
```

---

## 7. Backpropagation

### Câu chuyện

Đội bóng thua 1-0. **Không phải lỗi của tất cả** — có người đá đỉnh, có người đá tệ. HLV cần biết **ai sai bao nhiêu** để training cho đúng người.

**Backpropagation** = "truy ngược lỗi". HLV xuất phát từ kết quả ("thua 1-0") đi ngược:
- "Thủng lưới phút 89" → ai canh gôn? Thủ môn.
- "Sao thủ môn chậm?" → tại hậu vệ không tổ chức tốt.
- "Sao hậu vệ không tổ chức?" → tại tiền vệ không lùi sớm.
- ...

Cuối cùng mỗi cầu thủ nhận được "phần lỗi" tương ứng → biết cần luyện thêm phần nào.

### Ý nghĩa

Backprop = thuật toán tính gradient cho **mọi weight** trong network bằng cách áp dụng chain rule (đạo hàm ngược).

- Forward pass đi xuôi: input → output → loss.
- Backward pass đi ngược: loss → output → ... → input. Mỗi layer nhận gradient từ layer sau.
- **Mỗi weight có "phần lỗi"** → biết cần điều chỉnh bao nhiêu.

### Vấn đề

- Tốn memory vì cần lưu activations từ forward pass.
- Có thể vanishing/exploding (như đã nói ở gradient).

### Trong dự án

PyTorch tự động làm backprop. Bạn không cần viết code backward bằng tay (trừ khi research mới).

```python
loss.backward()    # Đó là backprop
```

---

## 8. Learning Rate

### Câu chuyện

Đi xuống đồi từ trên đỉnh. **Bước to** = đi nhanh, nhưng có thể nhảy qua đáy thung lũng, sang đồi bên kia (overshoot). **Bước nhỏ** = an toàn, đi rất lâu.

**Learning rate ($\eta$)** = kích thước bước nhảy mỗi lần update weight.
- $\eta = 0.1$: bước rất to.
- $\eta = 1\text{e-}3 = 0.001$: bước vừa.
- $\eta = 1\text{e-}5$: bước siêu nhỏ.

### Vấn đề

- LR quá lớn: loss diverge (NaN), oscillate.
- LR quá nhỏ: train rất chậm, mắc kẹt local minimum.
- **LR là hyperparameter quan trọng nhất**. Sai LR là lý do số 1 model không train được.

### Strategy thông minh

Thay vì dùng LR cố định, dùng **schedule** giảm dần:
- Lúc đầu: LR cao (đi nhanh).
- Càng gần đáy: LR giảm dần (đi cẩn thận).
- Phổ biến: cosine schedule, exponential decay.

### Trong dự án

Recommended:
- **VAE-GAN warmup**: $\eta = 1\text{e-}3$.
- **VAE-GAN adversarial**: $\eta_G = 1\text{e-}4$, $\eta_D = 4\text{e-}4$.
- **SeqGAN**: $\eta_{MLE} = 1\text{e-}3$, $\eta_{adv} = 1\text{e-}4$.
- **Gumbel-Softmax**: $\eta = 2\text{e-}4$ + cosine schedule.

---

## 9. Optimizer

### Câu chuyện

Bạn đi xuống đồi:
- **SGD (Stochastic Gradient Descent)** = đi theo dốc hiện tại từng bước. Đơn giản nhưng chậm và lắc lư.
- **Momentum** = giữ đà. Nếu vừa đi nhanh xuống dốc, tiếp tục đi nhanh dù dốc nhẹ. Như xe đạp xuống dốc.
- **Adam** = thông minh nhất. Nhớ lịch sử cả hướng và tốc độ, tự động điều chỉnh bước riêng cho từng chân (= từng weight). 99% dự án dùng Adam.

### Ý nghĩa

Optimizer = thuật toán quyết định **cách dùng gradient** để update weight.
- Cùng gradient → optimizer khác → kết quả khác.
- Adam thường convergence nhanh + ổn định + ít sensitive với LR setting.

### Code

```python
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

for batch in data:
    output = model(batch)
    loss = compute_loss(output, batch.label)
    
    optimizer.zero_grad()  # Reset gradient cũ
    loss.backward()        # Tính gradient mới (backprop)
    optimizer.step()       # Update weight (dùng optimizer)
```

3 dòng cuối là **vòng lặp training cốt lõi** — gặp ở mọi project deep learning.

### Trong dự án

Cả 3 approach dùng Adam (hoặc AdamW cho Transformer). Riêng GAN cần setting đặc biệt:
- Adam $\beta_1 = 0.5$ thay default 0.9 → ổn định hơn cho GAN.

---

## 10. Tổng kết: Vòng lặp Training

Tất cả AI training đều là vòng lặp 5 bước:

```
LẶP cho đến khi loss đủ thấp:
    1. Lấy batch dữ liệu (vd 32 mẫu).
    2. Forward pass: cho qua model → output.
    3. Tính loss giữa output và label thật.
    4. Backward pass: tính gradient cho mọi weight.
    5. Optimizer update: weight ← weight - LR × gradient.
```

5 bước này = 1 "iteration". Train 1 model thường cần **vài chục nghìn đến vài triệu iteration**.

### Ví dụ code thật

```python
for epoch in range(100):                   # 100 lần đi qua dataset
    for batch in dataloader:               # Mỗi batch 32 samples
        output = model(batch.input)        # Bước 2
        loss = criterion(output, batch.label)  # Bước 3
        
        optimizer.zero_grad()
        loss.backward()                    # Bước 4
        optimizer.step()                   # Bước 5
        
    print(f"Epoch {epoch}, loss: {loss.item():.4f}")
```

Đó là **80%** code train AI. Phần còn lại là kiến trúc model và evaluation.

---

## 11. Bạn đã hiểu gì rồi?

Sau khi đọc bài này, bạn nên trả lời được:
- ✅ Neural Network là gì? (Dây chuyền nhà máy nhiều "công nhân" tính toán nhỏ)
- ✅ Train AI nghĩa là làm gì? (Điều chỉnh weight để giảm loss)
- ✅ Forward pass và Backward pass khác nhau thế nào? (Đi xuôi dự đoán vs đi ngược truy ngược lỗi)
- ✅ Vì sao cần Loss Function? (Cần con số đo "model sai bao nhiêu" để mà tối ưu)
- ✅ Gradient là gì? (La bàn chỉ hướng tăng loss; ngược chiều = giảm loss)
- ✅ Learning rate cao/thấp ảnh hưởng gì? (Cao: nhanh nhưng dễ trượt; Thấp: chậm nhưng ổn định)

Nếu chưa rõ chỗ nào — quay lại đọc câu chuyện đó. Toán không quan trọng, **trực giác mới quan trọng**.

---

## 12. Đọc tiếp

Sau bài này, đọc bài 02: `Onboarding_AI_Knowledge_02_CNN_RNN_Sequences.md` — học về CNN (cho ảnh + 1 phần text), RNN/LSTM/GRU (cho sequence text).

Khi đã quen, có thể nhảy sang `AI_Foundations_For_Team_01_*.md` để đọc bản có toán hàn lâm — sẽ hiểu sâu hơn.
