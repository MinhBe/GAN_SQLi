# MODEL ARCHITECTURE — VISUAL REFERENCE
# Conditional SeqGAN V2 — SQLi Generation

> Dùng file này để vẽ lại mô hình trong draw.io / Figma / PowerPoint / Miro.
> Mỗi box = 1 layer. Số trong ngoặc [ ] = shape tensor tại điểm đó.
> Tất cả tham số đều là số thực từ codebase, không ước lượng.

---

## 0. BẢNG MÀU VẼ DIAGRAM

```
  Generator (G)     → BG: #E3F2FD   Border: #2196F3  (xanh dương nhạt)
  Discriminator (D) → BG: #FFF3E0   Border: #E65100  (cam nhạt)
  Reward Oracle     → BG: #E8F5E9   Border: #2E7D32  (xanh lá nhạt)
  REINFORCE Loop    → BG: #F3E5F5   Border: #7B1FA2  (tím nhạt)
  Data flow arrow   → Màu: #1B2A4A  Dày: 2px
  Dimension label   → Màu: #C62828  Font: Consolas   (đỏ, in đậm kích thước)
  Gate (×)          → Màu: #E65100  Hình: ◇ diamond
  Concat (+)        → Màu: #2196F3  Hình: ⊕ circle-plus
```

---

## 1. SƠ ĐỒ TỔNG QUAN — BIG PICTURE

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONDITIONAL SeqGAN V2 — FULL SYSTEM                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

 TRAINING DATA                    GENERATOR (G)                 FAKE SEQUENCES
 ┌─────────────┐                  ┌───────────────────┐         ┌─────────────┐
 │ 17,821 SQLi │                  │  LSTM × 3 layers  │────────→│ 64 payloads │
 │ 4 types     │──attack_type_id→ │  512 hidden dim   │         │ length ≤ 80 │
 │ 89 vocab    │                  │  89 vocab out     │         └──────┬──────┘
 └─────────────┘                  └───────────────────┘                │
        │                                   ↑                          │
        │ real sequences                    │                    ┌─────┴──────┐
        │                          REINFORCE│                    │            │
        ↓                          gradient │              ┌─────▼──────┐  ┌──▼─────┐
 ┌─────────────┐                  ┌─────────┴─────────┐   │   TEXT CNN  │  │ REWARD │
 │DISCRIMINATOR│←── real+fake ───→│ advantage=r−EMA_r │   │    (D)      │  │ ORACLE │
 │  TextCNN    │                  │ ∇L=−logp×advantage│   │ scalar score│  │ STACK  │
 │ scalar score│                  └───────────────────┘   └─────────────┘  └──┬─────┘
 └─────────────┘                                                               │
                                                                        r ∈ [−1, +1]
                                                                               │
                                                                  ┌────────────┼────────────┐
                                                              SQL  │       DB   │    WAF     │
                                                             Parse │     Sandbox│   Oracle  │
                                                                   │            │            │
                                                                Custom │    AST │  Overlap  │
                                                                Rules  │ Tracker│  Penalty  │
```

---

## 2. GENERATOR (G) — LAYER BY LAYER

### 2A. Một bước sinh token (time step t)

```
INPUTS (tại bước t)
───────────────────────────────────────────────────────────────────────────────

 attack_type_id                      token_{t-1}
 (scalar: 0, 1, 2, hoặc 3)          (scalar: 0..88)
        │                                   │
        ▼                                   ▼
┌───────────────────┐            ┌──────────────────────┐
│  TYPE EMBEDDING   │            │   TOKEN EMBEDDING    │
│                   │            │                      │
│  Look-up table    │            │  Look-up table       │
│  shape: [4 × 32]  │            │  shape: [89 × 256]   │
│                   │            │                      │
│  4 attack types   │            │  89 vocab tokens     │
│  32-dim per type  │            │  256-dim per token   │
└────────┬──────────┘            └──────────┬───────────┘
         │                                  │
         │  [32]                            │  [256]
         └──────────────────┬───────────────┘
                            │
                           [⊕]  CONCATENATE
                            │
                         [288]  ← input vector mỗi step
                            │
                            ▼
```

```
LSTM LAYERS (batch_first=True, dropout=0.2 giữa các layer)
───────────────────────────────────────────────────────────────────────────────

  HIDDEN STATE (latent space) từ step trước:
  h_{t-1}: [batch × 3 × 512]   ← 3 layer × 512 dim mỗi layer
  c_{t-1}: [batch × 3 × 512]   ← cell state tương ứng
  (tổng latent dim = 3,072 per sample)


  x_t [batch × 288]
        │
        │  input_size = 288
        ▼
  ┌─────────────────────────────────────────────────────┐
  │                  LSTM LAYER 1                       │
  │                                                     │
  │   input_size  : 288                                 │
  │   hidden_size : 512                                 │
  │   Parameters  : 4 × (288+512) × 512 = 1,638,400    │
  │                                                     │
  │   W_ih: [4×512 × 288]  W_hh: [4×512 × 512]         │
  │   Gates: i, f, g, o (input, forget, gate, output)  │
  │                                                     │
  │   dropout(0.2) on output before next layer          │
  └─────────────────────┬───────────────────────────────┘
                        │ output: [batch × 512]
                        │
  ┌─────────────────────────────────────────────────────┐
  │                  LSTM LAYER 2                       │
  │                                                     │
  │   input_size  : 512                                 │
  │   hidden_size : 512                                 │
  │   Parameters  : 4 × (512+512) × 512 = 2,097,152    │
  │                                                     │
  │   dropout(0.2) on output before next layer          │
  └─────────────────────┬───────────────────────────────┘
                        │ output: [batch × 512]
                        │
  ┌─────────────────────────────────────────────────────┐
  │                  LSTM LAYER 3                       │
  │                                                     │
  │   input_size  : 512                                 │
  │   hidden_size : 512                                 │
  │   Parameters  : 4 × (512+512) × 512 = 2,097,152    │
  │                                                     │
  │   (no dropout on last layer)                        │
  └─────────────────────┬───────────────────────────────┘
                        │ h_t: [batch × 512]
                        │ c_t: [batch × 512]
                        │  → saved as new hidden state
                        ▼
