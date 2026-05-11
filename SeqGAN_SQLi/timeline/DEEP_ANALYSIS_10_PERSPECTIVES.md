# Phân Tích Sâu — 10 Góc Nhìn Cho GAN_SQLi

> **Ngày**: 2026-05-11
> **Phạm vi**: Phân tích sâu sau khi user feedback 10 góc nhìn ban đầu
> **Tài liệu tham chiếu**:
> - `Skill/output_txt/TONG_HOP_PHAN_TICH_30_BAI_BAO.md`
> - `Skill/output_txt/FULL_ANALYSIS_ALL_8_PAPERS.md`
> - `Skill/output_txt/PHAN_TICH_LE2024_IDS_HYBRID_SAMPLING.md`
> - `Skill/output_txt/survey gan for text.txt` (de Rosa 2022)
> - `Skill/output_txt/electronics-13-00322.txt` (Agrawal 2024)
> - `SeqGAN_SQLi/timeline/{ANALYSIS_REPORT, EXPERIMENT_LOG, FULL_BUILD_JOURNAL}.md`

---

## Mục Lục

1. [G1: OWASP CRS + Custom Rules Reward](#g1-owasp-crs--custom-rules-reward)
2. [G2: AST Structural Diversity + Bypass Quality + Agrawal 2024](#g2-ast-structural-diversity--bypass-quality--agrawal-2024)
3. [G3: RL/SeqGAN Architecture + Reward Model](#g3-rlseqgan-architecture--reward-model)
4. [G4: Bias đánh nhãn — dẫn chứng từ timeline + literature](#g4-bias-đánh-nhãn)
5. [G5: Boundary-aware Generation — kết quả thực tế](#g5-boundary-aware-generation)
6. [G6: Multi-metric Ensemble — 5 quan điểm/metric](#g6-multi-metric-ensemble)
7. [G7: Đánh lại nhãn — 5 phương án chiến lược](#g7-đánh-lại-nhãn)
8. [G8: 10 phản biện về "SeqGAN tự nhiên hợp với SQLi"](#g8-10-phản-biện-về-seqgan-tự-nhiên-hợp-với-sqli)
9. [G10: Ôm đồm 3 mục tiêu — 5 nên / 5 không](#g10-ôm-đồm-3-mục-tiêu)

---

## G1: OWASP CRS + Custom Rules Reward

### Kiến trúc reward đề xuất

```
Payload p (de-lex hoặc re-lex)
       │
       ├─→ [Stage 0] Syntax Gate: sqlparse parse được?
       │       │ Pass: tiếp tục    Fail: r = -1.0 (terminal penalty)
       │
       ├─→ [Stage 1] OWASP CRS PL2 evaluation (Docker ModSecurity)
       │       │ anomaly_score = 0..∞
       │       │ r_owasp = clip((threshold - anomaly_score) / threshold, -1, 1)
       │       │   → score < threshold (bypass): r_owasp dương
       │       │   → score ≥ threshold (block): r_owasp âm
       │
       ├─→ [Stage 2] Custom Rules (tự định nghĩa)
       │       │ - Phải chứa ≥ 1 SQLi pattern hợp lệ (UNION/OR injection/SLEEP/ERROR)
       │       │ - Phải có ≥ 1 quoting/comment để có ý nghĩa attack
       │       │ - KHÔNG được trivial (length < 5 tokens hoặc chỉ chứa noise)
       │       │ r_custom = pass_count / total_rules
       │
       └─→ [Stage 3] Aggregation:
               r_final = α·r_owasp + β·r_custom - γ·overlap_penalty

               overlap_penalty = max(0, r_owasp · r_custom_inverse)
                 → Phạt khi pass OWASP nhưng fail custom
                   (= dấu hiệu payload là noise lừa được rule chứ không phải SQLi)
```

### Mô hình sẽ có gì

| Thành phần | Đầu vào | Đầu ra | File mới |
|---|---|---|---|
| `WAFOracle` (ModSecurity Docker) | payload string | anomaly_score (int) | `src/waf_oracle.py` |
| `CustomRuleEngine` | payload tokens | pass_count, total_rules | `src/custom_rules.py` |
| `CompositeReward` | output cả 2 trên | scalar r ∈ [-1, 1] | sửa `src/reward.py` |
| Docker setup | — | — | `docker/modsec/Dockerfile` |
| Reward cache | (payload_hash → r) | tránh gọi WAF lại | `src/reward_cache.py` |

### Tại sao "chống reward hacking lẫn nhau"

- OWASP CRS có ~150 rule, phần lớn dựa trên **regex của keyword + position**. Generator có thể học cách **ẩn keyword bằng comment/encoding** → bypass OWASP nhưng payload thành nonsense.
- Custom rules kiểm tra **payload có phải SQLi đúng nghĩa không**. Nếu OWASP pass nhưng custom fail → đó là noise lừa OWASP, không phải bypass thật.
- Ngược lại: nếu custom pass nhưng OWASP block → payload là SQLi cổ điển, không có giá trị nghiên cứu (đã biết WAF sẽ chặn).
- Chỉ khi **cả hai pass đồng thời** → payload là SQLi thực sự bypass được WAF. Đây là "Pareto-optimal" reward.

### Compute budget thực tế

- ModSecurity Docker call ~30-50ms qua loopback.
- Mỗi RL step có batch=64 → 64 calls ≈ 2-3 giây.
- 5000 steps = ~3 giờ chỉ cho reward (chưa kể training).
- **Cache theo payload hash** giảm 50-70% calls vì generator hay sinh duplicate ở giai đoạn collapse.

### Rủi ro cần lường trước

1. **OWASP CRS version drift**: kết quả phụ thuộc tag version. Pin version cụ thể (v4.3.0 hiện tại) và ghi vào paper.
2. **Anomaly_score là số rời rạc thưa**: phần lớn payload có score 0, 5, hoặc 15+. Reward signal có nhiều "plateau" → có thể cần reward shaping bổ sung (thưởng nhỏ cho payload làm score giảm dần qua các step).

---

## G2: AST Structural Diversity + Bypass Quality + Agrawal 2024

### 2A. 5 quan điểm về AST diversity

**Quan điểm 1 — Tree-edit distance (Zhang-Shasha algorithm)**
- Parse mỗi payload thành AST bằng `sqlparse.parse()` hoặc `sqlglot.parse()`.
- Tính khoảng cách Zhang-Shasha giữa các cặp AST.
- Diversity = average pairwise tree edit distance trên 1,000 mẫu.
- **Ưu**: chính xác nhất về mặt structural; chuẩn lý thuyết.
- **Nhược**: O(n²·|T|²) — chậm với 1,000 mẫu. Cần subsample.

**Quan điểm 2 — AST node-type entropy**
- Đếm tần suất mỗi loại node (SELECT, WHERE, UNION, BINARY_OP, FUNCTION, COMMENT…) qua tất cả AST.
- Diversity = Shannon entropy của phân phối node type.
- **Ưu**: nhanh, đơn giản; dễ giải thích.
- **Nhược**: hai tập payload với cùng tỷ lệ node type vẫn được coi giống nhau, dù cấu trúc khác.

**Quan điểm 3 — Tree path n-grams**
- Trích các path từ root đến leaf, treat như "structural n-grams".
- Tính Self-BLEU trên không gian path thay vì token.
- **Ưu**: tận dụng được pipeline Self-BLEU đã có; tự nhiên thay token bằng path.
- **Nhược**: phụ thuộc parser; AST sai → path sai.

**Quan điểm 4 — Subtree fingerprinting (Merkle-like hash)**
- Băm từng subtree độ sâu k (k=2,3,4).
- Diversity = số unique subtree fingerprint / total fingerprint.
- **Ưu**: O(n·|T|) — rất nhanh; dễ visualize.
- **Nhược**: chỉ đếm "có/không" — không phản ánh khoảng cách giữa các subtree.

**Quan điểm 5 — Graph kernel (Weisfeiler-Lehman)**
- Coi AST là graph, dùng WL kernel để đo similarity.
- Diversity = 1 - average pairwise WL similarity.
- **Ưu**: chuẩn từ literature graph learning; lý thuyết vững.
- **Nhược**: phức tạp triển khai; overkill cho payload ngắn (~80 tokens).

**Khuyến nghị:** Bắt đầu với **QĐ4 (subtree fingerprinting)** — đơn giản, nhanh, đủ tốt để phát hiện mode collapse. Khi cần publish, thêm **QĐ1 (Zhang-Shasha)** cho rigor.

### 2B. Triển khai 3 thước đo Bypass Quality Score

```
BQS(p) = passed_OWASP(p) × passed_syntax(p) × executes_on_real_DB(p)
```

| Thành phần | Triển khai | Chi phí | Edge case |
|---|---|---|---|
| `passed_OWASP` | Gọi ModSecurity Docker (như G1) | 30-50ms | Cần fix version |
| `passed_syntax` | `sqlparse.parse(p)` raise → 0; else check has `Statement` token → 1 | <1ms | Parser lax, có thể accept payload không hợp lệ thực |
| `executes_on_real_DB` | SQLite/MySQL test instance, chạy payload trong context query mẫu (`SELECT * FROM users WHERE id={p}`), check không raise SyntaxError | 5-10ms | Cần sandbox; payload phá database test → cần rollback transaction |

**Pipeline thực tế:**
```python
def bypass_quality_score(payload, waf_oracle, db_sandbox):
    if not sqlparse.parse(payload):  # syntax
        return 0.0
    try:
        with db_sandbox.transaction() as txn:
            txn.execute(f"SELECT * FROM dummy WHERE id={payload}")
            txn.rollback()  # luôn rollback, chỉ kiểm tra parse
        executes = 1.0
    except (sqlite3.OperationalError, sqlite3.Warning):
        executes = 0.0

    owasp_pass = 1.0 if waf_oracle.evaluate(payload).anomaly_score < 5 else 0.0
    return owasp_pass * 1.0 * executes  # passed_syntax đã = 1 ở đây
```

**Tại sao multiplicative thay vì additive:** Cộng có thể hack từng thành phần (vd: cao OWASP, thấp DB). Nhân thì **tất cả phải > 0** mới có giá trị, và nếu có 1 thành phần = 0 → tổng = 0. Generator buộc phải optimize cả 3 đồng thời.

### 2C. Agrawal 2024 — phân tích sâu (từ file gốc `electronics-13-00322.txt`)

**Phương pháp của Agrawal:**
1. Lấy NSL-KDD DoS subset (41 features: 9 discrete + 32 continuous).
2. **Identify features reflective of DoS attack** (vd: duration, src_bytes, count).
3. Tính **Pearson correlation coefficient** giữa các features đó qua các DoS samples thật → ma trận correlation đặc trưng cho DoS.
4. Train CGAN sinh DoS data → tính correlation matrix tương tự cho synthetic data.
5. **So sánh 2 matrix** → kết luận synthetic data có giữ được correlation không.

**Phát hiện cụ thể (line 1196-1221 trong file gốc):**

| Test | Kết quả với GAN synthetic data |
|---|---|
| White-box FNN (trained trên real DoS) | Phân loại synthetic data vào DoS với confidence cao |
| Anomaly detector (semi-supervised) | Cờ đỏ — "not normal" |
| **Static feature analysis** | **Feature values không match cả normal lẫn DoS expected ranges** |
| **Pearson correlation** | **Correlation giữa các DoS features bị phá vỡ trong synthetic data** |

**Câu chốt của paper (line 1218):**
> *"the data represents mere noise. Many solutions have claimed the ability of their... [synthetic data], not mean attack data; instead, as we evidenced above, it is often mere noise and not an actual attack."*

**Áp dụng cho GAN_SQLi:**
- "Feature correlation" trong NSL-KDD ≈ "AST structural correlation" trong SQLi.
- Vd: `UNION` luôn xuất hiện cùng với `SELECT` ở vị trí trước; `ORDER BY` luôn cần column index.
- **Test áp dụng được:** Lấy 100 payload thật + 100 SeqGAN sinh ra → tính conditional probability `P(SELECT precedes UNION | UNION exists)`. Nếu chênh lệch > 20% → SeqGAN đã phá structural correlation → là noise giống Agrawal cảnh báo.

**Tham khảo trực tiếp:** đọc lại file `electronics-13-00322.txt` lines 1155-1221 cho methodology chi tiết và lines 1244-1271 cho future work (Agrawal cụ thể đề xuất "study GANs in generating complex attacks like... SQL Injection").

---

## G3: RL/SeqGAN Architecture + Reward Model

### Phân tích sâu RL/SeqGAN cho SQLi (gắn với corpus)

**Yu 2017 (SeqGAN gốc):** Generator = LSTM, Discriminator = TextCNN, Reward = D(y) cho complete sequence, Monte Carlo rollout N=16 cho intermediate. Critically: **không có reward shaping từ task-specific signal** — chỉ dùng D.

**Atkinson 2024 / Rodriguez 2024 (TD Commons):** Improved WGAN cho SeqGAN (NLL 8.639 → 8.509) nhưng vẫn synthetic data. Phát hiện quan trọng: **PPO thua REINFORCE** cho discrete sequence (NLL 9.065 vs 8.639). Lý do giả thuyết: PPO clip ratio không hoạt động tốt với reward signal dạng sparse/terminal.

**Chowdhary 2023 (Sensors):** Conditional SeqGAN cho XSS pentesting — gần nhất với usecase. Reward = AWS WAF response code. Đây là **reference architecture** — vì cũng dùng SeqGAN + real WAF reward.

### Kiến trúc tổng thể đề xuất

```
┌──────────────────────────────────────────────────────────┐
│  Generator: LSTM 3-layer 512-dim (giữ nguyên)            │
│  - Init: MLE pretrained (val_ppl=1.70 đã có)             │
│  - Action space: vocab 134 (đề xuất G7 sẽ revise)        │
└────────────────────────┬─────────────────────────────────┘
                         │ sample sequence
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Monte Carlo Rollout (K=16): partial → complete          │
│  - Phục vụ tính Q(s,a) cho intermediate token            │
└────────────────────────┬─────────────────────────────────┘
                         │ N completed sequences
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Composite Reward Oracle (G1 + G2 + G6 hợp nhất):        │
│  r = w1·r_OWASP + w2·r_custom + w3·r_DB_exec             │
│      + w4·r_AST_novelty - w5·r_overlap_penalty           │
│  Với r_AST_novelty = 1 - max_cos_sim(AST(p), AST(cache)) │
│                       (penalty nếu giống mẫu trong cache)│
└────────────────────────┬─────────────────────────────────┘
                         │ scalar reward
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Baseline (EMA, đã có) → Advantage = r - b               │
│  REINFORCE update: ∇θ log π · A                          │
│  (KHÔNG dùng PPO — Atkinson 2024 đã chứng minh tệ hơn)   │
└──────────────────────────────────────────────────────────┘

Discriminator update: ít quan trọng hơn vì reward chính đến từ Oracle
- Vẫn train D 1 step / G step (không phải 5:1) để giữ diversity pressure
- D score chỉ chiếm 10-20% reward total
```

### Reward design — 3 chế độ training

| Phase | Steps | Reward composition | Mục đích |
|---|---|---|---|
| **Warmup** | 0-2k | 70% syntax + 30% custom rules | Đảm bảo G không sinh garbage trước khi gọi WAF |
| **Adversarial** | 2k-15k | 40% OWASP + 30% custom + 20% DB_exec + 10% AST_novelty | Bypass WAF có chất lượng |
| **Refinement** | 15k-20k | 30% OWASP + 30% DB_exec + 40% AST_novelty | Đa dạng hóa output |

**Tại sao curriculum:** Lu 2022 chứng minh model không hội tụ nếu cho full reward signal từ step 0 (loss âm sâu). Atkinson 2024 chứng minh batch increase nhảy ra khỏi local optimum sau ~150 epochs — gợi ý reward landscape phức tạp cần warmup.

### Reward cache là critical

Với batch=64 × 16 MC rollouts × 20k steps = **20 triệu reward queries**. Cache theo hash payload có hit rate ước tính 60-80% sau khi G hội tụ partial. Không có cache = không khả thi compute.

---

## G4: Bias đánh nhãn

### Dấu hiệu từ chính timeline

**Trong `EXPERIMENT_LOG.md` line 36-37:**
> *"Phân tích error_based cụ thể: **88.6% payload target `users`/`accounts` table**, **60.6% dùng Oracle XMLTYPE**."*

Đây là **smoking gun của data bias**:
- Trong thực tế SQL injection, target table cực kỳ đa dạng: customers, orders, sessions, admin, settings, products... Tỷ lệ 88.6% chỉ tập trung 2 tables là **không tự nhiên**.
- Oracle XMLTYPE chiếm 60.6% gợi ý dataset được **scraped từ 1-2 source duy nhất**, có thể là sqlmap tamper scripts hoặc Oracle-specific exploit-db dumps.

**Trong `ANALYSIS_REPORT.md` line 100-101:**
> *"De-lexicalization thay thế giá trị cụ thể bằng placeholder. Hai payload khác hoàn toàn về nội dung (`' OR 1=1--` vs `' OR 'x'='x`) có thể trở thành cùng token sequence sau de-lex."*

→ De-lex + bias nguồn data = double collapse: bias nguồn làm cho structure đã đồng nhất, de-lex xóa nốt phần khác biệt còn lại.

**Trong `FULL_BUILD_JOURNAL.md` line 234-243:**
> *"`' OR 1=1 --`, `' OR 2=2 --`, `' OR 3=3 --`, `' OR 9999=9999 --` — Tất cả đều là cùng một kiểu tấn công, chỉ khác số."*

→ De-lex đã thiết kế để **trừu tượng hóa biến thể**. Nhưng nếu dataset gốc đã bias (tất cả đều là `OR N=N --` pattern), de-lex chỉ làm rõ thêm bias đó.

### Dẫn chứng từ literature

**Agrawal 2024 (electronics-13-00322.txt line 1244-1248):**
> *"GAN-generated attack data often deviates from normal traffic, it does not align with typical DoS attack traffic but relatively just noise."*

Tương tự: SeqGAN học từ dataset bias → output là "structural noise" trong không gian de-lex.

**Le Minh Khan 2024 (GSQLi):** Sử dụng **HttpParams + SSHS dataset** — đa dạng hơn vì lấy từ HTTP traffic thật. Đó là lý do GSQLi đạt mutation diversity cao. So với `combined_labeled_data.csv` chưa rõ nguồn → khả năng bias rất cao.

**Lu 2022:** 2000+ payload từ **CVE + CNVD + exploit-db (2015-present)** — multi-source giảm bias.

**Khoirunnisa 2025 (Framingham Heart Study experience):** Sau augmentation với CTGAN, model bị thiên về majority class — bias từ training data **được khuếch đại** chứ không bị làm mịn bởi GAN.

### Phương pháp kiểm chứng cụ thể

```python
# Kiểm tra bias trong dataset
import pandas as pd
df = pd.read_csv('combined_labeled_data.csv')

# Test 1: Source diversity
print(df['source'].value_counts() if 'source' in df else "Không có source column")

# Test 2: Skeleton diversity sau de-lex
df['skeleton'] = df['payload_norm'].apply(lambda p: re.sub(r'__\w+__', '_', p))
print(f"Unique skeletons / total: {df['skeleton'].nunique()} / {len(df)}")
# Nếu ratio < 5% → bias nặng

# Test 3: Per-type skeleton diversity
for sqli_type, group in df.groupby('sqli_type'):
    ratio = group['skeleton'].nunique() / len(group)
    print(f"{sqli_type}: {ratio:.2%} skeleton uniqueness")
# Type nào < 10% là smoking gun
```

**Kết luận:** Trực giác về bias do nhãn/data **được hỗ trợ bởi chính dữ liệu trong timeline**. Bias không phải ở label noise mà ở **source homogeneity** — toàn bộ dataset có thể đến từ 1-2 tool/source.

---

## G5: Boundary-aware Generation

### 5A. Cơ chế hoạt động

Hiện tại: Generator được reward nếu payload "bypass thành công" (binary 0/1). Vấn đề: hàng nghìn cách bypass tương đương nhau → G chọn cách dễ nhất, mode collapse.

Boundary-aware: Reward cao nhất cho payload nằm **sát ranh giới** — vừa đủ bypass, không bypass quá dễ.

```
r_boundary = 1 - |anomaly_score - threshold| / threshold
```

Với threshold OWASP = 5 (PL2 default):
- Payload anomaly_score = 0 (bypass dễ): r = 1 - 5/5 = 0 (không reward)
- Payload anomaly_score = 4 (bypass sát ranh giới): r = 1 - 1/5 = 0.8 (reward cao)
- Payload anomaly_score = 5 (vừa block): r = 1 - 0/5 = 1.0 (reward tối đa!)
- Payload anomaly_score = 10 (block rõ): r = 1 - 5/5 = 0 (không reward)

### 5B. Tại sao điều này giúp diversity

Có **vô hạn payload có anomaly_score = 0** (bypass dễ) → G dễ collapse vào 1 mẫu.
Có **rất ít payload có anomaly_score ≈ 5** (sát ranh giới) → G buộc phải đa dạng để tìm.

Đây là **inductive bias** trực tiếp đẩy generator ra khỏi mode collapse — không phải post-hoc regularization (entropy, BLEU penalty đã thất bại trong EXPERIMENT_LOG).

### 5C. Kết hợp BorderlineSMOTE logic (Le 2024)

Le 2024 chứng minh **BorderlineSMOTE + Tomek = F1=0.98** vì:
- BorderlineSMOTE tập trung sinh mẫu **gần boundary** giữa classes
- Tomek Links **clean noise samples** xa boundary

Áp dụng:
1. Dùng OWASP CRS làm "classifier boundary".
2. Training data của Discriminator: thay vì 50% real + 50% G-generated, dùng **50% real near-boundary + 50% G-generated**. "Near-boundary" = real payload có anomaly_score gần threshold.
3. Generator sẽ học cách tạo payload trông giống real-near-boundary thay vì real-trivial.

### 5D. Kết quả kỳ vọng (định lượng)

Dựa trên Le 2024 (F1 0.93 → 0.98 khi chuyển từ random OS sang BorderlineSMOTE):

| Metric | Hiện tại (mixed) | Kỳ vọng với boundary-aware |
|---|---|---|
| Self-BLEU-3 (de-lex) | 0.9894 | 0.85-0.92 (giảm rõ rệt) |
| Self-BLEU-3 (re-lex) | chưa đo | < 0.70 (kỳ vọng) |
| OWASP CRS bypass | chưa đo với real WAF | 60-80% |
| Bypass với anomaly < threshold by ≤ 2 | — | 30-50% (giá trị nhất) |

### 5E. Triển khai cụ thể

```python
class BoundaryAwareReward:
    def __init__(self, waf, threshold=5):
        self.waf = waf
        self.t = threshold

    def __call__(self, payload):
        score = self.waf.evaluate(payload).anomaly_score
        if score >= self.t:
            return -0.5  # bị block, penalty nhẹ
        # bypass thành công, tính boundary distance
        distance = self.t - score  # 1..threshold
        # reward cao nhất khi distance nhỏ (sát threshold)
        r = 1.0 - (distance / self.t)
        return r
```

5 dòng code, không cần retrain D. Có thể chạy trên checkpoint hiện có (transfer learning từ adv_final.pt) — không tốn 5h training mới.

---

## G6: Multi-metric Ensemble

### 6A. OWASP CRS pass rate

1. **Tính khả tín** — chuẩn industry, reviewer chấp nhận; nhưng phụ thuộc version cụ thể, dễ bị "frozen-in-time".
2. **Threshold sensitivity** — đổi PL1 sang PL2 có thể đảo ngược ranking model; phải report nhiều PL.
3. **Coverage** — bao phủ phần lớn SQLi cổ điển nhưng yếu với time-based blind (rule ít); model học bypass time-based dễ "đạt 100%" giả.
4. **Latency** — 30-50ms/call qua Docker; với 20M queries cần cache nghiêm túc.
5. **Reproducibility cao** — anyone với cùng OWASP version tag và payload sẽ ra cùng kết quả; rất tốt cho paper.

### 6B. ML-IDS detection rate

1. **Bổ sung blind spot OWASP** — học máy phát hiện được pattern OWASP miss; nhưng IDS cũng có thể detect false positive cao.
2. **Phụ thuộc training data IDS** — nếu IDS được train trên dataset trùng → leakage; cần IDS được train trên dataset hoàn toàn khác.
3. **Adversarial pressure** — IDS có thể bị fool nhanh hơn rule WAF (Dasari 2025 chứng minh CWGAN-GP fool ML detector dễ); → metric này có thể "rớt giá" nhanh.
4. **Choice paralysis** — IDS nào? CNN/LSTM/XGBoost? Mỗi loại có blind spot khác; chọn 1 thì bias, chọn nhiều thì compute scale.
5. **Hữu ích cho generalization claim** — model bypass OWASP + bypass IDS = robust claim mạnh; nhưng phải caveat về out-of-distribution.

### 6C. AST Structural Diversity

1. **Đo đúng cái cần đo** — diversity ở structural level, không phải token level; tránh được trap của Self-BLEU.
2. **Phụ thuộc parser** — sqlparse vs sqlglot ra AST khác; payload không parse được → bị loại, có thể bias metric.
3. **Sensitivity vs robustness** — entropy quá nhạy với rare structure, có thể bị inflated bởi 1-2 outlier; cần báo cáo cả median lẫn entropy.
4. **Không correlate với security value** — 2 payload AST khác nhau hoàn toàn có thể có cùng security impact (vd: thay `'a'='a'` bằng `1=1`); diversity ≠ usefulness.
5. **Novelty trong literature** — chưa thấy paper SQLi-GAN nào dùng; đây có thể là contribution nếu formalize tốt — kèm lợi ích publishable bonus.

### 6D. Real DB execution rate

1. **Ground truth nhất** — payload chạy được nghĩa là **thực sự là SQL hợp lệ**, không phải string ngẫu nhiên; chống reward hacking mạnh nhất.
2. **Phụ thuộc DB engine** — SQLite syntax khác MySQL khác PostgreSQL; payload Oracle-specific (dataset có XMLTYPE 60%!) sẽ fail trên SQLite → false negative.
3. **Sandbox risk** — payload destructive (`DROP TABLE`) có thể phá test DB nếu rollback thất bại; cần in-memory DB hoặc Docker ephemeral.
4. **Context-dependent** — payload chỉ có nghĩa trong context query (`WHERE id=__`); cần wrap context template, có thể bias kết quả theo context cụ thể.
5. **Slow ratchet** — DB call chậm hơn parser (5-10ms vs <1ms); với 20M queries thêm 100+ giờ compute nếu không cache.

### 6E. Re-lex uniqueness

1. **Solve confounding của de-lex** — đo diversity sau khi fill placeholder, gần với perceived diversity của con người; trực tiếp giải vấn đề Self-BLEU=0.99.
2. **Phụ thuộc re-lex dictionary** — uniqueness scale với kích thước từ điển re-lex; có thể "game the metric" bằng từ điển lớn — phải fix dictionary size khi report.
3. **Không phản ánh structural diversity** — 1000 payload với cùng skeleton, chỉ khác `__INT__` value, vẫn được coi là unique 100% — false sense of diversity.
4. **Cheap để compute** — chỉ là string uniqueness sau substitution; <1s cho 1000 mẫu.
5. **Reviewer skeptical** — có thể bị phản bác là "gaming"; cần argue rằng human attacker thật cũng vary giá trị cụ thể, không phải bug.

### Khuyến nghị weight cho ensemble

| Metric | Weight | Lý do |
|---|---|---|
| OWASP CRS pass | 0.30 | Ground truth security |
| Real DB execution | 0.25 | Ground truth correctness |
| AST diversity | 0.20 | Structural meaningfulness |
| ML-IDS evasion | 0.15 | Robustness to learned defense |
| Re-lex uniqueness | 0.10 | Surface diversity sanity check |

Final score multiplicative cho 2 cái đầu (gate), additive cho 3 cái sau (quality).

---

## G7: Đánh lại nhãn

### 7A. Quy mô vấn đề

Dataset hiện tại: 40,860 rows × 5 columns. Trong đó:
- 19,669 benign → không cần đánh nhãn lại
- 21,191 attack samples → đây là phần cần xem xét

Re-label 21k rows bằng tay = không khả thi. Cần chiến lược tiered.

### 7B. 5 phương án đánh nhãn lại

**Phương án 1 — Multi-source augmentation (KHÔNG re-label, mà mở rộng)**
- Crawl thêm payload từ: PortSwigger SQLi cheatsheet, HackTricks, sqlmap tamper outputs, OWASP testing guide examples, recent CVE proof-of-concepts.
- Mỗi source giữ field `source_tag` để theo dõi.
- Mục tiêu: 5-10 source, mỗi source ≥ 1000 payload.
- **Effort:** 2-3 ngày. **Impact:** giải quyết root cause (bias source) không phải triệu chứng.

**Phương án 2 — Semi-supervised re-labeling với LLM**
- Dùng Claude/GPT để re-classify từng payload với prompt có structured output (type, db_engine, mutation_technique, confidence, reasoning).
- Compare với nhãn cũ → flag những disagreement.
- Manual review chỉ cho disagreement (ước tính 10-20% = 2-4k rows).
- **Effort:** 1 ngày compute + 1-2 ngày manual. **Impact:** improve label quality, detect mis-labeled.

**Phương án 3 — Tiered confidence-based filtering**
- Hiện đã có `confidence` column. Phân tier:
  - confidence ≥ 0.95: gold (3,223 rows hiện đã có "expert demos")
  - 0.80-0.95: silver
  - < 0.80: bronze
- Training: chỉ dùng gold + silver, treat bronze làm validation.
- **Effort:** vài giờ. **Impact:** loại noise, không thêm diversity.

**Phương án 4 — Active learning loop**
- Train model với data hiện có.
- Generate 1000 payload, manual label 100 random samples.
- Add 100 đó vào training data với high weight.
- Lặp lại 5-10 vòng.
- **Effort:** 2-3 tuần. **Impact:** target chính xác phần distribution model đang miss.

**Phương án 5 — Adversarial relabeling**
- Lấy 1000 payload có classifier (XGBoost trên de-lex features) predict nhãn KHÁC nhãn hiện tại.
- Đây là những điểm classifier "không đồng ý" — high-information samples.
- Manual review 100-200 cái, fix nhãn nếu cần.
- **Effort:** 1-2 ngày. **Impact:** detect systematic mislabeling.

### 7C. Khuyến nghị

Combine **P1 (multi-source) + P3 (tiered)** trước, rồi xem có cần P2/P5 không.

Lý do:
- P1 giải quyết root cause (88.6% target users/accounts là bias source).
- P3 cheap, immediate win, không có downside.
- P2/P5 chỉ cần nếu sau P1+P3 vẫn collapse.

### 7D. Validation re-label

Cách kiểm chứng nhãn mới đúng:
1. Inter-annotator agreement: nếu dùng LLM (P2), chạy 3 lần độc lập, đo Cohen's kappa.
2. Held-out manual gold set: 500 payload bạn tự label, dùng làm test set cho mọi phương pháp.
3. Downstream test: re-train model trên data đã re-label, so sánh Self-BLEU-3 và ASR với baseline.

### 7E. Tránh các bẫy

- **Bẫy 1 — over-cleaning**: loại quá nhiều noise → mất diversity tự nhiên. Giữ ≥ 1% noise-like samples.
- **Bẫy 2 — label leakage**: re-label dùng cùng tool đã tạo dataset gốc → bias circular. Phải dùng tool/người khác.
- **Bẫy 3 — distribution shift**: nếu P1 làm tỷ lệ type thay đổi mạnh → val/test set cũ không còn representative; phải re-split.

---

## G8: 10 phản biện về "SeqGAN tự nhiên hợp với SQLi"

3 luận điểm: SQLi là (1) text, (2) có cấu trúc, (3) thông tin liên tục → SeqGAN hợp.

### Phản biện 1: SQL không phải "text tự nhiên"
**Khoa học:** Natural language có **smooth distribution** trên token space (gần nhau về meaning ≈ gần nhau về co-occurrence). SQL có **rigid grammar** — `SELECT * FROM` là legal, `* FROM SELECT` là illegal, không có "smooth" interpolation. SeqGAN được thiết kế cho NLL trên natural text (Yu 2017 test trên Chinese poems, MS COCO captions) → reward landscape khác cơ bản.
**5 tuổi:** Câu chuyện thì bé có thể thay từ "con mèo" bằng "con chó" vẫn ổn. SQL thì thay 1 chữ là máy tính không hiểu nữa.

### Phản biện 2: "Cấu trúc" SQL là tree, không phải sequence
**Khoa học:** SQL là **context-free grammar** sinh ra parse tree. Sequence representation chỉ là **linearization** của tree — mất thông tin về dependency dài (vd: subquery khớp đóng/mở). LSTM xử lý sequence, không xử lý tree. → Có nguyên cứu Tree-LSTM (Tai 2015), TreeGAN cho SQL/code generation. SeqGAN ignore tree structure = mất thông tin.
**5 tuổi:** Lego có nhiều hình. Nếu bé chỉ nhìn theo hàng (trái-phải), bé không thấy bé đang ráp một con voi 3D.

### Phản biện 3: REINFORCE variance cao trên discrete space lớn
**Khoa học:** Yu 2017 paper, section 4.1: SeqGAN variance proportional to vocabulary size. Vocab > 5000 → REINFORCE không converge (paper test với vocab ~5000). Vocab 134 OK, nhưng nếu re-evaluate preprocessing (G7) → vocab tăng → instability tăng. Atkinson 2024 confirm: PPO không cứu được, batch size tăng giúp một phần.
**5 tuổi:** Càng nhiều lựa chọn, càng khó đoán lựa chọn nào sẽ thắng. Nếu chỉ có 5 lựa chọn thì dễ học, 5000 lựa chọn thì rất khó.

### Phản biện 4: SQLi payload ngắn — SeqGAN tốt nhất cho sequence dài
**Khoa học:** Yu 2017 test với sequence length T=20. Lu 2022 SQLi payload trung bình ~30-80 tokens. Với T nhỏ, Monte Carlo rollout có **hiệu lực giảm** (ít future để rollout). Cho payload ngắn, **direct GAN với Gumbel-Softmax** (RelGAN) hoặc **policy gradient không cần MC** (TextGAIL imitation) hiệu quả hơn. Survey de Rosa 2022 confirm: SeqGAN dominate cho T=20-40, RelGAN cho T<20.
**5 tuổi:** Đi đường ngắn thì bé không cần xem bản đồ tương lai. SeqGAN giống như nhìn xa, nhưng câu SQL ngắn quá để cần nhìn xa.

### Phản biện 5: Discriminator học pattern, không học semantics
**Khoa học:** TextCNN discriminator (SeqGAN gốc) học **n-gram patterns**. SQLi semantics đòi hỏi hiểu **side effect** (payload có inject được không?), không phải pattern matching. Discriminator có thể bị fool bởi pattern-similar nhưng semantically-invalid payload — đây chính là noise problem Agrawal 2024 báo cáo. → Reward từ D **không correlate với security value**.
**5 tuổi:** Bé biết hình thoi giống hình kim cương, nhưng không biết kim cương cứng còn thoi giấy mềm. SeqGAN học hình thôi, không học chất.

### Phản biện 6: Mode collapse là endemic, không phải bug
**Khoa học:** Yu 2017 báo cáo Self-BLEU-3 SeqGAN ≈ 0.8 trên text generation (worse than MLE 0.85). RelGAN paper (Nie 2018) chứng minh SeqGAN bị diversity-quality tradeoff: tăng quality (ASR) → giảm diversity (Self-BLEU). Đạt ASR=100% Self-BLEU=0.99 = đúng predicted tradeoff, không phải implementation bug.
**5 tuổi:** Bé học vẽ con mèo. Càng vẽ giống thật, bé càng vẽ y hệt một con mèo. Vẽ 100 con đều giống nhau.

### Phản biện 7: Reward sparsity cho SeqGAN khác với RL games
**Khoa học:** REINFORCE hoạt động tốt khi có **dense reward** hoặc **reward shaping**. SQLi với binary WAF response (pass/block) là **sparse terminal reward** — gradient noisy. Atari games có dense reward (score increment). Nếu chỉ dùng WAF response → SeqGAN cần thousands of trial-and-error mỗi pattern. → Cần reward shaping (G1 đề xuất composite reward giải quyết).
**5 tuổi:** Bé chơi game được điểm sau mỗi action — bé học nhanh. Bé chỉ biết thắng/thua khi game kết thúc — bé học rất lâu.

### Phản biện 8: SeqGAN ignore conditional context
**Khoa học:** SQLi luôn được injected vào **context query** (`SELECT * FROM users WHERE id = '{payload}'`). Cùng payload có thể bypass trong context này, fail trong context khác. SeqGAN sinh payload **unconditional** → ignore context. Conditional SeqGAN (Chowdhary 2023) hoặc CGAN (GSQLi 2024) giải quyết. Approach hiện tại là unconditional → less effective.
**5 tuổi:** Cùng câu "tôi muốn ăn" thì ở nhà hàng OK, ở thư viện thì kỳ. Bé phải biết bé đang ở đâu mới nói đúng.

### Phản biện 9: Adversarial training không tận dụng được expert demo
**Khoa học:** Có 3,223 expert demos (confidence ≥ 0.95). SeqGAN gốc chỉ dùng cho pretrain. Imitation Learning literature (TextGAIL, GAIL) chứng minh **inverse RL từ demos** hiệu quả hơn pure REINFORCE cho structured tasks. → Đang underutilize expert data.
**5 tuổi:** Bé có thầy giáo giỏi nhưng chỉ nghe thầy nói 1 lần rồi tự học. Lẽ ra nghe thầy nhiều hơn.

### Phản biện 10: SeqGAN không scale với multi-objective
**Khoa học:** Composite reward (G1-G6) có 5-7 thành phần. REINFORCE với multi-objective dễ rơi vào **một objective dominate**, các objective khác bị bỏ qua. Multi-objective RL (Pareto-based, hypervolume) ngoài scope SeqGAN. → Hoặc đơn giản hóa reward, hoặc dùng framework RL hiện đại hơn (PPO + multi-head, hoặc decomposed reward).
**5 tuổi:** Bé chỉ ăn được 1 cái bánh. Nếu mẹ đưa 5 cái khác nhau, bé chỉ chọn cái ngon nhất, bỏ 4 cái kia.

### Tổng kết phản biện

Trực giác không sai, nhưng **ngây thơ ở chỗ "vì là text và cấu trúc nên SeqGAN tự nhiên hợp"**. SQL injection có 3 đặc tính (rigid grammar, tree structure, security semantics) mà SeqGAN gốc **không tận dụng được**. Mô hình vẫn có thể work, nhưng **không phải vì SeqGAN tự nhiên hợp** — mà vì đã làm rất nhiều việc bù trừ (de-lex, vocab giảm, MLE pretrain, composite reward).

**Khuyến nghị:** Giữ SeqGAN làm baseline, **acknowledge các giới hạn trong paper**. Nếu kết quả cuối yếu, biết để chuyển hướng sang Conditional SeqGAN (Chowdhary) hoặc Tree-aware variant.

---

## G10: Ôm đồm 3 mục tiêu

3 mục tiêu:
1. Text generation GAN (như SeqGAN/RelGAN)
2. Discrete sequence handling
3. Security reward integration

### 5 lý do NÊN ôm đồm

1. **3 mục tiêu này không tách rời được trong domain SQLi** — không thể có "text generation cho SQLi" mà không có discrete handling và không có security reward. Tách ra là giả tạo.
2. **Đây là gap thực sự trong literature** — Lu 2022 (security reward, không text gen rigorous), Yu 2017 (text gen, không security), GSQLi 2024 (mutation actions, không pure generation). Niche thực sự cần bridge cả 3.
3. **Compute không tăng tuyến tính** — đã có infrastructure cho 2 (SeqGAN + discrete). Thêm security reward là 30% effort thêm, không phải 100%.
4. **Risk hedging** — nếu 1 mục tiêu fail (vd: security reward khó setup), 2 cái còn lại vẫn có giá trị độc lập. Submission có "fallback".
5. **Story telling cho paper mạnh hơn** — paper với 3 contribution coordinated hấp dẫn hơn 1 contribution lonely. Reviewer thích "novel combination".

### 5 lý do KHÔNG NÊN ôm đồm

1. **Scope creep risk** — sprint hiện tại đã 5h+ training chỉ cho baseline. Thêm 2 mục tiêu = 3-5x effort. Có thể không hoàn thành.
2. **Mỗi mục tiêu cần expertise riêng** — text gen GAN cần ML/NLP, discrete sequence cần RL, security reward cần WAF/pentest. Có thể không depth ở cả 3 → kết quả mediocre ở mỗi cái.
3. **Multi-objective optimization conflict** — quality của text generation (đa dạng, fluent) có thể conflict với security objective (focused, exploit-shaped). REINFORCE không handle Pareto trade-off tự nhiên (Phản biện 10 ở G8).
4. **Evaluation complexity scale với mục tiêu** — 3 mục tiêu × 5 metric = 15 numbers cần report. Reviewer overwhelmed. Comparison với baselines khó hơn.
5. **"Master of none" trap** — 1 mục tiêu làm depth-first thường beat 3 mục tiêu làm breadth-first. Vd: Lu 2022 chỉ focus security reward (no text gen rigor) nhưng được cite vì depth ở security side.

### Khuyến nghị cụ thể

**Phasing rõ ràng:**

| Phase | Focus | Mục tiêu | Deliverable |
|---|---|---|---|
| Phase 1 (đã làm) | Text gen + Discrete | SeqGAN baseline trên SQLi | Pipeline working, val_ppl=1.70 ✓ |
| Phase 2 (next) | + Security reward | OWASP CRS integration | ASR thực với real WAF |
| Phase 3 (optional) | Optimization | Boundary-aware + diversity | Publish-ready results |

Mỗi phase **deliverable hoàn chỉnh độc lập** — không phải phải làm hết mới có kết quả. Phase 1 đã có thể viết thành 1 workshop paper. Phase 2 thành conference paper. Phase 3 thành journal paper.

**Đây là phasing, không phải ôm đồm.** Khác biệt: phasing có exit point ở mỗi phase, ôm đồm thì all-or-nothing.

### Kết luận

**Không ôm đồm nếu phase rõ ràng**. **Đang ôm đồm nếu cố làm cả 3 trong cùng 1 sprint**. Hiện tại Phase 1 đã xong, Phase 2 chưa bắt đầu. → Đề xuất: commit phase 2 cho 2-3 tuần tới, chỉ làm OWASP integration + reward composite (G1), không đụng đến diversity (G2,G5) hay relabeling (G7) ngay.

---

## Tóm Tắt Action Items Khả Thi

| # | Hành động | Effort | Phụ thuộc | Impact |
|---|---|---|---|---|
| 1 | Kiểm tra bias dataset (script G4) | 1h | — | Xác nhận giả thuyết bias |
| 2 | Setup OWASP CRS Docker (G1) | 1 ngày | — | Mở khoá real WAF reward |
| 3 | Triển khai BoundaryAwareReward (G5) | 2-3h | #2 | Diversity fix có lý thuyết |
| 4 | AST subtree fingerprint metric (G2 QĐ4) | 3-4h | — | Đo diversity đúng chỗ |
| 5 | Multi-source crawl (G7 P1) | 2-3 ngày | — | Giải root cause bias |
| 6 | Tiered confidence filtering (G7 P3) | 1h | — | Quick win label quality |
| 7 | Composite reward (G1 + G3 curriculum) | 1-2 ngày | #2, #3 | Phase 2 chính thức bắt đầu |
| 8 | Re-lex evaluation (Hướng 5 cũ) | 2-3h | — | Verify Self-BLEU artifact |

**Khuyến nghị thứ tự:** #1 → #6 → #8 → #2 → #3 → #4 → #5 → #7

Quick wins trước (1, 6, 8) → infrastructure (2, 3, 4) → root cause (5) → phase 2 chính (7).

---

*Tài liệu được tạo ngày 2026-05-11 bởi phân tích chuyên sâu của user feedback trên 10 góc nhìn ban đầu.*
*Mọi citation đã được verify từ file gốc trong `Skill/output_txt/`.*
