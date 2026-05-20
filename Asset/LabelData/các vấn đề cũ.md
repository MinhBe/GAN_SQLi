# Các Vấn Đề Cũ — Pipeline Labeling V1–V4

> Tổng hợp phân tích sai lầm, hậu quả chuỗi và định hướng khắc phục
> Dự án: GAN_SQLi — SeqGAN SQLi Payload Generator
> Ngày: 2026-05-18

---

## KẾT QUẢ THỰC TẾ V4 (ĐỀU FAIL)

| Metric | Kết quả V4 | Target | Trạng thái |
|--------|-----------|--------|------------|
| Collision rate | 40.18% | < 10% | [FAIL] |
| Top-10 coverage | 17.37% | < 10% | [FAIL] |
| Type entropy | 1.76 bits | > 2.0 bits | [FAIL] |
| Gold set size | 662 rows | > 4,000 rows | [FAIL] |
| Function preservation | ~70% | > 95% | [FAIL] |

---

## SAI LẦM #1 — Không Dedup Trước Khi Label

### Vấn đề cụ thể

Payload `' OR '1'='1' --` xuất hiện trong 3 nguồn Kaggle khác nhau (gambleryu, sajid576, syedsaqlainhussain).
Không có bước SHA-256 dedup trước khi label → payload này tồn tại **3 lần** trong dataset.

### Hậu quả chuỗi

```
3 copies cùng payload → dataset "phình ra" giả tạo
→ Model thấy payload đơn giản này 3 lần nhiều hơn payload phức tạp 1 lần
→ Model học OVERWEIGHT cho pattern đơn giản
→ Val perplexity 1.74 trông tốt nhưng model đang MEMORIZE duplicates
→ Khi generate: chỉ sinh ra patterns đơn giản, quen thuộc
→ WAF dễ detect vì patterns quá phổ biến
→ Gold set nhỏ (662 rows) một phần vì duplicate payload có contradictory labels
   → confidence thấp → bị drop khỏi gold
```

### Nguyên nhân gốc

Không có pipeline step nào enforce dedup trước labeling. Nhiều Kaggle sources đều crawl từ cùng nguồn SQLi payload lists → trùng lặp ngầm.

### Paper support

**Lee_2022** — *Deduplicating Training Data Makes Language Models Better*:
"Near-duplicate training examples gây memorization và giảm generalization 30%+.
Cần cả exact-match dedup (SHA-256) lẫn near-dedup (MinHash/SimHash)."

---

## SAI LẦM #2 — Strip Wrapper Chạy SAU Delex (Thứ Tự Ngược)

### Đây là sai lầm quan trọng nhất

**Ví dụ trực quan — payload wrapper trong dataset:**

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
```

Payload THẬT (attack) nằm BÊN TRONG dấu nháy: `admin' OR '1'='1' --`

**Khi delex chạy TRƯỚC (sai lầm của V4):**

```
Input: SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
                                                     ↑
                                             Attack ở đây!

delex → thay TẤT CẢ string literals bằng __STR__:
Output: SELECT __ID__ FROM __TABLE__ WHERE __ID__ = __STR__
                                                     ↑
                                     OR '1'='1' đã bị nuốt vào __STR__!
```

Bây giờ một payload `union_based` dạng wrapper:
```sql
SELECT * FROM users WHERE username = 'admin' UNION SELECT 1,2,3 --'
```
Sau delex → cũng trở thành: `SELECT __ID__ FROM __TABLE__ WHERE __ID__ = __STR__`

**Kết quả:** boolean_blind wrapper và union_based wrapper → **CÙNG 1 delex string** → COLLISION!

**Khi strip_wrapper chạy TRƯỚC (đúng):**

```
Input: SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
Step 1 - strip_wrapper: extract inner → admin' OR '1'='1' --
Step 2 - delex: __STR__ OR __STR__ = __STR__ --
```

Pattern `OR` và `--` được giữ lại → collision giảm từ **71.89% → 4.33%** (đã proven trên 1000-row prototype).

### Hậu quả chuỗi

```
Thứ tự ngược: delex → strip_wrapper
→ ~16% rows có wrapper bị nuốt attack pattern
→ Collision rate: 71.89% (V1) → 40.18% (V4, vẫn FAIL)
→ Generator nhìn thấy delex string giống nhau cho các attack type khác nhau
→ Không học được type-specific patterns
→ Conditional generation sai: generate union_based nhưng output là boolean_blind
```

### Paper support

Không có paper về pipeline ordering cho SQLi — đây là **empirical finding** của chính dự án.
Prototype 1000 rows: thứ tự đúng → collision 71.89% → 4.33%.

---

## SAI LẦM #3 — Hai Labeler Cùng Design: Rule + Heuristic Đều Dùng Keyword Matching