```

```
OUTPUT HEAD
───────────────────────────────────────────────────────────────────────────────

  h_t [batch × 512]
        │
        ▼
  ┌───────────────────────────────────┐
  │   LINEAR (no bias optional)       │
  │   in : 512                        │
  │   out: 89  ← vocab size           │
  │   Parameters: 512 × 89 = 45,568   │
  └──────────────┬────────────────────┘
                 │ logits: [batch × 89]
                 │
                 ▼
  ┌───────────────────────────────────┐
  │   SOFTMAX (dim=-1)               │
  │   → probability over 89 tokens   │
  └──────────────┬────────────────────┘
                 │ probs: [batch × 89]
                 │
        ┌────────┴────────┐
        │                 │
   TRAINING          INFERENCE
 log_prob             argmax
 (for REINFORCE)    (greedy) or
                  temperature sample
                    (temp=1.1 V3)
                        │
                   token_t (scalar)
```

### 2B. Toàn bộ chuỗi (T = 80 steps)

```
  START token                    attack_type (cố định suốt chuỗi)
      │                                    │
      ▼                                    │
  ┌───────┐                               [32]
  │ token │                                │
  │  [0]  │─[256]─────────────────────────⊕──[288]─→ LSTM → h₁,c₁ → Linear → Softmax → token₁
  └───────┘                                                    ↓
                                                        h₁,c₁ (latent state)
                                                               │
  ┌────────┐                                                   │
  │ token₁ │─[256]─────────────────────────⊕──[288]─→ LSTM → h₂,c₂ → Linear → Softmax → token₂
  └────────┘                                                   ↓
                                                               ...
                                                               │
  ┌────────┐
  │token₇₉│─[256]─────────────────────────⊕──[288]─→ LSTM → h₈₀,c₈₀ → Linear → Softmax → token₈₀/EOS
  └────────┘

  Generated sequence: [token₁, token₂, ..., token₈₀]
  De-tokenize → payload string → Re-lex → actual SQL string → Reward Oracle
```

### 2C. Latent Space — LSTM Hidden States

```
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                    LATENT SPACE của Generator                        ║
  ╠═══════════════════════════════════════════════════════════════════════╣
  ║                                                                       ║
  ║  Không có z ~ N(0,I) như VAE hay GAN thông thường.                  ║
  ║  "Latent" của SeqGAN = LSTM Hidden State (h_t, c_t)                 ║
  ║                                                                       ║
  ║  Kích thước:                                                          ║
  ║    h_t : [batch × num_layers × hidden_size]                          ║
  ║         = [64    ×     3     ×    512    ]                           ║
  ║         = 98,304 values per batch                                    ║
  ║                                                                       ║
  ║    c_t : [batch × num_layers × hidden_size]                          ║
  ║         = [64    ×     3     ×    512    ]                           ║
  ║         = 98,304 values per batch                                    ║
  ║                                                                       ║
  ║  Per sample latent dim = 3 × 512 × 2 = 3,072                        ║
  ║                                                                       ║
  ║  Conditioning:                                                        ║
  ║                                                                       ║
  ║   type_embedding [32-dim] được concat vào input MỖI BƯỚC             ║
  ║   → Tạo 4 vùng phân tách trong không gian ẩn:                        ║
  ║                                                                       ║
  ║     h-space                                                           ║
  ║       │                                                               ║
  ║       │  ●●●  error_based   (type_id=0, embed=[e₀₁,e₀₂,...,e₀₃₂])   ║
  ║       │   ○○  boolean_blind (type_id=1, embed=[e₁₁,e₁₂,...,e₁₃₂])   ║
  ║       │   ▲▲  time_blind    (type_id=2, embed=[e₂₁,e₂₂,...,e₂₃₂])   ║
  ║       │   ■■  union_based   (type_id=3, embed=[e₃₁,e₃₂,...,e₃₃₂])   ║
  ║       └─────────────────────────────────────────────────────→        ║
  ║                                                                       ║
  ║  h₀ = 0 (zero init) → "prior" trung tính, type_embed là signal       ║
  ║  Sau MLE pretrain: h-space học phân phối SQLi trong tập train        ║
  ║  Sau adversarial: h-space học phân phối bypass WAF                   ║
  ╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 3. DISCRIMINATOR (D) — TextCNN

