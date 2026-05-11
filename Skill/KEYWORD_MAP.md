# Keyword Map — 7 nhóm trọng tâm

> **Mục đích**: Tra cứu nhanh hệ thống keyword theo cây phân cấp. Dùng kèm mindmap text (đọc từ gốc → lá). 
> **Ký hiệu**: `→ (xem N.x)` = keyword có liên kết sang nhóm khác; `[M]` = must-know; `[A]` = advanced.

---

## N1. Neural Network & Training

```
Neural Network (NN) [M]
├── Neuron (Perceptron)
│   ├── Weight & Bias [M]
│   │   ├── Weight Matrix W
│   │   ├── Bias Vector b
│   │   ├── Weight Initialization
│   │   │   ├── Xavier / Glorot (tanh, sigmoid)
│   │   │   ├── He (ReLU)
│   │   │   └── Bias init = 0
│   │   ├── Regularization [M]
│   │   │   ├── L2 / Weight Decay
│   │   │   ├── L1 (sparsity)
│   │   │   └── Dropout
│   │   └── Quantization (float32 → int8)
│   ├── Activation Function [M]
│   │   ├── Sigmoid (saturate, vanishing) → (xem N2: Vanishing Gradient)
│   │   ├── Tanh
│   │   ├── ReLU (phi tuyến, không saturate positive)
│   │   └── GELU (CDF chuẩn N(0,1))
│   └── Universal Approximation Theorem
├── MLP (Multilayer Perceptron) [M]
│   ├── Fully Connected Layer (dense)
│   ├── Parameter Count Σ(dₗ·dₗ₋₁ + dₗ)
│   └── Output Activation [M]
│       ├── Linear (regression)
│       ├── Sigmoid (binary classification)
│       └── Softmax (multi-class, smooth argmax)
├── Forward Pass [M]
│   ├── zₗ = Wₗ·hₗ₋₁ + bₗ (affine)
│   ├── hₗ = φₗ(zₗ) (activation)
│   ├── Batched Forward: matrix-matrix product
│   ├── Intermediate Activations (lưu cho backward)
│   └── Inference vs Training Mode
├── Loss Function [M]
│   ├── MSE / MAE (regression)
│   ├── Cross-Entropy / BCE (classification)
│   ├── KL Divergence [A] → (xem N4: KL Divergence)
│   ├── Adversarial Loss (GAN: log D, -log D)
│   ├── Wasserstein Loss (WGAN: E[D(x)] - E[D(G(z))])
│   ├── Multi-component Loss
│   │   ├── L_total = L_task + λ₁L_reg + λ₂L_aux
│   │   └── Weight Balancing (λ₁, λ₂)
│   └── Surrogate Loss (differentiable)
├── Gradient & Đạo hàm [M]
│   ├── Gradient ∇f (vector đạo hàm riêng)
│   ├── Chain Rule: ∂f(g(x))/∂x = f'·g'
│   ├── Jacobian (vector → vector)
│   ├── Hessian (đạo hàm cấp 2)
│   ├── Autograd (automatic differentiation) [M]
│   │   ├── PyTorch / TF / JAX
│   │   ├── Eager vs Graph Mode
│   │   └── Gradient Checkpointing
│   └── Gradient Flow Problems [M]
│       ├── Vanishing Gradient → (xem N2)
│       ├── Exploding Gradient
│       └── Gradient Clipping (||∇|| ≤ c)
├── Backpropagation [M]
│   ├── Chain Rule qua dynamic programming
│   ├── δ⁽ˡ⁾ = (W⁽ˡ⁺¹⁾)ᵀ δ⁽ˡ⁺¹⁾ ⊙ φ'(z⁽ˡ⁾)
│   ├── Computational Cost O(P)
│   └── Gradient Through Stochastic Ops [A]
│       ├── Reparameterization Trick → (xem N4)
│       ├── Gumbel-Softmax → (xem N4)
│       └── REINFORCE / Score Function → (xem N5)
├── Learning Rate (η) [M]
│   ├── LR Schedule [A]
│   │   ├── Step Decay: ηₜ = η₀ · γ^⌊t/T⌋
│   │   ├── Exponential Decay
│   │   ├── Cosine Annealing
│   │   ├── Warmup + Cosine
│   │   └── ReduceLROnPlateau
│   ├── LR Range Test (scan 1e-7 → 1e0)
│   └── Per-parameter LR (Adam)
└── Optimizer [M]
    ├── SGD + Momentum
    │   └── Nesterov Momentum (look-ahead)
    ├── AdaGrad (per-parameter, G accumulates)
    ├── RMSprop (EMA of squared gradient)
    ├── Adam [M]
    │   ├── mₜ (1st moment / EMA gradient)
    │   ├── vₜ (2nd moment / EMA squared gradient)
    │   ├── Bias Correction (m̂, v̂)
    │   └── Default β₁=0.9, β₂=0.999
    ├── AdamW (decoupled weight decay)
    └── GAN-specific Adam (β₁=0.5) [A]
```

---

## N2. CNN / RNN / LSTM / GRU