### Vấn đề cốt lõi

Bạn có 2 hệ thống labeling, nhưng thực ra chúng **KHÔNG độc lập**.

**Phép so sánh:**
```
Hỏi 2 người học cùng lớp, cùng đọc cùng giáo trình → không phải 2 ý kiến độc lập
Hỏi 1 người học giáo trình + 1 người thực chiến → 2 ý kiến thực sự độc lập
```

```
Rule-based A:  if 'SLEEP(' in payload → time_blind
Heuristic C:   if re.search(r'\bsleep\s*\(', payload) → time_blind
```

Khi đồng ý → không phải "2 bằng chứng độc lập" mà là **"1 bằng chứng được đếm 2 lần"**.

**Hậu quả:**
```
SLEEP(5):         A=time_blind, C=time_blind → agree → confidence 0.95 → GOLD
extractvalue(…):  A=error_based, C=None → confidence 0.75 → SILVER
UNION /*comment*/SELECT: A=None, C=None → confidence 0.0 → DROP!
```

Obfuscated payloads (comment insertion, whitespace variation, case variation) → **KHÔNG có trong gold set**.
Model học patterns "vanilla", không học được bypass technique.

### Hậu quả chuỗi

```
Gold set = chỉ payload đơn giản (SLEEP, basic UNION, basic OR)
→ Generator học patterns dễ detect
→ WAF bypass rate thấp (WAF cũng chặn patterns vanilla)
→ OWASP bypass rate chỉ 2% ở best checkpoint
→ InfoGAN Q-loss (cải thiện accuracy) chỉ là bandage, không fix root cause
```

### Paper support

**Ratner_2017** (Snorkel) — "Labeling functions phải đa dạng về methodology; correlated LFs
không cải thiện label quality, chỉ tạo ra false confidence."

**Gilardi_2023** — "LLM labeling (ChatGPT/Claude) cho kết quả tốt hơn heuristics 25pp trên
nhiều task classification."

---

## SAI LẦM #4 — Gold Threshold 0.90 Với Chỉ 2 Nguồn: Toán Học Không Khả Thi

### Giải thích bằng số học

```
Với 2 nguồn (A và C):
  sources_agree ≥ 2 → 100% agreement (A=C)
  Nhưng 55% rows có A ≠ C → chỉ 45% rows ELIGIBLE cho gold
  Thêm confidence ≥ 0.90 → lọc thêm → còn 662/40,545 = 1.6%
```

**Minimum cần thiết:**
```
4 attack types × 5 db_engines = 20 cells
Minimum 50 rows/cell = 1,000 gold rows cần thiết
Thực tế: 662 rows → cell union_based×oracle có thể chỉ 5-10 rows
→ Model không học được rare type combinations
```

### Hậu quả chuỗi

```
662 gold rows → MLE val_ppl 1.74 (trông tốt!)
→ Thực ra model overfit vào 662 patterns
→ Val perplexity không reflect generalization (662 quá nhỏ)
→ Adversarial phase collapse nhanh (model quá "comfortable" với 662 patterns)
→ V4 crash tại step 750
```

---

## SAI LẦM #5 — Type Distribution Phản Ánh Labeler Bias, Không Phải Thực Tế Tấn Công

### Phân tích distribution trong gold set V4

| Type | Gold V4 | Lý do bị bias |
|------|---------|--------------|
| time_blind | 44.7% | SLEEP() rất dễ detect → A và C đều đồng ý → vào gold nhiều |
| benign | 32.2% | Không có attack pattern → không gây nhầm lẫn |
| boolean_blind | 17.2% | Một số patterns đơn giản lọt qua |
| union_based | 5.9% (39 rows!) | Nhiều variants → A và C không đồng ý → bị drop |
| error_based | ~0% | Tương tự union_based |

**Union_based và error_based trong thực tế** chiếm tỉ lệ lớn ở các cuộc tấn công thực, nhưng gần như VẮNG MẶT trong gold set.

### Hậu quả

```
Model train chủ yếu trên time_blind (44.7%)
→ Conditional generation: request union_based → model sinh time_blind
→ type_accuracy ~45% (sai 55% thời gian)
→ Ngay cả InfoGAN Q-loss, nếu union_based training data quá ít → accuracy không cải thiện nhiều
```

### Paper support

**Agrawal_2024** — "Class imbalance trong attack datasets thường phản ánh detection bias
(hệ thống dễ detect gì thì có nhiều hơn), không phải actual attack distribution."

**Udu_2025** — "Oversampling (SMOTE, GAN augmentation) không substitute cho diverse source data."

---

## SAI LẦM #6 — Không Label DB Engine: Oracle và MySQL Indistinguishable

### Ví dụ