```
INPUT: Token sequence (length T=80)
───────────────────────────────────────────────────────────────────────────────

  token_ids: [batch × 80]   ← sequence of integers 0..88
        │
        ▼
  ┌──────────────────────────────────┐
  │        EMBEDDING                 │
  │  Look-up: [89 × 128]            │
  │  → out: [batch × 80 × 128]      │
  └────────────────┬─────────────────┘
                   │  [batch × 80 × 128]
                   │  Transpose → [batch × 128 × 80]
                   │  (Conv1D expects: [batch × channels × length])
                   │
                   ▼
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼

CONV BRANCH 1   CONV BRANCH 2   CONV BRANCH 3
kernel_size=3   kernel_size=4   kernel_size=5
───────────────────────────────────────────────────────────────────────────────

┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Conv1D     │  │  Conv1D     │  │  Conv1D     │
│             │  │             │  │             │
│ in :  128   │  │ in :  128   │  │ in :  128   │
│ out:  128   │  │ out:  128   │  │ out:  128   │
│ k  :    3   │  │ k  :    4   │  │ k  :    5   │
│ pad: k//2=1 │  │ pad: k//2=2 │  │ pad: k//2=2 │
│             │  │             │  │             │
│ [b×128×80]  │  │ [b×128×80]  │  │ [b×128×80]  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
      ReLU             ReLU             ReLU
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Adaptive    │  │ Adaptive    │  │ Adaptive    │
│ MaxPool1D   │  │ MaxPool1D   │  │ MaxPool1D   │
│             │  │             │  │             │
│ output_size │  │ output_size │  │ output_size │
│   = 1       │  │   = 1       │  │   = 1       │
│             │  │             │  │             │
│ squeeze(-1) │  │ squeeze(-1) │  │ squeeze(-1) │
│ → [b × 128] │  │ → [b × 128] │  │ → [b × 128] │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │  CONCAT (dim=1)
                        ▼
                  [batch × 384]
                        │
                        ▼
               ┌────────────────┐
               │   LINEAR       │
               │                │
               │  in : 384      │
               │  out:   1      │
               │  bias: True    │
               └────────┬───────┘
                        │ [batch × 1]
                        │  squeeze → scalar
                        ▼
               score (WGAN-style, NO sigmoid)
               Positive = "real-looking"
               Negative = "fake-looking"

───────────────────────────────────────────────────────────────────────────────
  NOTE: D chỉ đóng góp 10-20% vào reward signal trong V2.
  Phần lớn reward đến từ Reward Oracle Stack (bên dưới).
───────────────────────────────────────────────────────────────────────────────
```

---

## 4. MONTE CARLO ROLLOUT

```
Mục đích: Tính Q(s_t, a_t) = reward kỳ vọng cho token tại bước t

───────────────────────────────────────────────────────────────────────────────

Giả sử chuỗi đang sinh đến bước t = 5 / 80:

  [ tok₁, tok₂, tok₃, tok₄, tok₅ ]  ← đã sinh
  [  ?,    ?,    ?,   ...         ]  ← chưa sinh (75 bước còn lại)

Monte Carlo: từ trạng thái này, chạy G thêm K=16 lần đến hết chuỗi:

  Rollout 1:  [tok₁..tok₅, r₁₆, r₁₇, ..., rT]  → reward oracle → r₁
  Rollout 2:  [tok₁..tok₅, r₂₆, r₂₇, ..., rT]  → reward oracle → r₂
  ...
  Rollout 16: [tok₁..tok₅, r₁₆₆,r₁₆₇,..., rT]  → reward oracle → r₁₆

                          ↓
               Q(s₅, a₅) = (r₁ + r₂ + ... + r₁₆) / 16

───────────────────────────────────────────────────────────────────────────────

Tổng reward computation per step (phase adversarial):
  80 steps × K=16 rollouts × batch=64 = 81,920 reward calls per training step
  WAF cache hit rate ~97% → thực tế ~2,458 unique WAF calls per step
  WAF latency 30-50ms → ~73-123s WAF time per step (với cache)

Minh họa timeline sinh chuỗi + rollout:

  t=1   t=2   t=3  ...  t=80
  ┌─┐   ┌─┐   ┌─┐       ┌─┐
  │A│──→│B│──→│C│──→...─│Z│  ← chuỗi đang sinh (forward pass)
  └─┘   └─┘   └┬┘       └─┘
               │
               │ tại t=3, dừng lại
               │ chạy K=16 rollouts từ đây
               ↓
  ┌─┐   ┌─┐   ┌─┐   ┌────────────────────────────────────┐
  │A│──→│B│──→│C│──→│ rand₁,rand₂,...,randT → Oracle→r₁  │
  │A│──→│B│──→│C│──→│ rand₁,rand₂,...,randT → Oracle→r₂  │
  ...                ...
  │A│──→│B│──→│C│──→│ rand₁,rand₂,...,randT → Oracle→r₁₆│
  └─┘   └─┘   └─┘   └────────────────────────────────────┘
                            ↓
                   Q(s₃,a₃) = mean(r₁..r₁₆)
                            ↓
               Đây là reward dùng trong REINFORCE
               để cập nhật weight của G tại bước t=3
```