```
CNN (Convolutional Neural Network) [M]
├── Convolution [M]
│   ├── 1D Convolution (sequence)
│   ├── 2D Convolution (image)
│   ├── Cross-correlation (DL convention)
│   └── Multi-channel (C_in → C_out)
├── Kernel / Filter [M]
│   ├── Kernel Size (thường lẻ: 3, 5, 7)
│   ├── Number of Filters (C_out)
│   └── Stack small kernels (VGG: 3×3 stack)
├── Stride (s)
│   ├── s=1: preserve spatial dim
│   ├── s=2: halve dim (thay Pooling)
│   └── Output Size Formula
├── Padding [M]
│   ├── Same (output = input size)
│   ├── Valid (P=0, output co lại)
│   └── Causal (pad trái, cho autoregressive)
├── Pooling [A]
│   ├── Max Pooling
│   ├── Average Pooling
│   ├── Global Pooling (per channel → scalar)
│   └── Trend: Strided Conv thay Pooling
├── Inductive Bias của CNN [M]
│   ├── Locality (neighborhood connections)
│   ├── Translation Equivariance
│   │   └── f(shift(x)) = shift(f(x))
│   └── Weight Sharing (shared kernel across space)
├── Receptive Field (RF)
│   ├── RF tăng dần qua các layer
│   └── Low-level → High-level features
├── TextCNN (Kim 2014) [A]
│   ├── 1D CNN kernels [3,4,5] cho n-gram
│   └── Max-over-time pooling
└── Dilated CNN (Atrous Convolution) [A]
    ├── Dilation Rate r
    │   └── O(i) = Σ I(i + r·m) K(m)
    ├── Receptive Field: RF = 1 + Σ(M-1)·rₗ
    ├── Exponential Dilation (rₗ = 2ˡ⁻¹)
    │   └── WaveNet (audio, RF hàng chục nghìn)
    └── Multi-scale kernels cho SQL hierarchy [A]
        ├── [2,3]: toán tử + keyword kép (UNION SELECT)
        ├── [5,8]: mệnh đề đơn (WHERE id = <NUM>)
        └── [12,16]: subquery lồng nhau

───────────

RNN Family [M]
├── Vanilla RNN (Elman 1990)
│   ├── Hidden State hₜ = φ(W_hh·hₜ₋₁ + W_xh·xₜ + bₕ)
│   ├── Weight Tied qua các bước thời gian
│   ├── BPTT (Backprop Through Time)
│   │   └── Jacobian Product Chain → Vanish/Explode
│   └── Limitations [M]
│       ├── Sequential → không parallel
│       ├── Vanishing Gradient cho long-range
│       └── Bị Transformer thay thế sau 2017
├── Vanishing & Exploding Gradient [M]
│   ├── Spectral Analysis: eigenvalue λ_max của W_hh
│   ├── Mitigations [M]
│   │   ├── Gradient Clipping (cho exploding)
│   │   ├── ReLU Activation (không saturate)
│   │   ├── LSTM / GRU (gated flow)
│   │   ├── Skip / Residual Connections
│   │   └── Spectral Normalization
│   └── Vấn đề chung với GAN [A]
│       ├── D quá mạnh → G gradient vanish
│       └── WGAN-GP mitigates → (xem N4)
├── LSTM (Long Short-Term Memory) [M]
│   ├── Cell State cₜ (gradient highway)
│   ├── Gating Mechanism [M]
│   │   ├── Forget Gate fₜ (σ): quyết định xóa
│   │   ├── Input Gate iₜ (σ): quyết định ghi
│   │   ├── Candidate c̃ₜ (tanh): nội dung mới
│   │   ├── cₜ = fₜ ⊙ cₜ₋₁ + iₜ ⊙ c̃ₜ (update)
│   │   └── Output Gate oₜ (σ): quyết định đọc
│   ├── Hidden State hₜ = oₜ ⊙ tanh(cₜ)
│   ├── Gradient Flow: ∂cₜ/∂cₜ₋₁ = fₜ ∈ [0,1]ᵈ
│   ├── Parameter Count: 4×(dₕ·(dₕ+dₓ) + dₕ)
│   └── Variants
│       ├── Bidirectional LSTM (forward + backward)
│       ├── Stacked LSTM (multi-layer)
│       └── Peephole LSTM (+ cell state vào gates)
└── GRU (Gated Recurrent Unit) [A]
    ├── 2 Gates vs LSTM 3 Gates
    │   ├── Update Gate zₜ: overwrite ratio
    │   ├── Reset Gate rₜ: forget ratio
    │   └── hₜ = (1-zₜ)⊙hₜ₋₁ + zₜ⊙h̃ₜ
    ├── Parameter Count: 3×(dₕ·(dₕ+dₓ) + dₕ)
    ├── So sánh LSTM vs GRU
    │   ├── GRU: nhanh hơn ~30%, comparable accuracy
    │   └── LSTM: expressive hơn cho rất long sequence
    └── Trong SeqGAN: có thể dùng GRU thay LSTM
```

---

## N3. Attention & Transformer

