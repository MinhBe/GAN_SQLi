# AI Foundations — Bài 03: Attention & Transformer

> **Đối tượng**: Đã đọc Bài 01-02. Bài này dạy cơ chế **attention** — phát minh quan trọng nhất của NLP từ 2017 — và kiến trúc **Transformer** thay thế RNN trong hầu hết task generation. Phong cách 4 tầng.
>
> **Phiên bản đơn giản hóa**: `Onboarding_AI_Knowledge_03_Attention_And_Transformer.md`.

> **Cập nhật**: 2026-05-04
> **Concepts trong bài**: Self-attention (Q, K, V), multi-head attention, cross-attention, positional encoding, encoder/decoder block, full Transformer, Autoencoder, seq2seq, autoregressive generation, teacher forcing.

---

## Mục lục

1. [Self-attention — Q, K, V](#1-self-attention)
2. [Multi-Head Attention](#2-multi-head-attention)
3. [Cross-Attention](#3-cross-attention)
4. [Positional Encoding](#4-positional-encoding)
5. [Encoder Block, Decoder Block](#5-encoder--decoder-block)
6. [Full Transformer Architecture](#6-full-transformer)
7. [Autoencoder](#7-autoencoder)
8. [Seq2seq Paradigm](#8-seq2seq)
9. [Autoregressive Generation + Teacher Forcing](#9-autoregressive-generation)

---

## 1. Self-Attention

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Self-attention** = mỗi token "nhìn" mọi token khác trong sequence và quyết định **chú ý đến ai bao nhiêu**, sau đó tổng hợp thông tin từ các token được chú ý. Khi: muốn model học mối quan hệ tùy ý (không chỉ neighbor như CNN, không chỉ tuần tự như RNN). Vì sao: cho phép parallel computation + long-range dependency.

> **Ví dụ trẻ em**: Một lớp 30 học sinh. Cô giáo hỏi câu "Ai là người đoạt giải toán?". Mỗi học sinh **nhìn quanh lớp**, đánh giá: "Bạn A vừa nhắc đến → quan trọng (chú ý 80%); Bạn B đang ngủ → không quan trọng (5%); ...". Sau đó mỗi học sinh **tổng hợp** câu trả lời dựa trên trọng số chú ý. Tất cả 30 học sinh làm cùng lúc, không phải lần lượt.

### Tầng 2 — Toán học (hàn lâm)

Cho input $\mathbf{X} \in \mathbb{R}^{L \times d}$ ($L$ tokens, $d$ embed dim).

Tính 3 ma trận từ $\mathbf{X}$:
$$\mathbf{Q} = \mathbf{X} \mathbf{W}^Q, \quad \mathbf{K} = \mathbf{X} \mathbf{W}^K, \quad \mathbf{V} = \mathbf{X} \mathbf{W}^V$$
- $\mathbf{Q}$: queries — "tôi đang tìm gì".
- $\mathbf{K}$: keys — "tôi có nội dung gì để được tìm".
- $\mathbf{V}$: values — "nội dung tôi sẽ trả khi được chọn".
- $\mathbf{W}^Q, \mathbf{W}^K, \mathbf{W}^V \in \mathbb{R}^{d \times d_k}$ là learnable.

**Scaled Dot-Product Attention** (Vaswani et al. 2017):
$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q} \mathbf{K}^T}{\sqrt{d_k}}\right) \mathbf{V}$$

**Phân tích từng bước**:
1. $\mathbf{Q} \mathbf{K}^T \in \mathbb{R}^{L \times L}$: **attention scores** giữa mọi cặp token. $(QK^T)_{ij}$ = "token $i$ attention đến token $j$ bao nhiêu".
2. Chia $\sqrt{d_k}$: stabilize gradient (variance dot product ~ $d_k$ → softmax saturate).
3. Softmax: chuẩn hóa thành **xác suất** — mỗi row sum = 1.
4. Nhân $\mathbf{V}$: tổng hợp values theo trọng số attention.

**Computational complexity**: $O(L^2 \cdot d)$ — quadratic theo length. Vấn đề khi $L$ lớn (>10k).

**Phép toán nền tảng**: dot product, softmax, matrix multiplication, scaled normalization.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Tên "self" vì $Q, K, V$ đều từ **cùng** input $X$. Khác **cross-attention** ($Q$ từ source, $K, V$ từ target).
- Attention pattern (sau softmax) thường có thể **interpret** — visualize được "token X attention chủ yếu đến token Y, Z" → giúp debug.
- **Heads**: thực tế có nhiều head (xem mục 2), mỗi head học pattern attention khác.
- **Causal mask** cho autoregressive: ép $(QK^T)_{ij} = -\infty$ với $j > i$ → token $i$ không "nhìn được" token tương lai.

### Tầng 4 — Mặt dữ liệu

**Input shape**: `(batch, seq_len, embed_dim)`.
**Output shape**: same as input — preserves sequence structure.

**Trong dự án**:
- VAE-GAN Encoder/Decoder: Transformer với multi-head self-attention.
- Gumbel-Softmax Generator: Transformer Decoder với masked self-attention.
- Discriminator (TextCNN/Dilated CNN) **không dùng** attention — vẫn dùng conv.

---

## 2. Multi-Head Attention

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Multi-head attention** = chạy attention song song $h$ lần với $h$ bộ $(W^Q, W^K, W^V)$ khác nhau, rồi concatenate. Khi: muốn model học **nhiều kiểu pattern attention** đồng thời. Vì sao: 1 head chỉ focus được 1 kiểu relationship; multi-head capture đa dạng.

> **Ví dụ trẻ em**: Bạn đọc cuốn truyện. **Đọc 1 lần** chỉ chú ý nhân vật chính. **Đọc lần 2** chú ý bối cảnh. **Đọc lần 3** chú ý tình tiết. Multi-head = đọc song song nhiều lần, mỗi lần focus 1 khía cạnh, sau đó tổng hợp hiểu biết.

### Tầng 2 — Toán học (hàn lâm)

$$\text{MHA}(\mathbf{X}) = \text{Concat}(\text{head}_1, ..., \text{head}_h) \mathbf{W}^O$$

với mỗi head:
$$\text{head}_i = \text{Attention}(\mathbf{X} \mathbf{W}^Q_i, \mathbf{X} \mathbf{W}^K_i, \mathbf{X} \mathbf{W}^V_i)$$

- $\mathbf{W}^Q_i, \mathbf{W}^K_i, \mathbf{W}^V_i \in \mathbb{R}^{d \times d_k}$ với $d_k = d/h$ (chia đều).
- $\mathbf{W}^O \in \mathbb{R}^{(h \cdot d_k) \times d}$ projection cuối.

**Số tham số**: $4 \cdot h \cdot d \cdot d_k = 4 d^2$ (tổng) — không phụ thuộc số head khi giữ $d$ fixed.

**Phép toán nền tảng**: tensor reshaping, parallel computation, concatenation, learned projection.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Phổ biến: $h = 8$ hoặc $h = 16$. Original Transformer: $h=8, d=512, d_k=64$.
- **Different heads learn different patterns**: 1 head có thể attention syntactic (next/prev word), head khác attention semantic.
- Trong inference, có thể **prune** một số head không quan trọng (Voita et al. 2019) — giảm compute mà không mất nhiều quality.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:
- VAE-GAN Encoder: 4-6 layers Transformer, mỗi layer có MHA $h=8$.
- Suggested config: $d=256, h=8, d_k=32$.

---

## 3. Cross-Attention

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Cross-attention** = attention với $Q$ từ **một sequence** và $K, V$ từ **sequence khác**. Khi: trong encoder-decoder, decoder cần "nhìn" output của encoder. Vì sao: kết nối thông tin giữa 2 sequences (nguồn ↔ đích).

> **Ví dụ trẻ em**: Bạn dịch câu tiếng Anh sang tiếng Việt. Đang viết từ thứ 5 trong câu Việt — **nhìn lại** câu Anh: "từ nào quan trọng cho từ Việt mình đang viết?". Q = từ Việt đang viết, K/V = các từ Anh trong câu nguồn. Attention từ Q sang K/V = cross-attention.

### Tầng 2 — Toán học (hàn lâm)

$$\text{CrossAttn}(\mathbf{X}_{tgt}, \mathbf{X}_{src}) = \text{softmax}\left(\frac{\mathbf{X}_{tgt} \mathbf{W}^Q (\mathbf{X}_{src} \mathbf{W}^K)^T}{\sqrt{d_k}}\right) (\mathbf{X}_{src} \mathbf{W}^V)$$

- $\mathbf{X}_{tgt} \in \mathbb{R}^{L_t \times d}$: target sequence (đang generate).
- $\mathbf{X}_{src} \in \mathbb{R}^{L_s \times d}$: source sequence (đã encoded).
- Output shape: $\mathbb{R}^{L_t \times d}$ — same as target.

**Phép toán nền tảng**: same as self-attention nhưng inputs khác source.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Cross-attention là **cơ chế bridge** trong encoder-decoder Transformer (machine translation, summarization).
- Trong vision-language models (CLIP, Flamingo): cross-attention giữa image features và text tokens.
- **Trong dự án — VAE-GAN**:
  > "Generator/Decoder $G$: Giải mã vector ẩn $z$ thành chuỗi token SQL autoregressively. Dùng Transformer decoder với **cross-attention vào $z$**."
  → Decoder mỗi step nhìn $z$ qua cross-attention.

### Tầng 4 — Mặt dữ liệu

**Trong dự án — VAE-GAN**:
- Encoder output: latent $z \in \mathbb{R}^{256}$ (1 vector per sample).
- Decoder input: token đang generate + cross-attend tới $z$ (broadcast về sequence form).

---

## 4. Positional Encoding

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Positional encoding (PE)** = thêm thông tin về **vị trí** vào embedding của mỗi token. Khi: bắt buộc cho Transformer (vì attention không có thứ tự inherent). Vì sao: nếu không có PE, Transformer treat sequence như **bag of tokens** — mất thông tin thứ tự.

> **Ví dụ trẻ em**: Cô giáo viết câu lên bảng nhưng cắt rời từng từ thành những mảnh giấy, đảo lộn. Bạn nhặt được "nó / mèo / con / yêu" — không biết câu ban đầu là "Nó yêu con mèo" hay "Con mèo yêu nó". → Cần **đánh số** mỗi mảnh giấy: "(1) Nó (2) yêu (3) con (4) mèo" → biết thứ tự. PE = đánh số đó.

### Tầng 2 — Toán học (hàn lâm)

**Sinusoidal PE** (Transformer original):
$$PE(pos, 2i) = \sin\left(\frac{pos}{10000^{2i/d}}\right)$$
$$PE(pos, 2i+1) = \cos\left(\frac{pos}{10000^{2i/d}}\right)$$

- $pos \in \{0, 1, ..., L-1\}$: vị trí token.
- $i \in \{0, ..., d/2-1\}$: dim index.
- Tần số khác nhau → mỗi pos có "fingerprint" duy nhất.

Cộng vào embedding: $\mathbf{x}_{pos} = \mathbf{x}_{embed} + PE(pos)$.

**Tính chất**:
- $PE(pos+k)$ có thể được biểu diễn **tuyến tính** từ $PE(pos)$ → model có thể học relative position.
- Generalize đến sequence dài hơn lúc train.

**Learned PE** (BERT, GPT): $PE(pos)$ là learnable parameter $\in \mathbb{R}^{L_{max} \times d}$.
- Đơn giản hơn nhưng không generalize đến $pos > L_{max}$.

**Modern PE**:
- **RoPE** (Rotary Position Embedding): rotate Q, K theo position. Tốt hơn cho long context.
- **ALiBi**: bias attention scores theo distance. Không cần thêm dim.

**Phép toán nền tảng**: trigonometric functions, frequency analysis, rotation matrices (RoPE).

### Tầng 3 — Mặt trí tuệ nhân tạo

- PE là điểm khác biệt lớn giữa Transformer và RNN: RNN có inherent order (sequential), Transformer cần PE explicit.
- Without PE: Transformer = permutation-invariant function of tokens.
- Choice of PE ảnh hưởng đến:
  - Length generalization (extend beyond training length).
  - Long-context performance.

### Tầng 4 — Mặt dữ liệu

**Implementation** trong dự án (suggested):
```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:x.size(1)]
```

---

## 5. Encoder & Decoder Block

### 5.1 Encoder Block

#### Tầng 1
**Encoder block** = 1 layer Transformer cho **encoder side** — gồm Multi-Head Self-Attention + Feed-Forward Network + LayerNorm + Residual.

> **Ví dụ trẻ em**: Một "trạm xử lý". Token đi vào, được học nhìn các token khác (self-attention), được chế biến tiếp (FFN), rồi đi ra. Stack nhiều trạm → encoder.

#### Tầng 2
$$\mathbf{h}^{(l)} = \text{LayerNorm}(\mathbf{x}^{(l-1)} + \text{MHA}(\mathbf{x}^{(l-1)}))$$
$$\mathbf{x}^{(l)} = \text{LayerNorm}(\mathbf{h}^{(l)} + \text{FFN}(\mathbf{h}^{(l)}))$$

**FFN**: 2-layer MLP với GELU/ReLU activation:
$$\text{FFN}(x) = W_2 \cdot \phi(W_1 x + b_1) + b_2$$
Dim: $d \to 4d \to d$ (4× expansion in middle).

**Residual + LayerNorm**: stabilize training cho deep networks.

#### Tầng 3-4
- Tham số per block: ~$12 d^2$ (4 attention proj + 2 FFN).
- Trong VAE-GAN encoder: 4-6 blocks stacked.

### 5.2 Decoder Block

#### Tầng 1
**Decoder block** = encoder block + **cross-attention** layer ở giữa, và self-attention dùng **causal mask**.

#### Tầng 2
$$\mathbf{h}_1 = \text{LayerNorm}(\mathbf{x} + \text{MaskedMHA}(\mathbf{x}))$$
$$\mathbf{h}_2 = \text{LayerNorm}(\mathbf{h}_1 + \text{CrossAttn}(\mathbf{h}_1, \mathbf{x}_{enc}))$$
$$\mathbf{x}_{out} = \text{LayerNorm}(\mathbf{h}_2 + \text{FFN}(\mathbf{h}_2))$$

**Causal mask**: $M_{ij} = -\infty$ nếu $j > i$, else $0$. Cộng vào attention score trước softmax → token $i$ chỉ attend ≤ $i$.

#### Tầng 3-4
- Trong VAE-GAN: decoder attend cross-wise vào latent $z$ (broadcast).
- Trong Gumbel-Softmax: decoder-only Transformer (chỉ self-attention với mask, không cross).

---

## 6. Full Transformer Architecture

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Transformer** (Vaswani et al. 2017, "Attention Is All You Need") = kiến trúc full encoder-decoder dựa trên attention. Khi: most modern NLP tasks. Vì sao: thay thế RNN/LSTM, parallel hơn, scale tốt hơn.

> **Ví dụ trẻ em**: 1 "nhà máy 2 tầng":
> - **Tầng 1 (Encoder)**: nhận câu nguồn, qua N trạm xử lý → output là "hiểu biết" về câu nguồn.
> - **Tầng 2 (Decoder)**: sinh từng từ output, mỗi từ được sinh ra dựa trên (a) các từ đã sinh trước, (b) "hiểu biết" từ tầng 1.

### Tầng 2 — Toán học (hàn lâm)

**Encoder**:
$$\mathbf{H}_{enc} = \text{Encoder}(\mathbf{X}_{src}) \in \mathbb{R}^{L_s \times d}$$
$N$ encoder blocks stacked.

**Decoder** (autoregressive):
$$\mathbf{H}_{dec}^{(t)} = \text{Decoder}(\mathbf{Y}_{<t}, \mathbf{H}_{enc})$$
$$P(y_t | \mathbf{Y}_{<t}, \mathbf{X}_{src}) = \text{softmax}(\mathbf{H}_{dec}^{(t)} \mathbf{W}_{vocab})$$

**Variants**:
- **Encoder-only** (BERT): cho classification, masked LM.
- **Decoder-only** (GPT): cho autoregressive generation.
- **Encoder-decoder** (T5, BART): cho seq2seq.

**Scale**:
- Original: 6 enc + 6 dec layers, $d=512$, $h=8$ → ~65M params.
- BERT-base: 12 layers, $d=768$, $h=12$ → 110M.
- GPT-3: 96 layers, $d=12288$, $h=96$ → 175B.

**Phép toán nền tảng**: composition của attention + FFN + residual, autoregressive factorization.

### Tầng 3 — Mặt trí tuệ nhân tạo

- Transformer = **architectural backbone** của LLM era (GPT, BERT, T5, ...).
- **Strengths**:
  - Parallel training (không sequential như RNN).
  - Long-range dependency (full attention).
  - Scale extremely well với data + compute.
- **Weaknesses**:
  - $O(L^2)$ attention với length → khó với very long context.
  - Cần PE explicit.
  - Tham số nhiều, cần lots of data.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:

| Approach | Encoder | Decoder | Notes |
|---|---|---|---|
| VAE-GAN | Transformer 4-6 layer | Transformer 4-6 layer + cross-attn vào $z$ | Encoder-decoder full |
| SeqGAN | (không có encoder) | LSTM hoặc Transformer Decoder | Decoder-only |
| Gumbel-Softmax | (không có encoder) | Transformer Decoder + Gumbel-Softmax | Decoder-only |

---

## 7. Autoencoder

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Autoencoder (AE)** = NN có 2 phần: **Encoder** nén input thành **code (z)** trong không gian thấp chiều, **Decoder** giải mã $z$ trở lại input. Train với loss = "khôi phục giống input đến đâu". Khi: dimensionality reduction, denoising, representation learning. Vì sao: ép network học **representation hữu ích** trong $z$.

> **Ví dụ trẻ em**: Ghi chú bài giảng. **Encoder** = bạn tóm tắt 100 trang giáo trình thành 1 trang note. **Decoder** = bạn (sau 1 tuần) đọc 1 trang note và **kể lại** 100 trang. Nếu kể đúng → tóm tắt tốt → note (= z) chứa đủ thông tin.

### Tầng 2 — Toán học (hàn lâm)

**Architecture**: $f_\theta = D \circ E$ với:
- $E_\phi: \mathcal{X} \to \mathcal{Z}$ encoder.
- $D_\psi: \mathcal{Z} \to \mathcal{X}$ decoder.
- $\dim(\mathcal{Z}) \ll \dim(\mathcal{X})$ (bottleneck).

**Loss** (reconstruction):
$$\mathcal{L}_{AE}(\theta) = \mathbb{E}_{x \sim p_{data}} \| x - D_\psi(E_\phi(x)) \|^2$$

**Bottleneck constraint**: dim($z$) nhỏ → ép encoder chọn lọc thông tin quan trọng nhất.

**Variants**:
- **Denoising AE**: input nhiễu $x + \epsilon$, target sạch $x$. Học robust features.
- **Sparse AE**: thêm sparsity penalty trên $z$.
- **Variational AE (VAE)**: $z$ là distribution $\mathcal{N}(\mu, \sigma^2)$ thay vector. (Xem File 04.)

**Phép toán nền tảng**: function composition, dimensionality reduction (PCA là AE tuyến tính).

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Use cases**:
  - Dimensionality reduction (visualization t-SNE từ AE).
  - Anomaly detection (high reconstruction error = anomaly).
  - Representation learning (pretrain encoder cho downstream tasks).
- **Limitation**: vanilla AE không generative — không thể sample $z$ random và sinh data. Cần VAE.
- **Trong dự án — VAE-GAN**: Encoder là Transformer encoder, Decoder là Transformer decoder. Latent $z \in \mathbb{R}^{256}$.

### Tầng 4 — Mặt dữ liệu

**Input**: payload sequence (after tokenize + embed).
**Output**: reconstructed sequence (same length).
**Latent**: vector $z \in \mathbb{R}^{256}$.

---

## 8. Seq2seq Paradigm

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Seq2seq** = paradigm ánh xạ **chuỗi → chuỗi**, dùng encoder-decoder. Khi: machine translation, summarization, dialogue, code generation. Vì sao: input và output đều là sequences với độ dài khác nhau, possibly khác alphabet.

> **Ví dụ trẻ em**: Translator. Đầu vào: câu tiếng Anh ("Hello world"). Đầu ra: câu tiếng Việt ("Xin chào thế giới"). Hai chuỗi khác độ dài, khác từ vựng — encoder hiểu Anh, decoder sinh Việt.

### Tầng 2 — Toán học (hàn lâm)

Học $P(\mathbf{y} | \mathbf{x})$ với $\mathbf{x} = (x_1, ..., x_{L_s})$, $\mathbf{y} = (y_1, ..., y_{L_t})$.

**Factorize autoregressively**:
$$P(\mathbf{y} | \mathbf{x}) = \prod_{t=1}^{L_t} P(y_t | y_{<t}, \mathbf{x})$$

**Maximum Likelihood Estimation (MLE)** loss:
$$\mathcal{L}_{MLE}(\theta) = -\sum_{(\mathbf{x}, \mathbf{y}) \in D} \sum_{t=1}^{L_t} \log P_\theta(y_t | y_{<t}, \mathbf{x})$$

**Beam search** cho inference: thay greedy argmax bằng giữ top-$k$ beams parallel → output tốt hơn nhưng đắt hơn $k$×.

**Phép toán nền tảng**: chain rule of probability, autoregressive factorization, dynamic programming (beam search).

### Tầng 3 — Mặt trí tuệ nhân tạo

- Original seq2seq (Sutskever 2014): RNN encoder-decoder.
- Sau đó: + attention (Bahdanau 2014) → Transformer (Vaswani 2017).
- **Trong dự án**: VAE-GAN có encoder-decoder structure giống seq2seq, nhưng encode về latent $z$ thay flat hidden states.

### Tầng 4 — Mặt dữ liệu

**Format dataset**:
```
{"src": "tokenized source seq", "tgt": "tokenized target seq"}
```

**Trong dự án**:
- VAE-GAN: src = input SQLi, tgt = same input SQLi (autoencoder objective).
- SeqGAN/Gumbel: chỉ có tgt (decoder-only generation), src = noise.

---

## 9. Autoregressive Generation

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Autoregressive generation** = sinh sequence **từng token một**, mỗi token được conditioned trên tokens đã sinh trước. Khi: text/speech/music generation. Vì sao: sequence có cấu trúc tuần tự, mỗi step phụ thuộc lịch sử.

> **Ví dụ trẻ em**: Viết câu chuyện. Bạn viết từ thứ 1, suy nghĩ → viết từ thứ 2 (dựa trên từ 1) → viết từ thứ 3 (dựa trên từ 1+2) → ... Mỗi từ phụ thuộc tất cả từ đã viết.

### Tầng 2 — Toán học (hàn lâm)

**Factorization**:
$$P(y_1, y_2, ..., y_T) = \prod_{t=1}^T P(y_t | y_{<t})$$

**Sampling strategies**:
1. **Greedy**: $y_t = \arg\max_v P(y_t = v | y_{<t})$. Đơn giản, deterministic, nhưng có thể repetitive.
2. **Beam search**: giữ top-$k$ candidates, chọn best beam cuối.
3. **Random sampling**: $y_t \sim P(\cdot | y_{<t})$. Đa dạng nhưng có thể incoherent.
4. **Top-k sampling**: chỉ sample từ top-$k$ tokens xác suất cao nhất.
5. **Top-p (nucleus) sampling**: sample từ smallest set cumulative prob ≥ $p$.
6. **Temperature**: $P_\tau(v) \propto P(v)^{1/\tau}$. $\tau \to 0$: greedy. $\tau \to \infty$: uniform.

**Phép toán nền tảng**: chain rule, conditional sampling, search algorithm (beam).

### Tầng 3 — Mặt trí tuệ nhân tạo

- Autoregressive là paradigm chủ đạo cho generation (GPT, LLaMA).
- **Teacher forcing** (lúc train): feed ground-truth $y_{t-1}$ thay $\hat{y}_{t-1}$ → train nhanh, ổn định, parallel.
- **Exposure bias**: model train với ground-truth, inference với own predictions → distribution mismatch → có thể tạo loop (stuck in repetition).
- **Mitigations**:
  - **Scheduled Sampling**: dần dần thay ground-truth bằng predictions trong train.
  - **Reinforcement Learning** (vd SeqGAN): tối ưu reward thực thay log-likelihood.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:
- VAE-GAN inference: sample $z \sim \mathcal{N}(0,I)$, decoder autoregressively sinh tokens. Sampling: thường top-k hoặc top-p, $\tau=0.8$.
- SeqGAN: pre-train với MLE + Scheduled Sampling. Adversarial loop với REINFORCE.
- Gumbel-Softmax: sinh tokens với Gumbel-Softmax sampling (continuous relaxation), không argmax thuần.

---

## 10. Teacher Forcing — Chi tiết

### Tầng 1
**Teacher forcing** = trong train, feed ground-truth previous token thay token model dự đoán → train nhanh, parallel.

### Tầng 2
Standard MLE training:
$$\mathcal{L} = -\sum_t \log P(y_t^{*} | y_{<t}^{*})$$
($y^*$: ground truth)

Có thể parallelize qua time bởi vì không cần sequential dependency của model output.

### Tầng 3-4
- **Vấn đề exposure bias** (mismatch train/inference) đã đề cập.
- **SeqGAN giải quyết**: dùng REINFORCE với reward từ Discriminator + WAF Oracle để supervise model với own predictions.

---

## 11. Tổng kết — Vai trò trong dự án

| Concept | VAE-GAN | SeqGAN | Gumbel-Softmax |
|---|---|---|---|
| Self-attention | ✅ Encoder + Decoder | ⚠️ Optional (LSTM alternative) | ✅ Decoder |
| Cross-attention | ✅ Decoder ← latent z | ❌ | ❌ |
| Positional encoding | ✅ | ✅ (nếu Transformer) | ✅ |
| Autoencoder | ✅ Core (V**AE**-GAN) | ❌ | ❌ |
| Seq2seq | ✅ Reconstruction | ❌ Decoder-only | ❌ Decoder-only |
| Autoregressive | ✅ Decoder | ✅ Generator | ✅ Generator |
| Teacher forcing | ✅ MLE warm-up | ✅ MLE pretrain | ✅ MLE pretrain |

---

## 12. Tài liệu tham chiếu chéo

- File 01 — Neural Net basics.
- File 02 — RNN/LSTM (will be replaced by Transformer in many cases).
- File 04 — GAN, VAE generative models.
- `Onboarding_AI_Knowledge_03_*.md` — bản đơn giản hóa.

## 13. Đọc thêm

- **Vaswani et al. 2017** — "Attention Is All You Need" (paper Transformer gốc).
- **The Illustrated Transformer** by Jay Alammar — visualization tốt nhất.
- **The Annotated Transformer** (Harvard NLP) — code-by-code walkthrough.
- **Stanford CS224n** — chapters về Transformer + attention.
- **Andrej Karpathy "nanoGPT"** tutorials — implement GPT from scratch.