---

## 5. REWARD ORACLE STACK — 5 Stages

```
INPUT: payload string (sau re-lex, ví dụ: "1' OR sleep(5)--")
───────────────────────────────────────────────────────────────────────────────

                     payload string
                           │
          ┌────────────────▼────────────────┐
          │         STAGE 0                 │
          │    SQL PARSER GATE              │
          │                                 │
          │  sqlparse.parse(               │
          │    "SELECT * FROM t WHERE       │
          │     id=" + payload             │
          │  )                              │
          │  → fallback: sqlglot            │
          │                                 │
          │  pass_score = 0 or 1           │
          └────────────┬────────────────────┘
                       │
          FAIL (0) ────┤──── PASS (1)
             │                  │
             ▼                  ▼
         r = -1.0          STAGE 1 ↓
         (STOP)
                   ┌───────────────────────────┐
                   │      DB SANDBOX           │
                   │                           │
                   │  SQLite in-memory         │
                   │  Schema: dummy(id INT,    │
                   │          name TEXT)       │
                   │                           │
                   │  Execute:                 │
                   │  "SELECT * FROM dummy     │
                   │   WHERE id={payload}"    │
                   │                           │
                   │  exec_score = 0 or 1     │
                   └────────────┬──────────────┘
                                │
               FAIL (0) ────────┤──── PASS (1)
                  │                     │
                  ▼                     ▼
              r = -0.5            STAGE 2 ↓

                      ┌─────────────────────────────────────┐
                      │         WAF ORACLE                  │
                      │                                     │
                      │  POST http://localhost:8080          │
                      │  ?id={payload}                      │
                      │  X-ModSec-Paranoia: 2               │
                      │                                     │
                      │  → anomaly_score (0 .. 999)         │
                      │  → blocked (True/False)             │
                      │  threshold = 5 (PL2)                │
                      │                                     │
                      │  Boundary reward:                   │
                      │                                     │
                      │  if score < 5:                      │
                      │    r_waf = 1 - (5-score)/5          │
                      │                                     │
                      │  score=0 → r_waf = 0.0              │
                      │  score=1 → r_waf = 0.2              │
                      │  score=2 → r_waf = 0.4              │
                      │  score=3 → r_waf = 0.6              │
                      │  score=4 → r_waf = 0.8  ← đây tốt  │
                      │                                     │
                      │  if score ≥ 5: r_waf = -0.5 (block)│
                      └─────────────────┬───────────────────┘
                                        │ r_waf
                                        ▼
                      ┌─────────────────────────────────────┐
                      │      CUSTOM RULES ENGINE            │
                      │                                     │
                      │  5 rules (each returns True/False): │
                      │                                     │
                      │  R1: ≥1 SQLi keyword               │
                      │      (union, select, or 1, sleep...)│
                      │                                     │
                      │  R2: ≥1 quoting/comment            │
                      │      (' " -- /* */ # ;)            │
                      │                                     │
                      │  R3: len(payload.strip()) ≥ 5      │
                      │                                     │
                      │  R4: NOT trivial                   │
                      │      (not fullmatch [\w\s]+)       │
                      │                                     │
                      │  R5: ≥1 operator or query kw       │
                      │      ([=<>] | union | select)      │
                      │                                     │
                      │  r_custom = pass_count / 5          │
                      │  range: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]│
                      └─────────────────┬───────────────────┘
                                        │ r_custom
                                        ▼
                      ┌─────────────────────────────────────┐
                      │     AST FINGERPRINT TRACKER         │
                      │                                     │
                      │  1. Parse payload → AST (sqlparse) │
                      │  2. Extract subtrees depth=3        │
                      │  3. Hash each subtree              │
                      │  4. fp = frozenset(hashes)         │
                      │                                     │
                      │  novelty = 1 - |fp ∩ cache| / |fp| │
                      │                                     │
                      │  novelty=1.0 → hoàn toàn mới       │
                      │  novelty=0.0 → đã thấy rồi         │
                      │                                     │
                      │  cache: max 10,000 fingerprints     │
                      │  reset every 1000 steps (Phase 3)  │
                      └─────────────────┬───────────────────┘
                                        │ novelty
                                        ▼
          ┌─────────────────────────────────────────────────────┐
          │                COMPOSITE REWARD                     │
          │                                                     │
          │  overlap_penalty = max(0, r_waf - r_custom)         │
          │                   [if r_waf > 0, else 0]           │
          │                                                     │
          │  ┌─────────────────────────────────────────────┐   │
          │  │  r = syntax_gate                            │   │
          │  │      × exec_gate                            │   │
          │  │      × (  w_owasp   × r_waf                │   │
          │  │          + w_custom  × r_custom             │   │
          │  │          + w_div     × novelty              │   │
          │  │          - w_overlap × overlap_penalty )    │   │
          │  └─────────────────────────────────────────────┘   │
          │                                                     │
          │  WEIGHTS PER PHASE:                                 │
          │  ┌──────────────┬─────────┬─────────┬──────────┐   │
          │  │ Component    │ Warmup  │ Advers. │ Refine   │   │
          │  ├──────────────┼─────────┼─────────┼──────────┤   │
          │  │ w_owasp      │  0.0    │  0.4    │   0.3    │   │
          │  │ w_custom     │  0.7    │  0.3    │   0.1    │   │
          │  │ w_diversity  │  0.0    │  0.2    │   0.5    │   │
          │  │ w_overlap    │  0.0    │  0.1    │   0.1    │   │
          │  └──────────────┴─────────┴─────────┴──────────┘   │
          │                                                     │
          │  OUTPUT: r ∈ [-1.0, +1.0]                          │
          └─────────────────────────────────────────────────────┘
```