```
Self-Attention [M]
├── Query (Q): "tôi đang tìm gì"
├── Key (K): "tôi có nội dung gì để được tìm"
├── Value (V): "nội dung tôi trả khi được chọn"
├── Scaled Dot-Product Attention [M]
│   ├── Attention(Q,K,V) = softmax(Q·Kᵀ / √dₖ) · V
│   ├── Step 1: Q·Kᵢ ∈ ℝᴸˣᴸ (scores)
│   ├── Step 2: Scale ÷ √dₖ (stabilize gradient)
│   ├── Step 3: softmax (row = distribution)
│   └── Step 4: Weighted sum of V
├── Computational Complexity O(L²·d)
├── Causal Mask (autoregressive) [M]
│   └── M_ij = -∞ nếu j > i (không nhìn tương lai)
├── Attention Pattern Interpretability
└── So sánh: Self vs Cross → (xem Cross-Attention)

───────────

Multi-Head Attention (MHA) [M]
├── h heads song song, mỗi head 1 pattern riêng
├── head_i = Attention(X·W_Q_i, X·W_K_i, X·W_V_i)
├── d_k = d / h (head dimension)
├── Concat(head₁,...,headₕ) · W_O
├── Parameter Count: 4d² (không phụ thuộc số head)
└── Phổ biến: h=8, d=512, d_k=64

───────────

Cross-Attention [M]
├── Q từ target sequence, K/V từ source sequence
├── CrossAttn(X_tgt, X_src) = softmax((X_tgtW_Q)(X_srcW_K)ᵀ/√dₖ)·(X_srcW_V)
├── Là cầu nối Encoder ↔ Decoder [M]
└── VAE-GAN Decoder: cross-attend vào latent z [A]

───────────

Positional Encoding (PE) [M]
├── Why: Attention không có thứ tự inherent
├── Sinusoidal PE (Vaswani 2017)
│   ├── PE(pos, 2i) = sin(pos/10000²ⁱ/ᵈ)
│   ├── PE(pos, 2i+1) = cos(pos/10000²ⁱ/ᵈ)
│   ├── PE(pos+k) linear from PE(pos)
│   └── Generalize đến sequence dài hơn
├── Learned PE (BERT, GPT) — fix L_max
├── Modern PE [A]
│   ├── RoPE (Rotary): rotate Q,K theo position
│   └── ALiBi: bias attention scores theo distance
└── Without PE: Transformer = bag of tokens

───────────

Encoder Block [M]
├── Multi-Head Self-Attention (bidirectional)
├── Feed-Forward Network (d → 4d → d, GELU/ReLU)
├── LayerNorm (stabilize training)
├── Residual Connection (x + F(x))
└── Parameter Count per block: ~12d²

Decoder Block [M]
├── Masked Multi-Head Self-Attention (causal)
├── Cross-Attention (attend vào encoder output)
├── Feed-Forward Network
├── LayerNorm + Residual
└── Parameter Count: ~14d² (extra cross-attn)

───────────

Full Transformer Architecture [M]
├── Encoder-Decoder (Vaswani 2017)
│   ├── N encoder stacks → H_enc
│   ├── N decoder stacks (autoregressive)
│   ├── P(yₜ | y_<t, x) = softmax(H_dec·W_vocab)
│   └── Examples: T5, BART
├── Encoder-Only (BERT)
│   └── Masked Language Model, Classification
├── Decoder-Only (GPT, LLaMA)
│   └── Autoregressive generation
├── Scale: Original 65M → BERT 110M → GPT-3 175B
└── Strengths vs Weaknesses [M]
    ├── +: Parallel, Long-range, Scale extremly well
    └── -: O(L²), Need PE, Large data required

───────────

Autoencoder (AE) [M]
├── Encoder E_φ: X → Z (bottleneck)
├── Decoder D_ψ: Z → X (reconstruction)
├── Loss: L_AE = ||x - D(E(x))||²
├── Bottleneck: dim(Z) << dim(X)
├── Variants
│   ├── Denoising AE (input x + ε)
│   ├── Sparse AE (sparsity penalty on z)
│   └── Variational AE (VAE) → (xem N4)
└── Limitation: Không generative (cần VAE)

───────────

Seq2seq Paradigm [M]
├── Mapping: Chuỗi → Chuỗi (khác độ dài)
├── P(y|x) = ∏ₜ P(yₜ | y_<t, x) (AR factorization)
├── MLE Loss: - Σ log P_θ(yₜ* | y_<t*, x)
├── Beam Search (keep top-k beams)
└── Evolution: RNN → +Attention → Transformer

───────────

Autoregressive Generation [M]
├── P(y₁,...,y_T) = ∏ P(yₜ | y_<t) (chain rule)
├── Sampling Strategies [M]
│   ├── Greedy: yₜ = argmax P (có thể repetitive)
│   ├── Beam Search: top-k candidates
│   ├── Random Sampling: yₜ ~ P(·)
│   ├── Top-k Sampling: filter top-k tokens
│   ├── Top-p / Nucleus: smallest set with cumprob ≥ p
│   └── Temperature: P_τ(v) ∝ P(v)^(1/τ)
├── Teacher Forcing [M]
│   ├── Train: feed ground-truth yₜ₋₁*
│   ├── Inference: feed own prediction ŷₜ₋₁
│   └── Exposure Bias (distribution mismatch)
├── Scheduled Sampling [A]
│   └── Gradually replace GT với prediction
└── RL Approach: SeqGAN → (xem N5)
```

---

## N4. GAN / WGAN / VAE

