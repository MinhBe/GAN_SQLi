# Onboarding AI — Bài 04: Generative Models (GAN, VAE)

> **Đối tượng**: Member mới đã đọc bài 01-03. Bài này là **quan trọng nhất** với dự án — vì 3 hướng AI đều thuộc generative models.
>
> **Phong cách**: dày tầng kid + practical. Bản đầy đủ toán: `AI_Foundations_For_Team_04_Generative_Models.md`.

> **Cập nhật**: 2026-05-04
> **Concepts**: GAN G/D, mode collapse, WGAN, WGAN-GP, biến thể GAN, VAE, latent space, KL divergence, reparameterization.

---

## 1. GAN — Generative Adversarial Network

### Câu chuyện chính

**Trò chơi tiền giả**:

- **Thợ giả mạo (Generator G)**: ban đầu vẽ tiền giả cẩu thả, dễ phát hiện.
- **Cảnh sát (Discriminator D)**: kiểm tra, phân biệt thật/giả.

Vòng đối kháng:
1. Cảnh sát học detect tiền giả → giỏi hơn.
2. Thợ giả thấy tiền của mình bị bắt → vẽ tinh vi hơn.
3. Cảnh sát thấy tiền giả tinh vi → phải học detect tốt hơn.
4. ... lặp lại không hồi kết.

Cuối cùng: **thợ giả vẽ giống thật đến mức cảnh sát đoán random** (50/50). Lúc đó thợ giả đã học được phân phối của tiền thật.

**Đó là GAN**. Hai NN cạnh tranh nhau, cùng cải thiện qua đối kháng.

### Vì sao GAN mạnh?

- Sample chất lượng cao (vd StyleGAN sinh ảnh người fake giống thật khó tin).
- Không cần model explicit của distribution — chỉ cần sample được.

### Vấn đề kinh điển

- **Training instability**: oscillate, divergence — như 2 đứa trẻ đánh nhau hoài không bên nào thắng rõ.
- **Mode collapse**: Generator chỉ sinh 1 vài kiểu → không phủ hết phân phối thật.
- **Vanishing gradient**: Discriminator quá mạnh → Generator không học được gì.

### Trong dự án

3 approach (VAE-GAN, SeqGAN, Gumbel-Softmax) đều là **GAN cho text**. Đặc biệt khó vì text là **discrete** (token IDs), không continuous như ảnh → cần trick (Gumbel-Softmax, REINFORCE) để gradient flow được.

---

## 2. Generator (G) — Họa sĩ tài hoa

### Câu chuyện

Họa sĩ tài hoa nhận **xúc xắc rolled** (= noise vector z, random). Ông dùng các con số để **vẽ bức tranh** (= sample). Mỗi xúc xắc khác → bức tranh khác.

### Trong AI

G là NN map noise z (vd 100 chiều random Gaussian) → sample x (cùng shape với data thật).

**Layers thường gặp trong text Generator**:
- Embedding layer (token ↔ vector).
- Transformer Decoder hoặc LSTM (sinh sequence).
- Output projection (hidden → vocab logits).
- **Sampling layer**:
  - Argmax: chọn token xác suất cao nhất. Không gradient.
  - Gumbel-Softmax: continuous approximation, có gradient. **Dùng trong dự án**.
  - Multinomial: sample theo distribution. Cho RL/REINFORCE (SeqGAN).

### Trong dự án

| Approach | G architecture |
|---|---|
| VAE-GAN | Transformer Decoder + Gumbel-Softmax sampling, input từ latent z |
| SeqGAN | LSTM hoặc Transformer Decoder, sampling theo policy π_θ |
| Gumbel-Softmax | Transformer Decoder + Gumbel-Softmax sampling, input từ noise z |

---

## 3. Discriminator (D) — Cảnh sát

### Câu chuyện

Cảnh sát kiểm tra tiền. Mỗi tờ tiền → trả lời "thật" hay "giả" (kèm độ tự tin).

### Trong AI

D là NN map sample x → score (0 = giả, 1 = thật, hoặc số bất kỳ cho WGAN).

**Layers**:
- Embedding (cho text).
- CNN layers (TextCNN hoặc Dilated CNN) — bắt n-gram patterns.
- Pooling.
- MLP head.
- Output: scalar.

### Trong dự án

Tất cả 3 approach D đều dùng CNN:
- VAE-GAN, SeqGAN: TextCNN với kernels [3, 4, 5].
- Gumbel-Softmax: Dilated CNN với kernels [2, 3, 5, 8, 12, 16].

---

## 4. Mode Collapse — "Thợ giả mạo lười"

