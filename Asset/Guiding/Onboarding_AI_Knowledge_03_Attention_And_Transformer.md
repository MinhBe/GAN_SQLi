# Onboarding AI — Bài 03: Attention và Transformer

> **Đối tượng**: Member mới đã đọc bài 01-02. Bài này dạy cơ chế **attention** — phát minh AI quan trọng nhất 10 năm qua — và kiến trúc **Transformer** đứng đằng sau ChatGPT, GPT-4, Claude.
>
> **Phong cách**: dày tầng kid + practical. Bản đầy đủ toán: `AI_Foundations_For_Team_03_Attention_And_Transformer.md`.

> **Cập nhật**: 2026-05-04
> **Concepts**: Self-attention, multi-head attention, cross-attention, positional encoding, encoder/decoder, Transformer, autoencoder, seq2seq, autoregressive generation.

---

## 1. Self-Attention — "Chú ý có chọn lọc"

### Câu chuyện

Một lớp 30 học sinh. Cô giáo hỏi: "Ai là người đoạt giải toán?".

Mỗi học sinh **nhìn quanh lớp**, đánh giá từng bạn:
- "Bạn A vừa nhắc đến → quan trọng (chú ý 80%)".
- "Bạn B đang ngủ → không liên quan (5%)".
- "Bạn C đang giơ tay → có lẽ biết (40%)".
- ...

Sau đó mỗi học sinh **tổng hợp câu trả lời** dựa trên trọng số chú ý mình tự đánh giá. **Tất cả 30 học sinh làm cùng lúc**, không phải lần lượt — đây là điểm mạnh của attention.

### Trong AI

**Self-attention** = mỗi token "nhìn" mọi token khác trong câu, quyết định **chú ý đến token nào bao nhiêu**, sau đó tổng hợp thông tin.

Ví dụ câu: `"The cat sat on the mat because it was tired"`. Khi xử lý từ "**it**":
- Attention đến "the cat" cao (95%) — "it" tham chiếu đến cat.
- Attention đến các từ khác thấp.

→ Model hiểu "it" = "the cat" mà không cần ai dạy quy tắc grammar. Tự học từ data.

### So với RNN

- **RNN**: đọc tuần tự token 1 → 2 → 3 → ... → đến token cuối mới hiểu toàn câu.
- **Self-attention**: mọi token nhìn mọi token cùng lúc → song song, nhanh + bắt được dependency xa.

### Q, K, V — 3 cô gái trong câu chuyện

Mỗi token sinh ra 3 vector:
- **Query (Q)**: "Tôi đang tìm gì?" (vd: "tôi cần subject của câu này").
- **Key (K)**: "Tôi có nội dung gì?" (vd: "tôi là một danh từ chỉ động vật").
- **Value (V)**: "Khi được chọn, tôi đóng góp gì?" (vd: "thông tin về 'cat'").

Attention: token A so sánh Q của mình với K của mọi token → ra điểm "chú ý" → tổng hợp V theo trọng số.

### Trong dự án

VAE-GAN encoder + decoder, Gumbel-Softmax decoder đều dùng self-attention để hiểu cấu trúc SQL. Vd token `UNION` "chú ý" đến `SELECT` ngay sau và `FROM` xa hơn → hiểu pattern union-based attack.

---

## 2. Multi-Head Attention

### Câu chuyện

Bạn đọc cuốn truyện 1 lần — chỉ chú ý nhân vật chính.
Đọc lần 2 — chú ý bối cảnh.
Đọc lần 3 — chú ý tình tiết.

Mỗi lần focus 1 khía cạnh, sau đó **tổng hợp**.

**Multi-head attention** = chạy attention song song nhiều lần (mỗi "head" = 1 lần đọc), mỗi head focus 1 kiểu pattern khác.

Phổ biến: 8 heads hoặc 16 heads. Mỗi head có bộ Q, K, V riêng.

### Vì sao hữu ích?

1 head chỉ học 1 kiểu relationship. Đa dạng tasks cần đa dạng pattern → multi-head capture nhiều aspects.

### Trong dự án

VAE-GAN encoder: 8 heads × 4-6 layers Transformer. Mỗi head học một loại attention pattern (next/previous word, syntax, semantic, ...).

---

## 3. Cross-Attention

### Câu chuyện

Bạn dịch câu Anh → Việt. Đang viết từ thứ 5 trong câu Việt — **nhìn lại câu Anh**: "từ nào quan trọng cho từ Việt mình đang viết?".

Q = từ Việt đang viết (target). K, V = các từ Anh trong câu nguồn (source).

**Cross-attention** = attention giữa **2 sequences khác nhau** (target nhìn source).

### Trong dự án

**VAE-GAN Decoder** dùng cross-attention để decoder "nhìn" latent vector $z$ (đã được encoder nén từ input):
- Lúc decode mỗi token, decoder query latent z → biết "phải sinh tiếp gì".