```sql
-- Payload A: error_based, DB = MySQL
SELECT * FROM users WHERE id=1 AND extractvalue(1,concat(0x7e,version()))

-- Payload B: error_based, DB = Oracle
SELECT * FROM users WHERE id=1 AND xmltype((select version from v$instance))
```

Sau delex_v1 (xóa TẤT CẢ function names):
```
Payload A → SELECT __ID__ FROM __TABLE__ WHERE __ID__ = __NUM__ AND __FUNC__(...)
Payload B → SELECT __ID__ FROM __TABLE__ WHERE __ID__ = __NUM__ AND __FUNC__(...)
```

Hai payload hoàn toàn khác nhau về syntax → **CÙNG 1 delex string** → COLLISION!

### Hậu quả

```
Generator nhận condition [attack_type=error_based] nhưng không biết db_engine
→ Generate payload mix Oracle + MySQL syntax
→ Payload invalid (MySQL không hiểu xmltype, Oracle không hiểu extractvalue)
→ DB execution rate 99.8% là FALSE
  (SQLite không strict với SQL syntax → accept cả Oracle/MySQL-specific queries)
→ Composite score 0.471 bị overstated
→ Real-world MySQL/PostgreSQL execution rate thực sự rất thấp
```

### Paper support

**Lu_2022** — Taxonomy SQLi có dimension db_engine. Cần phân loại theo cả attack type lẫn DB engine.

---

## SAI LẦM #7 — Không Validate SQL Executability: Garbage Vào Training

### Ví dụ garbage trong dataset

```
%27+OR+%271%27%3D%271          ← URL-encoded, chưa decode
' OR '1'='1                    ← truncated (thiếu --)
SELECT * FROM                  ← incomplete SQL fragment
<script>alert(1)</script>      ← XSS, không phải SQLi
```

Những strings này được label là "sqli" (binary label từ nguồn gốc) → vào pipeline → vào training.
Model học syntax không hợp lệ → generated payloads cũng có syntax sai.

### Hậu quả

```
Invalid SQL trong training → generator học invalid patterns
→ Generated payloads không execute được trên real DB
→ DB execution rate 99.8% là FALSE (SQLite accept garbage queries)
→ Composite score 0.471 không reflect real performance
```

### Paper support

**Lu_2022** — "SQLParse syntax validation là bước tiền lọc quan trọng."

**Dasari_2025** — "Không thể trust single metric; dùng multiple quality metrics
(BLEU, cosine similarity, execution rate trên real DB) để validate synthetic data quality."

---

## SAI LẦM #8 — Không Dedup Trước Train/Val Split

### Vấn đề

Near-duplicate payloads (chỉ khác capitalization hoặc whitespace) có thể nằm ở cả train VÀ val:

```
Train: select * from users where id=1 OR 1=1
Val:   SELECT * FROM users WHERE id=1 OR 1=1   ← chỉ khác case
```

### Hậu quả

```
Near-duplicates trong cả train và val
→ Val perplexity 1.74 bị inflate (model thực sự đang memorize, không generalize)
→ Adversarial phase collapse nhanh hơn vì model không generalize tốt
→ Không detect được vì val metric trông tốt
```

### Paper support

**Lee_2022** — "Near-dedup với MinHash/SimHash cần thiết; train-val contamination
là silent killer của model quality."

---

## SAI LẦM #9 — 8 Anti-Collapse Fixes Được Apply Đồng Thời Trong V4

### Những gì V4 thay đổi cùng lúc

```
① entropy_coeff:         0.02 → 0.05
② temperature:           1.0  → 1.2
③ EMA alpha:             0.999 → 0.9999
④ type-balanced batch:   OFF → ON
⑤ diversity bonus:       OFF → ON
⑥ dynamic D steps:       OFF → ON
⑦ benign SQL injection:  OFF → ON
⑧ BiLSTM encoder:        LSTM → BiLSTM
```

V4 crash tại step 750.

### Hậu quả

```
8 thay đổi đồng thời → không biết change nào gây crash
→ Không thể debug hiệu quả (isolate effect)
→ V4 abandoned hoàn toàn, mất toàn bộ checkpoint
→ Phải thiết kế lại từ đầu (V5 Gumbel-Softmax)
→ Mất thời gian training và compute
```

### Nguyên tắc đúng (Paper support)

**Yu_2017** (SeqGAN, Ablation section) — "Thay đổi 1 variable tại 1 thời điểm để isolate effect.
Ablation study = baseline của experimental rigor."

---

## SAI LẦM #10 — Reward Ceiling Cố Định: REINFORCE Không Thể Học Thêm

### Giải thích cơ chế