### Câu chuyện

Thợ giả mạo phát hiện cảnh sát luôn cho qua **tờ 100k màu xanh**. Anh ta lười, **chỉ vẽ tờ 100k xanh**, không vẽ loại khác.

Cảnh sát check 1000 tờ giả → toàn 100k xanh. Tiền thật trên thị trường có 5 mệnh giá, 5 màu sắc → thợ giả thiếu 4 modes.

**Đó là mode collapse**: Generator chỉ sinh ra 1-2 kiểu, bỏ qua phần còn lại của phân phối thật.

### Cách phát hiện

- Sample 500 mẫu từ G mỗi 1000 iterations.
- Tính độ đa dạng giữa chúng.
- Nếu rất giống nhau (vd median edit distance < 5 tokens) → collapsed.

### Cách xử lý

- **Tăng dropout** trong G (force diverse samples).
- **Inject noise** vào latent.
- **WGAN-GP** (loss function tốt hơn — xem mục 5).
- **Minibatch discrimination**: D thấy cả batch, detect collapse trực tiếp.

### Trong dự án

Mỗi roadmap đều có quy tắc detect mode collapse:
- VAE-GAN: "median edit distance < 5 tokens → tăng dropout 0.1 → 0.3".
- Gumbel-Softmax: "variance giảm đột ngột → tăng dropout hoặc inject noise".

---

## 5. WGAN — "Cách đo khoảng cách hợp lý"

### Câu chuyện

2 đống cát (= 2 phân phối):
- **JSD (Jensen-Shannon Divergence)**: chỉ trả lời "khác hay không?" — 0 hoặc 1, không có gradient ở giữa. Khi 2 đống cát không chạm nhau → không biết hướng nào để mang đống A gần đống B.
- **Wasserstein distance (WD)**: trả lời "**vận chuyển bao nhiêu cát qua quãng đường nào để biến đống A thành đống B**". Số đo có nghĩa kể cả khi 2 đống xa nhau. → có gradient → G biết đi hướng nào.

WGAN dùng Wasserstein distance thay JSD → **stable hơn** + **ít mode collapse**.

### Lipschitz Constraint

Để Wasserstein hoạt động, Discriminator (giờ gọi là **critic**) phải **1-Lipschitz** — tức "không quá nhạy". Cụ thể: nếu input đổi 1 đơn vị, output không được đổi quá 1 đơn vị.

### Trong dự án

3 approach đều dùng **WGAN-GP** (xem mục 6).

---

## 6. WGAN-GP — "Phạt mềm" thay "giam tay"

### Câu chuyện

**WGAN gốc** ép Lipschitz bằng cách **giam tay cảnh sát** (clip weight về [-c, c]). Cứng nhắc, capacity hạn chế.

**WGAN-GP** ép Lipschitz bằng cách **phạt khi cảnh sát đánh quá mạnh** — thêm term loss "phạt" gradient lớn. Mềm mại, hiệu quả hơn.

### Tham số

- **D:G = 5:1**: D update 5 lần per G update.
- **λ_gp = 10**: weight cho gradient penalty term.
- **Optimizer**: Adam $\beta_1=0.5, \beta_2=0.9$.

### Trong dự án

Tất cả 3 approach dùng config WGAN-GP này. Đây là **default GAN training** trong nhiều paper hiện đại — proven stable.

---

## 7. Biến thể GAN

### DCGAN (2015)
GAN cho ảnh dùng deep CNN. **Trong dự án**: không dùng (text, không phải ảnh).

### cGAN — Conditional GAN (2014)
GAN có thêm điều kiện y (label). G(z, y) — sinh data CONDITION trên y.

**Ví dụ**: G(z, y="union_based") → sinh union-based payload.

**Trong dự án**: chưa dùng nhưng natural extension.

### SeqGAN (2017)
GAN cho text với **policy gradient (REINFORCE)** — bypass argmax non-differentiability.

**Trong dự án**: 1 trong 3 approach. G coi như "agent", D + WAF Oracle cung cấp reward.

### MaliGAN (2017)
SeqGAN variant với gradient có variance thấp hơn. **Baseline benchmark** trong Gumbel-Softmax approach.

### RelGAN (2019)
Generator dùng **relational memory** thay LSTM. Tốt cho long sequence. **Baseline** trong Gumbel-Softmax.

### StyleGAN, BigGAN, CycleGAN
Image-only. **Không dùng** trong dự án nhưng nên biết tên.

---

## 8. VAE — Variational Autoencoder

### Câu chuyện

