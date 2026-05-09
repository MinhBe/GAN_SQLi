# AI Foundations — Bài 02: CNN, Dilated CNN, RNN, LSTM, GRU

> **Đối tượng**: Thành viên team đã đọc Bài 01 (Neural Net & Training). Bài này giới thiệu các kiến trúc chuyên biệt cho dữ liệu có **cấu trúc không gian** (CNN) và **cấu trúc thời gian** (RNN family). Phong cách 4 tầng.
>
> **Phiên bản đơn giản hóa cho member không-tech**: `Onboarding_AI_Knowledge_02_CNN_RNN_Sequences.md`.

> **Cập nhật**: 2026-05-04
> **Concepts trong bài**: CNN (1D/2D), kernels, stride, padding, pooling, Dilated CNN, vanilla RNN, vanishing gradient, LSTM, GRU.

---

## Mục lục

1. [CNN — Convolutional Neural Network](#1-cnn)
2. [CNN: kernels, stride, padding, pooling](#2-cnn-các-thành-phần)
3. [Dilated CNN](#3-dilated-cnn)
4. [RNN — Recurrent Neural Network](#4-rnn)
5. [Vanishing & Exploding Gradient](#5-vanishing--exploding-gradient)
6. [LSTM — Long Short-Term Memory](#6-lstm)
7. [GRU — Gated Recurrent Unit](#7-gru)

---

## 1. CNN — Convolutional Neural Network

### Tầng 1 — What / When / Why + ví dụ trẻ em

**CNN** = neural network dùng phép **tích chập (convolution)** thay matrix multiplication, tận dụng tính chất **địa phương + tịnh tiến bất biến** của dữ liệu không gian. Khi: ảnh, audio, sequence (1D CNN). Vì sao: MLP không hiệu quả với input lớn — cần shared parameters và local connectivity.

> **Ví dụ trẻ em**: Bạn dán **kính lúp** lên ảnh, **trượt từ trái sang phải, từ trên xuống dưới**. Mỗi vị trí, kính lúp "nhìn" 1 vùng nhỏ và đánh giá "có dấu hiệu khuôn mặt không?". Kính lúp = **kernel/filter**. Kết quả tổng hợp tất cả vị trí = **feature map**. Cùng 1 kính lúp dùng khắp ảnh → nếu khuôn mặt ở góc nào cũng được nhận diện → **translation-invariant**.

### Tầng 2 — Toán học (hàn lâm)

**Convolution 1D** (cho sequence):
$$(f * g)(t) = \sum_{k} f(t - k) g(k)$$

Trong deep learning, thực ra dùng **cross-correlation** (không flip kernel):
$$(I * K)(i) = \sum_{m=0}^{M-1} I(i + m) K(m)$$
- $I \in \mathbb{R}^L$: input.
- $K \in \mathbb{R}^M$: kernel.
- Output $O \in \mathbb{R}^{L-M+1}$ (no padding).

**Convolution 2D** (cho ảnh):
$$O(i,j) = \sum_{m=0}^{M-1} \sum_{n=0}^{N-1} I(i+m, j+n) K(m, n)$$

**Multi-channel**: $I \in \mathbb{R}^{C_{in} \times H \times W}$, kernel $K \in \mathbb{R}^{C_{out} \times C_{in} \times M \times N}$, output $O \in \mathbb{R}^{C_{out} \times H' \times W'}$.

**Tham số CNN layer**: $C_{out} \cdot C_{in} \cdot M \cdot N + C_{out}$ (bias) — **không phụ thuộc** $H, W$ → ít tham số hơn MLP rất nhiều.

**Inductive bias**:
- **Locality**: chỉ kết nối với neighborhood — phù hợp với pixel kề nhau correlated.
- **Translation equivariance**: $f(\text{shift}(x)) = \text{shift}(f(x))$ — feature lặp lại cùng pattern bất kể vị trí.
- **Weight sharing**: cùng kernel dùng khắp input → giảm tham số đáng kể.

**Phép toán nền tảng**: convolution (tích chập), cross-correlation, Fourier transform (convolution theorem: $F(f*g) = F(f) \cdot F(g)$).

### Tầng 3 — Mặt trí tuệ nhân tạo

- CNN cách mạng hóa computer vision (AlexNet 2012). Từ đó được áp dụng cho audio (1D CNN trên waveform), text (1D CNN trên token sequence), graph (Graph CNN).
- **Receptive field**: vùng input ảnh hưởng đến 1 output neuron. Stack nhiều layer → receptive field tăng dần → từ low-level features (edges) → high-level (objects).
- **TextCNN** (Kim 2014): 1D CNN trên text với kernels [3,4,5] để bắt n-gram patterns. Được dùng làm Discriminator trong GAN-for-text.

### Tầng 4 — Mặt dữ liệu

**Input shape** cho 1D CNN:
- `(batch, channels_in, length)` — PyTorch convention.
- `(batch, length, channels_in)` — TF convention.

**Trong dự án** — Discriminator của 3 approach:
- VAE-GAN, SeqGAN: 1D CNN với kernels [3, 4, 5] (TextCNN style). Input shape: `(B, vocab_size, L)` sau one-hot hoặc `(B, embed_dim, L)` sau embedding.
- Gumbel-Softmax: Dilated CNN (xem mục 3).

---

## 2. CNN — Các thành phần

### 2.1 Kernel (filter)

#### Tầng 1
**Kernel** = ma trận nhỏ (vd 3×3) chứa weights, "trượt" qua input, tính dot product. Khi: thành phần cốt lõi mỗi conv layer. Vì sao: mỗi kernel học detect 1 pattern cụ thể.

> **Ví dụ trẻ em**: Như **mẫu giấy đục lỗ**. Đặt lên trang, qua các lỗ nhìn được phần input bên dưới → đánh dấu vị trí có pattern đó.

#### Tầng 2
$K \in \mathbb{R}^{M \times N}$ với $M, N$ thường lẻ (3, 5, 7) để có pixel trung tâm.

**Số kernel** ($C_{out}$) = số pattern khác nhau muốn detect. Phổ biến: 32, 64, 128, 256, 512.

#### Tầng 3
- **Kernel nhỏ** (3×3) stack nhiều layer ≈ receptive field lớn nhưng ít params hơn 1 kernel lớn.
- **VGGNet** (2014) chứng minh: stack 3×3 hiệu quả hơn 5×5, 7×7.

#### Tầng 4
**Trong dự án**:
- TextCNN Discriminator: 3 kernels song song [3, 4, 5] (mỗi kernel detect n-gram khác).
- Gumbel-Softmax Dilated CNN: kernels [2, 3, 5, 8, 12, 16] với dilation rate khác nhau.

### 2.2 Stride

#### Tầng 1
**Stride** $s$ = bước nhảy của kernel mỗi lần trượt. Khi: muốn downsample feature map. Vì sao: giảm spatial dimension → tăng receptive field nhanh hơn, giảm compute.

> **Ví dụ trẻ em**: Với kính lúp, **trượt cách bao nhiêu pixel**? Stride = 1: trượt từng pixel (kỹ). Stride = 2: nhảy 2 pixel (nhanh, nhưng có thể bỏ sót).

#### Tầng 2
Output size: $L_{out} = \lfloor (L_{in} - M + 2P)/s \rfloor + 1$ với $P$ là padding.

#### Tầng 3-4
- Stride = 1 (default): preserve spatial dim.
- Stride = 2: halve dim → thay thế cho pooling trong modern architectures (vd ResNet).

### 2.3 Padding

#### Tầng 1
**Padding** = thêm 0 (hoặc giá trị khác) vào biên input. Khi: muốn giữ output cùng size với input. Vì sao: nếu không pad, mỗi conv layer mất (M-1)/2 ở mỗi cạnh → mất thông tin biên.

> **Ví dụ trẻ em**: Đóng khung trắng quanh ảnh trước khi áp kính lúp → kính lúp đến tận cạnh ảnh được luôn.

#### Tầng 2
**Same padding**: $P = (M-1)/2$ → output size = input size khi stride=1.
**Valid padding**: $P = 0$ → output co lại.
**Causal padding**: chỉ pad bên trái → output tại vị trí $i$ chỉ phụ thuộc vào input ≤ i (cho autoregressive).

### 2.4 Pooling

#### Tầng 1
**Pooling** = downsample bằng cách lấy max/avg trong cửa sổ. Khi: giảm spatial dim, tăng tính bất biến local. Vì sao: thay alternative cho stride>1, không có learnable parameters.

> **Ví dụ trẻ em**: Mỗi vùng 2×2 pixel chọn pixel **sáng nhất** (max pooling) → ảnh thu nhỏ một nửa, giữ lại đặc trưng nổi bật.

#### Tầng 2
**Max pooling**: $\text{MaxPool}(x)_{i,j} = \max_{(m,n) \in W_{i,j}} x(m,n)$.
**Average pooling**: $\text{AvgPool}(x)_{i,j} = \frac{1}{|W|} \sum_{(m,n) \in W_{i,j}} x(m,n)$.
**Global pooling**: pool toàn bộ feature map → 1 scalar per channel.

#### Tầng 3-4
- Modern trend: thay max pool bằng strided conv (learnable downsample).
- Global Average Pooling thay flatten + fully-connected ở cuối CNN classifier (giảm params, tránh overfit).

---

## 3. Dilated CNN

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Dilated CNN (Atrous Convolution)** = CNN với kernel có "khoảng trống" giữa các weight. Khi: cần receptive field lớn mà không tăng số param hoặc layer. Vì sao: với sequence dài hoặc ảnh độ phân giải cao, vanilla CNN cần nhiều layer để cover toàn bộ context.

> **Ví dụ trẻ em**: Kính lúp 3 lỗ. **Vanilla**: 3 lỗ liên tiếp ▮▮▮ — nhìn 3 pixel kề nhau. **Dilated rate=2**: 3 lỗ cách 1 pixel ▮_▮_▮ — nhìn 3 pixel cách xa hơn. Cùng 3 lỗ nhưng phủ được vùng to hơn → hiểu context xa hơn.

### Tầng 2 — Toán học (hàn lâm)

**Dilated convolution** với dilation rate $r$:
$$O(i) = \sum_{m=0}^{M-1} I(i + r \cdot m) K(m)$$

**Receptive field** với $L$ layers dilated:
$$RF = 1 + \sum_{l=1}^L (M-1) \cdot r_l$$

Nếu $r_l = 2^{l-1}$ (exponential dilation): $RF = 1 + (M-1)(2^L - 1)$ — **exponential growth** với linear depth.

So sánh:
- Vanilla CNN, kernel 3, $L=10$: $RF = 1 + 10 \cdot 2 = 21$.
- Dilated, $r=[1,2,4,8,16,...,512]$, $L=10$: $RF = 1 + 2 \cdot 1023 = 2047$.

**Phép toán nền tảng**: spaced sampling, exponential series, multi-scale analysis.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **WaveNet** (Van den Oord 2016): dilated 1D conv cho audio generation — receptive field hàng chục nghìn samples với chỉ 30 layers.
- **Semantic segmentation** (DeepLab): dilated conv giữ resolution mà tăng receptive field.
- **Trong dự án — Gumbel-Softmax Roadmap**:
  > "**Dilated Convolutional Network** với multi-scale kernels được thiết kế theo cấu trúc phân tầng của SQL:
  > - Kernels [2, 3]: bắt các toán tử và từ khóa kép (`UNION SELECT`, `OR 1`).
  > - Kernels [5, 8]: bắt các mệnh đề đơn (`WHERE id = <NUM>`).
  > - Kernels [12, 16]: bắt các cấu trúc lồng nhau như subquery (`SELECT ... FROM (SELECT ...)`)."
  > **Lý do chọn Dilated CNN thay TextCNN**: SQL có cấu trúc phân tầng và global dependency; dilation cho phép receptive field lớn mà không tăng số tham số.

### Tầng 4 — Mặt dữ liệu

**Input shape**: cùng như CNN bình thường.

**Hyperparameter quan trọng**: dilation rate. Thường chọn:
- Linear: $r = 1, 2, 3, 4, ...$
- Exponential: $r = 1, 2, 4, 8, 16, 32, ...$ — phổ biến hơn cho coverage rộng.

**Trong dự án**: Discriminator Gumbel-Softmax sẽ implement dilated CNN với 6 multi-scale kernels như trên.

---

## 4. RNN — Recurrent Neural Network

### Tầng 1 — What / When / Why + ví dụ trẻ em

**RNN** = NN có **kết nối lặp** (recurrent) — output bước trước là input bước sau, cho phép "nhớ" qua thời gian. Khi: dữ liệu dạng chuỗi (text, audio, time series). Vì sao: cần model có **state** thay đổi theo thời gian.

> **Ví dụ trẻ em**: Đọc truyện. Mỗi trang bạn đọc, **nhớ** nội dung trang trước. Khi đến trang 100, hiểu chi tiết trang 100 vì nhớ trang 1-99. RNN làm điều tương tự: hidden state $h_t$ = "trí nhớ" tại bước $t$, được update mỗi khi nhận token mới.

### Tầng 2 — Toán học (hàn lâm)

**Vanilla RNN** (Elman 1990):
$$h_t = \phi(W_{hh} h_{t-1} + W_{xh} x_t + b_h)$$
$$y_t = W_{hy} h_t + b_y$$

- $h_t \in \mathbb{R}^d$: hidden state tại $t$.
- $h_0 = 0$ (hoặc learnable).
- Same weights $W_{hh}, W_{xh}, W_{hy}$ chia sẻ qua mọi bước thời gian.

**Unrolled view**: với sequence $T$ bước, RNN tương đương MLP $T$ layer với weight tied.

**Số tham số**: $d^2 + d \cdot n + d$ cho hidden, $d \cdot K + K$ cho output. Không phụ thuộc $T$.

**Backpropagation Through Time (BPTT)**:
$$\nabla_{W_{hh}} \mathcal{L} = \sum_{t=1}^T \frac{\partial \mathcal{L}_t}{\partial W_{hh}} = \sum_{t=1}^T \sum_{k=1}^t \frac{\partial \mathcal{L}_t}{\partial h_t} \prod_{j=k+1}^t \frac{\partial h_j}{\partial h_{j-1}} \frac{\partial h_k}{\partial W_{hh}}$$

Tích nhiều Jacobian $\prod \frac{\partial h_j}{\partial h_{j-1}}$ → root nguyên nhân vanishing/exploding gradient.

**Phép toán nền tảng**: dynamical systems, fixed-point iteration, BPTT, time-shared parameters.

### Tầng 3 — Mặt trí tuệ nhân tạo

- RNN thống trị NLP từ 1990s đến 2017 (trước Transformer).
- **Variants**: bidirectional RNN (forward + backward), stacked RNN (multi-layer), Encoder-Decoder RNN (seq2seq).
- **Limitation chính**: 
  - Vanishing gradient cho long-range dependency.
  - Sequential computation → không parallelizable.
  - Bị Transformer thay thế trong hầu hết task NLP.
- Vẫn dùng cho: low-resource setting, on-device, real-time streaming (Transformer cần KV cache lớn).

### Tầng 4 — Mặt dữ liệu

**Input shape**: `(batch, seq_len, feature_dim)`.

**Trong dự án**:
- **SeqGAN Roadmap**: "Generator — Policy Network: kiến trúc **LSTM** (phù hợp với sequence dài, tránh vanishing gradient) **hoặc** Transformer Decoder."
- VAE-GAN, Gumbel-Softmax: dùng Transformer (xem File 03), không RNN.

---

## 5. Vanishing & Exploding Gradient

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Vanishing gradient** = gradient nhỏ dần qua các bước time, nhanh chóng về 0 → model không học được dependency dài. **Exploding gradient** = ngược lại, gradient phình vô hạn → loss NaN.

> **Ví dụ trẻ em**: Một dây chuyền 100 người **nhắn tin tai-mép** từ người 1 đến người 100. Mỗi lần truyền **mất 10% âm thanh** (vanishing) — đến người 100 còn $0.9^{100} \approx 0$ → không nghe gì. Hoặc mỗi lần **khuếch đại 1.1×** (exploding) — đến người 100 thành $1.1^{100} \approx 13780$ → tai điếc luôn.

### Tầng 2 — Toán học (hàn lâm)

Trong BPTT, gradient $\frac{\partial h_t}{\partial h_k} = \prod_{j=k+1}^t \frac{\partial h_j}{\partial h_{j-1}}$.

Mỗi factor là Jacobian: $\frac{\partial h_j}{\partial h_{j-1}} = \text{diag}(\phi'(z_j)) \cdot W_{hh}^T$.

**Spectral analysis**: gọi $\lambda_{max}$ là eigenvalue lớn nhất của $W_{hh}$. 
- Nếu $\lambda_{max} < 1/\max\phi'$: gradient → 0 (vanishing).
- Nếu $\lambda_{max} > 1/\min\phi'$: gradient → ∞ (exploding).

Với sigmoid $\phi'(z) \in (0, 0.25]$, vanilla RNN gần như chắc chắn vanishing.

**Mitigations**:
- **Gradient clipping** (cho exploding): nếu $\|\nabla\|_2 > c$, scale: $\nabla \leftarrow \nabla \cdot c/\|\nabla\|_2$.
- **Better activations**: ReLU (không saturate ở positive).
- **Better architectures**: LSTM, GRU (gated mechanism allows gradient flow).
- **Skip connections**: ResNet, Highway Networks.
- **Spectral normalization**: ép $\|W\|_2 \leq 1$.

**Phép toán nền tảng**: matrix powers, eigendecomposition, spectral radius.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Vanishing gradient là lý do RNN không học được long-range. LSTM/GRU giải quyết qua **gating + cell state**.
- Trong GAN: D quá strong → G gradient vanish (discriminator output saturate). Mitigate bằng WGAN-GP.
- **Trong dự án — VAE-GAN Roadmap**: "Monitor gradient norm của G liên tục — nếu gradient norm của G đột ngột tăng > 10x: dừng, kiểm tra balance giữa $\lambda$ và $\gamma$."

### Tầng 4 — Mặt dữ liệu

**Practical defaults**:
- Gradient clipping threshold: $c = 1.0$ hoặc $c = 5.0$.
- LSTM/GRU có default mitigations.
- Khi train: monitor `||grad_G||` và `||grad_D||` qua TensorBoard.

---

## 6. LSTM — Long Short-Term Memory

### Tầng 1 — What / When / Why + ví dụ trẻ em

**LSTM** = RNN có **3 gate** (forget, input, output) + **cell state** $c_t$ chạy song song với hidden state $h_t$. Khi: cần học dependency dài (50-200+ bước). Vì sao: cell state cho phép gradient flow gần như không suy giảm.

> **Ví dụ trẻ em**: Mỗi người trong dây chuyền tai-mép có **cuốn sổ nhỏ** (cell state). Họ:
> - **Forget gate**: quyết định **xóa** mục nào trong sổ (vì không quan trọng nữa).
> - **Input gate**: quyết định **viết thêm** thông tin mới gì.
> - **Output gate**: quyết định **đọc** mục nào trong sổ ra ngoài (cho người tiếp theo).
> Sổ này được copy nguyên gần như không sửa qua các bước → gradient flow xa không vanish.

### Tầng 2 — Toán học (hàn lâm)

**LSTM cell** (Hochreiter & Schmidhuber 1997):

$$f_t = \sigma(W_f [h_{t-1}, x_t] + b_f) \quad \text{(forget gate)}$$
$$i_t = \sigma(W_i [h_{t-1}, x_t] + b_i) \quad \text{(input gate)}$$
$$\tilde{c}_t = \tanh(W_c [h_{t-1}, x_t] + b_c) \quad \text{(candidate)}$$
$$c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t \quad \text{(cell state update)}$$
$$o_t = \sigma(W_o [h_{t-1}, x_t] + b_o) \quad \text{(output gate)}$$
$$h_t = o_t \odot \tanh(c_t) \quad \text{(hidden state)}$$

$\sigma$ = sigmoid (output [0,1] làm "valve"). $\odot$ = element-wise product.

**Gradient flow**:
$$\frac{\partial c_t}{\partial c_{t-1}} = f_t \in [0, 1]^d$$

Khi $f_t \approx 1$ (forget gate "mở"): gradient flow gần như identity. Vẫn có thể vanish nếu $f_t < 1$ qua nhiều bước, nhưng **học được khi nào nên forget vs preserve**.

**Số tham số**: $4 \cdot (d_h \cdot (d_h + d_x) + d_h)$ — gấp 4 lần vanilla RNN do 4 weight matrices (forget, input, candidate, output).

**Phép toán nền tảng**: gating mechanism, element-wise product, sigmoid (smooth gate), residual-like connection.

### Tầng 3 — Mặt trí tuệ nhân tạo

- LSTM là kiến trúc dominant cho NLP 2014-2017 (machine translation, language modeling).
- **Variants**: 
  - **Peephole LSTM**: gate phụ thuộc cả $c_{t-1}$.
  - **Bidirectional LSTM**: forward + backward LSTM concatenated.
  - **Stacked LSTM**: nhiều layer LSTM stack.
- Bị Transformer thay thế cho hầu hết task NLP từ 2018.

### Tầng 4 — Mặt dữ liệu

**Input shape**: `(batch, seq_len, feature_dim)`.
**Output**: `(batch, seq_len, hidden_dim)` cho hidden states + cell state cuối.

**Trong dự án — SeqGAN**:
- Generator có thể là LSTM 3 layers, hidden 512.
- Input: token embedding $\mathbb{R}^{d_{embed}=256}$.
- Output: distribution over vocab tại mỗi step.

```python
# PyTorch sketch
class GeneratorLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=256, hidden_dim=512, num_layers=3):
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True)
        self.out = nn.Linear(hidden_dim, vocab_size)
```

---

## 7. GRU — Gated Recurrent Unit

### Tầng 1 — What / When / Why + ví dụ trẻ em

**GRU** = phiên bản đơn giản của LSTM, **2 gate** (reset, update) thay 3, không có cell state riêng. Khi: muốn LSTM-like performance với ít tham số hơn. Vì sao: thường 30% nhanh hơn, comparable accuracy.

> **Ví dụ trẻ em**: Như LSTM nhưng **bỏ cuốn sổ riêng**, chỉ có 1 hidden state. 2 gate:
> - **Reset gate**: nên **quên** bao nhiêu thông tin cũ.
> - **Update gate**: nên **đè** thông tin mới lên thông tin cũ bao nhiêu.
> Đơn giản hơn, gọn hơn, hoạt động gần tốt như LSTM trong nhiều task.

### Tầng 2 — Toán học (hàn lâm)

**GRU cell** (Cho et al. 2014):

$$z_t = \sigma(W_z [h_{t-1}, x_t] + b_z) \quad \text{(update gate)}$$
$$r_t = \sigma(W_r [h_{t-1}, x_t] + b_r) \quad \text{(reset gate)}$$
$$\tilde{h}_t = \tanh(W_h [r_t \odot h_{t-1}, x_t] + b_h) \quad \text{(candidate)}$$
$$h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t \quad \text{(state update)}$$

Khi $z_t \approx 0$: $h_t \approx h_{t-1}$ (preserve).
Khi $z_t \approx 1$: $h_t \approx \tilde{h}_t$ (overwrite).

**Số tham số**: $3 \cdot (d_h \cdot (d_h + d_x) + d_h)$ — gấp 3 vanilla RNN, ít hơn LSTM 25%.

**Phép toán nền tảng**: như LSTM nhưng đơn giản hơn 1 gate.

### Tầng 3 — Mặt trí tuệ nhân tạo

- GRU vs LSTM:
  - LSTM expressive hơn (3 gates + cell), tốt hơn cho rất long sequence.
  - GRU đơn giản hơn, train nhanh hơn, comparable cho most tasks.
- Empirically: tùy dataset, không có winner rõ ràng. **Recommendation**: thử GRU trước, nếu không đủ thì LSTM.

### Tầng 4 — Mặt dữ liệu

**Input/output shape**: giống LSTM (chỉ không có cell state).

**Trong dự án**: SeqGAN có thể dùng GRU thay LSTM nếu muốn train nhanh hơn — hyperparameter chọn lúc implement.

---

## 8. Tổng kết — So sánh CNN vs RNN family

| Aspect | CNN | RNN/LSTM/GRU |
|---|---|---|
| Inductive bias | Locality, translation-invariance | Sequentiality, recurrence |
| Parallelizable | ✅ Yes | ❌ No (sequential) |
| Long-range dep | ❌ Cần stack nhiều layer (vanilla) hoặc dilated | ✅ Theory; thực tế LSTM/GRU |
| Tham số | Ít (shared weights) | Trung bình |
| Đào tạo | Stable | Có thể vanishing gradient |
| Khi dùng cho text | TextCNN cho classification | Seq2seq cho generation |

**Trong dự án**:
- CNN dùng cho **Discriminator** (classification thật/giả).
- RNN/LSTM dùng cho **Generator** trong SeqGAN (sequential generation).
- Cả hai sẽ bị Transformer (File 03) thay thế dần trong VAE-GAN, Gumbel-Softmax.

---

## 9. Tài liệu tham chiếu chéo

- File 01 — Neural Net cơ sở.
- File 03 — Transformer (sẽ thay thế RNN cho hầu hết task).
- File 04 — Generative models (GAN, VAE) dùng các kiến trúc này.
- `Onboarding_AI_Knowledge_02_*.md` — bản đơn giản hóa.

## 10. Đọc thêm

- Olah's blog: "Understanding LSTM Networks" (visualization tuyệt vời).
- "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling" (Chung et al. 2014) — so sánh LSTM vs GRU.
- "WaveNet" (Van den Oord et al. 2016) — dilated CNN cho generation.
- Stanford CS231n: chapters về CNN.
- Stanford CS224n: chapters về RNN/LSTM cho NLP.