```
GAN (Generative Adversarial Network) [M]
├── Generator G_θ: Z → X (noise → sample)
│   ├── G Architectures [M]
│   │   ├── Image: DCGAN, ResNet (BigGAN), StyleGAN
│   │   ├── Audio: Dilated Conv (WaveGAN)
│   │   ├── Text: LSTM (SeqGAN), Transformer + Gumbel-Softmax
│   │   └── Tabular: MLP
│   ├── G Input: Noise z ~ N(0,I), d_z = 100-512
│   └── G Text Output Layers
│       ├── Embedding Layer
│       ├── LSTM / Transformer Decoder
│       ├── Output Projection W_out ∈ ℝᵈˣⱽ
│       └── Sampling Layer: Argmax / Gumbel-Softmax / Multinomial
├── Discriminator D_φ: X → [0,1] (hoặc ℝ cho WGAN)
│   ├── D Architectures [M]
│   │   ├── TextCNN (kernels [3,4,5]) [A]
│   │   └── Dilated CNN (kernels [2,3,5,8,12,16]) [A]
│   ├── D Layers
│   │   ├── Embedding Layer
│   │   ├── Convolutional Layers (TextCNN / Dilated)
│   │   ├── Pooling (max-over-time)
│   │   ├── MLP Head
│   │   └── Output: Sigmoid (GAN) / Linear (WGAN)
│   ├── Spectral Normalization [A]
│   │   └── W̄ = W / σ(W) — ||D||_Lip ≤ 1
│   ├── Feature Matching [A]
│   │   └── L_fm = ||E[f(x_real)] - E[f(G(z))]||²
│   └── D:G Ratio (thường 1:1 → 5:1)
├── Minimax Game (Original GAN) [M]
│   ├── min_G max_D V(D,G) = E[log D(x)] + E[log(1-D(G(z)))]
│   ├── Optimal D: D*(x) = p_data / (p_data + p_g)
│   ├── V(D*, G) = -log 4 + 2·JSD(p_data || p_g)
│   ├── JSD (Jensen-Shannon Divergence)
│   │   └── JSD(P||Q) = ½KL(P||(P+Q)/2) + ½KL(Q||(P+Q)/2)
│   ├── Non-saturating G Loss [M]
│   │   └── L_G = -E_z[log D(G(z))] (thay log(1-D))
│   └── Training Instability → WGAN
├── GAN Training Loop [M]
│   └── Alternating: Step D (k times) → Step G (1 time)
├── Mode Collapse [M]
│   ├── G chỉ sinh 1 vài modes của p_data
│   ├── Detection [M]
│   │   ├── Self-BLEU (cao = collapse) → (xem N9)
│   │   ├── Pairwise Edit Distance (thấp = collapse) → (xem N9)
│   │   ├── Inception Score (thấp = collapse)
│   │   └── FID (Fréchet Inception Distance, cao = collapse)
│   ├── Nguyên nhân: JSD saturate khi disjoint support
│   └── Mitigations [M]
│       ├── WGAN-GP (Wasserstein, gradient flow) [M]
│       ├── Minibatch Discrimination
│       ├── Unrolled GAN
│       ├── Increase Dropout in G
│       ├── Inject Noise vào Latent
│       └── Diversity-Promoting Loss
└── GAN Variants [A]
    ├── DCGAN (Deep Conv GAN, image)
    ├── cGAN (Conditional GAN: G(z,y), D(x,y))
    ├── SeqGAN (policy gradient for text) → (xem N5)
    ├── MaliGAN (MLE-augmented gradient)
    ├── RelGAN (Relational Memory Generator)
    ├── StyleGAN (style-based, photorealistic)
    ├── BigGAN (scale + class-conditional)
    └── CycleGAN (unpaired image translation)

───────────

WGAN (Wasserstein GAN) [M]
├── Wasserstein-1 Distance (Earth Mover's)
│   └── W₁(P,Q) = inf_{γ∈Π(P,Q)} E[||x - y||]
├── Kantorovich-Rubinstein Duality [A]
│   └── W₁(P,Q) = sup_{||f||_L ≤ 1} E_P[f] - E_Q[f]
├── Critic (thay Discriminator, output ℝ, không sigmoid)
├── 1-Lipschitz Constraint [M]
│   └── |f(x) - f(y)| ≤ ||x - y||
├── WGAN Objective
│   └── min_G max_f: E[D(x)] - E[D(G(z))]
└── Weight Clipping (original WGAN) [A]
    └── w ← clip(w, -c, c) — capacity loss, gradient issue

───────────

WGAN-GP (Gradient Penalty) [M]
├── GP thay Weight Clipping (ép Lipschitz mềm)
├── D Loss: E[D(G(z))] - E[D(x)] + λ_gp · E[(||∇D(ẑ)||₂ - 1)²]
├── Random Interpolation ẑ = εx + (1-ε)G(z), ε~U(0,1)
├── λ_gp = 10 (default)
├── G Loss (unchanged): -E_z[D(G(z))]
├── No BatchNorm in D (BN breaks GP)
├── D:G = 5:1 (recommended)
├── Adam β=(0.5, 0.9) (GAN-specific)
└── Default training scheme cho modern GAN [M]

───────────

VAE (Variational Autoencoder) [M]
├── Generative Model: p_θ(x) = ∫ p_θ(x|z) p(z) dz
├── Encoder q_φ(z|x) = N(μ_φ(x), σ_φ²(x))
│   └── Output: μ ∈ ℝᵈᶻ, log σ² ∈ ℝᵈᶻ
├── Decoder p_θ(x|z): NN → distribution over x
├── ELBO (Evidence Lower Bound) [M]
│   ├── log p(x) ≥ E_q[log p(x|z)] - KL[q(z|x) || p(z)]
│   └── = -L_VAE (training loss)
├── VAE Loss: L_recon + L_KL [M]
│   ├── L_recon: -E_q[log p(x|z)] (reconstruction)
│   ├── L_KL: KL[q(z|x) || p(z)] (regularization)
│   └── β-VAE: L = L_recon + β·L_KL
├── Posterior Collapse [A]
│   ├── KL → 0, latent không informative
│   ├── Mitigations
│   │   ├── KL Annealing: β: 0 → 1 (giảm dần)
│   │   └── Free Bits: max(KL_i, λ_fb) per dim
│   └── Monitor: KL ∈ [5, 50] nats OK
└── Reparameterization Trick [M]
    ├── z = μ + σ·ε, ε ~ N(0,I)
    ├── Gradient flow qua μ, σ (deterministic)
    ├── Cho discrete: Gumbel-Softmax
    └── Innovation chính cho VAE training

───────────

Latent Space Z [M]
├── Z = ℝᵈᶻ, d_z << dim(X)
├── Properties
│   ├── Smoothness: di chuyển z → output thay đổi smooth
│   ├── Disentanglement: từng dim z_i control 1 attribute
│   └── Density: vùng density cao → in-distribution output
├── Latent Walk / Interpolation [A]
│   ├── Linear: z_t = (1-t)z_A + t·z_B
│   └── Slerp (Spherical): cho Gaussian latent
├── VAE: latent = posterior mean hoặc sample
├── GAN: latent = noise input (không có encoder)
└── VAE-GAN Claim: latent separation "SQL thuần" vs "ngụy trang"

───────────

KL Divergence [M]
├── Definition: KL(P||Q) = Σ P(x) log(P(x)/Q(x))
├── Properties
│   ├── KL ≥ 0 (Gibbs' inequality), = 0 iff P=Q
│   ├── Asymmetric: KL(P||Q) ≠ KL(Q||P)
│   └── Không phải metric (no triangle inequality)
├── Forward KL (mode-covering) vs Reverse KL (mode-seeking)
├── Closed-form Gaussian KL
│   └── KL[N(μ,σ²)||N(0,1)] = ½Σ(μ_i² + σ_i² - log σ_i² - 1)
├── Mutual Information: I(X;Y) = KL[P(X,Y)||P(X)P(Y)]
└── Unit: nats (ln) hoặc bits (log₂)
```