**Autoencoder thường**: cuốn note **viết cố định** ("trang 1 = topic A"). Bạn đọc note → kể lại topic.

**VAE**: cuốn note viết với **độ mờ** ("trang 1 = topic A nằm trong vùng [0.3, 0.7]"). Khi cần sample mới, **mở random một điểm trong vùng** → đọc ra một biến thể của topic A.

→ VAE có thể **sinh data mới** (sample latent z random rồi decode), regular AE không.

### Cấu trúc

- **Encoder**: $x$ → $(\mu, \sigma)$ — output 2 vector mô tả Gaussian.
- **Sample**: $z = \mu + \sigma \odot \epsilon$, $\epsilon$ random $\mathcal{N}(0,I)$.
- **Decoder**: $z$ → $\hat{x}$ — reconstruct.

### Loss VAE = 2 thành phần

1. **Reconstruction loss**: $\hat{x}$ giống $x$ đến đâu.
2. **KL divergence loss**: ép posterior $q(z|x)$ về prior $p(z) = \mathcal{N}(0, I)$.

→ Loss tổng:
$$\mathcal{L}_{VAE} = \mathcal{L}_{recon} + \beta \cdot \mathcal{L}_{KL}$$

### Vấn đề: Posterior Collapse

Decoder quá mạnh → ignore z → KL → 0 → latent vô dụng.

**Mitigations**:
- **KL annealing**: tăng β từ 0 → 1 trong nhiều steps.
- **Free bits**: chỉ phạt KL nếu vượt ngưỡng (vd 2 nats).

### Trong dự án — VAE-GAN

- Encoder Transformer + Decoder Transformer.
- Latent z ∈ R^256.
- KL annealing 0→1 trong 10k steps.
- Free bits λ_fb = 2 nats.

→ Mục tiêu: **latent z học được tách biệt SQL thuần vs SQL ngụy trang**.

---

## 9. Latent Space — "Bản đồ thư viện"

### Câu chuyện

Bản đồ thư viện. Ngoài đời, **quyển sách** dày, nặng. Trên bản đồ, **vị trí sách** chỉ là 1 điểm.
- Sách "Toán học" gần "Vật lý", xa "Thơ ca".
- Bạn có thể **đi từ Toán sang Vật lý** trên bản đồ — tương đương smooth interpolation.
- Cuốn sách thật không tự đi được.

**Latent space** = bản đồ đó. Mỗi điểm = 1 sample tiềm năng.

### Tính chất mong đợi

- **Smoothness**: di chuyển z → output thay đổi smooth.
- **Disentanglement**: từng chiều z control 1 attribute độc lập (vd 1 chiều = "có UNION", 1 chiều = "có obfuscation").
- **Density**: vùng density cao trong z map sang vùng "in-distribution" trong x.

### Latent Walk

Chọn 2 sample $x_A, x_B$ → encode thành $z_A, z_B$ → đi từ $z_A$ đến $z_B$ qua các điểm trung gian → decode mỗi điểm → quan sát sample biến đổi từ A sang B.

### Trong dự án

VAE-GAN claim chính: latent space có thể tách biệt được "kiểu attack". Latent walk là **qualitative experiment** — visualize cấu trúc, không phải metric chính.

---

## 10. KL Divergence — "Khác biệt 2 phân phối"

### Câu chuyện

2 hộp kẹo:
- Hộp **P thật**: 50% sô-cô-la, 50% kẹo dẻo.
- Hộp **Q giả**: 80% sô-cô-la, 20% kẹo dẻo.

KL(P || Q) = "**dùng Q để dự đoán P, sai bao nhiêu**?".

- KL = 0 chỉ khi 2 hộp y hệt.
- Càng khác → KL càng cao.
- **Asymmetric**: KL(P||Q) ≠ KL(Q||P).

### Trong VAE

KL ép encoder $q(z|x)$ về prior $p(z) = \mathcal{N}(0, I)$:
$$\mathcal{L}_{KL} = KL[q(z|x) \| \mathcal{N}(0, I)]$$

Closed-form đẹp vì cả 2 đều Gaussian.

### Đơn vị

- **nats** (log $e$): phổ biến trong ML.
- **bits** (log 2): trong information theory.

### Trong dự án

VAE-GAN warm-up phase: target KL ∈ [5, 50] nats. KL → 0 = posterior collapse, KL → ∞ = prior không informative.

---

## 11. Reparameterization Trick

### Câu chuyện