Cross-attention là cầu nối giữa encoder và decoder.

---

## 4. Positional Encoding — "Đánh số thứ tự"

### Câu chuyện

Cô giáo viết câu lên bảng nhưng cắt rời từng từ thành mảnh giấy, đảo lộn. Bạn nhặt được "nó / mèo / con / yêu" — không biết câu thật là "Nó yêu con mèo" hay "Con mèo yêu nó".

→ Cần **đánh số mỗi mảnh giấy** thứ tự xuất hiện trong câu thật. Đó là **positional encoding (PE)**.

### Tại sao Transformer cần PE?

Self-attention **không có thứ tự inherent** — nếu không thêm PE, Transformer treat câu như "**bag of words**", mất hết thứ tự.

PE = vector đặc biệt cộng vào embedding mỗi token, mã hóa vị trí (1, 2, 3, ...) bằng các tần số khác nhau.

Token ở vị trí 1 và vị trí 5 sẽ có PE khác → model biết phân biệt thứ tự.

### Trong dự án

Mọi Transformer trong dự án (VAE-GAN, Gumbel-Softmax) đều dùng PE. Implementation: sinusoidal PE (công thức Vaswani 2017) — quen thuộc, generalize tốt.

---

## 5. Encoder & Decoder Block

### Câu chuyện

Một **trạm xử lý** trong nhà máy:
- Nhân vật đến trạm.
- Trạm cho nhân vật **nhìn quanh** (self-attention) — học liên kết với nhân vật khác.
- Trạm cho nhân vật **chế biến nội tâm** (FFN — feed forward network) — process info đã thu được.
- Nhân vật rời trạm → đi đến trạm tiếp theo.

**Stack nhiều trạm** = **stacked encoder/decoder layers**.

### Encoder vs Decoder

- **Encoder block** = self-attention + FFN. Bidirectional (nhìn cả trước + sau).
- **Decoder block** = masked self-attention (chỉ nhìn trước) + cross-attention (nhìn encoder output) + FFN.

**Mask** trong decoder: ép token thứ $t$ chỉ nhìn được token 1, 2, ..., $t-1$ — không "spoil" token tương lai (autoregressive).

---

## 6. Full Transformer

### Câu chuyện

**Một nhà máy 2 tầng**:
- **Tầng 1 (Encoder)**: nhận câu nguồn (vd "Hello world"), qua N trạm xử lý → output là "hiểu biết tổng thể" về câu nguồn.
- **Tầng 2 (Decoder)**: sinh từng từ output (vd "Xin chào thế giới"), mỗi từ được sinh dựa trên (a) các từ đã sinh trước, (b) "hiểu biết" từ tầng 1 (qua cross-attention).

**Variants**:
- **Encoder-only**: BERT (cho understanding tasks).
- **Decoder-only**: GPT, LLaMA (cho generation).
- **Encoder-decoder**: T5, BART (cho translation, summarization).

### Trong dự án

| Approach | Encoder | Decoder |
|---|---|---|
| VAE-GAN | ✅ Transformer 4-6 layers | ✅ Transformer + cross-attn vào latent z |
| SeqGAN | ❌ | LSTM hoặc Transformer Decoder |
| Gumbel-Softmax | ❌ | Transformer Decoder + Gumbel-Softmax sampling |

---

## 7. Autoencoder — "Tóm tắt + kể lại"

### Câu chuyện

Bạn ghi chú bài giảng:
- **Encoder**: tóm tắt 100 trang giáo trình thành **1 trang note**.
- **Decoder**: 1 tuần sau, đọc 1 trang note và **kể lại 100 trang**.

Nếu kể đúng → tóm tắt tốt → note (= **latent z**) chứa đủ thông tin.

### Trong AI

Autoencoder = NN có encoder + decoder, train sao cho **output giống input nhất có thể**.

Sau khi train:
- **Encoder** học cách nén thông tin → dùng cho dimensionality reduction, anomaly detection.
- **Decoder** không quan trọng (chỉ là tool để train encoder).

### VAE = Autoencoder probabilistic

- Encoder thường: $x \to z$ (vector cố định).
- Encoder VAE: $x \to (\mu, \sigma)$ → sample $z$ từ Gaussian.

→ Latent space "có cấu trúc xác suất" → có thể sample $z$ random → sinh data mới.

### Trong dự án

VAE-GAN có encoder Transformer + decoder Transformer. Latent z ∈ R^256.

**Claim của dự án**: latent z học được tách biệt "SQL thuần túy" vs "SQL ngụy trang" → control kiểu attack qua z.

---

## 8. Seq2seq — "Chuỗi → Chuỗi"

### Câu chuyện

Bạn là **translator**:
- Đầu vào: câu Anh ("Hello world") — **chuỗi token**.
- Đầu ra: câu Việt ("Xin chào thế giới") — **chuỗi token khác**.