---

## N5. SeqGAN (Policy Gradient / REINFORCE)

```
Policy Gradient (REINFORCE) [M]
├── State sₜ = chuỗi đã sinh (0..t)
├── Action aₜ = next token từ vocab
├── Policy π_θ(aₜ|sₜ) = distribution over vocab
├── ∇J(θ) = E_τ[ Σ A(sₜ,aₜ) · ∇log π_θ(aₜ|sₜ) ]
├── Advantage A(s,a) = Q(s,a) - b(s) [M]
│   ├── Q(s,a) = expected cumulative reward
│   └── b(s) = baseline (value function)
├── Likelihood Ratio Trick [A]
│   └── ∇π = π · ∇log π (score function)
├── Variance Reduction [M]
│   ├── Baseline b(s) (giảm variance)
│   └── MC Rollout (estimate Q)
├── MDP Formulation (Markov Decision Process)
├── REINFORCE Theorem (Williams 1992)
├── Unbiased Estimator (nhưng high variance)
└── Gradient Variance → Mitigations
    ├── Baseline Network
    ├── Gradient Clipping (||∇|| ≤ 1.0)
    └── Larger Batch / Reward Normalization

───────────

Monte Carlo Rollout [M]
├── Tại mỗi step t: sinh K rollouts đầy đủ → T
├── Q(sₜ, aₜ) ≈ (1/K) Σ R(τ⁽ᵏ⁾)
├── Rollout Policy = chính π_θ (on-policy)
├── K = 16 (trade-off variance vs compute)
├── Compute Cost O(K·L) extra forward passes
└── Credit Assignment: reward sparse → MC phân bổ về intermediate steps

───────────

MLE Pretraining [M]
├── L_MLE = - Σ log π_θ(xₜ* | x_<t*)
├── Teacher Forcing → (xem N3: Teacher Forcing)
├── Scheduled Sampling [M]
│   └── ε: 0→1 (thay GT bằng prediction dần)
├── Expert Demonstrations [A]
│   ├── Payload đã bypass WAF
│   ├── Upweighted (2-3×) trong MLE pretrain
│   └── Chiếm ~5-10% training set
└── Baseline cho adversarial phase

───────────

Discriminator (SeqGAN) [A]
├── 1D-CNN / TextCNN (kernels [3,4,5])
├── WGAN-GP Loss → (xem N4: WGAN-GP)
├── D:G = 5:1 (WGAN-GP standard)
└── D output = one component of total reward

───────────

Reward Shaping [M]
├── r_total = λ_D·D(x) + λ_bypass·r_bypass + λ_syntax·r_syntax
│   ├── λ_D = 0.3, λ_bypass = 0.5, λ_syntax = 0.2 (init)
│   └── r_bypass: ModSecurity WAF Oracle
│       └── r_syntax: sqlparse check
├── Reward Sparse (chỉ tại terminal state)
├── Reward Hacking Prevention
│   ├── Length Penalty
│   ├── Semantic Check
│   └── Min Attack Length
└── WAF Overfitting → Multi-WAF Training

───────────

Baseline Value Network [A]
├── b_ψ(sₜ): MLP nhỏ on hidden state
├── Train with MSE: L = (1/T) Σ (b_ψ(sₜ) - Q(sₜ,aₜ))²
└── EMA Decay 0.95 (stability)

───────────

V2 Enhancements (Composite Reward) [A]
├── WAFOracle (ModSecurity Docker, CRS v4.3.0)
│   ├── anomaly_score (int, OWASP)
│   └── Boundary-Aware Reward [A]
│       ├── r_boundary(score): reward cao nhất sát threshold
│       └── Chống reward hacking (không chỉ bypass dễ)
├── CustomRuleEngine (5 rules anti-noise)
│   ├── SQLi keyword check
│   ├── Quoting / Comment check
│   ├── Length check (≥ 5 chars)
│   ├── Non-benign check
│   └── Operator / Query keyword check
├── SQLParserGate (syntax gate, multiplicative)
├── DBSandbox (SQLite execution gate)
│   └── Executable check (không SyntaxError)
├── ASTFingerprintTracker (diversity reward)
│   ├── Subtree hashing (depth=3)
│   └── novelty_score = 1 - max_sim(cache)
├── CompositeReward Formula [M]
│   └── r = syntax_gate × executable_gate × (w_owasp·r_boundary + w_custom·r_custom + w_diversity·novelty - w_overlap·overlap_penalty)
├── 3-Phase Curriculum [M]
│   ├── MLE Pretrain (gold+silver data, 10 epochs)
│   ├── Warmup Adversarial (0-2k steps, syntax+custom only)
│   ├── Main Adversarial (2k-15k, full composite)
│   └── Refinement (15k-20k, diversity-weighted)
├── Conditional Generator (attack_type embedding)
│   └── 8 attack types: error_based, boolean_blind, time_blind, union_based, heavy_query, auth_bypass, out_of_band, other
├── Reward Cache (LRU, max 100k entries)
└── V2 Key Differences from V1
    ├── Heuristic proxy → OWASP CRS composite
    ├── No diversity → AST diversity reward
    ├── Unconditional → Conditional (attack type)
    ├── Single metric → 5-metric ensemble → (xem N9)
    └── One-phase → 3-phase curriculum
```