Cần "đo nhiệt độ giữa mong đợi và phương sai":
- **Cách 1 (không trick)**: lấy **nhiệt kế random** từ kho → đo. Bạn không kiểm soát nhiệt kế nào → khó học.
- **Cách 2 (có trick)**: lấy **nhiệt kế chuẩn** ($\epsilon$ random định trước) → bạn calibrate ($\mu, \sigma$) → đọc $z = \mu + \sigma \cdot \epsilon$. Bây giờ $\mu, \sigma$ là **knobs** bạn tune được.

### Vấn đề được giải quyết

Sampling $z \sim q(z|x)$ là stochastic → gradient không pass qua sampling. Trick: viết $z$ như deterministic transform của $\mu, \sigma$ và noise $\epsilon$ → gradient pass qua $\mu, \sigma$ được.

### Trong code

```python
# Encoder forward
mu, log_var = encoder(x)
std = torch.exp(0.5 * log_var)
eps = torch.randn_like(std)
z = mu + std * eps        # Reparameterization trick
recon = decoder(z)
```

### Trong dự án

VAE-GAN dùng reparameterization trick để train encoder differentiably. Đây là **innovation chính** của VAE.

Cho discrete: Gumbel-Softmax = continuous relaxation, đóng vai trò tương tự cho output decoder (sample token).

---

## 12. Tổng kết: 3 approach của dự án qua góc nhìn này

### VAE-GAN
- **Ý tưởng**: VAE (cấu trúc latent) + GAN (output sắc nét) hybrid.
- **Mạnh**: latent space có cấu trúc, control được kiểu attack.
- **Yếu**: 4 loss components, training phức tạp, posterior collapse risk.

### SeqGAN
- **Ý tưởng**: Generator như "agent" RL, reward từ Discriminator + WAF Oracle, REINFORCE.
- **Mạnh**: tối ưu trực tiếp metric thực (ASR — bypass WAF rate).
- **Yếu**: gradient high-variance, slow training, exposure bias.

### Gumbel-Softmax
- **Ý tưởng**: Gumbel-Softmax cho gradient flow qua discrete sampling, WGAN-GP loss, benchmark.
- **Mạnh**: ổn định, nhanh, đẹp về benchmark — dễ so sánh với baseline.
- **Yếu**: temperature schedule sensitive, không tối ưu ASR trực tiếp.

→ **3 approach = 3 góc nhìn khác nhau cho cùng bài toán** (sinh discrete sequence có ràng buộc grammar).

---

## 13. Bạn đã hiểu gì?

- ✅ GAN: 2 NN đối kháng (G + D) cùng học.
- ✅ Mode collapse: G lười sinh 1 kiểu → cần dropout/noise.
- ✅ WGAN, WGAN-GP: cách đo khoảng cách hợp lý → stable hơn.
- ✅ VAE: encoder probabilistic, ép latent về Gaussian.
- ✅ Latent space: "bản đồ" của data, smooth.
- ✅ KL divergence: đo khác biệt 2 phân phối.
- ✅ Reparameterization trick: cho gradient flow qua sampling.
- ✅ 3 approach của dự án và tradeoff của mỗi cái.

---

## 14. Tổng kết: Bạn đã đọc xong onboarding AI

Sau 4 bài, bạn có **mặt bằng kiến thức AI cơ bản** đủ để:
- ✅ Hiểu các cuộc họp kỹ thuật (không cần đóng góp sâu).
- ✅ Giới thiệu sản phẩm cho khách hàng ở mức "trung cấp".
- ✅ Đọc tiếp các Roadmap kỹ thuật khi rảnh.
- ✅ Tự nghiên cứu sâu hơn trong tương lai.

### Đọc tiếp (theo độ khó tăng dần)

1. **`Onboarding_Data_Engineering.md`** — pipeline data của dự án (đơn giản như onboarding AI).
2. **`AI_Foundations_For_Team_*.md`** — bản có toán hàn lâm cho cùng concepts (challenge yourself).
3. **`Data_Engineering_Foundation.md`** — concepts data engineering với 4 tầng giải thích.
4. **`SQLi-{VAE-GAN, SeqGAN, Gumbel-SoftmaxGAN}-Roadmap.md`** — roadmap kỹ thuật chi tiết 6 giai đoạn. Đọc khi cần thực thi.

### Lời khuyên cuối

Đừng cố hiểu hết trong 1 ngày. AI là field rộng — researchers PhD học cả đời còn chưa hết. Bạn chỉ cần **đủ ngữ cảnh** để trao đổi và làm việc với team. Khi gặp khái niệm mới — quay lại file Onboarding tra. Khi quen — chuyển sang file Foundations.

Chúc bạn onboard thành công! 🎉
