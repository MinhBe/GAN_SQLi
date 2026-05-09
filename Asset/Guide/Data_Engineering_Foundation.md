# Data Engineering Foundation — Nền tảng kiến thức cho Team

> **Đối tượng đọc**: Mọi thành viên team đã có ít background lập trình/AI nhưng cần hiểu vững các khái niệm data engineering của dự án. File này dùng **phong cách 4 tầng**: (1) What/When/Why + ví dụ trẻ em hiểu, (2) Toán học hàn lâm, (3) Mặt trí tuệ nhân tạo, (4) Mặt dữ liệu.
>
> Khác biệt với 2 file kề:
> - `Data_Engineering_Recap.md` → technical recap cho researcher (không 4 tầng).
> - `Onboarding_Data_Engineering.md` → đơn giản hóa hơn, dành cho member không có background.

> **Cập nhật**: 2026-05-04

---

## Mục lục

1. [Phân biệt vai trò: Data Analyst / Data Engineer / Data Researcher](#1-phân-biệt-vai-trò-data-analyst--data-engineer--data-researcher)
2. [Tokenization — Cắt chuỗi thành đơn vị xử lý](#2-tokenization)
3. [Normalization — Chuẩn hóa dữ liệu](#3-normalization)
4. [De-lexicalization — Ẩn danh hóa cấu trúc](#4-de-lexicalization)
5. [Deduplication — Loại trùng lặp](#5-deduplication)
6. [Classification — Phân loại dữ liệu](#6-classification)
7. [Labeling Rules — Quy tắc đánh nhãn](#7-labeling-rules)
8. [Train/Val/Test Split + Frozen Test Set](#8-trainvaltest-split)
9. [Data Quality Metrics](#9-data-quality-metrics)

---

## 1. Phân biệt vai trò: Data Analyst / Data Engineer / Data Researcher

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Data Analyst** = "người đọc số liệu để tìm câu chuyện". Khi: cần báo cáo, dashboard, KPI. Vì sao: business cần ra quyết định dựa trên dữ liệu.

**Data Engineer** = "người xây ống dẫn nước cho dữ liệu". Khi: dữ liệu nằm rải rác ở 5-10 nơi, cần gom lại sạch sẽ. Vì sao: muốn analyst/researcher có dữ liệu "đã rửa sạch" để dùng.

**Data Researcher** = "người thiết kế thí nghiệm trên dữ liệu". Khi: cần thử nghiệm cách mới (model AI, phương pháp đánh nhãn). Vì sao: tạo ra phương pháp/insight mới chưa từng có.

> **Ví dụ trẻ em**: Hình dung một quán phở.
> - **Analyst** = người đếm hôm nay bán bao nhiêu bát, khách nào ăn nhiều cay/ít cay → báo cáo cho chủ quán.
> - **Engineer** = người lo nhập thịt/bánh phở/rau từ chợ, sơ chế, lưu trong tủ lạnh đúng nhiệt độ, để đầu bếp lúc nào cũng có nguyên liệu sạch.
> - **Researcher** = người nghĩ ra công thức nước dùng mới, thử kết hợp nguyên liệu lạ, đo phản ứng khách → tạo ra món phở "phong cách 2026" chưa quán nào có.

### Tầng 2 — Toán học (hàn lâm)

3 vai trò có thể formalize qua **chuỗi xử lý dữ liệu** $D_{raw} \xrightarrow{T_E} D_{clean} \xrightarrow{T_A} S_{insights} \xrightarrow{T_R} M_{novel}$:

- **Data Engineer** thực hiện phép biến đổi $T_E: D_{raw} \to D_{clean}$ — định nghĩa **schema mapping**, **normalization functions**, **deduplication relations**, đảm bảo tính **idempotency** ($T_E(T_E(x)) = T_E(x)$) và **reproducibility**.
- **Data Analyst** thực hiện $T_A: D_{clean} \to S_{insights}$ — chủ yếu là phép **aggregation** ($\sum, \bar{x}, \text{percentile}$), **conditional probability** ($P(A|B)$), **hypothesis testing** ($H_0$ vs $H_1$).
- **Data Researcher** thực hiện $T_R: D_{clean} \to M_{novel}$ — đề xuất **mô hình toán mới** ($p_\theta(x)$, optimization objective), kiểm chứng qua **statistical significance** với confidence interval, bootstrap, A/B test.

**Phép toán nền tảng** chia sẻ: thống kê mô tả (mean, std, quantile), entropy ($H(X) = -\sum p(x)\log p(x)$), divergence (KL, JS, Wasserstein), linear algebra (rank, PCA, SVD).

### Tầng 3 — Mặt trí tuệ nhân tạo

Trong pipeline AI:
- **Engineer** đảm bảo input tensor đúng shape/dtype/scale cho model. Nếu data bẩn (NaN, mismatched shape) → model NaN loss, không train được.
- **Analyst** đo performance model (accuracy, F1, ROC-AUC) và phân phối lỗi để chỉ ra bias/leakage.
- **Researcher** thiết kế kiến trúc/loss/regularizer mới, viết paper với contribution có thể replicate được.

Trong dự án này, **bạn (researcher) đã đảm nhiệm cả 3 vai trò**: build pipeline (engineer), phân tích phân phối + confidence (analyst), thiết kế 3 hướng GAN (researcher).

### Tầng 4 — Mặt dữ liệu

Output mỗi vai trò produce trong dự án:
- **Engineer output**: `master_unlabeled.csv` (41,460 rows × 7 cột) + `result_batch_*.csv` (1,382 file × 30 rows × 5 cột) — tensor-ready data.
- **Analyst output**: bảng phân phối 13 SQLi types (mục 5 trong Recap), confusion matrix giữa rule-based vs AI classifier, distribution của confidence.
- **Researcher output**: 3 Roadmap (`SQLi-{VAE-GAN,SeqGAN,Gumbel-SoftmaxGAN}-Roadmap.md`) + sẽ là 3 model checkpoints + 1 paper.

---

## 2. Tokenization

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Tokenization** = chia chuỗi text thành các đơn vị nhỏ (tokens) mà model AI có thể xử lý. Khi: trước mọi NLP/sequence model. Vì sao: model không hiểu chuỗi ký tự liên tục, chỉ hiểu danh sách "ô" rời rạc đã được đánh số (token IDs).

> **Ví dụ trẻ em**: Một câu là một sợi dây dài. Tokenization là **cắt sợi dây** thành các đoạn ngắn (mỗi đoạn = một từ hoặc một ký hiệu). Cắt khéo: được những đoạn có nghĩa ("xin", "chào", "bạn"). Cắt vụng: được những đoạn vô nghĩa ("xinch", "àob", "ạn"). Cắt khéo hay vụng quyết định việc đứa trẻ AI có hiểu được câu không.

### Tầng 2 — Toán học (hàn lâm)

Tokenizer là một hàm $\text{tok}: \Sigma^* \to V^*$ với:
- $\Sigma$: alphabet (tập ký tự, vd Unicode).
- $V$: **vocabulary** — tập hữu hạn các tokens.
- $\Sigma^*$: chuỗi ký tự độ dài bất kỳ.
- $V^*$: chuỗi token độ dài bất kỳ.

**Các họ tokenizer**:

1. **Whitespace tokenizer**: $\text{tok}(s) = s.\text{split}(\text{` '})$. Đơn giản, không học gì.
2. **Regex-based**: $\text{tok}(s) = [\text{re.findall}(p_i, s) \text{ for } p_i \in \mathcal{P}]$. Pattern set $\mathcal{P}$ design cho domain.
3. **Byte-Pair Encoding (BPE)**: Train trên corpus, học merge rules để tối ưu hóa $\sum_v c(v) \log |v|$ (cân bằng tần suất với độ dài token).
4. **WordPiece / SentencePiece**: Variant của BPE với likelihood-based merging.

**Đo chất lượng tokenizer**: 
- **Compression ratio**: $r = \frac{|s|_{chars}}{|tok(s)|_{tokens}}$ — càng cao càng nén tốt.
- **OOV rate**: $\text{OOV} = \frac{\#\{v \notin V\}}{\#\{tokens\}}$ — càng thấp càng tốt.
- **Entropy preservation**: tokenization tốt giữ được $H(P_{token}) \approx H(P_{char})$ + delta nhỏ.

### Tầng 3 — Mặt trí tuệ nhân tạo

Trong pipeline:
- **Embedding layer** ánh xạ mỗi token ID → vector $\mathbb{R}^{d}$ (thường $d = 128$ - $1024$).
- Sequence model (RNN/Transformer) nhận sequence of embeddings và học pattern.
- **Lưu ý cho dự án này**: KHÔNG dùng BPE/WordPiece pretrained (vd `gpt2-tokenizer`) cho SQL. Lý do: chúng được train trên English corpus, sẽ chia `UNION` thành `UN` + `ION`, làm mất signal tấn công. Phải dùng **regex-based SQL-aware tokenizer** hoặc train BPE from scratch trên SQL corpus.

### Tầng 4 — Mặt dữ liệu

**Input**: string raw, vd `"' UNION SELECT 1,version() -- "`.

**Output**: list[int] hoặc list[str], vd:
```python
["'", "UNION", "SELECT", "1", ",", "version", "(", ")", "--"]
# hoặc IDs:
[37, 8, 9, 14, 12, 23, 5, 6, 4]
```

**Schema yêu cầu**:
- Dtype: `int64` cho IDs, `string` cho tokens.
- Shape: `(batch_size, seq_len)` sau khi pad/truncate.
- Vocabulary file: JSON map `token → id`, kèm special tokens (`<PAD>=0`, `<UNK>=1`, `<SOS>=2`, `<EOS>=3`, `<TABLE>`, `<COL>`, `<NUM>`, `<STR>`).
- Reverse map cho decoding: `id → token`.

**Trong dự án này**: tokenizer chưa được fix — sẽ định nghĩa cụ thể trong code của từng approach (xem `<Approach>_SQLi/src/tokenizer.py` trong Guiding tương ứng).

---

## 3. Normalization

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Normalization** = đưa các biến thể bề mặt khác nhau của cùng một payload về **một dạng chuẩn duy nhất**. Khi: trước classification và dedup. Vì sao: nếu không normalize, 2 payload `' UNION SELECT` và `%27%20UNION%20SELECT` (URL-encoded) sẽ bị coi là khác nhau dù bản chất giống.

> **Ví dụ trẻ em**: Cùng một bạn tên "An", có nơi viết "An", nơi viết "AN", nơi viết "Aaaan!", nơi viết "Án" (sai dấu). Normalization là **viết thống nhất thành "An"** ở mọi nơi để máy tính biết đây là cùng một người.

### Tầng 2 — Toán học (hàn lâm)

Normalization là một hàm **idempotent** $N: \Sigma^* \to \Sigma^*$ thỏa $N(N(x)) = N(x)$ (áp dụng 2 lần = 1 lần). Đặc tính idempotent là **bắt buộc** vì nếu pipeline chạy lại nhiều lần (vd resume sau crash), kết quả phải ổn định.

**Tổng hợp các bước trong dự án**:

$N(x) = N_{lower} \circ N_{ws} \circ N_{html} \circ N_{url}(x)$

- $N_{url}$: URL decode — `%27 → '`, `%20 → space`, áp dụng đệ quy nếu có double-encoding ($N_{url} \circ N_{url}$).
- $N_{html}$: HTML entity decode — `&#39; → '`, `&lt; → <`.
- $N_{ws}$: Whitespace collapse — replace `\s+` → ` ` (1 space), trim hai đầu.
- $N_{lower}$: Case fold — chỉ áp dụng với SQL keywords, KHÔNG với string literal trong dấu nháy (xem fragmentation rules).

**Phép toán nền tảng**: composition of functions, fixed-point iteration (cho double-decode), regex matching (finite automata).

### Tầng 3 — Mặt trí tuệ nhân tạo

Tại sao quan trọng cho model:
- Giảm **vocabulary explosion**: nếu không normalize, `UNION`, `union`, `UnIoN`, `%55nion` đều thành tokens khác nhau → vocabulary lớn vô lý → model khó học.
- Tăng **signal-to-noise ratio**: model tập trung học pattern logic của tấn công, không bị phân tâm bởi obfuscation surface.
- Đặc biệt quan trọng với **few-shot classes** (rce, polyglot có < 20 mẫu): mọi sample đều quý, không thể để 50% bị "ẩn" bằng obfuscation.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:
- Cột `payload_raw` = giữ nguyên, dùng để audit hoặc unrlike.
- Cột `payload_norm` = output của $N$, đây là **input thực sự cho model**.
- Cột `is_obfuscated` = flag nếu $\exists i: x \neq N_i(x)$ (nếu có ít nhất 1 bước normalize thay đổi nội dung) → biết payload nào là "natural", payload nào là "obfuscated".

**Ví dụ row**:
```csv
payload_raw                    | payload_norm                | is_obfuscated
"%27%20OR%201%3D1--"          | "' OR 1=1--"                | True
"' OR 1=1--"                  | "' OR 1=1--"                | False
"&#39; OR 1&#61;1--"          | "' OR 1=1--"                | True
```

**Note**: 3 row trên có `payload_norm` giống hệt → ở bước dedup sẽ collapse về 1, nhưng giữ count "frequency" làm metadata.

---

## 4. De-lexicalization

### Tầng 1 — What / When / Why + ví dụ trẻ em

**De-lexicalization** = thay tên cụ thể (tên bảng, tên cột, số, chuỗi) bằng **placeholder tổng quát** (`<TABLE>`, `<COL>`, `<NUM>`, `<STR>`). Khi: muốn ép model học **cấu trúc logic** thay vì memorize giá trị cụ thể. Vì sao: nếu giữ nguyên tên "users", "products", "id_42", model sẽ học theo từng tên → overfit, không generalize sang DB khác.

> **Ví dụ trẻ em**: Câu chuyện "Thỏ hái cà rốt" và "Mèo bắt cá" có **cấu trúc giống nhau** (chủ ngữ + hành động + đối tượng). Nếu kể truyện cho trẻ chỉ để dạy "có chủ ngữ-động từ-tân ngữ", ta thay thành "**Nhân vật** thực hiện **hành động** lên **đối tượng**". Trẻ học được khung thay vì học từng câu chuyện.

### Tầng 2 — Toán học (hàn lâm)

De-lexicalization là một **abstraction function** $\delta: V^* \to V^{*}_{abstract}$ với $V_{abstract} = V_{keywords} \cup \{T, C, N, S, ...\}$ (giữ keyword + thêm placeholder).

**Hai biến thể**:

1. **Full de-lex** (cho SeqGAN, Gumbel-Softmax):
   $$\delta_{full}(t) = \begin{cases} t & \text{if } t \in V_{keywords} \cup V_{operators} \\ \tau(t) & \text{otherwise (replace by placeholder type)} \end{cases}$$
   với $\tau: V \to \{<\text{TABLE}>, <\text{COL}>, <\text{NUM}>, <\text{STR}>\}$ là type classifier.

2. **Partial de-lex** (cho VAE-GAN):
   $$\delta_{partial}(t) = \begin{cases} t & \text{if } t \in V_{keywords} \cup V_{attack\_signals} \\ \tau(t) & \text{otherwise} \end{cases}$$
   với $V_{attack\_signals} \supset V_{keywords}$, bao gồm cả các function tấn công (`SLEEP`, `BENCHMARK`, `extractvalue`, `pg_sleep`, ...).

**Information-theoretic view**: De-lex giảm **entropy** corpus, làm phân phối **tập trung** ở các pattern logic. $H(\delta(X)) < H(X)$ — đây là intentional information loss để tăng generalization.

**Phép toán nền tảng**: type-based substitution, set membership check, finite-state classification.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Variance reduction**: De-lex giảm variance của input distribution → policy gradient (SeqGAN) ổn định hơn.
- **Latent space structure**: Trong VAE-GAN, partial de-lex giúp encoder học latent z chỉ encode "kiểu tấn công", không encode "tên bảng cụ thể" → latent space có cấu trúc rõ ràng.
- **Vocabulary size giảm**: Từ ~50k unique tokens (raw) → ~500 tokens (full de-lex) → embedding layer nhỏ, train nhanh.

### Tầng 4 — Mặt dữ liệu

**Trong `master_unlabeled.csv`**:
- Cột `payload_norm`: bản đã normalize, GIỮ tên cụ thể.
- Cột `payload_delex`: bản đã de-lex (full).

**Ví dụ**:
```
payload_norm:   "select * from users where id = '42' or 1 = 1 -- "
payload_delex:  "select * from <TABLE> where <COL> = <STR> or <NUM> = <NUM> -- "
```

**Re-lexicalization** (bước ngược): khi inference (Generator output `<TABLE>`), cần thay placeholder bằng giá trị thực dựa trên **target schema** (JSON: tables, columns, types). Đây là phần **Re-lex module** trong `Gumbel-Softmax_SQLi/src/relex.py` (sẽ implement). Xem chi tiết trong `SQLi-Gumbel-SoftmaxGAN-Roadmap.md` Giai đoạn 6.

---

## 5. Deduplication

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Deduplication (dedup)** = loại bỏ các bản trùng lặp khỏi dataset. Khi: ngay sau normalize, trước classify. Vì sao: payload trùng nhau làm phân phối lệch (model học quá nhiều 1 mẫu) và lãng phí compute.

> **Ví dụ trẻ em**: Bạn có 100 cuốn sách. Đếm thì hóa ra có 30 cuốn "Doraemon tập 1", 70 cuốn khác nhau. Dedup là **bỏ 29 cuốn Doraemon thừa, giữ lại 1 cuốn**. Còn 71 cuốn thực sự "khác nhau".

### Tầng 2 — Toán học (hàn lâm)

Dedup là phép **partition** dataset $D$ thành các equivalence classes theo một quan hệ tương đương $\sim$, sau đó chọn 1 đại diện mỗi class.

**3 cấp dedup trong dự án**:

1. **Exact match** (sau normalize):
   $$x \sim_E y \iff N(x) = N(y)$$
   Implementation: hash-based, $O(n)$ với hash table.

2. **Normalized + structural** (sau de-lex):
   $$x \sim_S y \iff \delta(N(x)) = \delta(N(y))$$
   Bắt được các payload cùng cấu trúc khác giá trị (vd `OR 1=1` và `OR 7=7` → cùng `OR <NUM>=<NUM>`).

3. **Semantic dedup** (MinHash + LSH):
   $$x \sim_{sem} y \iff \text{Jaccard}(\text{shingles}(x), \text{shingles}(y)) \geq \theta$$
   với $\theta$ thường = 0.85. **MinHash** xấp xỉ Jaccard với cost $O(k)$ thay $O(|s|)$. **LSH** (Locality-Sensitive Hashing) bucket các MinHash gần nhau, tránh phải so sánh $O(n^2)$ pairs.

**Jaccard similarity**:
$$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

**MinHash estimator**: Với $h_1, ..., h_k$ random hash functions:
$$\hat{J}(A, B) = \frac{1}{k}\sum_{i=1}^k \mathbb{1}\{\min h_i(A) = \min h_i(B)\}$$
$\hat{J} \to J(A,B)$ khi $k \to \infty$, với $\text{Var}(\hat{J}) = \frac{J(1-J)}{k}$.

**Phép toán nền tảng**: equivalence relation, hash function, set theory, probabilistic data structures (Bloom filter, MinHash, HyperLogLog).

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Class balance**: Dedup ngăn 1 payload phổ biến (vd `' OR 1=1--`) chiếm 30% corpus → model bias.
- **Train/test contamination**: Nếu không dedup giữa train và test, sample test có thể xuất hiện trong train → metric đánh giá bị phồng giả tạo.
- **Self-BLEU evaluation**: Sau khi train, đo Self-BLEU trên samples sinh ra. Nếu Self-BLEU cao = model collapse vào ít mode. Dedup tốt input → có thể đo Self-BLEU output có nghĩa.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:
- Trước dedup: ~195k mẫu raw từ 5 nguồn.
- Sau exact dedup: ~80k.
- Sau structural dedup: ~50k.
- Sau semantic dedup (Jaccard ≥ 0.85): **41,460** (số cuối cùng trong `master_unlabeled.csv`).

**Code**: `data_engine/deduplicator.py`. Workflow:
1. Tính `payload_norm_hash = sha256(payload_norm)` → exact dedup bằng hash table.
2. Tính `payload_delex_hash` → structural dedup.
3. Compute MinHash signature (k=128 functions, shingle size=5) → LSH với threshold 0.85 → semantic dedup.

**Verify**: chạy `Asset/Opencode/check_duplicates_v2.py` để spot-check còn duplicate nào không.

---

## 6. Classification

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Classification** = gán mỗi sample một nhãn từ tập rời rạc các loại. Khi: muốn biết payload thuộc loại tấn công nào (union, boolean, time, error, ...). Vì sao: (a) split per-type cho conditional generation, (b) report per-class metric, (c) đảm bảo train data balance.

> **Ví dụ trẻ em**: Bạn có 100 con vật. Phân loại = chia thành **chó / mèo / chim / cá**. Mỗi con vật được dán 1 nhãn duy nhất. Sau đó bạn có thể đếm "mỗi loại bao nhiêu con" hoặc cho con cá vào hồ riêng, con chim vào lồng riêng.

### Tầng 2 — Toán học (hàn lâm)

Classifier là một hàm $f: \mathcal{X} \to \mathcal{Y}$ với $\mathcal{Y} = \{c_1, ..., c_K\}$ tập K class hữu hạn.

**3 paradigm trong dự án**:

1. **Rule-based** $f_{rule}$:
   $$f_{rule}(x) = \arg\max_c \mathbb{1}\{\exists \text{ pattern } p_c \in \mathcal{P}_c: p_c \text{ matches } x\}$$
   Pattern set $\mathcal{P}_c$ design thủ công. **Confidence** = số pattern match được, normalize.

2. **ML-based** (TF-IDF + Random Forest):
   - TF-IDF: $\phi(x)_{w} = \text{tf}(w, x) \cdot \log\frac{N}{\text{df}(w)}$ với tf = term frequency trong document, df = document frequency trong corpus.
   - Random Forest: ensemble của $T$ decision trees, mỗi tree vote, majority wins.
   - Loss train: cross-entropy $\mathcal{L} = -\sum_i \log p(y_i | x_i; \theta)$.

3. **AI-based (LLM)** $f_{LLM}$:
   - Prompt engineering: feed payload + 13 class definitions vào LLM, parse JSON output.
   - Confidence từ LLM self-assessment hoặc log-prob của token.

**Hierarchical classification** (nếu áp dụng): chia tree, vd cấp 1 = `injection_type` (blind/visible), cấp 2 = `mechanism` (time/boolean cho blind; union/error cho visible).

**Multi-label** (chưa dùng trong dự án): một payload có thể vừa `union_based` vừa `auth_bypass`. Nhưng dự án này dùng **single-label** với `polyglot` là class riêng cho trường hợp đa cấu trúc.

**Phép toán nền tảng**: probability distribution over labels, softmax, decision boundary, mutual information $I(X; Y)$.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Cascading classification**: Tier 1 → Tier 2 → Tier 3 (xem mục 7 Recap). Lý do: rule-based nhanh + chính xác cho easy cases, LLM đắt nhưng cần cho hard cases.
- **Confidence threshold**: Sample với confidence < 0.6 được flag để human review. Đây là **active learning** — dùng AI uncertainty để target effort của con người.
- **Class imbalance**: 13 class có phân phối lệch (76% unknown, 0.0% rce). Khi train classifier, dùng **weighted loss**: $\mathcal{L} = -\sum_i w_{y_i} \log p(y_i|x_i)$ với $w_c = \frac{N}{K \cdot N_c}$.

### Tầng 4 — Mặt dữ liệu

**Input** cho classifier:
- Rule-based: chuỗi raw hoặc đã norm.
- ML: vector TF-IDF (sparse, dim ~5000-10000).
- LLM: prompt + payload (text).

**Output schema** (như trong `result_batch_*.csv`):
| col | type | range |
|---|---|---|
| sqli_type | enum | 1 trong 13 |
| db_engine | enum | 1 trong 7 |
| confidence | float | [0, 1] |
| reasoning | string | max 200 chars |

**Trong dự án**: ML classifier đã train, lưu tại `Asset/Data/data/artifacts/tfidf_vectorizer.pkl` (chỉ vectorizer, model có thể đã embed trong pickle khác hoặc cần re-train từ `data_engine/train_classifier.py`).

---

## 7. Labeling Rules

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Labeling rules** = bộ quy tắc để con người (hoặc AI) nhất quán trong việc gán nhãn. Khi: trước khi đánh nhãn dataset. Vì sao: nếu mỗi người gán theo cảm tính, dataset không đáng tin (1 payload có thể bị gán 3 nhãn khác nhau bởi 3 người).

> **Ví dụ trẻ em**: Trong lớp cô giáo dán nhãn vở "giỏi/khá/trung bình". Nếu cô giáo cảm tính, hôm nay vui dán "giỏi" cho điểm 7, hôm sau dán "khá" cho điểm 7 → trẻ con không biết tiêu chí đâu mà phấn đấu. **Labeling rules** = "≥ 9 = giỏi, 7-8.9 = khá, < 7 = trung bình" → mọi người, mọi ngày đều gán giống nhau.

### Tầng 2 — Toán học (hàn lâm)

Labeling rules có thể formalize qua:

**Inter-annotator agreement** đo bằng **Cohen's Kappa**:
$$\kappa = \frac{p_o - p_e}{1 - p_e}$$
- $p_o$: observed agreement (tỉ lệ 2 annotator gán cùng nhãn).
- $p_e$: expected agreement nếu họ gán random theo phân phối marginal.
- $\kappa \in [-1, 1]$. Threshold thường: $\kappa \geq 0.8$ là acceptable cho academic publication.

**Multi-annotator** (>2): mở rộng thành **Fleiss' Kappa**:
$$\kappa_F = \frac{\bar{P} - \bar{P_e}}{1 - \bar{P_e}}$$

**Decision tree cho 13-class taxonomy** (cấu trúc rules):
```
Level 1: Có pattern attack rõ không? 
  ├─ Không → unknown
  └─ Có →
     Level 2: Loại signal chính?
        ├─ UNION SELECT → union_based
        ├─ Boolean (1=1, 1=2) → boolean_blind
        ├─ Time (SLEEP, WAITFOR, pg_sleep) → time_blind
        ├─ Error (extractvalue, utl_inaddr) → error_based
        ├─ Stacked (;) + DDL/DML → stacked_queries
        ├─ Heavy CPU (cross-join) → heavy_query
        ├─ DNS/HTTP exfil → out_of_band
        ├─ EXEC/xp_cmdshell → rce
        ├─ ' OR '1'='1' for login → auth_bypass
        ├─ Multi-context (XSS+SQLi) → polyglot
        ├─ JOIN → lateral
        └─ Stored (multi-step) → second_order
```

**Confidence calibration**: rule-based output 0/1 → cần map sang [0,1] qua **Platt scaling** hoặc **isotonic regression** trên held-out set.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Label noise**: nếu rule có lỗi (gán sai 5%), ML classifier học sẽ inherit noise → cap accuracy ở ~95%. Cần thường xuyên audit nhãn.
- **Label smoothing** trong training: thay one-hot $[0,...,1,...,0]$ bằng $[\epsilon/K, ..., 1-\epsilon, ..., \epsilon/K]$ để tránh model overconfident.
- **Soft labels** từ LLM: `{"union_based": 0.85, "stacked_queries": 0.15}` → có thể train với KL loss thay cross-entropy → leverage uncertainty từ teacher.

### Tầng 4 — Mặt dữ liệu

**Trong dự án — quy tắc thực tế**:
1. Nếu match nhiều rule (vd vừa có `UNION` vừa có `;`) → ưu tiên rule có **confidence cao hơn** (tính theo specificity).
2. Confidence ≥ 0.85: accept tự động.
3. Confidence 0.60-0.85: human review (đã làm thủ công bởi chính bạn).
4. Confidence < 0.60: gán `unknown`, queue cho re-classify pass sau.
5. `db_engine` nếu không match signature → `unknown`, không bịa.

**File rules**: implicit trong `data_engine/classifier.py` (rule patterns) + `data_engine/ai_classifier.py` (LLM prompt template). Nên **export rules ra JSON** để audit dễ hơn.

---

## 8. Train/Val/Test Split

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Train/Val/Test split** = chia dataset thành 3 phần: **train** để dạy model, **val** để chỉnh hyperparameter, **test** để đánh giá cuối cùng. Khi: ngay sau khi có dataset sạch và labeled. Vì sao: nếu test chung với train, model "biết câu trả lời", metric đánh giá không có nghĩa.

> **Ví dụ trẻ em**: Cô giáo có 100 bài toán. **Train (70 bài)** = đưa cho học sinh học và làm thử. **Val (15 bài)** = đưa kiểm tra giữa kỳ, nếu trẻ làm tệ thì cô đổi cách dạy. **Test (15 bài)** = bài thi cuối kỳ, KHÔNG được xem trước. Nếu cô lỡ cho trẻ xem test trước thì điểm cao cũng vô nghĩa.

### Tầng 2 — Toán học (hàn lâm)

Cho dataset $D = \{(x_i, y_i)\}_{i=1}^N$, split $D = D_{train} \sqcup D_{val} \sqcup D_{test}$ (disjoint union) với tỉ lệ điển hình 70/15/15 hoặc 80/10/10.

**Stratified split**: với mỗi class $c$, $\frac{|D_{train,c}|}{|D_c|} = \frac{|D_{train}|}{|D|}$ — đảm bảo phân phối class trong mỗi tập giống full dataset.

**Frozen test set**: $D_{test}$ được commit vào git, KHÔNG được tái shuffle. Lý do: mọi baseline so sánh phải trên cùng test set, nếu không số liệu không comparable.

**K-fold cross-validation** (alternative cho val): chia thành $k$ fold, train trên $k-1$, val trên 1, lặp $k$ lần, lấy mean. Ưu: dùng full data để val. Nhược: tốn $k$ lần compute.

**Phép toán nền tảng**: random sampling without replacement, hypergeometric distribution, stratification.

**Stratification formula**: 
$$P(\text{sample}_i \in D_{train}) = p_{train}, \quad P(c | \text{sample} \in D_{train}) = P(c | D)$$

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Data leakage** = sample test xuất hiện gần giống trong train (vd cùng URL nhưng khác user_id). Phổ biến: time-series leakage, near-duplicates leakage. Trong dự án này, dedup TRƯỚC split để tránh near-dup leakage.
- **Validation purpose**: tune hyperparameters (learning rate, batch size, β trong VAE-GAN, τ trong Gumbel-Softmax). Mỗi lần thay HP, train trên train, đo trên val. KHÔNG đo trên test.
- **Test purpose**: chạy 1 lần duy nhất sau khi đã chọn HP → report số trong paper. Nếu chạy nhiều lần và pick best → "test set leakage" — invalidate kết quả.

### Tầng 4 — Mặt dữ liệu

**Trong dự án**:
- Đã có `Asset/Data/data/splits/train_idx.npy`, `test_idx.npy` (stored as numpy index arrays).
- Phương án đề xuất sau khi merge `master_sqli.csv`:
  - Stratified split theo `sqli_type`, tỉ lệ 70/15/15.
  - Sample size: train ~29,022; val ~6,219; test ~6,219.
  - **Frozen test**: lưu thành `Asset/Data/frozen_test_set.csv`, hash MD5, commit git.
  - Per-approach split bổ sung: VAE-GAN/SeqGAN/Gumbel có thể cần dataset transformation khác từ cùng base split (vd full vs partial de-lex).

**Verification cần làm**:
```python
assert len(set(train_idx) & set(test_idx)) == 0  # no overlap
assert abs(p_class_train - p_class_full) < 0.01  # stratification preserved
```

---

## 9. Data Quality Metrics

### Tầng 1 — What / When / Why + ví dụ trẻ em

**Data quality metrics** = các con số đo "dataset có ổn không". Khi: sau pipeline hoàn thiện, trước feed vào model. Vì sao: model AI dù tốt đến đâu cũng "garbage in, garbage out" — input rác = output rác.

> **Ví dụ trẻ em**: Bạn nấu phở. Trước khi bưng cho khách, **kiểm tra chất lượng**: nước có trong không, thịt có chín không, rau có sạch không, có bị chua không. Nếu có "lỗi" thì sửa lại. Data quality metric là **bảng checklist kiểm tra dataset** trước khi đưa cho model.

### Tầng 2 — Toán học (hàn lâm)

5 nhóm metrics chính:

#### 9.1 Coverage
- $\text{Coverage} = \frac{|D_{labeled}|}{|D|}$ — tỉ lệ sample có nhãn (≠ unknown).
- Trong dự án: `Coverage = 1 - 0.763 = 0.237` (76.3% là unknown). Thấp → cần re-classify pass.

#### 9.2 Class Balance (Entropy-based)
$$H(Y) = -\sum_{c=1}^K p(c) \log p(c)$$
- $H(Y)$ tối đa khi uniform: $H_{max} = \log K$.
- **Normalized entropy**: $\eta = H(Y) / H_{max} \in [0,1]$.
- Trong dự án: $\eta \approx 0.4$ (rất imbalanced) → cần oversample/weighted loss.

#### 9.3 Duplication Rate
$$\text{DupRate} = 1 - \frac{|D_{unique}|}{|D|}$$
Sau dedup, nên < 0.01 (< 1% còn duplicate).

#### 9.4 Leakage Detection
- **Train-test similarity**: $\text{leakage} = \frac{|\{x \in D_{test} : \exists y \in D_{train}, \text{sim}(x,y) > \theta\}|}{|D_{test}|}$.
- Threshold $\theta = 0.9$ (rất gần) → leakage > 1% là alarming.

#### 9.5 Annotation Quality
- **Inter-annotator agreement**: Cohen's Kappa $\kappa$ (mục 7).
- **Confidence distribution**: histogram của `confidence` trong `result_batch_*.csv`. Mong đợi peak ở > 0.85.

**Phép toán nền tảng**: probability, entropy, similarity metrics (Jaccard, edit distance, embedding cosine), statistical hypothesis testing.

### Tầng 3 — Mặt trí tuệ nhân tạo

- **Coverage thấp** → model train trên 24% có nhãn, 76% unknown → khó học pattern hiếm.
- **Class imbalance** → loss bị dominate bởi class phổ biến → model gần như không sinh được class hiếm. Mitigation: weighted loss, focal loss, oversample minority.
- **Leakage** → metric đánh giá phồng giả tạo. Nếu test leak vào train → accuracy 99% nhưng deploy thật chỉ 60%.
- **Annotation noise** → cap accuracy của model. Nếu nhãn có noise 5%, model không thể đạt > 95% accuracy thật.

### Tầng 4 — Mặt dữ liệu

**Báo cáo data quality khuyến nghị** (sinh sau khi merge `master_sqli.csv`):

```
=== DATA QUALITY REPORT ===
Total samples: 41,460
Coverage: 23.7% (10,082 labeled, 31,378 unknown)

Class distribution (top 5):
  unknown: 76.3% (31,378)
  union_based: 6.8% (2,819)
  boolean_blind: 5.9% (2,446)
  error_based: 4.3% (1,783)
  time_blind: 4.1% (1,700)
Normalized entropy: 0.41 (imbalanced)

Duplication after dedup: 0.05% (21 dups remaining)
Train-test similarity > 0.9: 0.3% (verified, acceptable)

Confidence distribution:
  >= 0.85: 78.2%
  0.60-0.85: 18.7% (human-reviewed)
  < 0.60: 3.1% (queued for re-classify)
```

**Implementation**: chưa có script chuyên dụng — đề xuất tạo `data_engine/quality_report.py` chạy sau merge.

---

## 10. Ngữ cảnh dự án — Cách áp dụng

Mỗi concept ở trên đều áp vào pipeline thực tế. Cross-reference:

| Concept | File trong `data_engine/` | Output trong `Asset/Data/` |
|---|---|---|
| Tokenization | (per-approach trong từng folder) | (sẽ có sau implement) |
| Normalization | `normalizer.py`, `prepare.py` | `master_unlabeled.csv` cột `payload_norm` |
| De-lexicalization | `prepare.py` | `master_unlabeled.csv` cột `payload_delex` |
| Deduplication | `deduplicator.py` | implicit (trong process) |
| Classification | `classifier.py`, `train_classifier.py`, `ai_classifier.py` + `Asset/Opencode/classify*.py` | `results/result_batch_*.csv` |
| Labeling rules | implicit trong rule patterns + LLM prompts | (cần export ra JSON để audit) |
| Train/Val/Test split | `splitter.py` | `data/splits/{train,test}_idx.npy` |
| Quality metrics | (chưa có script) | (cần tạo `data_engine/quality_report.py`) |

---

## 11. Tài liệu tham chiếu chéo

- `Asset/Guiding/Data_Engineering_Recap.md` — Tổng quan technical pipeline cho researcher.
- `Asset/Guiding/Onboarding_Data_Engineering.md` — Phiên bản đơn giản hóa cho member mới.
- `Asset/Guiding/AI_Foundations_For_Team_*.md` — 4 file giáo dục AI concepts (neural net, CNN/RNN, Transformer, generative).
- `Asset/Guiding/SQLi-{VAE-GAN,SeqGAN,Gumbel-SoftmaxGAN}-Roadmap.md` — Roadmap chi tiết 6 giai đoạn cho từng approach.
- `Asset/Opencode/KE_HOACH.md` & `RECOVERY.md` — Workflow vận hành classification.

---

*File này được duy trì như "sổ tay nền tảng" — cập nhật khi có concept data engineering mới được áp vào pipeline. Không nên sửa khi chỉ thay đổi paths/numbers (đó là việc của Recap).*