---

## N8. Data Engineering

```
Tokenization [M]
├── Hàm tok: Σ* → V* (string → token IDs)
├── Vocabulary V (tập hữu hạn tokens)
├── Special Tokens [M]
│   ├── <PAD>=0 (padding)
│   ├── <UNK>=1 (out-of-vocabulary)
│   ├── <SOS>=2 (start of sequence)
│   ├── <EOS>=3 (end of sequence)
│   └── Placeholders: <TABLE>, <COL>, <NUM>, <STR>
├── Tokenizer Families
│   ├── Whitespace (đơn giản, không học)
│   ├── Regex-based (SQL-aware, cho dự án này) [M]
│   ├── BPE (Byte-Pair Encoding, data-driven)
│   └── WordPiece / SentencePiece
├── Quality Metrics
│   ├── Compression Ratio
│   ├── OOV Rate
│   └── Entropy Preservation
├── Lưu ý: KHÔNG dùng BPE pretrained (GPT-2) cho SQL
└── Output: list[int] | list[str], shape (B, L)

───────────

Normalization [M]
├── Hàm idempotent N: Σ* → Σ*, N(N(x)) = N(x)
├── Pipeline các bước [M]
│   ├── N_url: URL decode (%27 → '), đệ quy double-encode
│   ├── N_html: HTML entity decode (&#39; → ')
│   ├── N_ws: Whitespace collapse (\s+ → space)
│   └── N_lower: Case fold (chỉ SQL keywords)
├── Importance [M]
│   ├── Giảm Vocabulary Explosion
│   ├── Tăng Signal-to-Noise Ratio
│   └── Quan trọng với few-shot classes (rce, polyglot)
├── Tracking
│   ├── payload_raw (giữ nguyên)
│   ├── payload_norm (sau N)
│   └── is_obfuscated flag
└── Ví dụ: "%27%20OR%201%3D1--" → "' OR 1=1--"

───────────

De-lexicalization [M]
├── Hàm δ: V* → V*_abstract (abstraction)
├── Hai biến thể [M]
│   ├── Full De-lex (SeqGAN, Gumbel-Softmax)
│   │   └── Thay ALL identifiers bằng placeholders
│   └── Partial De-lex (VAE-GAN)
│       └── Giữ SQL keywords + attack functions
├── Placeholders [M]
│   ├── <TABLE> (tên bảng)
│   ├── <COL> (tên cột)
│   ├── <NUM> (số literal)
│   └── <STR> (string literal)
├── Information-theoretic View [A]
│   └── H(δ(X)) < H(X) — intentional information loss
├── Benefits
│   ├── Variance Reduction (cho policy gradient)
│   ├── Latent Structure (VAE-GAN learns attack type)
│   └── Vocabulary giảm: 50k → ~500 tokens
├── Re-lexicalization (ngược: placeholder → giá trị thực) [A]
└── Ví dụ: "select * from users where id = '42'" → "select * from <TABLE> where <COL> = <STR>"

───────────

Deduplication [M]
├── 3 cấp Dedup [M]
│   ├── Exact Match: N(x) = N(y) (hash-based)
│   ├── Structural: δ(N(x)) = δ(N(y)) (de-lex + hash)
│   └── Semantic: Jaccard(shingles) ≥ θ, MinHash + LSH
├── MinHash + LSH [A]
│   ├── MinHash Estimator: Ĵ = (1/k) Σ 1{min h_i(A) = min h_i(B)}
│   ├── LSH: bucket các MinHash gần nhau
│   └── Jaccard Similarity: J(A,B) = |A∩B| / |A∪B|
├── Raw 195k → Exact 80k → Structural 50k → Semantic 41,460
├── Importance
│   ├── Class Balance (tránh 1 payload chiếm 30%)
│   ├── Train/Test Contamination Prevention
│   └── Meaningful Self-BLEU
└── Code: data_engine/deduplicator.py

───────────

Classification [M]
├── Hàm f: X → Y (13 SQLi types)
├── 3-Tier Hybrid [M]
│   ├── Tier 1: Rule-based (classifier.py, ~ms/payload, ~25% coverage)
│   ├── Tier 2: ML (TF-IDF + Random Forest, ~95.2% acc)
│   │   └── TF-IDF: φ(x)_w = tf(w,x)·log(N/df(w))
│   └── Tier 3: AI (LLM, GPT-4o-mini, JSON output)
├── 13-label SQLi Taxonomy [M]
│   ├── union_based (~6.8%)
│   ├── error_based (~4.3%)
│   ├── boolean_blind (~5.9%)
│   ├── time_blind (~4.1%)
│   ├── heavy_query (~0.9%)
│   ├── stacked_queries (~0.1%)
│   ├── lateral (~0.8%)
│   ├── second_order (~0.7%)
│   ├── auth_bypass (~0.1%)
│   ├── out_of_band (~0.0%)
│   ├── rce (~0.0%)
│   ├── polyglot (~0.0%)
│   └── unknown (~76.3%)
├── Casading Classification: Tier 1 → Tier 2 → Tier 3
├── Class Imbalance → Weighted Loss
│   └── w_c = N/(K·N_c)
└── Confidence → Soft Labels / Label Smoothing

───────────

Labeling Rules [A]
├── Decision Tree cho 13-class taxonomy [M]
│   ├── Level 1: Có pattern attack? (Yes/No)
│   └── Level 2: Type-specific (UNION → union_based, SLEEP → time_blind, ...)
├── Inter-annotator Agreement
│   ├── Cohen's Kappa: κ = (p_o - p_e)/(1 - p_e)
│   │   └── κ ≥ 0.8: acceptable
│   └── Fleiss' Kappa (multi-annotator)
├── Confidence Threshold [M]
│   ├── ≥ 0.85: auto accept
│   ├── 0.60-0.85: human review
│   └── < 0.60: gán unknown, re-classify
├── Confidence Calibration
│   ├── Platt Scaling
│   └── Isotonic Regression
└── Label Noise → cap accuracy ~95%

───────────

Train / Val / Test Split [M]
├── Tỉ lệ: 70 / 15 / 15 (hoặc 80 / 10 / 10)
├── Stratified Split [M]
│   └── P(c|split) = P(c|full) — preserve class distribution
├── Frozen Test Set [M]
│   ├── Commit git, MD5 hash
│   ├── KHÔNG tái shuffle
│   └── Chung cho cả 3 approach
├── Data Leakage Prevention [M]
│   ├── Dedup TRƯỚC split
│   ├── Near-dup detection
│   └── Train/Test Similarity Check
└── K-fold Cross-validation (alternative)

───────────

Data Quality Metrics [A]
├── Coverage = |D_labeled| / |D| (23.7% cho unknown)
├── Class Balance — Normalized Entropy η = H(Y)/H_max ∈ [0,1]
│   └── η ≈ 0.4 (rất imbalanced)
├── Duplication Rate (sau dedup < 1%)
├── Leakage Detection (sim > 0.9 → alarming)
└── Annotation Quality — Confidence Distribution

───────────

Pipeline 6 Bước (Data Engineering) [M]
├── B1: Loaders (5 nguồn — SQLiv5, sqlmap, SecLists, ExploitDB, BCCC-SFU)
├── B2: Normalizer (URL decode, case fold, whitespace)
├── B3: Classifier (Rule + ML + AI)
├── B4: Deduplicator (Exact + Structural + Semantic)
├── B5: Splitter (Per-type train/val/test)
└── B6: Reporter (Stats, distribution)

───────────

DB Engines & Evasion [A]
├── 6 DB Engines
│   ├── mysql (version(), @@version, 0x..., /*!...*/)
│   ├── oracle (utl_inaddr, dbms_lock.sleep, dual)
│   ├── postgresql (pg_sleep, ::text cast)
│   ├── mssql (xp_cmdshell, WAITFOR DELAY)
│   ├── sqlite (sqlite_master, randomblob)
│   └── nosql ($where, $regex, MongoDB)
└── Evasion Techniques (is_obfuscated flag)
    ├── URL encoding (%27)
    ├── Case variation (UnIoN sElEcT)
    ├── Hex string (0x53454c454354)
    ├── Comment obfuscation (UN/**/ION)
    ├── Whitespace tricks
    └── Encoding chains (double URL, HTML entity)
```