---

## 6. TRAINING LOOP — REINFORCE

```
ONE TRAINING STEP (phase: adversarial)
───────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 1. SAMPLE batch of attack_type_ids from training distribution           │
  │    attack_types: [0,1,2,3,...] shape [64]                              │
  └──────────────────────────────────────────┬──────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 2. GENERATE sequences (G forward, autoregressive, temperature=1.1 V3)   │
  │                                                                         │
  │    For t = 1..80:                                                       │
  │      logits_t, h_t = G(token_{t-1}, attack_type, h_{t-1})             │
  │      probs_t = softmax(logits_t / temperature)                         │
  │      token_t ~ Categorical(probs_t)                                    │
  │      log_prob_t = log(probs_t[token_t])                                │
  │                                                                         │
  │    fake_seqs:   [64 × 80] token ids                                    │
  │    log_probs:   [64 × 80] log probabilities                            │
  └──────────────────────────────────────────┬──────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 3. MONTE CARLO ROLLOUT → rewards for each position                      │
  │                                                                         │
  │    For each position t = 1..80:                                         │
  │      Run K=16 completions from position t                              │
  │      Decode each completion → actual SQL (after re-lex)                │
  │      Call Reward Oracle → r_k                                           │
  │      Q_t = mean(r_1..r_16)                                             │
  │                                                                         │
  │    rewards: [64 × 80]  ← Q values per position                         │
  └──────────────────────────────────────────┬──────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 4. COMPUTE ADVANTAGES (V2: batch mean; V3: EMA baseline)                │
  │                                                                         │
  │    V2 (FAILED — root cause of mode collapse):                           │
  │      baseline = rewards.mean()    ← same value for all in batch        │
  │      advantages = rewards - baseline  ← ≈ 0 when all rewards equal     │
  │                                                                         │
  │    V3 (FIX):                                                            │
  │      ema_baseline = 0.9 × ema_baseline + 0.1 × rewards.mean()         │
  │      advantages = rewards - ema_baseline  ← persistent signal          │
  │      advantages /= (advantages.std() + 1e-8)  ← normalize             │
  └──────────────────────────────────────────┬──────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 5. GENERATOR LOSS (REINFORCE + Entropy Bonus V3)                        │
  │                                                                         │
  │    reinforce_loss = -(log_probs × advantages).mean()                   │
  │                                                                         │
  │    [V3 addition]:                                                       │
  │    entropy = -(probs × log_probs).sum(dim=-1).mean()  ← per vocab      │
  │    g_loss = reinforce_loss - entropy_coeff × entropy                   │
  │                                                                         │
  │    entropy_coeff schedule:                                              │
  │      warmup:      0.05                                                  │
  │      adversarial: 0.03                                                  │
  │      refinement:  0.01                                                  │
  └──────────────────────────────────────────┬──────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 6. DISCRIMINATOR LOSS (WGAN, 1-5 D steps per G step)                   │
  │                                                                         │
  │    real_score = D(real_seqs)  ← from training data                     │
  │    fake_score = D(fake_seqs.detach())                                  │
  │    d_loss = fake_score.mean() - real_score.mean()   ← Wasserstein      │
  │                                                                         │
  │    Gradient penalty (WGAN-GP):                                         │
  │    interpolated = α×real + (1-α)×fake  (α ~ Uniform[0,1])             │
  │    gp = (‖∇D(interpolated)‖₂ - 1)²                                    │
  │    d_loss += lambda_gp × gp                                            │
  └──────────────────────────────────────────┬──────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 7. OPTIMIZER STEP                                                       │
  │                                                                         │
  │    G optimizer: Adam(β₁=0.5, β₂=0.999)                                │
  │    D optimizer: Adam(β₁=0.5, β₂=0.999)                                │
  │                                                                         │
  │    lr_g schedule:                                                       │
  │      MLE pretrain:  1e-3                                                │
  │      Warmup:        1e-4                                                │
  │      Adversarial:   5e-5                                                │
  │      Refinement:    1e-5                                                │
  │                                                                         │
  │    lr_d = 1e-4 (constant through adversarial + refinement)             │
  │    grad_clip: 1.0 (both G and D)                                       │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 7. METRICS — VISUAL FORMULAS

### 7A. Self-BLEU-3 (Mode Collapse Detector)

```
  Tập N payloads: {y₁, y₂, y₃, ..., yₙ}   N = 500 hoặc 1,000

  Với mỗi payload yᵢ:
    Reference set = {y₁, ..., yₙ} \ {yᵢ}
    ┌──────────────────────────────────────┐
    │ BLEU-3(yᵢ | refs) = BP × exp(       │
    │   (1/3) × Σₙ₌₁³ log(pₙ(yᵢ, refs)) │
    │ )                                    │
    │                                      │
    │ pₙ = n-gram precision                │
    │ BP = brevity penalty                 │
    └──────────────────────────────────────┘

  Self-BLEU-3 = (1/N) × Σᵢ BLEU-3(yᵢ | refs\{yᵢ})

  ┌──────────────────────────────────────────────────────┐
  │ Thang đo:                                            │
  │                                                      │
  │  0.0 ──────────── 0.60 ────── 0.85 ───── 0.99 ─ 1.0 │
  │  │                 │           │           │         │
  │ Hoàn toàn         Target     V1 MLE     V1 SeqGAN   │
  │ khác nhau         V2         0.9833     0.9894 ❌    │
  │ (impossible)      <0.70                 Mode collapse│
  └──────────────────────────────────────────────────────┘

  Đơn vị đo: trên de-lex space (token sequences)
  Confound: de-lex làm nhiều payload khác → cùng token sequence
  → Cần đo thêm trên re-lex space (surface diversity)
