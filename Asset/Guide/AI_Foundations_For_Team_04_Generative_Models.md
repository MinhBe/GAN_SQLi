# AI Foundations — Bài 04: Generative Models (GAN, VAE, biến thể)

> **Đối tượng**: Đã đọc Bài 01-03. Đây là bài cốt lõi nhất với dự án vì 3 hướng tiếp cận đều thuộc generative model. Phong cách 4 tầng.
>
> **Phiên bản đơn giản hóa**: `Onboarding_AI_Knowledge_04_Generative_Models.md`.

> **Cập nhật**: 2026-05-04
> **Concepts trong bài**: GAN (Generator, Discriminator, minimax game), Layers trong G/D, Mode collapse, WGAN, WGAN-GP, Wasserstein loss, biến thể GAN, VAE, latent space, KL divergence, reparameterization trick.

---

## Mục lục

1. [GAN — Generative Adversarial Network](#1-gan)
2. [Generator (G) — kiến trúc & layers](#2-generator)
3. [Discriminator (D) — kiến trúc & layers](#3-discriminator)
4. [GAN Training Loop & Minimax Game](#4-gan-training-loop)
5. [Mode Collapse](#5-mode-collapse)
6. [WGAN — Wasserstein GAN](#6-wgan)
7. [WGAN-GP — Gradient Penalty](#7-wgan-gp)
8. [Biến thể GAN (DCGAN, cGAN, SeqGAN, MaliGAN, RelGAN, ...)](#8-biến-thể-gan)
9. [VAE — Variational Autoencoder](#9-vae)
10. [Latent Space](#10-latent-space)
11. [KL Divergence](#11-kl-divergence)
12. [Reparameterization Trick](#12-reparameterization-trick)

---

## 1. GAN — Generative Adversarial Network

### Tầng 1 — What / When / Why + ví dụ trẻ em

**GAN (Goodfellow 2014)** = 2 mạng đối kháng — **Generator (G)** sinh data giả, **Discriminator (D)** phân biệt thật/giả. Khi: muốn sinh data realistic (image, audio, text) mà không cần explicit likelihood. Vì sao: implicit generative model — học $p_{data}$ qua game thay tối ưu trực tiếp likelihood.

> **Ví dụ trẻ em**: **Trò chơi tiền giả**. **Thợ giả mạo (G)** vẽ tiền giả ngày càng tinh vi. **Cảnh sát (D)** kiểm tra, phân biệt tiền thật/giả. Cả hai cùng học:
> - Lúc đầu thợ giả vẽ cẩu thả → cảnh sát bắt dễ.
> - Thợ giả học từ phản hồi cảnh sát → vẽ tinh vi hơn.
> - Cảnh sát thấy tiền giả tinh vi hơn → phải học detect tốt hơn.
> - Cuộc đua không hồi kết. Cuối cùng **thợ giả vẽ giống thật đến mức cảnh sát đoán random** → G đã học được phân phối tiền thật.

### Tầng 2 — Toán học (hàn lâm)

**Setup**: 
- $p_{data}(x)$: phân phối thật.
- $p_z(z) = \mathcal{N}(0, I)$: prior noise.
- $G_\theta: \mathcal{Z} \to \mathcal{X}$: generator.
- $D_\phi: \mathcal{X} \to [0, 1]$: discriminator.

**Original GAN objective** (minimax):
$$\min_G \max_D V(D, G) = \mathbb{E}_{x \sim p_{data}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$$

**Optimal D** (cho fixed G):
$$D^*(x) = \frac{p_{data}(x)}{p_{data}(x) + p_g(x)}$$

với $p_g$ = phân phối induced bởi $G$.

**Substitute back**:
$$V(D^*, G) = -\log 4 + 2 \cdot JSD(p_{data} \| p_g)$$

→ minimize objective tương đương minimize **Jensen-Shannon Divergence** giữa $p_{data}$ và $p_g$. Khi $p_g = p_{data}$: JSD = 0, $D^*(x) = 1/2$ everywhere → cảnh sát đoán random.

**Theorem** (Goodfellow 2014): nếu G và D đủ capacity và update theo $\nabla_G$, $\nabla_D$ tối ưu, hệ hội tụ về $p_g = p_{data}$.

**Phép toán nền tảng**: minimax game theory, expectation, log-probability, Jensen-Shannon Divergence:
$$JSD(P \| Q) = \frac{1}{2} KL\left(P \| \frac{P+Q}{2}\right) + \frac{1}{2} KL\left(Q \| \frac{P+Q}{2}\right)$$

### Tầng 3 — Mặt trí tuệ nhân tạo

- GAN là **implicit generative model** — không cần biết $p_g(x)$ explicit, chỉ cần sample được.
- So với VAE/normalizing flows: GAN sample chất lượng cao hơn nhưng training không ổn định.
- **Vấn đề original GAN**:
  - Training instability (oscillation, divergence).
  - Mode collapse (G chỉ sinh 1-2 mode).
  - Vanishing gradient (D quá mạnh).
- **Modern variants** giải quyết: WGAN, WGAN-GP, Spectral Normalization, R1 regularization.

### Tầng 4 — Mặt dữ liệu

**Input cho G**: noise $z \sim \mathcal{N}(0, I) \in \mathbb{R}^{d_z}$, thường $d_z = 100$ - $512$.
**Output của G**: sample $x \in \mathcal{X}$ có cùng shape với data thật.
**Input cho D**: $x$ (thật hoặc giả).
**Output của D**: scalar trong $[0, 1]$ (hoặc $\mathbb{R}$ cho WGAN).

**Trong dự án**: $\mathcal{X}$ là space của SQLi token sequence. G output sequence of one-hot/Gumbel-Softmax vectors → D phân biệt.

---

## 2. Generator (G) — Kiến trúc & Layers

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Generator** = NN map noise vector $z$ thành sample $x$ giả. Khi: là half của GAN. Vì sao: cần một cách để turn random noise thành structured data.

> **Ví dụ trẻ em**: Một họa sĩ tài hoa. Ai đó đưa **xúc xắc rolled** ($z$ random). Họa sĩ dùng các con số để vẽ **bức tranh** ($x$). Mỗi xúc xắc khác → bức tranh khác.

### Tầng 2 — Toán học (hàn lâm)

$G_\theta: \mathbb{R}^{d_z} \to \mathcal{X}$, parameterized by $\theta$.

**Kiến trúc tùy domain**:

| Domain | Kiến trúc G phổ biến |
|---|---|
| Image | Transposed Conv (DCGAN), ResNet (BigGAN), StyleGAN |
| Audio | Dilated Conv (WaveGAN), SpecGAN |
| Text | RNN/LSTM (SeqGAN), Transformer + Gumbel-Softmax |
| Tabular | MLP |

**Layers thường gặp trong text Generator**:

1. **Embedding layer** (cho input/output): map token IDs ↔ vectors.
2. **Transformer Decoder** hoặc **LSTM**: sinh sequence autoregressively.
3. **Output projection** $W_{out} \in \mathbb{R}^{d \times |V|}$: map hidden → vocab logits.
4. **Sampling layer**:
   - Argmax (không differentiable) — chỉ inference.
   - Gumbel-Softmax (differentiable approximation).
   - Sampling từ multinomial (cho RL/REINFORCE).

**Phép toán nền tảng**: function approximation, sequence modeling, sampling.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Trong dự án**:
  - **VAE-GAN G**: Transformer Decoder, input là $z \in \mathbb{R}^{256}$, output sequence + Gumbel-Softmax sampling.
  - **SeqGAN G**: LSTM hoặc Transformer Decoder, output policy $\pi_\theta(a_t|s_t)$ over vocab, sampling = `multinomial` từ policy.
  - **Gumbel-Softmax G**: Transformer Decoder + Gumbel-Softmax layer, output soft one-hot vectors.

### Tầng 4 — Mặt dữ liệu

**Output shape**:
- Image G: `(B, C, H, W)`.
- Text G (one-hot): `(B, L, V)` với $V$ = vocab size.
- Text G (token IDs): `(B, L)` int.

---

## 3. Discriminator (D) — Kiến trúc & Layers

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Discriminator** = classifier phân biệt sample thật vs giả. Khi: half còn lại của GAN. Vì sao: cung cấp learning signal cho G qua gradient.

> **Ví dụ trẻ em**: Cảnh sát kiểm tra tiền. Đưa cho cảnh sát 1 tờ tiền → trả lời "thật" hay "giả". Cảnh sát giỏi → tóm được giả mạo nhanh.

### Tầng 2 — Toán học (hàn lâm)

$D_\phi: \mathcal{X} \to [0, 1]$ (original GAN) hoặc $D_\phi: \mathcal{X} \to \mathbb{R}$ (WGAN).

**Layers thường gặp trong text Discriminator**:

1. **Embedding layer**: map token IDs → vectors.
2. **Convolutional layers**:
   - **TextCNN** (Kim 2014): kernels [3, 4, 5], multi-channel feature maps.
   - **Dilated CNN** (Gumbel-Softmax dự án): kernels [2, 3, 5, 8, 12, 16] với dilation.
3. **Pooling**: max-over-time pooling theo channel.
4. **MLP head**: 1-2 fully connected layers.
5. **Output**:
   - Sigmoid (original GAN) → $[0, 1]$.
   - Linear (WGAN) → $\mathbb{R}$.

**Spectral Normalization** (Miyato 2018) — kỹ thuật regularization:
$$\bar{W} = W / \sigma(W)$$
với $\sigma(W)$ = spectral norm (largest singular value). Ép $\|D\|_{Lip} \leq 1$ → stable.

**Phép toán nền tảng**: convolution, pooling, classification.

### Tầng 3 — Mặt trí tuệ nhân tạo

- D phải đủ mạnh để cung cấp signal hữu ích, nhưng KHÔNG quá mạnh (saturate G gradient).
- **D:G update ratio**: thường D update 1-5 lần cho mỗi G update. WGAN-GP recommend 5:1.
- **Feature matching**: thay objective adversarial bằng matching intermediate features → stable hơn:
$$\mathcal{L}_{fm} = \| \mathbb{E}[f(x_{real})] - \mathbb{E}[f(G(z))] \|^2$$
với $f$ là intermediate D layer.

**Trong dự án — VAE-GAN Roadmap**:
> "Feature Matching: Lấy output từ layer trước penultimate (không phải layer cuối) để tính feature matching loss. Layer quá cuối → generator học copy surface statistics. Layer quá đầu → signal quá yếu. Cụ thể: layer $L-2$ của CNN stack."

### Tầng 4 — Mặt dữ liệu

**Input shape**:
- Real samples: `(B, L)` token IDs hoặc `(B, L, V)` one-hot.
- Fake samples (từ G): same shape.

**Output**: scalar per sample, total shape `(B,)` hoặc `(B, 1)`.

---

## 4. GAN Training Loop & Minimax Game

### Tầng 1
Train G và D **luân phiên**:
1. Step D: maximize objective theo $\phi$ (D giỏi hơn).
2. Step G: minimize objective theo $\theta$ (G lừa giỏi hơn).

> **Ví dụ trẻ em**: Mỗi tuần:
> - Thứ 2-6: cảnh sát học detect (D update).
> - Thứ 7: thợ giả vẽ thử, xem cảnh sát detect được bao nhiêu, học từ failures (G update).

### Tầng 2

**Pseudocode**:
```
For each iteration:
    # Step 1: Update D
    For k steps (k=1 to 5):
        Sample {x_1, ..., x_B} ~ p_data
        Sample {z_1, ..., z_B} ~ p_z
        Update φ: maximize V(D_φ, G_θ)
            ∇_φ [(1/B) Σ log D(x_i) + log(1 - D(G(z_i)))]
    
    # Step 2: Update G
    Sample {z_1, ..., z_B} ~ p_z
    Update θ: minimize V(D_φ, G_θ)
        ∇_θ [(1/B) Σ log(1 - D(G(z_i)))]
```

**Trick — non-saturating G loss**:
Original $\log(1 - D(G(z)))$ gradient vanish khi D mạnh. Replace bằng:
$$\mathcal{L}_G = -\mathbb{E}_z[\log D(G(z))]$$
Same gradient direction nhưng magnitude ổn định hơn.

### Tầng 3-4
**Trong dự án**:
- VAE-GAN warm-up phase: train VAE alone (recon + KL) trước, sau đó add D.
- Adversarial phase: D:G = 5:1 với WGAN-GP loss.
- Monitor: gradient norms, D loss, G loss, sample quality (validity rate).

---

## 5. Mode Collapse

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Mode collapse** = G chỉ sinh ra **một vài sample giống nhau** (1 hoặc vài "modes"), bỏ qua phần còn lại của $p_{data}$. Khi: vấn đề phổ biến nhất của GAN. Vì sao: G tìm "shortcut" — chỉ sinh sample mà D dễ phán "thật" → maximize reward local.

> **Ví dụ trẻ em**: Thợ giả mạo phát hiện cảnh sát luôn cho qua tờ 100k màu xanh. Anh ta **chỉ vẽ tờ 100k xanh, không vẽ loại khác**. Cảnh sát check 1000 tờ giả → toàn 100k xanh. Tiền thật trên thị trường có 5 mệnh giá, 5 màu sắc → thợ giả thiếu 4 modes. Đó là collapse.

### Tầng 2 — Toán học (hàn lâm)

**Định nghĩa formal**: $p_g$ tập trung vào subset $\mathcal{X}_{collapse} \subset \text{supp}(p_{data})$, với $|\mathcal{X}_{collapse}| \ll |\text{supp}(p_{data})|$.

**Đo lường**:
- **Self-BLEU**: cao = nhiều samples giống nhau.
- **Pairwise edit distance** (cho text): median thấp = collapsed.
- **Inception Score**: thấp khi collapse.
- **FID** (Fréchet Inception Distance): cao khi collapse.

**Nguyên nhân toán học**:
- Original GAN minimize JSD. JSD bị **saturate** khi $p_g$ và $p_{data}$ disjoint support → gradient = 0.
- G tìm $x^*$ maximize $D(x)$ thay vì cover $p_{data}$.

**Phép toán nền tảng**: support of distribution, JSD saturation, gradient flow analysis.

### Tầng 3 — Mặt trí tuệ nhân tạo

**Detection**:
- Sample N=500 từ G mỗi K iterations.
- Tính pairwise edit distance (text) hoặc visual diversity (image).
- Nếu drop dramatically → collapsed.

**Mitigations**:
1. **WGAN-GP**: Wasserstein loss không saturate → better gradient.
2. **Minibatch discrimination**: D thấy minibatch, không chỉ single sample → detect collapse trực tiếp.
3. **Unrolled GAN**: simulate D updates ahead khi G updates.
4. **Increase dropout** trong G.
5. **Inject noise** vào latent.
6. **Diversity-promoting loss**: thêm term phạt collapse.

**Trong dự án — Roadmap mode collapse detection**:
- VAE-GAN: "Sau mỗi 1000 steps, sample 500 sequences, tính pairwise edit distance. Nếu median edit distance < 5 tokens: mode collapse đang xảy ra."
- Gumbel-Softmax: "Kiểm tra variance của các batch sinh ra sau mỗi epoch; nếu variance giảm đột ngột dưới ngưỡng $\sigma_{min}^2$: tăng Dropout hoặc inject thêm nhiễu vào Latent Space."

### Tầng 4 — Mặt dữ liệu

**Practical thresholds**:
- Median pairwise edit distance < 5 tokens trên samples 100-token: collapsed.
- Self-BLEU n=3 > 0.95 trên 1000 samples: severe collapse.

---

## 6. WGAN — Wasserstein GAN

### Tầng 1 — What / When / Why + ví dụ trẻ em

**WGAN (Arjovsky 2017)** = GAN với **Wasserstein distance** thay JSD. Khi: muốn ổn định training và avoid mode collapse. Vì sao: Wasserstein distance smooth + có gradient kể cả khi distributions disjoint.

> **Ví dụ trẻ em**: Hai đống cát. JSD nói "khác nhau hay không?" — chỉ trả lời 0/1, không nói khác nhau bao nhiêu. Wasserstein nói **"để biến đống A thành đống B cần phải vận chuyển bao nhiêu cát qua quãng đường nào"** — số đo có nghĩa kể cả khi 2 đống không chạm nhau. Gradient từ WD giúp G biết đi hướng nào để giảm khoảng cách.

### Tầng 2 — Toán học (hàn lâm)

**Wasserstein-1 distance** (Earth Mover's Distance):
$$W_1(P, Q) = \inf_{\gamma \in \Pi(P,Q)} \mathbb{E}_{(x,y) \sim \gamma}[\|x - y\|]$$
$\Pi(P,Q)$ = couplings của $P, Q$. $\gamma(x,y)$ = "lượng mass chuyển từ $x$ sang $y$".

**Kantorovich-Rubinstein duality**:
$$W_1(P, Q) = \sup_{\|f\|_L \leq 1} \mathbb{E}_{x \sim P}[f(x)] - \mathbb{E}_{x \sim Q}[f(x)]$$

$\|f\|_L \leq 1$ = $f$ là **1-Lipschitz** ($|f(x) - f(y)| \leq \|x - y\|$).

**WGAN objective** (D thay bằng "critic" $f_\phi$):
$$\min_G \max_{f_\phi: \|f_\phi\|_L \leq 1} \mathbb{E}_{x \sim p_{data}}[f_\phi(x)] - \mathbb{E}_{z \sim p_z}[f_\phi(G(z))]$$

**Critic gradient flow**: $\nabla_\theta \mathbb{E}[f_\phi(G(z))]$ — không cần log, không bị saturate.

**Original WGAN enforces Lipschitz qua weight clipping**: $w \leftarrow \text{clip}(w, -c, c)$. Nhược điểm: capacity hạn chế, gradient explode/vanish ở biên.

**Phép toán nền tảng**: optimal transport theory, Lipschitz continuity, Kantorovich-Rubinstein duality, dual norm.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Wasserstein loss correlates với sample quality (JSD doesn't).
- Critic không còn là classifier — output là score, không có sigmoid.
- "Mode coverage" cải thiện rõ rệt so với original GAN.

### Tầng 4
**Trong dự án**: tất cả 3 approach đều dùng WGAN-GP (thay clipping bằng Gradient Penalty — xem mục 7).

---

## 7. WGAN-GP — Gradient Penalty

### Tầng 1 — What / When / Why + ví dụ trẻ em

**WGAN-GP (Gulrajani 2017)** = WGAN với **gradient penalty** thay weight clipping. Khi: cải thiện WGAN. Vì sao: weight clipping của WGAN gốc gây capacity loss, GP "ép Lipschitz mềm" qua loss term.

> **Ví dụ trẻ em**: Thay vì **giam tay cảnh sát trong khoảng** (weight clip), ta **phạt khi cảnh sát đánh quá mạnh** (gradient penalty). Mềm mại hơn, không cản trở học.

### Tầng 2 — Toán học (hàn lâm)

**WGAN-GP objective**:
$$\mathcal{L}_D = \mathbb{E}_{\tilde{x} \sim p_g}[D(\tilde{x})] - \mathbb{E}_{x \sim p_{data}}[D(x)] + \lambda_{gp} \mathbb{E}_{\hat{x} \sim p_{\hat{x}}}[(\|\nabla_{\hat{x}} D(\hat{x})\|_2 - 1)^2]$$

- $\hat{x} = \epsilon x + (1-\epsilon) \tilde{x}$, $\epsilon \sim U(0,1)$ — interpolation giữa real và fake.
- $\lambda_{gp} = 10$ (default).

**Lý do**: optimal critic của Wasserstein objective có $\|\nabla_x f^*(x)\|_2 = 1$ a.e. trên support. GP ép D về điều này.

**G objective** (không đổi):
$$\mathcal{L}_G = -\mathbb{E}_{z \sim p_z}[D(G(z))]$$

**Architecture lưu ý**: 
- Không dùng BatchNorm trong D (BN làm gradient sample-dependent → break GP).
- Dùng LayerNorm hoặc InstanceNorm thay.

**Phép toán nền tảng**: random interpolation, gradient norm regularization, soft constraint.

### Tầng 3 — Mặt trí tuệ nhân tạo

- WGAN-GP là **default GAN training scheme** trong nhiều paper hiện đại.
- D:G = 5:1 (D update 5 lần per G update) — recommend.
- Optimizer: Adam $\beta_1=0.5, \beta_2=0.9$ thay default.

### Tầng 4
**Trong dự án — toàn bộ 3 approach dùng WGAN-GP**:
- $\lambda_{gp} = 10$.
- D:G = 5:1.
- Adam $\beta=(0.5, 0.9)$.

---

## 8. Biến thể GAN

### 8.1 DCGAN (Deep Convolutional GAN, 2015)

#### Tầng 1
GAN dùng deep conv kiến trúc cho image. **Khi**: image generation. **Vì sao**: chứng minh GAN scale được với conv.

#### Tầng 2-4
Guidelines:
- Replace pooling với strided conv.
- BatchNorm trong G và D.
- Remove fully connected.
- ReLU trong G (Tanh output), LeakyReLU trong D.

**Trong dự án**: không dùng (text, không phải image).

### 8.2 cGAN (Conditional GAN, 2014)

#### Tầng 1
GAN có **condition** $y$ (class label, text). $G(z, y)$, $D(x, y)$.

#### Tầng 2
$$\min_G \max_D \mathbb{E}_{x,y \sim p_{data}}[\log D(x, y)] + \mathbb{E}_{z, y}[\log(1 - D(G(z, y), y))]$$

#### Tầng 3-4
**Trong dự án**: có thể extend bằng condition trên `sqli_type` (vd "sinh union_based payload") — chưa trong roadmap nhưng natural extension.

### 8.3 SeqGAN (2017)

#### Tầng 1
GAN cho text với **policy gradient** — bypass argmax non-differentiability.

#### Tầng 2
$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=1}^T A(s_t, a_t) \nabla_\theta \log \pi_\theta(a_t|s_t)\right]$$

Reward = D output + auxiliary (syntax, WAF). MC rollout estimate $Q(s, a)$.

#### Tầng 3-4
**Trong dự án**: 1 trong 3 approach. Xem `SeqGAN_SQLi/Guiding.md`.

### 8.4 MaliGAN (Maximum-Likelihood Augmented Discrete GAN, 2017)

#### Tầng 1
SeqGAN variant với MLE-augmented gradient (lower variance).

#### Tầng 2
Importance sampling từ $D$:
$$\nabla_\theta J = \mathbb{E}_{x \sim G_\theta}\left[\frac{D(x)}{1 - D(x)} \nabla_\theta \log G_\theta(x)\right]$$

#### Tầng 3-4
**Trong dự án**: baseline trong Gumbel-Softmax benchmark.

### 8.5 RelGAN (Relational Memory GAN, 2019)

#### Tầng 1
Generator dùng **relational memory** (RMC) thay LSTM. Tốt hơn cho long sequence.

#### Tầng 2-4
Memory matrix $M$ với self-attention. **Trong dự án**: baseline.

### 8.6 StyleGAN, BigGAN, CycleGAN

Image-only. **Không dùng** trong dự án nhưng nên biết để literature awareness:
- **StyleGAN** (2018): style-based architecture, photorealistic.
- **BigGAN** (2018): scale + class-conditional, ImageNet SOTA.
- **CycleGAN** (2017): unpaired image-to-image translation.

---

## 9. VAE — Variational Autoencoder

### Tầng 1 — What / When / Why + ví dụ trẻ em

**VAE (Kingma & Welling 2013)** = autoencoder probabilistic — encoder map $x$ → distribution $q(z|x)$ thay vector cố định, decoder sample $z$ và sinh $x$. Khi: muốn AE có khả năng generate (sample $z$ random rồi decode). Vì sao: regular AE không sample được; VAE ép latent space có cấu trúc Gaussian.

> **Ví dụ trẻ em**: Regular AE = cuốn note **viết cố định** ("trang 1 = topic A, trang 2 = topic B"). VAE = cuốn note **viết với độ mờ** ("trang 1 = topic A nằm trong vùng [0.3, 0.7]"). Khi cần sample mới, mở random một điểm trong vùng → đọc ra một biến thể của topic A.

### Tầng 2 — Toán học (hàn lâm)

**Generative model**: $p_\theta(x) = \int p_\theta(x|z) p(z) dz$ với $p(z) = \mathcal{N}(0, I)$.

Likelihood intractable → tối ưu **ELBO** (Evidence Lower Bound):
$$\log p_\theta(x) \geq \mathbb{E}_{z \sim q_\phi(z|x)}[\log p_\theta(x|z)] - KL[q_\phi(z|x) \| p(z)]$$
$$= \text{ELBO}(x; \theta, \phi)$$

**VAE loss** (negative ELBO):
$$\mathcal{L}_{VAE} = -\mathbb{E}_{q_\phi(z|x)}[\log p_\theta(x|z)] + KL[q_\phi(z|x) \| p(z)]$$
$$= \mathcal{L}_{recon} + \mathcal{L}_{KL}$$

**Encoder** $q_\phi(z|x) = \mathcal{N}(\mu_\phi(x), \sigma_\phi^2(x))$ — output mean và log-variance.

**Decoder** $p_\theta(x|z)$ = NN output Bernoulli (binary) hoặc Gaussian (continuous) hoặc Categorical (discrete tokens).

**KL closed-form** (Gaussian):
$$KL[\mathcal{N}(\mu, \sigma^2) \| \mathcal{N}(0, 1)] = \frac{1}{2}\sum_i (\mu_i^2 + \sigma_i^2 - \log \sigma_i^2 - 1)$$

**β-VAE**: weight KL term với β:
$$\mathcal{L}_{\beta-VAE} = \mathcal{L}_{recon} + \beta \cdot \mathcal{L}_{KL}$$

$\beta > 1$: latent disentangled hơn. $\beta < 1$: better reconstruction.

**Phép toán nền tảng**: variational inference, ELBO, KL divergence, Gaussian distribution, log-likelihood.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **VAE pros**: principled probabilistic, smooth latent space, easy to interpolate.
- **VAE cons**: blurry/simpler outputs (KL pull về N(0,I)). Posterior collapse — KL → 0, latent không informative.
- **Posterior collapse**: powerful decoder ignore $z$, $q(z|x) \to p(z)$, KL → 0.
- **Mitigations**:
  - **KL annealing**: tăng β từ 0 → 1 trong $T$ steps đầu.
  - **Free bits**: $\max(KL, \lambda_{fb})$ — chỉ phạt KL trên ngưỡng.

**Trong dự án — VAE-GAN**: encoder Transformer, decoder Transformer, latent $z \in \mathbb{R}^{256}$, KL annealing 0→1 trong 10k steps, free bits $\lambda_{fb} = 2$ nats.

### Tầng 4 — Mặt dữ liệu

**Encoder output**: 2 vectors $\mu, \log \sigma^2 \in \mathbb{R}^{d_z}$.

**Sampling**: $z = \mu + \sigma \odot \epsilon$, $\epsilon \sim \mathcal{N}(0, I)$ (reparameterization — xem mục 12).

**Decoder output**: distribution over each token (categorical), parameterized by softmax logits.

---

## 10. Latent Space

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Latent space** = không gian thấp chiều $\mathcal{Z}$ chứa biểu diễn nén của data. Khi: trong VAE, GAN với $z$ explicit. Vì sao: cấu trúc trong $\mathcal{Z}$ phản ánh "manifold" của data — di chuyển trong $\mathcal{Z}$ → biến đổi smooth trong $\mathcal{X}$.

> **Ví dụ trẻ em**: Bản đồ thư viện. Ngoài đời, **quyển sách ($x$)** dày, nặng, không di chuyển dễ. Trên bản đồ, **vị trí sách ($z$)** chỉ là 1 điểm. Sách "Toán học" gần "Vật lý", xa "Thơ ca". Bạn có thể **đi từ Toán sang Vật lý** trên bản đồ — tương đương smooth interpolation. Cuốn sách thật không tự đi được.

### Tầng 2 — Toán học (hàn lâm)

$\mathcal{Z} = \mathbb{R}^{d_z}$ với $d_z \ll \dim(\mathcal{X})$.

**Properties (mong đợi)**:
- **Smoothness**: di chuyển $z$ → output thay đổi smooth.
- **Disentanglement**: từng chiều $z_i$ control 1 attribute độc lập.
- **Density**: vùng có density cao trong $\mathcal{Z}$ map sang vùng "in-distribution" trong $\mathcal{X}$.

**Latent walk** (interpolation):
$$z_t = (1-t) z_A + t z_B, \quad t \in [0, 1]$$

Spherical interpolation cho Gaussian latent:
$$\text{slerp}(z_A, z_B, t) = \frac{\sin((1-t)\theta)}{\sin\theta} z_A + \frac{\sin(t\theta)}{\sin\theta} z_B$$
$\theta$ = angle giữa $z_A, z_B$.

**Phép toán nền tảng**: manifold theory, spherical/linear interpolation, density estimation.

### Tầng 3 — Mặt trí tuệ nhân tạo

- VAE: latent = posterior mean $\mu$ hoặc sample $z$. Distribution biased về $\mathcal{N}(0, I)$.
- GAN: latent = noise input. Không có encoder, không thể "encode" $x$ → $z$.
- **Trong dự án — VAE-GAN claim chính**: latent space tách biệt được "SQL thuần túy" vs "SQL ngụy trang" → có thể control kiểu attack qua $z$.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**: $z \in \mathbb{R}^{256}$, prior $\mathcal{N}(0, I)$.

**Latent walk experiment**: chọn 2 payload $x_A, x_B$ → encode → $z_A, z_B$ → walk → decode mỗi điểm → quan sát chuỗi payload trung gian. Định tính, không phải metric chính.

---

## 11. KL Divergence

### Tầng 1 — What / When / Why + ví dụ trẻ em

**KL divergence** = đo "khác nhau" giữa 2 phân phối. Khi: trong VAE loss, distribution matching, regularization. Vì sao: cần con số đại diện "$q$ khác $p$ bao nhiêu".

> **Ví dụ trẻ em**: 2 hộp kẹo. Hộp $P$ thật có 50% sô-cô-la, 50% kẹo dẻo. Hộp $Q$ giả có 80% sô-cô-la, 20% kẹo dẻo. KL nói **dùng $Q$ để dự đoán hộp $P$, sai nhiều bao nhiêu**? Càng khác nhau, KL càng cao. KL = 0 chỉ khi 2 hộp y hệt.

### Tầng 2 — Toán học (hàn lâm)

**Định nghĩa** (cho discrete):
$$KL(P \| Q) = \sum_x P(x) \log \frac{P(x)}{Q(x)}$$

(Continuous: thay sum bằng integral.)

**Tính chất**:
- $KL(P \| Q) \geq 0$ (Gibbs' inequality).
- $KL(P \| Q) = 0 \iff P = Q$ a.e.
- **Asymmetric**: $KL(P\|Q) \neq KL(Q\|P)$.
- Không phải metric (không thỏa triangle inequality).

**Forward vs Reverse KL**:
- $KL(P \| Q)$ = "mode-covering" — penalty cao nếu $Q(x) = 0$ where $P(x) > 0$ → $Q$ phải cover mọi mode của $P$.
- $KL(Q \| P)$ = "mode-seeking" — $Q$ có thể tập trung 1 mode của $P$.

**Closed-form** (2 Gaussians):
$$KL[\mathcal{N}(\mu_1, \Sigma_1) \| \mathcal{N}(\mu_2, \Sigma_2)] = \frac{1}{2}\left[\log\frac{|\Sigma_2|}{|\Sigma_1|} - d + \text{tr}(\Sigma_2^{-1}\Sigma_1) + (\mu_2-\mu_1)^T \Sigma_2^{-1}(\mu_2-\mu_1)\right]$$

**Mutual Information** quan hệ với KL:
$$I(X;Y) = KL[P(X,Y) \| P(X)P(Y)]$$

**Phép toán nền tảng**: information theory, Shannon entropy, Gibbs' inequality.

### Tầng 3 — Mặt trí tuệ nhân tạo

- KL trong VAE = regularize encoder $q(z|x)$ về prior $p(z)$.
- KL trong knowledge distillation = student match teacher distribution.
- **Trong dự án**:
  - VAE-GAN: KL annealing để tránh posterior collapse (β: 0 → 1).
  - Original GAN: minimize JSD (related to KL).
  - WGAN: replaces KL/JSD bằng Wasserstein → better gradients.

### Tầng 4 — Mặt dữ liệu

**Đơn vị**: nats (log $e$) hoặc bits (log 2).

**Trong dự án — VAE-GAN Roadmap**:
> "Train encoder-decoder như VAE thuần túy cho đến khi: ... KL divergence nằm trong khoảng [5, 50] nats."
> "Free bits $\lambda_{fb} = 2$ nats per dimension như backstop phòng posterior collapse."

---

## 12. Reparameterization Trick

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Reparameterization trick** = trick để gradient flow qua sampling step. Khi: trong VAE training. Vì sao: $z \sim q(z|x)$ là stochastic, gradient không pass qua sampling. Trick chuyển sampling thành deterministic transform của random noise.

> **Ví dụ trẻ em**: Bạn cần "đo nhiệt độ giữa mong đợi và phương sai". 
> - **Cách 1 (không trick)**: lấy nhiệt kế random từ kho → đo. Bạn không kiểm soát nhiệt kế nào → khó học.
> - **Cách 2 (có trick)**: lấy 1 nhiệt kế chuẩn (random noise $\epsilon$ định trước) → **bạn calibrate** ($\mu, \sigma$) → đọc $z = \mu + \sigma \epsilon$. Bây giờ $\mu, \sigma$ là **knobs** bạn tune được.

### Tầng 2 — Toán học (hàn lâm)

**Vấn đề**: cần $\nabla_\phi \mathbb{E}_{z \sim q_\phi(z|x)}[f(z)]$ nhưng sampling không differentiable theo $\phi$.

**Trick**: viết $z$ như deterministic function của $\phi$ và noise $\epsilon$:
$$z = g_\phi(\epsilon, x), \quad \epsilon \sim p(\epsilon) \text{ (independent of } \phi\text{)}$$

Cho Gaussian:
$$z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

Bây giờ:
$$\nabla_\phi \mathbb{E}_{z \sim q_\phi}[f(z)] = \mathbb{E}_{\epsilon}[\nabla_\phi f(g_\phi(\epsilon, x))]$$

→ gradient pass qua $\mu_\phi, \sigma_\phi$ thông qua chain rule.

**Generalize** cho continuous distributions có **invertible CDF**: 
$$z = F^{-1}(u; \phi), \quad u \sim U(0, 1)$$

**Cho discrete**: cần Gumbel-Softmax (xem File 03 hoặc Roadmap Gumbel).

**Phép toán nền tảng**: change of variables, deterministic-stochastic decomposition, gradient of expectation.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Reparam trick là innovation chính của VAE — cho phép end-to-end backprop qua probabilistic encoder.
- Tương tự trick: **Gumbel-Softmax** cho discrete (continuous relaxation).

### Tầng 4 — Mặt dữ liệu

**Implementation** (PyTorch):
```python
def sample_z(mu, log_var):
    std = torch.exp(0.5 * log_var)
    eps = torch.randn_like(std)
    return mu + std * eps
```

**Trong dự án — VAE-GAN encoder forward**:
```python
mu, log_var = encoder(x)         # (B, 256), (B, 256)
z = mu + torch.exp(0.5*log_var) * torch.randn_like(mu)
recon = decoder(z)
```

---

## 13. Tổng kết — Kết nối với 3 approach của dự án

| Concept | VAE-GAN | SeqGAN | Gumbel-Softmax |
|---|---|---|---|
| GAN G/D | ✅ Both | ✅ Both | ✅ Both |
| WGAN-GP | ✅ Adversarial phase | ✅ Discriminator | ✅ Core loss |
| Mode collapse mitigation | KL anneal + dropout | Variance check + dropout | Temp reset + dropout |
| VAE component | ✅ Encoder + KL + free bits | ❌ | ❌ |
| Latent space (structured) | ✅ z ∈ R^256 | ❌ | ❌ |
| KL divergence | ✅ Loss term | ❌ | ⚠️ (cho replaced JSD) |
| Reparameterization | ✅ z = μ + σε | ❌ | Gumbel-Softmax variant |
| Cross-attention | ✅ Decoder ← z | ❌ | ❌ |
| Policy gradient (REINFORCE) | ❌ | ✅ Core | ❌ |
| Gumbel-Softmax sampling | ✅ Cho discrete decode | ❌ | ✅ Core |

---

## 14. Tài liệu tham chiếu chéo

- File 01-03 — Foundations (NN, CNN/RNN, Transformer/Attention).
- 3 Roadmap files:
  - `SQLi-VAE-GAN-Roadmap.md`
  - `SQLi-SeqGAN-Roadmap.md`
  - `SQLi-Gumbel-SoftmaxGAN-Roadmap.md`
- 3 Guiding files (sẽ tạo):
  - `VAE-GAN_SQLi/Guiding.md`
  - `SeqGAN_SQLi/Guiding.md`
  - `Gumbel-Softmax_SQLi/Guiding.md`
- `Onboarding_AI_Knowledge_04_*.md` — bản đơn giản hóa cho member không-tech.

## 15. Đọc thêm

- **Goodfellow et al. 2014** — "Generative Adversarial Networks" (paper gốc GAN).
- **Kingma & Welling 2013** — "Auto-Encoding Variational Bayes" (paper VAE).
- **Arjovsky et al. 2017** — "Wasserstein GAN".
- **Gulrajani et al. 2017** — "Improved Training of Wasserstein GANs" (WGAN-GP).
- **Yu et al. 2016** — "SeqGAN: Sequence GAN with Policy Gradient".
- **Jang et al. 2016** — "Categorical Reparameterization with Gumbel-Softmax".
- **Higgins et al. 2017** — "β-VAE: Learning Basic Visual Concepts with a Constrained Variational Framework".
- **Lilian Weng's blog** — "From GAN to WGAN" (consolidated overview).