---

## N9. Evaluation Metrics

```
Attack Success Rate (ASR) / WAF Evasion Rate (WER) [M]
├── ASR = #{x: bypass ModSecurity CRS} / N (thường N=1000)
├── Per-type ASR (per attack type breakdown)
├── 3 WAF Targets
│   ├── ModSecurity CRS default (PL1)
│   ├── ModSecurity CRS Paranoia Level 3
│   └── Cloudflare-equivalent emulation
├── Threshold: WER ≥ 30% (vs template baseline ~5%)
└── Bootstrap CI (n=10,000) cho ASR [A]

───────────

Syntax Validity Rate [M]
├── Parse N samples bằng sqlparse
├── Threshold: ≥ 85% (ranking), ≥ 50% (hard constraint)
├── If < threshold → ASR metrics không có ý nghĩa
└── sqlglot fallback (cho SQL dialect variants)

───────────

Self-BLEU (Diversity) [M]
├── n-gram order N=3
├── Score cao = ít đa dạng (collapse)
├── Threshold self-BLEU < 0.60 (V1: 0.9894 → fail)
├── De-lex vs Re-lex Space (report both)
└── Contrast with dataset Self-BLEU

───────────

Wasserstein Distance Ŵ₁ [A]
├── Compute on embedding space: P_G (generated) vs P_data (test set)
├── Sinkhorn Divergence approximation
├── Dual form via Critic (consistent with WGAN-GP loss)
├── Avoids JSD saturation (disjoint supports)
└── Lower = distribution match better

───────────

Constraint Density δ [A]
├── δ = ratio of grammar-constrained tokens
├── δ Correlation Experiment
│   └── δ ∈ {0.1, 0.3, 0.5, 0.7, 0.9} vs WER gap
├── Expected: gap → 0 khi δ → 1 (high constraint)
└── Compare δ(output G) vs δ(corpus)

───────────

Composite Score (Gumbel-Softmax approach) [A]
├── S = w₁·Validity + w₂·(1 - Self-BLEU) + w₃·(1 - Ŵ₁)
│   └── w₁=0.4, w₂=0.3, w₃=0.3 (init, tune via ablation)
├── Hard Constraint: Validity < 50% → disqualify
├── Ablation Study on weights
└── Threshold: S(Gumbel-GAN) > S(MLE) + 15%

───────────

5-Metric Ensemble (SeqGAN V2) [A]
├── Metric & Weight
│   ├── OWASP CRS Bypass Rate (0.30) — target > 60%
│   ├── DB Execution Rate (0.25) — target > 80%
│   ├── AST Diversity Entropy (0.20) — target > 3.0
│   ├── ML-IDS Evasion Rate (0.15) — target > 0.5
│   └── Re-lex Uniqueness (0.10) — target > 0.90
├── Final Score = weighted sum (target > 0.55)
├── Per-type Breakdown (8 attack types)
└── Confounding Controls
    ├── AST diversity: report % parse fail
    └── Re-lex: fix dictionary size 50 entries

───────────

Structural Diversity [A]
├── Pairwise Edit Distance (mean ± std)
│   └── Threshold median < 5 tokens → collapsed
├── AST Subtree Fingerprint Entropy
│   ├── Shannon entropy of subtree distribution
│   └── sqlparse AST depth=3
└── Reward Convergence Plot (plateau early → ASR thấp)

───────────

Statistical Rigor [M]
├── Bootstrap CI (n=10,000) for all metrics
├── Mean ± std over ≥ 3 random seeds (42, 123, 7)
├── Significance Testing
│   ├── Paired t-test (parametric)
│   └── Wilcoxon Signed-Rank Test (non-parametric)
├── Fixed Random Seed (torch + numpy)
└── Ablation Study
    ├── Boundary reward vs binary
    ├── Conditional embedding vs unconditional
    ├── Custom rules vs no custom
    └── Multi-source data vs single source

───────────

Sample Efficiency [A]
├── Learning curve: WER vs training size (1k, 5k, 10k, 50k)
├── Baseline converges < 5k
├── Deep models need > 10k
└── Experiment 3 trong VAE-GAN protocol
```