```

### 7B. AST Entropy (Structural Diversity)

```
  1. Parse N payloads → N AST trees (sqlparse)
  2. Extract subtrees ở depth=3 từ mỗi tree
  3. Hash mỗi subtree → fingerprint integer
  4. Đếm tần suất mỗi fingerprint: f(fᵢ)
  5. Tính Shannon entropy:

  ┌──────────────────────────────────────────┐
  │                                          │
  │  H = - Σᵢ p(fᵢ) × log(p(fᵢ))           │
  │                                          │
  │  p(fᵢ) = f(fᵢ) / Σⱼ f(fⱼ)             │
  │  đơn vị: nats (log tự nhiên)            │
  │                                          │
  └──────────────────────────────────────────┘

  Thang đo (nats):

  0.0 ──── 1.0 ──── 2.0 ──── 3.0 ──── 4.0 ──── 5.0+
   │        │        │        │        │         │
  1 unique  Low    V2 step  V2 MLE  Target V3  High
  payload   div    1000     3.083   >3.0 ✅    diversity
           collapse 2.417
                    ↓
           V2 step2000+: frozen at 2.5649 (mode collapse)
```

### 7C. Novelty Score (Real-time trong Reward)

```
  payload p
      │
      ▼
  AST fingerprint:  fp(p) = frozenset(hash(subtree) for subtree in AST(p))
      │
      │  cache C = set of all fp seen so far (max 10,000 fingerprints)
      │
      ▼
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  overlap = |fp(p) ∩ C| / |fp(p)|                    │
  │                                                      │
  │  novelty = 1 - overlap                               │
  │                                                      │
  │  novelty = 1.0 → payload có cấu trúc SQL hoàn toàn  │
  │                   mới, chưa trong cache              │
  │  novelty = 0.0 → tất cả subtree đã thấy rồi         │
  │                   (mode collapse signal)             │
  └──────────────────────────────────────────────────────┘
```

### 7D. 5-Metric Composite Score

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  OWASP bypass rate  ─── weight 0.30 ─── r₁ ∈ [0,1]               │
  │  DB execution rate  ─── weight 0.25 ─── r₂ ∈ [0,1]               │
  │  AST entropy        ─── weight 0.20 ─── r₃/5.0 ∈ [0,1]           │
  │  ML-IDS evasion     ─── weight 0.15 ─── r₄ ∈ [0,1]               │
  │  Re-lex uniqueness  ─── weight 0.10 ─── r₅ ∈ [0,1]               │
  │                                                                     │
  │  composite = 0.30r₁ + 0.25r₂ + 0.20(r₃/5) + 0.15r₄ + 0.10r₅    │
  │                                                                     │
  │  [Weights sum to 1.00]                                             │
  └─────────────────────────────────────────────────────────────────────┘

  RADAR CHART VALUES (mỗi trục normalize 0→1):

                    OWASP bypass
                       /  \
                      /    \
                     /  V3  \
                    / target  \
  Re-lex ─────────●─────────●───── DB exec
  unique          /           \
                 /             \
                ●   V2step1000  ●
               /  ●  V2 MLE     \
  ML-IDS ─────●────────────────●── AST entropy
  evasion

  V2_MLE:       [0.00, 0.03, 0.62, 0.03, 0.66]
  V2_step1000★: [0.00, 1.00, 0.48, 0.39, 0.01]
  V3_target:    [0.60, 0.80, 0.70, 0.50, 0.70]
```

### 7E. WAF Boundary Reward Curve

```
  r_waf
  1.0 ┤                                          ●  score=4
  0.8 ┤                                    ●
  0.6 ┤                              ●
  0.4 ┤                        ●
  0.2 ┤                  ●
  0.0 ┤            ●score=0
      ┤
 -0.5 ┤──────────────────────────────────────────────● blocked (score≥5)
      └───┬────┬────┬────┬────┬────┬────┬────┬────┬──→ anomaly_score
          0    1    2    3    4    5    7    10   15   999

  Công thức:
  r_waf = 1 - (threshold - score) / threshold   [if score < threshold=5]
  r_waf = -0.5                                   [if score ≥ threshold]

  Tại sao không binary (0/1)?
  → score=0 (easy bypass) nhận reward thấp hơn score=4 (sát ranh giới)
  → Buộc G tìm bypass khó, tạo diversity tự nhiên
```