```
Reward ceiling = 0.70
Generator sinh payload đạt reward 0.70 sau vài trăm steps

Từ đó:
  advantage = reward - baseline = 0.70 - 0.70 = ~0
  REINFORCE gradient = advantage × log_prob_gradient ≈ 0
  → Generator không update nữa (gradient = 0)
  → Mode collapse: mọi sample đều giống nhau
```

Đây như **đặt bar kiểm tra ở 7/10 điểm**. Sau khi học đủ để qua bar, không có lý do để học thêm.

### Timeline mode collapse

```
V1: entropy reg tắt → collapse ở step ~800
V3: entropy reg bật → collapse ở step ~2500 (+1700 steps)
V4: 8 fixes đồng thời → crash step 750 (không phải collapse, là bug)
```

Entropy regularization chỉ **trì hoãn** collapse, không **ngăn** được. Ceiling vẫn còn → collapse inevitable.

### Giải pháp duy nhất

**Gumbel-Softmax (V5)**: Gradient tồn tại LUÔN LUÔN, không phụ thuộc advantage.
Không cần reward signal để có gradient → không bị ceiling problem.

### Paper support

**Jang_2017** (Gumbel-Softmax) — "Straight-Through Estimator gradient không cần advantage estimate,
luôn tồn tại bất kể reward distribution."

**Williams_1992** (REINFORCE) — "Fundamental limitation: gradient = 0 khi variance reward thấp
hoặc advantage → 0."

---

## TỔNG HỢP ROOT CAUSES

| Sai lầm | Root Cause | Hậu quả chính |
|---------|------------|---------------|
| #1 Không dedup | Không có step enforce dedup | Val_ppl inflated, gold set nhỏ |
| #2 Thứ tự pipeline ngược | strip_wrapper sau delex | Collision 40.18% (target <10%) |
| #3 2 labeler correlated | Cả 2 dùng keyword matching | Obfuscated payload không có trong gold |
| #4 Threshold không khả thi | 0.90 với 2 nguồn = 1.6% gold rate | 662 rows thay vì 4,000+ |
| #5 Labeler bias | SLEEP() dễ detect nhất | time_blind 44.7%, union_based 5.9% |
| #6 Không label db_engine | Taxonomy thiếu dimension | Oracle + MySQL indistinguishable |
| #7 Không validate SQL | URL-encoded garbage lọt vào | DB execution rate 99.8% là FALSE |
| #8 Không dedup trước split | Near-duplicate train/val | Val_ppl 1.74 inflated |
| #9 8 fixes đồng thời | Không ablation test | V4 crash, không debug được |
| #10 Reward ceiling | REINFORCE fundamental limitation | Mode collapse inevitable |

---

## ĐỊNH HƯỚNG XỬ LÝ MỚI (V5 PIPELINE)

### Kiến trúc skill-based multi-dimensional

Thay vì 2 labeler keyword-based correlated, dùng **nhiều detector functions độc lập**:

```python
score_time_blind(payload)    → 0.0 - 1.0
score_boolean_blind(payload) → 0.0 - 1.0
score_union_based(payload)   → 0.0 - 1.0
score_error_based(payload)   → 0.0 - 1.0
detect_mysql(payload)        → 0.0 - 1.0
detect_postgres(payload)     → 0.0 - 1.0
detect_oracle(payload)       → 0.0 - 1.0
detect_comment_injection(payload) → 0.0 - 1.0  # obfuscation
```

### Dual system với AI fallback

```
OWASP scorer → score vector [0.9, 0.1, 0.0, 0.0]
Heuristic scorer → score vector [0.85, 0.2, 0.0, 0.0]

Nếu argmax giống nhau VÀ |diff| ≤ 0.30 → trusted, high confidence
Nếu argmax khác nhau HOẶC |diff| > 0.30 → gửi Claude Haiku review
```

### Pipeline thứ tự bắt buộc

```
RAW → HOLDOUT LOCK → DEDUP → DECODE → STRIP_WRAPPER → SKILL SCORING
    → DUAL SYSTEM COMPARE → AI REVIEW (if needed)
    → LABEL RESOLVE → DELEX_V2 → QUALITY GATES → TIER SPLIT → BALANCE
```

### Target metrics mới

| Metric | V4 (FAIL) | V5 Target |
|--------|-----------|-----------|
| Collision rate | 40.18% | < 10% |
| Type entropy | 1.76 bits | > 2.0 bits |
| Gold rows | 662 | > 4,000 |
| Function preservation | ~70% | > 95% |
| Obfuscated payload coverage | ~0% | > 15% of gold |
| DB engine cells | 4 | 20 (4 types × 5 engines) |

---

*File này là tổng hợp từ phân tích sâu pipeline V1–V4 và kế hoạch V5 ngày 2026-05-18.*
*Tham khảo: Lee_2022, Ratner_2017, Gilardi_2023, Lu_2022, Agrawal_2024, Jang_2017, Yu_2017*