---

## Cross-Group Connection Map

| Từ khóa | Xuất hiện ở nhóm |
|---|---|
| Vanishing Gradient | N1 (Gradient), N2 (RNN) |
| Reparameterization Trick | N1 (Backprop), N4 (VAE) |
| Gumbel-Softmax | N1 (Backprop), N4 (GAN), N5 (SeqGAN V2) |
| KL Divergence | N1 (Loss), N4 (VAE, KL Divergence) |
| Teacher Forcing / Exposure Bias | N3 (Autoregressive), N5 (MLE Pretrain) |
| Scheduled Sampling | N3 (Autoregressive), N5 (MLE Pretrain) |
| WGAN-GP | N4 (WGAN-GP), N5 (Discriminator), N9 (Wasserstein Ŵ₁) |
| Mode Collapse | N4 (Mode Collapse), N5 (V2 Limitations), N9 (Self-BLEU) |
| Self-BLEU | N4 (Mode Collapse), N5 (V2), N9 (Self-BLEU) |
| Constraint Density δ | N4 (Latent Space), N9 (Metrics) |
| TextCNN / Dilated CNN | N2 (CNN), N4 (Discriminator), N5 (Discriminator) |
| Autoregressive Generation | N3, N4 (Generator), N5 (Policy) |
| Latent Space / Latent Walk | N3 (Autoencoder), N4 (Latent Space, VAE) |
| Stochastic Ops Gradient | N1 (Backprop), N4 (Reparam, Gumbel), N5 (REINFORCE) |
| Wasserstein Distance | N4 (WGAN), N9 (Ŵ₁) |