---

## 8. PARAMETER REFERENCE CARD

```
╔════════════════════════════════════════════════════════════════════╗
║               PARAMETER REFERENCE — CONDITIONAL SeqGAN V2         ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  DATASET                                                           ║
║  ─────────────────────────────────────────────────────────────    ║
║  sqli rows         : 17,821                                        ║
║  benign rows       : 19,669                                        ║
║  vocab size        : 89 tokens  (V2; V1 had 134)                  ║
║  max sequence len  : 80 tokens                                     ║
║  attack types      : 4  (error_based, boolean_blind,               ║
║                          time_blind, union_based)                  ║
║  confidence tiers  : gold(≥0.95) 60% · silver(0.80-0.94) 25%      ║
║                      bronze(<0.80) 15%                             ║
║                                                                    ║
║  GENERATOR (G)                                                     ║
║  ─────────────────────────────────────────────────────────────    ║
║  type: ConditionalGeneratorLSTM                                    ║
║  token_embed_dim   : 256                                           ║
║  type_embed_dim    :  32                                           ║
║  lstm_input_size   : 256+32 = 288                                  ║
║  lstm_hidden_size  : 512                                           ║
║  lstm_num_layers   :   3                                           ║
║  dropout           : 0.2 (between layers)                          ║
║  head              : Linear(512 → 89)                              ║
║                                                                    ║
║  Total G params:                                                   ║
║    token_embed  : 89 × 256         =    22,784                    ║
║    type_embed   :  4 × 32          =       128                    ║
║    lstm_layer1  : 4×(288+512)×512  = 1,638,400                    ║
║    lstm_layer2  : 4×(512+512)×512  = 2,097,152                    ║
║    lstm_layer3  : 4×(512+512)×512  = 2,097,152                    ║
║    head linear  : 512 × 89         =    45,568                    ║
║                                   ─────────────                   ║
║    TOTAL G      :                   5,901,184 params              ║
║                                                                    ║
║  DISCRIMINATOR (D)                                                 ║
║  ─────────────────────────────────────────────────────────────    ║
║  type: DiscriminatorCNN (TextCNN, WGAN-style)                     ║
║  embed_dim         : 128                                           ║
║  kernel_sizes      : [3, 4, 5]                                     ║
║  num_filters       : 128 per kernel                                ║
║  fc_in             : 128×3 = 384                                   ║
║  fc_out            : 1  (scalar, no sigmoid)                       ║
║                                                                    ║
║  Total D params:                                                   ║
║    embed        : 89 × 128         =    11,392                    ║
║    conv_k3      : 128×128×3        =    49,152                    ║
║    conv_k4      : 128×128×4        =    65,536                    ║
║    conv_k5      : 128×128×5        =    81,920                    ║
║    fc           : 384 × 1          =       384                    ║
║                                   ─────────────                   ║
║    TOTAL D      :                     208,384 params              ║
║                                                                    ║
║  TRAINING                                                          ║
║  ─────────────────────────────────────────────────────────────    ║
║  batch_size        : 64                                            ║
║  MC rollout K      : 16                                            ║
║  total steps       : 20,000 (warm:2k + adv:13k + refine:5k)       ║
║  optimizer_G       : Adam(β₁=0.5, β₂=0.999)                       ║
║  optimizer_D       : Adam(β₁=0.5, β₂=0.999)                       ║
║  grad_clip         : 1.0                                           ║
║  reward_cache_size : 100,000 entries (LRU)                         ║
║                                                                    ║
║  lr schedule:                                                      ║
║    MLE pretrain    : 1e-3 (cosine decay, 10 epochs)               ║
║    Warmup (G)      : 1e-4                                          ║
║    Adversarial (G) : 5e-5                                          ║
║    Refinement (G)  : 1e-5                                          ║
║    D (all phases)  : 1e-4                                          ║
║                                                                    ║
║  V3 ADDITIONS (verified 2026-05-12)                                ║
║  ─────────────────────────────────────────────────────────────    ║
║  entropy_coeff warmup  : 0.05                                      ║
║  entropy_coeff advers. : 0.03                                      ║
║  entropy_coeff refine  : 0.01                                      ║
║  EMA baseline α        : 0.95 ema + 0.05 batch_mean               ║
║  temperature warmup    : 1.2                                        ║
║  temperature advers.   : 1.1                                        ║
║  temperature refine    : 1.0                                        ║
║                                                                    ║
║  TRAINING RESULTS — V3 FINAL (2026-05-12)                         ║
║  ─────────────────────────────────────────────────────────────    ║
║  MLE pretrain val_ppl  : 1.27   (V1: 1.70)                        ║
║                                                                    ║
║  PRODUCTION MODEL: checkpoints/v3/adv_step2000.pt                 ║
║  (= end of warmup phase, before adversarial)                       ║
║                                                                    ║
║  composite score       : 0.471  (+133% vs MLE 0.202)              ║
║  DB execution rate     : 99.2%                                     ║
║  re-lex uniqueness     : 1.000  (V2 was 0.010 — FIXED)            ║
║  AST entropy           : 3.07   (target > 3.0 ACHIEVED)           ║
║  custom rules pass     : 94.6%                                     ║
║  OWASP bypass (WAF on) : 2.0%   (low — diversity prioritized)     ║
║  ML-IDS evasion        : 0%     (tradeoff vs V2's 31.4%)          ║
║  unique/batch (warmup) : 64/64  (V2 warmup: 1-2/64)               ║
║  cache hit rate        : 42%    (V2: 93%)                          ║
║                                                                    ║
║  V2 COMPARISON (step1000 best):                                    ║
║  composite  0.394 → V3: 0.471  (+20%)                             ║
║  relex      0.010 → V3: 1.000  (100× improvement)                 ║
║  AST-H      2.42  → V3: 3.07   (+27%)                             ║
║  ML-IDS     31.4% → V3: 0%     (tradeoff)                         ║
║                                                                    ║
║  NOTE: V3 step12000 (collapsed) has OWASP bypass=43.4%            ║
║  but relex_unique=0.008 → single payload repeated → not useful     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 9. VẼ LẠI BẰNG TOOL — HƯỚNG DẪN

### Cho draw.io / Figma / Lucidchart

```
Các shape cần dùng:
  ┌──────────┐
  │ Rectangle│  → Embedding layers, Linear, Full-connected
  └──────────┘  màu nền theo component (xem bảng màu đầu file)

  ┌──────────┐
  │ Rounded  │  → LSTM cells, Reward Oracle stages
  └──────────┘

  ◇             → Gate (×): syntax_gate, exec_gate
                  màu: #E65100

  ⊕             → Concatenate operations
                  màu: #2196F3

  ─────→        → Data flow, tensor dimensions viết trên arrow
                  font Consolas, màu #C62828

  ═════→        → Gradient flow (REINFORCE update)
                  dashed, màu #7B1FA2