Hai chuỗi:
- Có thể **khác độ dài**.
- Có thể **khác alphabet** (English vs Vietnamese).
- Có **mapping ngữ nghĩa** giữa nhau.

**Seq2seq** = paradigm ánh xạ chuỗi → chuỗi. Implementation phổ biến: encoder-decoder Transformer hoặc RNN.

### Use cases

- Machine translation.
- Summarization (long → short).
- Dialogue (input → response).
- Code generation (description → code).

### Trong dự án

VAE-GAN có structure giống seq2seq nhưng:
- Source = SQLi payload (từ dataset).
- Target = same payload (autoencoder objective: reconstruct).
- Latent z ở giữa — nén thông tin.

---

## 9. Autoregressive Generation — "Sinh từng token một"

### Câu chuyện

Bạn viết câu chuyện:
- Viết từ thứ 1.
- Suy nghĩ → viết từ thứ 2 (dựa trên từ 1).
- Viết từ thứ 3 (dựa trên từ 1+2).
- ...

Mỗi từ phụ thuộc tất cả từ đã viết.

### Trong AI

Generator (vd ChatGPT) sinh text **từng token một**:
- Token 1: random theo distribution.
- Token 2: condition trên token 1.
- Token 3: condition trên token 1+2.
- ...

### Sampling strategies

Khi model output distribution P(token), chọn token thế nào?

1. **Greedy**: chọn token xác suất cao nhất. Đơn giản, nhưng repetitive.
2. **Random**: sample từ distribution. Đa dạng nhưng có thể incoherent.
3. **Top-k**: chỉ sample từ top-k tokens. Cân bằng.
4. **Top-p (nucleus)**: sample từ top tokens cộng dồn ≥ p%.
5. **Temperature**: làm distribution "sắc" (τ thấp) hoặc "mềm" (τ cao).

### Teacher Forcing — Trick lúc train

**Lúc inference**: model dùng prediction của chính mình ($\hat{y}_{t-1}$) cho step tiếp theo.

**Lúc train** (teacher forcing): feed **ground-truth** ($y_{t-1}^*$) thay $\hat{y}_{t-1}$. Lý do:
- Train **nhanh** (parallel).
- Tránh model học từ chính lỗi của mình.

### Vấn đề: Exposure Bias

Train với ground-truth, inference với own predictions → distribution mismatch → model có thể stuck in repetition loop.

**Mitigations**:
- **Scheduled Sampling**: dần dần thay ground-truth bằng predictions trong train.
- **REINFORCE** (SeqGAN dùng): tối ưu reward thực thay log-likelihood.

### Trong dự án

Cả 3 approach Generator đều autoregressive:
- **VAE-GAN**: sample $z \sim N(0,I)$ → decode tokens autoregressively.
- **SeqGAN**: sample token theo policy $\pi_\theta$.
- **Gumbel-Softmax**: sample qua Gumbel-Softmax (continuous relaxation của argmax).

---

## 10. Tổng kết: Tại sao Transformer "chiến thắng"?

| Lý do | Giải thích |
|---|---|
| **Parallel** | Self-attention chạy mọi token cùng lúc, GPU love. RNN sequential, chậm. |
| **Long-range** | Self-attention nhìn được mọi token, không bị vanishing gradient. |
| **Scalable** | Càng nhiều data + compute → càng tốt (GPT scaling laws). |
| **Versatile** | Cùng kiến trúc dùng cho text, image, audio, code. |

→ **Transformer là backbone của LLM era**: GPT-4, Claude, Gemini, LLaMA đều là Transformer.

### Trong dự án

Trong 3 approach, Transformer xuất hiện:
- **VAE-GAN**: encoder + decoder.
- **SeqGAN**: alternative cho LSTM (nếu chọn).
- **Gumbel-Softmax**: decoder.

LSTM/GRU đang dần bị deprecate trong research mới, nhưng vẫn dùng cho low-resource setting.

---

## 11. Bạn đã hiểu gì?

- ✅ Self-attention: mỗi token nhìn mọi token, có chọn lọc.
- ✅ Q, K, V: 3 vai trò trong attention (tìm gì / có gì / đóng góp gì).
- ✅ Multi-head: nhiều "lần đọc" song song với pattern khác.
- ✅ Cross-attention: target nhìn source (encoder-decoder).
- ✅ Positional encoding: thêm thứ tự cho Transformer.
- ✅ Encoder block, decoder block: 2 dạng "trạm xử lý".
- ✅ Autoencoder: tóm tắt + khôi phục.
- ✅ Seq2seq: chuỗi → chuỗi qua encoder-decoder.
- ✅ Autoregressive: sinh từng token một.
- ✅ Teacher forcing + exposure bias: trick train + vấn đề kèm.

---

## 12. Đọc tiếp

Bài 04: `Onboarding_AI_Knowledge_04_Generative_Models.md` — học về **GAN, VAE, biến thể** — chính là kiến trúc của 3 approach trong dự án này. Bài cuối cùng và quan trọng nhất.
