# Guiding V2 — SeqGAN SQLi với Composite Reward & Boundary-Aware Generation

> **Đối tượng đọc**: Researcher đã đọc `Guiding.md` v1 và `timeline/DEEP_ANALYSIS_10_PERSPECTIVES.md`.
> **Phong cách**: Technical, self-contained, đầy đủ để re-implement từ đầu.
> **Cập nhật**: 2026-05-11
> **Trạng thái**: Specification — code chưa được triển khai cho approach mới.

---

## Mục Lục

1. [Tổng quan & Motivation](#1-tổng-quan)
2. [Pipeline end-to-end](#2-pipeline)
3. [Kiến trúc chi tiết](#3-kiến-trúc)
4. [Reward Oracle Stack](#4-reward-stack)
5. [Training: 3-phase Curriculum](#5-training)
6. [Evaluation: 5-metric Ensemble](#6-evaluation)
7. [Dataset Structure mới](#7-dataset)
8. [Hyperparameters](#8-hyperparams)
9. [Baseline Metrics](#9-baselines)
10. [10 Limitations dự đoán](#10-limitations)
11. [Mỗi góc nhìn giải quyết gì](#11-góc-nhìn)
12. [Cấu trúc thư mục v2](#12-skeleton)

---

## 1. Tổng quan

### 1.1 Tại sao cần V2

V1 (đã chạy 5h+ training) đạt:
- ASR=100%, Syntax=100% — pass hard target nhưng margin 0.3pp
- Self-BLEU-3=0.9894 — FAIL diversity target < 0.60
- Heuristic proxy reward — không có real WAF
- Mode collapse không giải được bằng entropy regularization hay per-type training

V2 giải quyết 4 vấn đề gốc rễ:

| Vấn đề V1 | Giải pháp V2 | Tham chiếu |
|---|---|---|
| Heuristic proxy quá dễ hack | OWASP CRS + Custom Rules composite reward | G1, G3 |
| Mode collapse endemic | Boundary-aware reward + AST diversity | G2, G5 |
| Self-BLEU đo sai không gian | 5-metric ensemble với AST fingerprinting | G2, G6 |
| Dataset bias source-homogeneous | Multi-source augmentation + tiered confidence | G4, G7 |

### 1.2 Mục tiêu V2

**Mục tiêu nghiên cứu chính:**
1. Demonstrate rằng composite reward (OWASP + custom + DB) outperform heuristic proxy về **meaningful ASR**.
2. Demonstrate rằng boundary-aware reward giảm mode collapse mà entropy regularization không làm được.
3. Establish 5-metric evaluation framework như một contribution methodology.

**Mục tiêu kỹ thuật:**
- ASR thực với OWASP CRS PL2: > 60% (so với MLE baseline)
- Self-BLEU-3 (re-lex space): < 0.70
- AST subtree fingerprint diversity: > 0.50
- Bypass Quality Score: > 0.40 trung bình
- Training time: ≤ 20 giờ end-to-end

### 1.3 Triết lý thiết kế V2

1. **Multiplicative gates, additive quality**: Reward dùng nhân cho components phải-đạt (syntax, executable), cộng cho components nâng-cao (diversity, IDS evasion). Chống reward hacking từng phần.
2. **Boundary > Maximum**: Reward cao nhất cho payload sát ranh giới block/pass, không phải payload bypass-dễ. Buộc đa dạng.
3. **Phasing rõ ràng**: Mỗi phase có deliverable độc lập. Không all-or-nothing.
4. **Evaluation > Optimization**: Đo trên 5 metric độc lập trước khi tin vào số liệu nào.

---

## 2. Pipeline End-to-End

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 0: DATA AUDIT & RE-PREP                               │
│  • Bias detection (skeleton uniqueness, source diversity)   │
│  • Multi-source augmentation (PortSwigger, HackTricks, ...)│
│  • Tiered confidence filter (gold/silver/bronze)            │
│  • Re-split với stratification mới                          │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: TOKENIZATION (Optional: Partial De-lex)            │
│  • Keep current 134 vocab cho baseline                       │
│  • Optional: P2 partial de-lex (giữ string content)         │
│  • Re-lex dictionary build (cho evaluation)                  │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: MODEL COMPONENTS                                    │
│  • Generator: LSTM 3-layer 512-dim (giữ nguyên V1)          │
│  • Conditional embedding (attack type) — NEW                 │
│  • Discriminator: TextCNN (giữ nguyên V1)                   │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: REWARD ORACLE STACK                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  WAFOracle (ModSecurity Docker, OWASP CRS v4.3.0)   │   │
│  │  → anomaly_score                                     │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  CustomRuleEngine                                   │   │
│  │  → pass_count / total_rules                         │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  SQLParser (sqlparse + sqlglot fallback)            │   │
│  │  → syntax_pass (0/1)                                │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  DBSandbox (SQLite in-memory)                       │   │
│  │  → executable (0/1)                                 │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  ASTFingerprintTracker (subtree hashing depth=3)    │   │
│  │  → novelty_score = 1 - max_sim(fingerprint, cache)  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  CompositeReward:                                            │
│   r = syntax_gate × executable_gate × (                      │
│         w_owasp · r_boundary(anomaly)                        │
│       + w_custom · r_custom                                  │
│       + w_diversity · novelty_score                          │
│       - w_overlap · overlap_penalty                          │
│   )                                                          │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: TRAINING — 3-Phase Curriculum                      │
│  • MLE pretrain (10 epochs, gold+silver data)               │
│  • Warmup adversarial (0-2k steps, syntax+custom only)      │
│  • Main adversarial (2k-15k, full composite)                │
│  • Refinement (15k-20k, diversity-weighted)                 │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: EVALUATION — 5-Metric Ensemble                     │
│  • OWASP CRS pass rate (w=0.30)                             │
│  • Real DB execution rate (w=0.25)                          │
│  • AST diversity entropy (w=0.20)                           │
│  • ML-IDS evasion rate (w=0.15)                             │
│  • Re-lex uniqueness (w=0.10)                               │
│  • Bootstrap CI cho mỗi metric                              │
│  • Per-type breakdown                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Kiến Trúc Chi Tiết

### 3.1 Generator (LSTM Policy, conditional)

```python
class ConditionalGeneratorLSTM(nn.Module):
    """
    LSTM 3-layer với conditional embedding (attack type).
    Input: sequence của previous tokens + attack_type embedding
    Output: logits over vocabulary cho next token
    """
    def __init__(
        self,
        vocab_size: int = 134,
        embed_dim: int = 256,
        hidden_dim: int = 512,
        num_layers: int = 3,
        num_attack_types: int = 8,
        type_embed_dim: int = 32,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.token_embed = nn.Embedding(vocab_size, embed_dim)
        self.type_embed = nn.Embedding(num_attack_types, type_embed_dim)
        self.lstm = nn.LSTM(
            input_size=embed_dim + type_embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, input_ids, attack_type_ids, hidden=None):
        # input_ids: (B, T), attack_type_ids: (B,)
        tok_emb = self.token_embed(input_ids)  # (B, T, E)
        type_emb = self.type_embed(attack_type_ids)  # (B, type_E)
        type_emb_expanded = type_emb.unsqueeze(1).expand(-1, tok_emb.size(1), -1)
        x = torch.cat([tok_emb, type_emb_expanded], dim=-1)  # (B, T, E+type_E)
        out, hidden = self.lstm(x, hidden)
        logits = self.head(out)  # (B, T, V)
        return logits, hidden
```

**Khác V1:**
- Thêm `attack_type_ids` (Phản biện 8 trong G8 — SeqGAN unconditional là weak).
- 8 attack types: `error_based, boolean_blind, time_blind, union_based, heavy_query, auth_bypass, out_of_band, other`.
- Init từ V1 checkpoint `mle_best.pt` cho token embeddings; type embeddings init random.

### 3.2 Discriminator (TextCNN, giữ nguyên V1)

```python
class DiscriminatorCNN(nn.Module):
    """
    TextCNN WGAN-GP discriminator.
    Input: sequence of token ids
    Output: scalar score (real/fake)
    """
    def __init__(
        self,
        vocab_size: int = 134,
        embed_dim: int = 128,
        kernel_sizes: list = [3, 4, 5],
        num_filters: int = 128,
    ):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.convs = nn.ModuleList([
            nn.Conv1d(embed_dim, num_filters, k, padding=k//2)
            for k in kernel_sizes
        ])
        self.fc = nn.Linear(num_filters * len(kernel_sizes), 1)

    def forward(self, input_ids):
        emb = self.embed(input_ids).transpose(1, 2)  # (B, E, T)
        pooled = [F.adaptive_max_pool1d(F.relu(conv(emb)), 1).squeeze(-1)
                  for conv in self.convs]
        x = torch.cat(pooled, dim=-1)  # (B, num_filters * len(kernels))
        return self.fc(x).squeeze(-1)  # (B,)
```

**Vai trò V2:** Giảm xuống — chỉ chiếm 10-20% reward total. Reward chính từ Oracle Stack.

### 3.3 Conditional Embedding Strategy

Attack type được lookup từ `data/train.csv` column `sqli_type`. Tại inference, có thể:
- **Unconditional**: random sample attack type theo prior distribution.
- **Conditional**: user specify attack type cụ thể.

Trade-off: Conditional làm complexity tăng, nhưng giải quyết Phản biện 8 (SeqGAN ignore context).

---

## 4. Reward Oracle Stack

### 4.1 WAFOracle (Real ModSecurity Docker)

```python
class WAFOracle:
    """
    OWASP ModSecurity CRS v4.3.0 trong Docker.
    Test mode: PL1 (default) hoặc PL2 (strict).
    """
    def __init__(self, docker_url="http://localhost:8080", paranoia=2, timeout=2.0):
        self.url = docker_url
        self.paranoia = paranoia
        self.timeout = timeout

    def evaluate(self, payload: str) -> dict:
        """
        Returns:
            anomaly_score: int (0..∞)
            blocked: bool (anomaly_score >= 5 in PL2)
            matched_rules: list of rule IDs triggered
        """
        try:
            resp = requests.post(
                self.url,
                params={"id": payload},
                headers={"X-ModSec-Paranoia": str(self.paranoia)},
                timeout=self.timeout,
            )
            return {
                "anomaly_score": int(resp.headers.get("X-ModSec-Score", 999)),
                "blocked": resp.status_code == 403,
                "matched_rules": resp.headers.get("X-ModSec-Matched", "").split(","),
            }
        except (requests.Timeout, requests.ConnectionError):
            return {"anomaly_score": 999, "blocked": True, "matched_rules": []}
```

**Boundary-aware reward (G5):**

```python
def waf_boundary_reward(anomaly_score, threshold=5):
    """
    Reward cao nhất khi anomaly_score gần threshold (sát ranh giới).
    """
    if anomaly_score >= threshold:
        return -0.5  # blocked, light penalty
    distance = threshold - anomaly_score
    return 1.0 - (distance / threshold)
```

### 4.2 CustomRuleEngine (anti-noise)

```python
class CustomRuleEngine:
    """
    Bộ rule custom kiểm tra payload có phải SQLi đúng nghĩa không.
    Chống reward hacking — payload chỉ bypass OWASP qua trick encoding
    nhưng không thực sự là SQLi sẽ fail ở đây.
    """
    RULES = [
        # Rule 1: Phải có ≥ 1 SQLi keyword/operator
        lambda p: any(kw in p.lower() for kw in [
            "union", "select", "or 1", "and 1", "sleep", "benchmark",
            "extractvalue", "updatexml", "xmltype", "concat",
        ]),
        # Rule 2: Phải có ≥ 1 quoting/comment/operator characteristic
        lambda p: any(c in p for c in ["'", '"', "--", "/*", "*/", "#", ";"]),
        # Rule 3: KHÔNG được trivial (length sau strip)
        lambda p: len(p.strip()) >= 5,
        # Rule 4: KHÔNG được chỉ là benign-like (vd: chỉ số/tên đơn lẻ)
        lambda p: not re.fullmatch(r"[\w\s]+", p),
        # Rule 5: Có ≥ 1 operator quan hệ hoặc keyword query
        lambda p: bool(re.search(r"[=<>]|union|select|order\s+by", p, re.I)),
    ]

    def evaluate(self, payload: str) -> float:
        passed = sum(1 for rule in self.RULES if rule(payload))
        return passed / len(self.RULES)
```

### 4.3 SQLParser Gate

```python
class SQLParserGate:
    """
    Syntax validity check. Returns 0 hoặc 1.
    """
    def evaluate(self, payload: str) -> int:
        # Wrap trong context query để parse được
        wrapped = f"SELECT * FROM dummy WHERE id={payload}"
        try:
            parsed = sqlparse.parse(wrapped)
            if not parsed or not parsed[0].tokens:
                return 0
            # Fallback: thử sqlglot nếu sqlparse pass dễ dãi
            try:
                sqlglot.parse_one(wrapped, dialect="mysql")
            except sqlglot.ParseError:
                return 0
            return 1
        except Exception:
            return 0
```

### 4.4 DBSandbox (Real Execution Gate)

```python
class DBSandbox:
    """
    SQLite in-memory để test payload chạy được không.
    KHÔNG quan tâm output đúng — chỉ quan tâm KHÔNG raise SyntaxError.
    """
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        # Setup dummy schema
        self.cur.execute("CREATE TABLE dummy (id INTEGER, name TEXT)")
        self.cur.execute("INSERT INTO dummy VALUES (1, 'test')")

    def evaluate(self, payload: str) -> int:
        wrapped = f"SELECT * FROM dummy WHERE id={payload}"
        try:
            self.cur.execute(wrapped)
            _ = self.cur.fetchall()
            return 1
        except (sqlite3.OperationalError, sqlite3.Warning):
            return 0
        finally:
            self.conn.rollback()
```

**Edge case:** SQLite syntax khác MySQL/Oracle. Dataset của bạn có 60% Oracle XMLTYPE → nhiều payload sẽ fail SQLite. → Lựa chọn: (a) SQLite chỉ check basic syntax, accept false negatives; (b) Multi-DB sandbox với MySQL Docker.

V2 starts với SQLite (a) cho compute, có thể nâng cấp (b) nếu cần.

### 4.5 ASTFingerprintTracker (Diversity Reward)

```python
class ASTFingerprintTracker:
    """
    Theo dõi subtree fingerprints (depth=3) của payload đã sinh ra.
    Reward novelty cho payload có fingerprint mới.
    """
    def __init__(self, max_cache_size=10000):
        self.cache = set()  # set of fingerprint hashes
        self.max_size = max_cache_size

    def fingerprint(self, payload: str, depth: int = 3) -> frozenset:
        """Compute set of subtree hashes."""
        try:
            tree = sqlparse.parse(f"SELECT * FROM dummy WHERE id={payload}")[0]
        except Exception:
            return frozenset()
        return frozenset(self._extract_subtrees(tree, depth))

    def _extract_subtrees(self, node, max_depth, current_depth=0):
        if current_depth >= max_depth:
            return [hash(str(node.ttype))]
        subtrees = [hash(str(node.ttype))]
        for child in getattr(node, "tokens", []):
            subtrees.extend(self._extract_subtrees(child, max_depth, current_depth+1))
        return subtrees

    def novelty(self, payload: str) -> float:
        fp = self.fingerprint(payload)
        if not fp:
            return 0.0
        if not self.cache:
            self.cache.update(fp)
            return 1.0
        overlap = len(fp & self.cache) / len(fp) if fp else 0
        novelty = 1.0 - overlap
        if len(self.cache) < self.max_size:
            self.cache.update(fp)
        return novelty
```

### 4.6 CompositeReward

```python
class CompositeReward:
    """
    Reward composite:
      r = syntax_gate × executable_gate × (
            w_owasp · r_boundary(anomaly)
          + w_custom · r_custom
          + w_diversity · novelty
          - w_overlap · overlap_penalty
      )
    """
    def __init__(self, phase="warmup"):
        self.waf = WAFOracle()
        self.custom = CustomRuleEngine()
        self.parser = SQLParserGate()
        self.db = DBSandbox()
        self.ast = ASTFingerprintTracker()
        self.cache = {}  # payload_hash → reward
        self.set_phase(phase)

    def set_phase(self, phase):
        """3-phase curriculum weights."""
        if phase == "warmup":
            self.weights = {"owasp": 0.0, "custom": 0.7, "diversity": 0.0, "overlap": 0.0}
        elif phase == "adversarial":
            self.weights = {"owasp": 0.4, "custom": 0.3, "diversity": 0.2, "overlap": 0.1}
        elif phase == "refinement":
            self.weights = {"owasp": 0.3, "custom": 0.1, "diversity": 0.5, "overlap": 0.1}
        else:
            raise ValueError(f"Unknown phase: {phase}")

    def __call__(self, payload: str) -> float:
        h = hash(payload)
        if h in self.cache:
            return self.cache[h]

        # Gates (multiplicative)
        syntax = self.parser.evaluate(payload)
        if syntax == 0:
            r = -1.0
            self.cache[h] = r
            return r
        executable = self.db.evaluate(payload)
        if executable == 0:
            r = -0.5
            self.cache[h] = r
            return r

        # Quality (additive)
        if self.weights["owasp"] > 0:
            anomaly = self.waf.evaluate(payload)["anomaly_score"]
            r_owasp = waf_boundary_reward(anomaly)
        else:
            r_owasp = 0.0
        r_custom = self.custom.evaluate(payload)
        r_diversity = self.ast.novelty(payload)

        # Overlap penalty: pass OWASP nhưng fail custom = noise
        overlap_penalty = max(0, r_owasp - r_custom) if r_owasp > 0 else 0

        r = (
            self.weights["owasp"] * r_owasp
            + self.weights["custom"] * r_custom
            + self.weights["diversity"] * r_diversity
            - self.weights["overlap"] * overlap_penalty
        )
        self.cache[h] = r
        return r
```

---

## 5. Training: 3-Phase Curriculum

### 5.1 MLE Pretrain (Phase 0)

| Setting | Value |
|---|---|
| Data | Gold (confidence ≥ 0.95) + Silver (0.80-0.95), upweight gold 3× |
| Epochs | 10 (early stop patience=3) |
| LR | 1e-3, cosine decay |
| Batch | 64 |
| Conditional | Yes — pass attack_type_ids |
| Init | Random (V2 không init từ V1 vì conditional embedding mới) |

**Expected:** val_ppl ≈ 1.5-1.8 (V1 đạt 1.70 unconditional, V2 conditional có thể tốt hơn vì type signal).

### 5.2 Warmup Adversarial (Phase 1, steps 0-2000)

| Setting | Value |
|---|---|
| Reward | syntax × executable × (0.7 custom + 0 OWASP + 0 diversity) |
| LR_G | 1e-4 |
| LR_D | 1e-4 |
| MC rollout K | 16 |
| D:G ratio | 1:1 (giảm từ 5:1 vì D không phải nguồn reward chính) |
| Batch | 64 |

**Mục đích:** Đảm bảo G không sinh garbage trước khi gọi WAF (mỗi WAF call 30-50ms, không muốn lãng phí).

**Validation mỗi 200 steps:** custom rule pass rate phải > 50%.

### 5.3 Main Adversarial (Phase 2, steps 2000-15000)

| Setting | Value |
|---|---|
| Reward | full composite (0.4 OWASP + 0.3 custom + 0.2 diversity + 0.1 overlap_penalty) |
| LR_G | 5e-5 (giảm khi WAF reward kick in) |
| LR_D | 1e-4 |
| MC rollout K | 16 |
| Reward cache | enabled, max 100k entries |

**Mục đích:** Học bypass WAF có chất lượng (sát boundary, không noise).

**Validation mỗi 500 steps:** OWASP bypass rate, custom rule pass rate, AST novelty trên 100 samples.

### 5.4 Refinement (Phase 3, steps 15000-20000)

| Setting | Value |
|---|---|
| Reward | diversity-weighted (0.3 OWASP + 0.1 custom + 0.5 diversity + 0.1 overlap) |
| LR_G | 1e-5 |
| AST cache | reset every 1000 steps để force exploration |

**Mục đích:** Đa dạng hóa output sau khi đã học bypass.

### 5.5 Tổng thời gian dự kiến

- MLE pretrain: ~10-15 phút
- Phase 1 (warmup, no WAF): ~30-45 phút
- Phase 2 (full reward): ~10-15 giờ (chính bottleneck)
- Phase 3 (refinement): ~3-5 giờ
- **Tổng: ~15-20 giờ trên 1 GPU**

Reward cache có thể giảm 40-60% Phase 2 thời gian sau khi G converge partial.

---

## 6. Evaluation: 5-Metric Ensemble

### 6.1 Metric Definitions

| Metric | Cách tính | Weight | Target |
|---|---|---|---|
| `owasp_bypass_rate` | % payload có anomaly_score < 5 trên 1000 samples | 0.30 | > 60% |
| `db_execution_rate` | % payload chạy được trên SQLite | 0.25 | > 80% |
| `ast_diversity` | Shannon entropy của AST subtree fingerprints | 0.20 | > 3.0 (log base e) |
| `ml_ids_evasion` | 1 - detection_rate của XGBoost IDS (trained on held-out) | 0.15 | > 0.5 |
| `relex_uniqueness` | unique payloads sau re-lex / total | 0.10 | > 0.90 |

### 6.2 Composite Score

```
final_score = 0.30 * owasp_bypass_rate
            + 0.25 * db_execution_rate
            + 0.20 * (ast_diversity / 5.0)  # normalize to [0,1]
            + 0.15 * ml_ids_evasion
            + 0.10 * relex_uniqueness
```

Target final_score: > 0.55.

### 6.3 Statistical Rigor

- Bootstrap CI (n=10,000) cho mỗi metric.
- Mean ± std trên ≥ 3 random seeds (42, 123, 7).
- Wilcoxon signed-rank test giữa V2 vs V1 baseline.

### 6.4 Per-Type Breakdown

Báo cáo mỗi metric theo `attack_type` (8 types). Identifying mode collapse cụ thể tại type nào.

### 6.5 Confounding Controls

- **AST diversity confound**: nếu payload không parse được sẽ bị loại → có thể inflate diversity. Báo cáo % parse fail.
- **Re-lex confound**: phụ thuộc kích thước re-lex dictionary. Fix dictionary size = 50 entries (5 cho mỗi placeholder type) khi report.

---

## 7. Dataset Structure mới

### 7.1 Multi-source Schema

```csv
payload,payload_norm,sqli_type,db_engine,confidence,source,reasoning
"' OR 1=1--",__STR__ OR __INT__=__INT__--,boolean_blind,mysql,0.98,exploitdb,...
"x' UNION SELECT...",__STR__ UNION SELECT...,union_based,mysql,0.95,portswigger,...
```

**Sources mục tiêu:**
1. `exploitdb` — current dataset
2. `portswigger` — PortSwigger SQLi cheatsheet
3. `hacktricks` — HackTricks SQL Injection
4. `sqlmap_tampers` — sqlmap tamper script outputs
5. `cve_pocs` — recent CVE proof-of-concepts
6. `owasp_testing` — OWASP testing guide examples
7. `synthetic_v1` — V1 SeqGAN generated (low confidence, bronze tier)
8. `manual` — manually curated by user

**Mục tiêu:** mỗi source ≥ 1000 payload, no source > 40% total.

### 7.2 Tiered Confidence

```
gold:   confidence >= 0.95    (training weight 3.0)
silver: 0.80 <= confidence < 0.95  (training weight 1.0)
bronze: confidence < 0.80    (validation only, không train)
```

### 7.3 Re-split với Stratification

Stratify bởi 2 cột: `sqli_type` × `source`. Đảm bảo train/val/test mỗi cái đều có balance của cả type lẫn source.

```python
from sklearn.model_selection import StratifiedShuffleSplit

# Compound stratification key
df['stratify_key'] = df['sqli_type'] + '|' + df['source']
splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
train_idx, temp_idx = next(splitter.split(df, df['stratify_key']))
# Tiếp tục split temp thành val/test
```

### 7.4 Re-lex Dictionary

```json
{
  "__STR__": ["'admin'", "'test'", "'root'", "'user'", "'guest'"],
  "__INT__": ["1", "0", "-1", "999", "10"],
  "__HEX__": ["0x616263", "0x73797374656d", "0x61646d696e", "0x70617373", "0x726f6f74"],
  "__TABLE__": ["users", "accounts", "admin", "sessions", "products"],
  "__COL__": ["id", "username", "password", "email", "role"],
  "__IDENT__": ["xmltype", "dbms_pipe", "ctxsys", "sys_context", "user_tables"],
  "__TIME__": ["5", "10", "1", "2", "3"],
  "__BIGINT__": ["9999", "100000", "1", "0", "65535"]
}
```

Fixed dictionary size 5 entries × 8 placeholder types = **40 entries total** (cho reproducibility).

---

## 8. Hyperparameters

### 8.1 Model

| Hyperparameter | Value | Notes |
|---|---|---|
| Vocab size | 134 (current) hoặc ~300 (P2 partial de-lex) | Trade-off |
| Embed dim | 256 | |
| Type embed dim | 32 | NEW |
| Hidden dim | 512 | |
| Num LSTM layers | 3 | |
| Dropout | 0.2 | |
| D embed dim | 128 | |
| D kernels | [3, 4, 5] | |
| D filters per kernel | 128 | |

### 8.2 Training

| Hyperparameter | MLE | Warmup | Adversarial | Refinement |
|---|---|---|---|---|
| LR (G) | 1e-3 | 1e-4 | 5e-5 | 1e-5 |
| LR (D) | — | 1e-4 | 1e-4 | 1e-4 |
| Batch size | 64 | 64 | 64 | 64 |
| Max length | 80 | 80 | 80 | 80 |
| MC rollout K | — | 16 | 16 | 16 |
| Steps | 10 epochs | 2000 | 13000 | 5000 |
| Optimizer | Adam β=(0.9, 0.999) | Adam β=(0.5, 0.999) | Same | Same |
| Grad clip | 1.0 | 1.0 | 1.0 | 1.0 |

### 8.3 Reward Weights

| Component | Warmup | Adversarial | Refinement |
|---|---|---|---|
| w_owasp | 0.0 | 0.4 | 0.3 |
| w_custom | 0.7 | 0.3 | 0.1 |
| w_diversity | 0.0 | 0.2 | 0.5 |
| w_overlap | 0.0 | 0.1 | 0.1 |
| boundary threshold | — | 5 (PL2) | 5 |
| AST cache reset interval | — | never | every 1000 steps |

### 8.4 Reward Cache

| Setting | Value |
|---|---|
| Cache type | LRU dict |
| Max entries | 100,000 |
| Eviction | LRU |
| Persistence | save mỗi 1000 steps to disk |

---

## 9. Baseline Metrics

### 9.1 Baselines bắt buộc

| Baseline | Description | File |
|---|---|---|
| **B1: Template** | Random fill template patterns | `baselines/template_based.py` (existing) |
| **B2: MLE only** | Conditional generator, no adversarial | `pretrain_mle.py` output |
| **B3: V1 SeqGAN** | Current V1 SeqGAN result (Self-BLEU=0.99) | `checkpoints/adv_final.pt` |
| **B4: V2 no boundary** | V2 nhưng dùng binary reward thay boundary | Ablation |
| **B5: V2 no diversity** | V2 nhưng w_diversity=0 | Ablation |
| **B6: V2 full** | Full V2 implementation | Main model |

### 9.2 Baseline Targets cho V2 vs V1

| Metric | V1 (current) | V2 target | Improvement |
|---|---|---|---|
| Heuristic ASR | 100% | 100% (sanity check) | = |
| OWASP CRS bypass | unknown | > 60% | NEW |
| DB execution rate | unknown | > 80% | NEW |
| Self-BLEU-3 (de-lex) | 0.9894 | < 0.85 | -14% |
| Self-BLEU-3 (re-lex) | unknown | < 0.70 | NEW |
| AST diversity entropy | unknown | > 3.0 | NEW |
| BQS (multiplicative) | unknown | > 0.40 mean | NEW |

### 9.3 Ablation Strategy

| Ablation | Hỏi gì | Run |
|---|---|---|
| - boundary reward | Boundary có giúp diversity không? | Replace với binary reward |
| - conditional embedding | Conditional có quan trọng không? | Set type_embed_dim=0 |
| - custom rules | Custom rules có chống noise không? | Set w_custom=0 |
| - AST diversity | AST có ảnh hưởng Self-BLEU không? | Set w_diversity=0 |
| - multi-source data | Data source có giảm bias không? | Train chỉ với exploitdb |

Mỗi ablation: 1 run với cùng seed, so sánh 5 metrics.

---

## 10. 10 Limitations Dự Đoán

### L1: ModSecurity CRS overfitting (specific WAF)
Model học bypass **OWASP CRS v4.3.0 PL2 cụ thể**. Generalize sang Cloudflare/AWS WAF không guaranteed.
**Mitigation kế hoạch:** Held-out test với phpIDS hoặc libinjection.

### L2: Reward cache memory pressure
100k entries × ~200 bytes/entry = 20MB OK, nhưng nếu hash collision hoặc grow uncontrolled có thể OOM.
**Mitigation:** LRU eviction, disk persistence.

### L3: Compute time ~15-20h end-to-end
Phase 2 adversarial dominates. Mỗi WAF call 30-50ms × 64 batch × 16 MC × 13k steps = 11-22 hours.
**Mitigation:** Cache (50%+ hit rate expected), reduce K to 8 nếu cần.

### L4: AST parser failures on adversarial payloads
Generator có thể sinh payload làm sqlparse crash hoặc trả AST trống → AST diversity bị bias.
**Mitigation:** Fallback sqlglot, ghi log fail rate, exclude từ diversity calc nhưng include in BQS.

### L5: SQLite vs MySQL/Oracle syntax mismatch
60% dataset là Oracle XMLTYPE. SQLite không hiểu → DB execution rate giảm artificially.
**Mitigation:** (a) Accept false negative; (b) Switch sang MariaDB Docker với compat mode.

### L6: Multi-source data dilute attack distribution
Thêm sources có thể làm tỷ lệ attack type lệch — vd: PortSwigger nặng UNION-based, làm error_based ratio giảm.
**Mitigation:** Stratified split by `sqli_type × source`, monitor distribution shift.

### L7: Composite reward weight tuning fragile
4 weights (owasp, custom, diversity, overlap) × 3 phases = 12 hyperparameters. Có thể không converge well.
**Mitigation:** Grid search nhỏ trên 3 random seeds. Document final weights.

### L8: Boundary threshold (anomaly=5) là magic number
PL2 default threshold=5 nhưng có thể tốt với threshold khác (3, 7).
**Mitigation:** Ablation với threshold ∈ {3, 5, 7}.

### L9: Self-BLEU có thể vẫn cao
Even với AST diversity tốt, token-level Self-BLEU có thể vẫn > 0.85 vì de-lex space giới hạn. Đây là **measurement artifact** — phải report cả 2 spaces.
**Mitigation:** Report Self-BLEU trên cả de-lex và re-lex, document tradeoff.

### L10: REINFORCE variance scales với composite reward variance
Reward = 4-component sum → variance ~ sum of variance → gradient noisier hơn V1.
**Mitigation:** Increase batch (64 → 128), reward normalization (running mean/std), gradient accumulation.

### Severity Ranking

| # | Likelihood | Impact | Priority |
|---|---|---|---|
| L3 (compute) | High | High | **Critical** |
| L1 (WAF overfit) | Medium | High | High |
| L7 (weight tuning) | High | Medium | High |
| L5 (DB mismatch) | High | Medium | Medium |
| L10 (RL variance) | Medium | Medium | Medium |
| L9 (Self-BLEU) | High | Low | Low (measurement) |
| L4 (parser fail) | Medium | Low | Low |
| L2 (memory) | Low | Medium | Low |
| L6 (data shift) | Low | Medium | Low |
| L8 (threshold) | Low | Low | Low |

---

## 11. Mỗi Góc Nhìn Giải Quyết Gì

Mapping từ `DEEP_ANALYSIS_10_PERSPECTIVES.md` → V2 components:

| Góc nhìn | Thành phần V2 | Section |
|---|---|---|
| G1: OWASP + Custom Rules | `WAFOracle` + `CustomRuleEngine` + overlap penalty | 4.1, 4.2 |
| G2: AST Diversity + BQS | `ASTFingerprintTracker` + `SQLParserGate` × `DBSandbox` × WAF | 4.3-4.5 |
| G3: RL/SeqGAN focus | Generator + Reward Oracle (no PPO, REINFORCE only) | 3.1, 4.6 |
| G4: Bias detection | Phase 0: bias audit script | 2 |
| G5: Boundary-aware | `waf_boundary_reward` function | 4.1 |
| G6: 5-metric ensemble | Section 6 evaluation framework | 6 |
| G7: Re-label strategy | Multi-source + tiered confidence | 7.1-7.2 |
| G8: Phản biện SeqGAN | Conditional embedding (Phản biện 8), composite reward (Phản biện 7) | 3.3, 4.6 |
| G10: Phasing | 3-phase curriculum + Phase exit points | 5 |

---

## 12. Cấu Trúc Thư Mục V2

```
SeqGAN_SQLi/
├── Guiding.md                          ← V1 (existing)
├── Guiding_V2.md                       ← THIS FILE
├── EXECUTION_PLAYBOOK.md               ← Step-by-step instructions
├── timeline/
│   ├── ANALYSIS_REPORT.md              ← Existing
│   ├── EXPERIMENT_LOG.md               ← Existing
│   ├── FULL_BUILD_JOURNAL.md           ← Existing
│   └── DEEP_ANALYSIS_10_PERSPECTIVES.md ← Existing
├── data/
│   ├── prepare_seqgan_data.py          ← Existing
│   ├── normalize_labels.py             ← Existing
│   ├── audit_bias.py                   ← NEW (G4)
│   ├── multi_source_loader.py          ← NEW (G7-P1)
│   ├── tier_filter.py                  ← NEW (G7-P3)
│   ├── relex_dictionary.json           ← NEW (G2)
│   └── v2/                             ← NEW dataset directory
│       ├── train.csv
│       ├── val.csv
│       ├── test.csv
│       └── stratify_report.txt
├── src/
│   ├── tokenizer.py                    ← Existing
│   ├── generator.py                    ← Sửa: add ConditionalGeneratorLSTM
│   ├── discriminator.py                ← Existing (giữ nguyên)
│   ├── env.py                          ← Existing
│   ├── reward.py                       ← Existing (giữ nguyên cho V1 backward compat)
│   ├── reward_v2.py                    ← NEW: CompositeReward
│   ├── waf_oracle.py                   ← NEW (G1)
│   ├── custom_rules.py                 ← NEW (G1)
│   ├── ast_tracker.py                  ← NEW (G2)
│   ├── db_sandbox.py                   ← NEW (G2)
│   ├── reward_cache.py                 ← NEW
│   ├── rollout.py                      ← Existing
│   ├── baseline.py                     ← Existing
│   ├── losses.py                       ← Existing
│   ├── scheduled_sampling.py           ← Existing
│   └── utils.py                        ← Existing
├── configs/
│   ├── seqgan_default.yaml             ← Existing (V1)
│   ├── seqgan_fast.yaml                ← Existing (V1)
│   └── seqgan_v2.yaml                  ← NEW
├── docker/
│   ├── modsec/
│   │   ├── Dockerfile                  ← NEW
│   │   └── docker-compose.yml          ← NEW
│   └── README.md                       ← NEW
├── eval/
│   ├── evaluate_v2.py                  ← NEW
│   ├── metrics/
│   │   ├── owasp_bypass.py             ← NEW
│   │   ├── db_execution.py             ← NEW
│   │   ├── ast_diversity.py            ← NEW
│   │   ├── ml_ids_evasion.py           ← NEW
│   │   └── relex_uniqueness.py         ← NEW
│   └── ids_classifier/
│       └── train_xgboost_ids.py        ← NEW (cho G6 metric)
├── baselines/                          ← Existing (giữ nguyên)
│   ├── template_based.py
│   ├── mle_lm_only.py
│   └── seqgan_vanilla.py
├── pretrain_mle.py                     ← Sửa: conditional support
├── pretrain_mle_v2.py                  ← NEW
├── train_adversarial.py                ← Existing (V1)
├── train_adversarial_v2.py             ← NEW
├── generate.py                         ← Existing
├── generate_v2.py                      ← NEW (conditional support)
├── evaluate.py                         ← Existing
├── run_full_pipeline.py                ← Existing (V1)
└── checkpoints/
    ├── mle_best.pt                     ← Existing (V1)
    ├── adv_final.pt                    ← Existing (V1)
    ├── error_based/                    ← Existing (V1)
    ├── error_based_entropy/            ← Existing (V1)
    └── v2/                             ← NEW
        ├── mle_best.pt
        ├── adv_warmup.pt
        ├── adv_main.pt
        └── adv_refined.pt
```

---

## 13. Lưu ý cuối

### 13.1 Backward Compatibility

V2 không xóa V1. Tất cả file mới có suffix `_v2` hoặc trong subdirectory `v2/`. V1 vẫn chạy được bằng `train_adversarial.py`.

### 13.2 Checkpoint từ V1

MLE pretrain của V1 (`mle_best.pt`, val_ppl=1.70) **không trực tiếp dùng được cho V2** vì:
- V2 có conditional embedding (architecture khác)
- V2 có thể có vocab khác (nếu P2 partial de-lex)

**Lựa chọn:** Init token embedding của V2 từ V1 weight (partial transfer); train type embedding từ random.

### 13.3 Compute Requirements

- GPU: 1× RTX 3060+ với ≥ 8GB VRAM
- RAM: 16GB+ (reward cache 100k entries)
- Disk: 10GB cho Docker images + checkpoints + logs
- Network: ModSecurity Docker localhost — không cần internet sau setup

### 13.4 Rollback Plan

Nếu V2 fail (kết quả tệ hơn V1 hoặc compute không đủ):
1. Document failure mode trong `timeline/V2_POSTMORTEM.md`
2. Fallback về V1 với chỉ G7 (multi-source data) — improvement nhỏ nhưng đảm bảo
3. Hoặc thử Conditional SeqGAN (Chowdhary 2023 reference) như V2.5

---

*File này specify approach V2 toàn diện. Để execute, xem `EXECUTION_PLAYBOOK.md`.*
*Tham chiếu chi tiết: `timeline/DEEP_ANALYSIS_10_PERSPECTIVES.md` cho lý luận khoa học.*