Thứ tự vẽ (left to right):
  1. Attack type embedding (trái)
  2. Token embedding (trái)
  3. CONCAT ⊕
  4. LSTM Layer 1, 2, 3 (giữa, theo chiều dọc)
  5. Linear + Softmax (phải)
  6. MC Rollout box (dưới G)
  7. Reward Oracle Stack (phải ngoài cùng)
  8. REINFORCE arrow (từ Oracle về G, vòng lại)
  9. D (TextCNN) (phía dưới, màu cam)
```

### Prompt cho AI vẽ (Eraser.io / Mermaid / PlantUML)

```
Nếu dùng Eraser.io (cloud diagram tool), paste prompt này:

"Draw a neural network architecture diagram for a Conditional SeqGAN model
with the following components:
- Left: Token Embedding [89×256] and Type Embedding [4×32] concatenated to [288]
- Center: 3-layer LSTM with 512 hidden units each, dropout=0.2
- Right: Linear [512→89] + Softmax → token sampling
- Below G: Monte Carlo Rollout box with K=16 rollouts
- Far right: Reward Oracle Stack with 5 stages vertically:
  Stage 0: SQL Parser Gate → pass(1)/fail(0)
  Stage 1: DB Sandbox SQLite → exec(1)/error(0)
  Stage 2: WAF Oracle ModSecurity → anomaly_score → r_waf
  Stage 3: Custom Rules 5/5 → r_custom
  Stage 4: AST Fingerprint → novelty
  Stage 5: Composite multiply gates then weighted sum
- Bottom separate: TextCNN Discriminator with 3 parallel conv branches [k=3,4,5]
  each 128 filters → MaxPool → Concat [384] → Linear [384→1]
- REINFORCE arrow curving from Reward back to G weights
Color coding: G=blue, Oracle=green, D=orange, REINFORCE=purple"
```

---

## 10. KIỂM TRA HÌNH VẼ — CHECKLIST

```
Sau khi vẽ xong, kiểm tra:

  [ ] G input: 2 luồng riêng biệt vào (type_embed + token_embed)
  [ ] CONCAT trước LSTM (không phải add, không phải sum)
  [ ] 3 LSTM layers riêng biệt, có nhãn "dropout=0.2"
  [ ] h_t và c_t (hidden + cell state) được vẽ như latent space
  [ ] Linear head: 512 → 89 (không phải 512 → vocab kích thước khác)
  [ ] D TextCNN: 3 conv branches song song (không nối tiếp)
  [ ] D output: scalar (không có sigmoid)
  [ ] Reward Oracle: 5 stages nối tiếp, có gates ◇ tại Stage 0 và 1
  [ ] WAF boundary reward: curve (không phải binary step)
  [ ] REINFORCE arrow: từ reward ngược về G (không phải về D)
  [ ] Dimension labels: tất cả arrows có [shape] annotation
  [ ] Latent space: LSTM hidden state, dim = 3 × 512 = 1,536
```

---

*File này: C:\Projects\GAN_SQLi\SeqGAN_SQLi\MODEL_ARCHITECTURE_VIZ.md*
*Tham chiếu code: SeqGAN_SQLi/src/generator.py · discriminator.py · reward_v2.py*
*Số liệu thực nghiệm: timeline/V2_RESULTS.md · timeline/eval_report.json*
