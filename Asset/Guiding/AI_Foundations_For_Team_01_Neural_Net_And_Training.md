# AI Foundations — Bài 01: Neural Network & Quá trình Huấn luyện

> **Đối tượng**: Thành viên team đã có ít background lập trình/toán cơ bản. File này dùng phong cách **4 tầng**: (1) What/When/Why + ví dụ trẻ em, (2) Toán học hàn lâm, (3) Mặt trí tuệ nhân tạo, (4) Mặt dữ liệu.
>
> **Phiên bản đơn giản hóa cho member không-tech**: xem `Onboarding_AI_Knowledge_01_Neural_Net_And_Training.md`.

> **Cập nhật**: 2026-05-04
> **Concepts trong bài**: Neural Network, MLP, Forward Pass, Loss Function, Gradient & Đạo hàm, Backpropagation, Weight & Bias, Learning Rate, Optimizer

---

## Mục lục

1. [Neural Network — Mạng nơ-ron](#1-neural-network)
2. [MLP — Multilayer Perceptron](#2-mlp)
3. [Forward Pass — Lan truyền tiến](#3-forward-pass)
4. [Weight & Bias — Trọng số và độ chệch](#4-weight--bias)
5. [Loss Function — Hàm mất mát](#5-loss-function)
6. [Gradient & Đạo hàm](#6-gradient--đạo-hàm)
7. [Backpropagation — Lan truyền ngược](#7-backpropagation)
8. [Learning Rate — Tốc độ học](#8-learning-rate)
9. [Optimizer — Bộ tối ưu](#9-optimizer)

---

## 1. Neural Network

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Neural Network (mạng nơ-ron)** = mô hình toán học mô phỏng cách não bộ xử lý thông tin: nhiều **đơn vị nhỏ (neuron)** kết nối thành mạng, mỗi neuron nhận tín hiệu, biến đổi, truyền tiếp. Khi: bài toán có pattern phi tuyến phức tạp mà rule-based không xử lý được. Vì sao: NN có khả năng **xấp xỉ vạn năng** (Universal Approximation Theorem) — về lý thuyết có thể học bất kỳ hàm liên tục nào.

> **Ví dụ trẻ em**: Hình dung một **dây chuyền nhà máy bánh kẹo**. Nguyên liệu (đường, bột, sữa) đi vào đầu dây chuyền. Mỗi công nhân (= 1 neuron) nhận một chút nguyên liệu, làm 1 việc nhỏ (đong, trộn, nướng, đóng gói), rồi đẩy sang công nhân kế tiếp. Sau 50 công nhân, ra được hộp kẹo hoàn chỉnh. Mỗi công nhân không "thông minh", nhưng cả dây chuyền cùng làm thì sản phẩm cuối phức tạp.

### Tầng 2 — Toán học (hàn lâm)

Một neuron (perceptron) tính:
$$y = \phi\left(\sum_{i=1}^n w_i x_i + b\right) = \phi(\mathbf{w}^T \mathbf{x} + b)$$
- $\mathbf{x} \in \mathbb{R}^n$: input vector.
- $\mathbf{w} \in \mathbb{R}^n$: weight vector (trọng số).
- $b \in \mathbb{R}$: bias (độ chệch).
- $\phi: \mathbb{R} \to \mathbb{R}$: **activation function** (hàm kích hoạt) — phi tuyến.

**Activation phổ biến**:
- Sigmoid: $\phi(z) = \frac{1}{1+e^{-z}}$, range $(0,1)$.
- Tanh: $\phi(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}}$, range $(-1,1)$.
- ReLU: $\phi(z) = \max(0, z)$.
- GELU: $\phi(z) = z \cdot \Phi(z)$ với $\Phi$ là CDF chuẩn N(0,1).

**Vì sao cần activation phi tuyến?** Nếu $\phi(z) = z$ (tuyến tính), composition của nhiều layer $\phi(W_2 \phi(W_1 x))= W_2 W_1 x$ vẫn tuyến tính → mạng sâu vô nghĩa. Phi tuyến cho phép network biểu diễn hàm phi tuyến.

**Universal Approximation Theorem** (Cybenko 1989, Hornik 1991): Mạng 1 hidden layer với đủ neuron + activation phi tuyến có thể xấp xỉ **mọi hàm liên tục** trên compact set với độ chính xác tùy ý.

**Phép toán nền tảng**: tích vô hướng, tổng có trọng số, hàm phi tuyến, composition of functions, định lý xấp xỉ.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Neural network là kiến trúc cơ sở cho mọi deep learning model. CNN, RNN, Transformer, GAN, VAE đều là biến thể chuyên biệt.
- Mỗi neuron sau khi train sẽ "chuyên môn hóa" detect 1 feature cụ thể (vd 1 neuron detect "có dấu nháy đơn", neuron khác detect "có UNION SELECT").
- **Depth vs Width tradeoff**: Deep NN (nhiều layer mỏng) thường học better hierarchical features hơn Wide NN (ít layer dày). Modern: rất sâu (50-100+ layers) nhờ skip connections (ResNet).

### Tầng 4 — Mặt dữ liệu

**Input shape**: $\mathbf{x} \in \mathbb{R}^n$ — vector số thực. Trước khi feed:
- Text → tokenize → token IDs → embed thành vectors.
- Image → flatten hoặc giữ tensor $\mathbb{R}^{H \times W \times C}$.
- Categorical → one-hot hoặc embedding.

**Scale**: thường normalize về mean=0, std=1 (chuẩn hóa) hoặc [0,1] (min-max). Neuron không thích input có scale rất khác nhau (gradient update không cân bằng).

**Trong dự án**: Generator/Discriminator của 3 approach đều là neural network. Input của G = noise vector $z \sim \mathcal{N}(0, I)$, Input của D = sequence of token embeddings.

---

## 2. MLP — Multilayer Perceptron

### Tầng 1 — What / When / Why + ví dụ trẻ em

**MLP (Perceptron đa lớp)** = nhiều layer neuron xếp chồng, **fully connected** (mỗi neuron layer trước nối với mọi neuron layer sau). Khi: dữ liệu dạng vector cố định, không có cấu trúc không gian/thời gian. Vì sao: là "vanilla NN", baseline đơn giản nhất.

> **Ví dụ trẻ em**: Như một **trường tiểu học** có 5 lớp. Mỗi lớp có 30 học sinh. Mỗi học sinh lớp 1 viết thư cho **mọi** học sinh lớp 2. Mỗi học sinh lớp 2 nhận 30 thư, đọc tổng hợp, viết thư mới gửi mọi học sinh lớp 3. Cứ thế đến lớp 5. Càng đi sâu, thông tin càng được "lọc + tổng hợp".

### Tầng 2 — Toán học (hàn lâm)

MLP với $L$ layers:
$$\mathbf{h}^{(l)} = \phi^{(l)}\left(\mathbf{W}^{(l)} \mathbf{h}^{(l-1)} + \mathbf{b}^{(l)}\right), \quad l = 1, ..., L$$
- $\mathbf{h}^{(0)} = \mathbf{x}$ (input).
- $\mathbf{h}^{(L)} = \mathbf{y}$ (output).
- $\mathbf{W}^{(l)} \in \mathbb{R}^{d_l \times d_{l-1}}$, $\mathbf{b}^{(l)} \in \mathbb{R}^{d_l}$.

**Số tham số**: $\sum_{l=1}^L (d_l \cdot d_{l-1} + d_l)$. Vd MLP `[784, 256, 128, 10]`: $784 \cdot 256 + 256 + 256 \cdot 128 + 128 + 128 \cdot 10 + 10 = 235,146$ tham số.

**Output activation tùy task**:
- Regression: linear (no activation).
- Binary classification: sigmoid → $p \in (0,1)$.
- Multi-class classification: softmax $\sigma(\mathbf{z})_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$ → distribution over $K$ classes.

**Phép toán nền tảng**: matrix-vector product, function composition, softmax (smooth argmax).

### Tầng 3 — Mặt trí tuệ nhân tạo

- MLP "fully connected" rất tốn tham số khi input lớn (vd ảnh 1000×1000 → 1M neurons input × 256 hidden = 256M tham số).
- Không tận dụng được **inductive bias** không gian (vị trí pixel kề nhau quan trọng) → cần CNN.
- Không tận dụng được **inductive bias** thời gian (thứ tự token quan trọng) → cần RNN/Transformer.
- **Trong GAN**: MLP nhỏ vẫn được dùng làm projection head hoặc feature combiner trong các architecture hybrid.

### Tầng 4 — Mặt dữ liệu

**Input**: vector $\mathbb{R}^n$, thường $n$ vài trăm đến vài nghìn.
**Hidden layers**: kích thước thường giảm dần (encoder) hoặc giữ nguyên (residual).
**Output**: vector $\mathbb{R}^K$ với $K$ là số class hoặc 1 nếu regression.

**Trong dự án**: `data_engine/train_classifier.py` dùng RandomForest trên TF-IDF, không phải MLP. Nhưng nếu thay bằng MLP, kiến trúc tham khảo: `[5000 (TF-IDF dim), 256, 128, 13 (số SQLi types)]`.

---

## 3. Forward Pass

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Forward pass (lan truyền tiến)** = chạy dữ liệu từ input qua các layer đến output để **tính dự đoán**. Khi: cả lúc train (để tính loss) và lúc inference (để predict). Vì sao: là cơ chế chính của NN.

> **Ví dụ trẻ em**: Quay lại nhà máy bánh kẹo. Forward pass = **đẩy nguyên liệu vào đầu dây chuyền, chờ ra hộp kẹo cuối**. Không sửa máy lúc này, chỉ chạy thuần.

### Tầng 2 — Toán học (hàn lâm)

Forward pass tính $\hat{y} = f_\theta(\mathbf{x})$ với $\theta = \{W^{(1)}, b^{(1)}, ..., W^{(L)}, b^{(L)}\}$ là toàn bộ parameters.

**Algorithm** (với MLP):
```
INPUT: x, parameters θ
OUTPUT: ŷ

h_0 = x
FOR l = 1 to L:
    z_l = W_l · h_{l-1} + b_l        # affine
    h_l = φ_l(z_l)                    # activation
ŷ = h_L
```

**Computational cost**: $O\left(\sum_l d_l \cdot d_{l-1}\right)$ — chủ yếu là matrix-vector products. Với batch $B$ samples, tận dụng matrix-matrix product: $\mathbf{Z}_l = \mathbf{H}_{l-1} \mathbf{W}_l^T + \mathbf{b}_l$ với $\mathbf{H}_{l-1} \in \mathbb{R}^{B \times d_{l-1}}$.

**Phép toán nền tảng**: matrix multiplication, BLAS routines (GEMM), parallelization on GPU.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Forward pass là phần "infer" — cho input, dự đoán output.
- Trong train: forward pass cần lưu **intermediate activations** $\mathbf{h}^{(l)}$ để dùng cho backward pass.
- Trong inference: không cần lưu intermediate → tiết kiệm memory.
- **Eager mode** (PyTorch default): compute từng bước, dễ debug. **Graph mode** (TF, TorchScript): compile sẵn graph, tối ưu hơn cho production.

### Tầng 4 — Mặt dữ liệu

**Batched forward**: 
- Input: $\mathbf{X} \in \mathbb{R}^{B \times n}$.
- Output: $\hat{\mathbf{Y}} \in \mathbb{R}^{B \times K}$.
- Batch size $B$ tùy memory: 16-256 phổ biến cho training, 1-32 cho inference latency-sensitive.

**Trong dự án**: Discriminator forward pass trên batch SQLi tokens, output discriminator score (scalar per sample). Generator forward pass từ noise → token sequence.

---

## 4. Weight & Bias

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Weight (trọng số)** $w$ = "mức độ quan tâm" của neuron với 1 input. **Bias** $b$ = "ngưỡng kích hoạt" — neuron có sẵn ý kiến trước khi nhận input. Khi: là parameters chính của NN, được điều chỉnh trong quá trình train. Vì sao: weight & bias là cách NN "nhớ" pattern đã học.

> **Ví dụ trẻ em**: Bạn quyết định "có nên ăn tối không" dựa trên 3 yếu tố: đói (x1), món ngon (x2), bạn rủ (x3). Mỗi yếu tố có mức quan trọng khác nhau với bạn — đó là **weight**. Vd với bạn: $w_1=3$ (đói rất quan trọng), $w_2=1$ (món ngon vừa thôi), $w_3=2$ (bạn rủ khá quan trọng). **Bias** = ngưỡng cá nhân — bạn có "khuynh hướng đi ăn" hay không nếu các yếu tố trung tính. Quyết định = $w_1 x_1 + w_2 x_2 + w_3 x_3 + b > 0$ → ăn.

### Tầng 2 — Toán học (hàn lâm)

**Weight matrix** $\mathbf{W} \in \mathbb{R}^{d_{out} \times d_{in}}$. Mỗi hàng = vector trọng số của 1 output neuron.

**Bias vector** $\mathbf{b} \in \mathbb{R}^{d_{out}}$.

**Khởi tạo (initialization)** — quan trọng:
- **Xavier/Glorot** (cho tanh, sigmoid): $W_{ij} \sim \mathcal{U}\left(-\sqrt{\frac{6}{d_{in}+d_{out}}}, \sqrt{\frac{6}{d_{in}+d_{out}}}\right)$ — preserves variance qua layers.
- **He** (cho ReLU): $W_{ij} \sim \mathcal{N}\left(0, \frac{2}{d_{in}}\right)$.
- Bias thường khởi tạo $b = 0$.

**Lý do khởi tạo cẩn thận**: Nếu init quá lớn → gradient explosion. Quá nhỏ → vanishing gradient + neuron "chết".

**Regularization trên W**:
- L2 (weight decay): $\Omega(\theta) = \lambda \|\mathbf{W}\|_F^2$ — phạt weight lớn → smooth function.
- L1: $\Omega(\theta) = \lambda \|\mathbf{W}\|_1$ — sparsity, nhiều weight = 0.

**Phép toán nền tảng**: linear algebra (matrix), random sampling từ uniform/Gaussian, Frobenius norm, L1/L2 norm.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Weight + bias = **kiến thức** của model. Lưu thành **checkpoint file** (vd `.pt`, `.h5`) → load lại để inference hoặc fine-tune.
- **Transfer learning**: khởi tạo weight từ model đã train sẵn (vd BERT, GPT) thay vì random → train nhanh hơn nhiều.
- **Frozen weights**: trong fine-tuning, có thể đóng băng 1 phần weight, chỉ update phần khác (vd freeze encoder, train classifier head).
- **Trong GAN**: G và D có 2 bộ weight độc lập. Khi train G, D bị frozen tạm thời, và ngược lại.

### Tầng 4 — Mặt dữ liệu

**Storage**: Weight thường float32 (4 bytes/value). Mạng 100M parameters → 400MB checkpoint.
**Quantization**: Có thể giảm xuống int8 (1 byte) → 100MB, mất ít accuracy.

**Trong dự án**: 
- VAE-GAN: ước lượng ~10-50M params (tùy config Transformer).
- SeqGAN: ~5-20M params.
- Gumbel-Softmax: ~10-30M params.
- Checkpoints sẽ lưu ở `<Approach>_SQLi/checkpoints/`.

---

## 5. Loss Function

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Loss function (hàm mất mát)** = số đo "model sai bao nhiêu". Khi: tại mỗi bước training. Vì sao: cần một con số để tối ưu — minimize loss = improve model.

> **Ví dụ trẻ em**: Bạn ném phi tiêu vào bia. Loss = **khoảng cách từ phi tiêu đến tâm bia**. Càng gần tâm → loss càng nhỏ → bạn càng giỏi. Nếu loss = 0, bạn ném trúng tâm. Mục tiêu luyện tập: giảm loss qua thời gian.

### Tầng 2 — Toán học (hàn lâm)

Loss là hàm $\mathcal{L}: \mathcal{Y} \times \mathcal{Y} \to \mathbb{R}_{\geq 0}$ với $\mathcal{L}(y, \hat{y}) \geq 0$, $\mathcal{L}(y, y) = 0$.

**Loss phổ biến**:

| Task | Loss | Công thức |
|---|---|---|
| Regression | MSE | $\mathcal{L} = \frac{1}{N}\sum_i (y_i - \hat{y}_i)^2$ |
| Regression robust | MAE | $\mathcal{L} = \frac{1}{N}\sum_i \|y_i - \hat{y}_i\|$ |
| Binary classification | BCE | $\mathcal{L} = -\frac{1}{N}\sum_i [y_i \log \hat{y}_i + (1-y_i)\log(1-\hat{y}_i)]$ |
| Multi-class classification | Cross-Entropy | $\mathcal{L} = -\frac{1}{N}\sum_i \sum_c y_{i,c} \log \hat{y}_{i,c}$ |
| Distribution matching | KL divergence | $\mathcal{L} = \sum_x p(x) \log \frac{p(x)}{q(x)}$ |
| GAN | Adversarial | $\mathcal{L}_G = -\log D(G(z))$, $\mathcal{L}_D = -[\log D(x) + \log(1-D(G(z)))]$ |
| Wasserstein GAN | Wasserstein | $\mathcal{L}_D = \mathbb{E}[D(x)] - \mathbb{E}[D(G(z))]$ |

**Total loss thường có nhiều thành phần**:
$$\mathcal{L}_{total} = \mathcal{L}_{task} + \lambda_1 \mathcal{L}_{reg} + \lambda_2 \mathcal{L}_{aux}$$
$\lambda_i$ là weights cân bằng giữa các terms.

**Phép toán nền tảng**: log, expectation, divergence, integration (cho continuous distributions).

### Tầng 3 — Mặt trí tuệ nhân tạo

- Loss phải **differentiable** (có đạo hàm) để backprop được. Vì thế:
  - Không dùng accuracy (step function, gradient = 0 mọi nơi).
  - Dùng surrogate loss: cross-entropy thay 0-1 loss.
- **Loss landscape**: hình dung loss như mặt cong trong không gian parameters. Train = đi từ random point xuống đáy thung lũng. Loss landscape phức tạp (nhiều minima local) → cần optimizer khôn ngoan (Adam, momentum).
- **Trong GAN**: G và D có loss đối nghịch — khi G giảm loss, D tăng loss. Đây là lý do GAN khó train (no monotonic convergence).

### Tầng 4 — Mặt dữ liệu

**Trong dự án — loss của 3 approach**:

- **VAE-GAN**: $\mathcal{L} = \mathcal{L}_{recon} + \beta \cdot \mathcal{L}_{KL} + \lambda \cdot \mathcal{L}_{adv} + \gamma \cdot \mathcal{L}_{fm}$
  - 4 thành phần, weights khởi đầu $\beta=1.0$, $\lambda=0.1$, $\gamma=10$.
- **SeqGAN**: $\mathcal{L}_{MLE}$ pretraining + $\mathcal{L}_{REINFORCE}$ adversarial.
- **Gumbel-Softmax GAN**: $\mathcal{L}_{WGAN-GP} = \mathbb{E}[D(x_{real})] - \mathbb{E}[D(G(z))] + \lambda_{gp} \mathbb{E}[(\|\nabla D\|_2 - 1)^2]$.

---

## 6. Gradient & Đạo hàm

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Gradient** = vector đạo hàm — chỉ ra **hướng tăng nhanh nhất** của loss theo từng parameter. Khi: trong backpropagation. Vì sao: muốn **giảm loss** thì đi ngược chiều gradient.

> **Ví dụ trẻ em**: Bạn đứng trên đồi, bịt mắt. Muốn đi xuống thung lũng (= minimize loss). Bạn không nhìn được toàn bộ đồi, nhưng cảm nhận được dưới chân **dốc bên nào nhất**. Đó là gradient. Đi ngược dốc = đi xuống. Lặp lại đến khi bằng phẳng = đã ở đáy.

### Tầng 2 — Toán học (hàn lâm)

**Đạo hàm** của hàm 1 biến $f: \mathbb{R} \to \mathbb{R}$:
$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$

**Gradient** của hàm nhiều biến $f: \mathbb{R}^n \to \mathbb{R}$:
$$\nabla f(\mathbf{x}) = \begin{bmatrix} \frac{\partial f}{\partial x_1} \\ \vdots \\ \frac{\partial f}{\partial x_n} \end{bmatrix}$$

**Tính chất**:
- $\nabla f$ trỏ về hướng tăng nhanh nhất.
- $-\nabla f$ trỏ về hướng giảm nhanh nhất → gradient descent.
- $\|\nabla f\|$ = tốc độ thay đổi.

**Chain rule** (cốt lõi của backprop):
$$\frac{\partial}{\partial x} f(g(x)) = f'(g(x)) \cdot g'(x)$$

Tổng quát cho composition $h = f_L \circ f_{L-1} \circ ... \circ f_1$:
$$\frac{\partial h}{\partial x} = \frac{\partial f_L}{\partial f_{L-1}} \cdot \frac{\partial f_{L-1}}{\partial f_{L-2}} \cdots \frac{\partial f_1}{\partial x}$$

**Jacobian** (cho vector-valued function $f: \mathbb{R}^n \to \mathbb{R}^m$):
$$J_f = \begin{bmatrix} \frac{\partial f_1}{\partial x_1} & \cdots & \frac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \frac{\partial f_m}{\partial x_1} & \cdots & \frac{\partial f_m}{\partial x_n} \end{bmatrix}$$

**Phép toán nền tảng**: limit, derivative, partial derivative, chain rule, Jacobian, Hessian (đạo hàm cấp 2).

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Automatic differentiation (autograd)**: PyTorch/TF tự động tính gradient bằng chain rule khi forward pass. User chỉ cần viết forward, framework lo backward.
- **Gradient flow problems**:
  - **Vanishing gradient**: gradient quá nhỏ → train chậm. Gặp với sigmoid/tanh trong deep network. Fix: dùng ReLU, batch norm, residual.
  - **Exploding gradient**: gradient quá lớn → loss NaN. Fix: gradient clipping ($\|\nabla\|_2 \leq c$).
- **Trong GAN**: Discriminator gradient được dùng để update Generator. Nếu D quá mạnh → G gradient = 0 (saturation). Nếu D quá yếu → G nhận signal nhiễu.

### Tầng 4 — Mặt dữ liệu

**Gradient có cùng shape với parameter**: Nếu $W \in \mathbb{R}^{d \times d}$ thì $\nabla_W \mathcal{L} \in \mathbb{R}^{d \times d}$.

**Storage**: Trong train, lưu cả forward activations và backward gradients → memory ~ 2-3× model size.

**Trong dự án**: Cần monitor gradient norm $\|\nabla_\theta G\|$ liên tục để phát hiện sớm mất ổn định:
- VAE-GAN Roadmap: "Nếu gradient norm của G đột ngột tăng > 10x → dừng, kiểm tra balance giữa $\lambda$ và $\gamma$."
- Gumbel-Softmax Roadmap: "Nếu $\|\nabla_\theta G\| < \epsilon$ khi $\tau < 0.3$ → trigger temperature reset."

---

## 7. Backpropagation

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Backpropagation (lan truyền ngược)** = thuật toán tính gradient cho mọi parameter trong NN một cách hiệu quả, bằng cách áp dụng **chain rule** từ output ngược về input. Khi: sau mỗi forward pass, để update parameters. Vì sao: tính gradient brute-force tốn $O(P^2)$ với $P$ tham số; backprop làm $O(P)$.

> **Ví dụ trẻ em**: Một đội bóng thua 1-0. **Không phải lỗi của tất cả** — có người đá đỉnh, có người đá tệ. Backprop = **truy ngược nguyên nhân**: huấn luyện viên bắt đầu từ "thua" (= loss), đi ngược: "do chuyền hỏng" → "do hậu vệ chậm" → "do thủ môn không tổ chức". Mỗi cầu thủ nhận được "phần lỗi" tương ứng. Cầu thủ nào lỗi nhiều → tập luyện thêm phần đó.

### Tầng 2 — Toán học (hàn lâm)

Cho NN $L$ layers với forward: $\mathbf{h}^{(l)} = \phi(\mathbf{z}^{(l)})$, $\mathbf{z}^{(l)} = \mathbf{W}^{(l)} \mathbf{h}^{(l-1)} + \mathbf{b}^{(l)}$.

**Backward algorithm**:
1. Tính $\delta^{(L)} = \nabla_{\mathbf{z}^{(L)}} \mathcal{L}$ (gradient tại output layer).
2. Lặp ngược $l = L-1, L-2, ..., 1$:
   $$\delta^{(l)} = (\mathbf{W}^{(l+1)})^T \delta^{(l+1)} \odot \phi'(\mathbf{z}^{(l)})$$
3. Với mỗi layer:
   $$\nabla_{\mathbf{W}^{(l)}} \mathcal{L} = \delta^{(l)} (\mathbf{h}^{(l-1)})^T$$
   $$\nabla_{\mathbf{b}^{(l)}} \mathcal{L} = \delta^{(l)}$$

**Computational cost**: $O(P)$ per sample, gấp đôi forward pass.

**Memory cost**: Cần lưu $\mathbf{h}^{(l)}$ và $\mathbf{z}^{(l)}$ cho mọi layer (forward) → $O(L \cdot d_{max})$ memory. Trong rất sâu network: dùng **gradient checkpointing** (recompute activations thay vì lưu) để giảm memory tốn thêm compute.

**Phép toán nền tảng**: chain rule, dynamic programming, transposed matrix multiplication, element-wise product (Hadamard $\odot$).

### Tầng 3 — Mặt trí tuệ nhân tạo

- Backprop là phát minh quan trọng nhất của deep learning era (Rumelhart, Hinton, Williams 1986).
- **Modern frameworks** (PyTorch, TF, JAX) implement autograd → user không cần code backward thủ công.
- **Higher-order gradients**: có thể backprop qua backprop để tính Hessian, second-order info.
- **Gradient through stochastic ops**: argmax, sampling không có gradient → cần workaround:
  - **Reparameterization trick** (cho VAE): $z = \mu + \sigma \odot \epsilon$ → gradient flow qua $\mu, \sigma$.
  - **Gumbel-Softmax** (cho discrete): continuous relaxation của argmax (xem File 04).
  - **REINFORCE** (cho discrete): gradient estimator dùng log-prob trick.

### Tầng 4 — Mặt dữ liệu

**Trong code**:
```python
loss.backward()           # Backprop
optimizer.step()          # Update theta -= lr * grad
optimizer.zero_grad()     # Reset gradients cho iteration sau
```

**Gradient accumulation**: Nếu batch quá lớn không vừa GPU, chia nhỏ, accumulate gradients qua nhiều micro-batch trước khi step.

**Trong dự án**: 3 approach đều dùng autograd của PyTorch (giả định). Riêng SeqGAN dùng REINFORCE (xem File 04 cho chi tiết).

---

## 8. Learning Rate

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Learning rate (tốc độ học)** $\eta$ = bước nhảy mỗi lần update parameter. Khi: trong gradient descent. Vì sao: cân bằng giữa "học nhanh" và "ổn định".

> **Ví dụ trẻ em**: Đi xuống đồi từ trên đỉnh. **Bước to** = đi xuống nhanh nhưng có thể nhảy quá đáy thung lũng, sang đồi bên kia. **Bước nhỏ** = an toàn nhưng đi rất lâu. Phải chọn bước phù hợp — thường lúc đầu bước to, càng gần đáy bước càng nhỏ.

### Tầng 2 — Toán học (hàn lâm)

**Gradient descent update**:
$$\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)$$

**Convergence theorem** (cho convex L-smooth function): với $\eta = 1/L$, GD converge với rate $O(1/T)$ sau $T$ steps.

**Learning rate schedules** (giảm dần):

1. **Step decay**: $\eta_t = \eta_0 \cdot \gamma^{\lfloor t/T_{step} \rfloor}$ (vd $\gamma=0.5$, $T_{step}=10000$).
2. **Exponential decay**: $\eta_t = \eta_0 \cdot e^{-rt}$.
3. **Cosine annealing**: $\eta_t = \eta_{min} + \frac{1}{2}(\eta_0 - \eta_{min})(1 + \cos(\pi t/T))$.
4. **Warmup + cosine**: $\eta$ tăng tuyến tính trong $T_{warmup}$ steps đầu, rồi cosine decay.
5. **Reduce on plateau**: giảm $\eta$ khi val loss không cải thiện $T_{patience}$ epochs.

**Learning rate range test**: scan $\eta$ qua 7 orders of magnitude (1e-7 → 1e0) trên 1 mini-epoch → chọn LR ở "knee" của curve.

**Phép toán nền tảng**: convergence analysis, Lipschitz constant, bộ điều khiển (control theory).

### Tầng 3 — Mặt trí tuệ nhân tạo

- LR là hyperparameter quan trọng nhất. Sai LR là lý do số 1 model không train được.
- **LR quá lớn**: loss diverge (NaN), oscillate.
- **LR quá nhỏ**: train chậm, mắc kẹt local minimum.
- **Per-parameter LR**: Adam, AdaGrad, RMSprop scale LR cho từng parameter dựa trên gradient history → giảm sensitivity với LR setting.
- **GAN cần LR thấp**: thường $\eta = 1\text{e-}4$ với Adam $\beta=(0.5, 0.999)$ thay vì default $(0.9, 0.999)$.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:
- VAE-GAN warm-up phase: $\eta = 1\text{e-}3$ cho VAE alone.
- Adversarial phase: $\eta_G = 1\text{e-}4$, $\eta_D = 4\text{e-}4$ (D nhanh hơn vì train 5x).
- SeqGAN MLE pretrain: $\eta = 1\text{e-}3$. Adversarial: $\eta_G = 1\text{e-}4$, $\eta_D = 1\text{e-}4$.
- Gumbel-Softmax: $\eta = 2\text{e-}4$ với cosine schedule.

---

## 9. Optimizer

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Optimizer** = thuật toán quyết định **cách dùng gradient** để update parameter. Khi: thay thế cho vanilla SGD. Vì sao: SGD đơn giản chậm và bất ổn; optimizer hiện đại (Adam) hội tụ nhanh, ổn định hơn.

> **Ví dụ trẻ em**: Bạn đi xuống đồi. **SGD** = bước theo dốc hiện tại, mỗi bước độc lập. **Momentum** = giữ đà — nếu vừa đi nhanh, tiếp tục đi nhanh dù dốc nhẹ. **Adam** = thông minh hơn nữa — nhớ lịch sử cả hướng và độ lớn dốc, điều chỉnh bước riêng cho từng chân.

### Tầng 2 — Toán học (hàn lâm)

Ký hiệu: $g_t = \nabla \mathcal{L}(\theta_t)$.

**SGD**:
$$\theta_{t+1} = \theta_t - \eta g_t$$

**SGD + Momentum**:
$$v_t = \mu v_{t-1} + g_t$$
$$\theta_{t+1} = \theta_t - \eta v_t$$
$\mu \in [0,1]$ là momentum coefficient (thường 0.9).

**Nesterov Momentum** (look-ahead):
$$v_t = \mu v_{t-1} + \nabla \mathcal{L}(\theta_t - \eta \mu v_{t-1})$$

**AdaGrad** (per-parameter scaling):
$$G_t = G_{t-1} + g_t^2$$
$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{G_t + \epsilon}} g_t$$
Adapt LR theo magnitude lịch sử nhưng $G_t$ tăng vô hạn → LR → 0.

**RMSprop**:
$$G_t = \rho G_{t-1} + (1-\rho) g_t^2$$
EMA thay sum → tránh LR → 0.

**Adam** (Adaptive Moment Estimation) — phổ biến nhất:
$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t \quad \text{(1st moment)}$$
$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \quad \text{(2nd moment)}$$
$$\hat{m}_t = m_t / (1 - \beta_1^t), \quad \hat{v}_t = v_t / (1 - \beta_2^t) \quad \text{(bias correction)}$$
$$\theta_{t+1} = \theta_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$
Default: $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$.

**AdamW**: Adam + decoupled weight decay. Recommended cho Transformer.

**Phép toán nền tảng**: exponential moving average, second-moment estimation, bias correction, adaptive scaling.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Adam** = default cho hầu hết tasks. Convergence nhanh, ít sensitive với LR.
- **SGD + Momentum** vẫn dùng cho large-scale image tasks (ResNet, ImageNet) — sometimes generalize better.
- **AdamW** cho Transformer (BERT, GPT) — fix issue weight decay của Adam.
- **GAN-specific**:
  - Adam với $\beta_1=0.5$ (low momentum) ổn định hơn cho GAN. Default $\beta_1=0.9$ có thể oscillate.
  - WGAN-GP paper khuyến nghị Adam $\beta=(0.5, 0.9)$.

### Tầng 4 — Mặt dữ liệu

**Trong code PyTorch**:
```python
optimizer_G = torch.optim.Adam(G.parameters(), lr=1e-4, betas=(0.5, 0.999))
optimizer_D = torch.optim.Adam(D.parameters(), lr=4e-4, betas=(0.5, 0.999))
```

**Storage**: Optimizer state (Adam: $m, v$ per param) tốn ~2× model size. Total memory: 4× model (weights + grads + 2× optimizer state).

**Trong dự án — đề xuất**:
- VAE-GAN: AdamW cho encoder/decoder, Adam $\beta=(0.5, 0.999)$ cho discriminator.
- SeqGAN: Adam cho cả G, D. SGD optional cho baseline value network.
- Gumbel-Softmax: Adam $\beta=(0.5, 0.9)$ theo WGAN-GP paper.

---

## 10. Tài liệu tham chiếu chéo

- File 02 — `AI_Foundations_For_Team_02_CNN_RNN_Sequences.md` — kiến trúc chuyên biệt cho không gian/thời gian.
- File 03 — `AI_Foundations_For_Team_03_Attention_And_Transformer.md` — cơ chế attention + Transformer.
- File 04 — `AI_Foundations_For_Team_04_Generative_Models.md` — GAN, VAE, biến thể.
- `Onboarding_AI_Knowledge_01_Neural_Net_And_Training.md` — bản đơn giản hóa cho member không-tech.

## 11. Đọc thêm (nếu muốn sâu)

- **Goodfellow, Bengio, Courville — Deep Learning** (textbook, MIT Press) — chapter 6 (deep feedforward), chapter 8 (optimization).
- **Stanford CS231n notes**: backprop, optimization, regularization — viết rất rõ.
- **Distill.pub**: "Why Momentum Really Works" (visualization tuyệt vời cho momentum).
- **Original papers**:
  - Backprop: Rumelhart, Hinton, Williams 1986.
  - Adam: Kingma, Ba 2014.
  - Xavier init: Glorot, Bengio 2010.
  - He init: He et al. 2015.
