# Guideline Định Hướng — SeqGAN SQLi (Revised)
**Ngày**: 2026-05-17  
**Kiến trúc**: SeqGAN framework (G + D + Reward) — giữ theo yêu cầu thesis  
**Thay đổi cốt lõi**: REINFORCE → Gumbel-Softmax trong Generator  
**Dựa trên**: Lessons learned V1→V4, phản hồi thầy Lâm 13/05, eval thực tế

---

## PHẦN 1 — VẤN ĐỀ GỐC RỄ CẦN GIẢI QUYẾT

### Tại sao V1–V4 collapse dù đã có 8 fixes

SeqGAN dùng REINFORCE để backprop reward signal từ Discriminator về Generator. Đây là vấn đề **cơ bản của REINFORCE với discrete tokens**, không phải bug có thể patch:

```
Cơ chế collapse (không thể tránh với REINFORCE):
  1. G tìm payload đạt reward 0.70 (ceiling của custom rules)
  2. Tất cả samples hội tụ về reward tương đương
  3. advantage = reward - baseline ≈ 0
  4. gradient = advantage × ∇log_π ≈ 0
  5. G không học thêm → freeze → lặp 1–2 payload mãi

V3 entropy reg chỉ làm chậm (~2500 steps thay vì ~1000).
V4 với 8 fixes đồng thời vẫn collapse theo cơ chế tương tự.
```

**Bằng chứng:**

| Version | Collapse tại | Unique/64 sau collapse | Biện pháp |
|---------|------------|----------------------|-----------|
| V1 | Step ~800 | 1–2/64 | Không có |
| V2 | Step ~2000 | 1–2/64 | Reward clipping |
| V3 | Step ~2500 | 6–7/64 | Entropy reg + EMA + Temp |
| V4 | Step 750 (crash) | N/A | 8 fixes đồng thời |

**Kết luận**: Thay REINFORCE bằng gradient estimator tốt hơn — không thay đổi framework SeqGAN.

---

## PHẦN 2 — HƯỚNG MỚI: SEQGAN + GUMBEL-SOFTMAX

### 2.1. Ý tưởng cốt lõi

Giữ nguyên **framework SeqGAN** (Generator + Discriminator + Reward) theo yêu cầu thesis.  
Thay duy nhất 1 thứ: **REINFORCE → Gumbel-Softmax Straight-Through Estimator** trong Generator.

```
SeqGAN gốc:                     SeqGAN + Gumbel-Softmax:
  G → discrete tokens               G → soft tokens (Gumbel-Softmax)
  reward = D(tokens)                reward = D(soft_tokens)
  REINFORCE gradient                 backprop trực tiếp
  → vanish khi advantage≈0          → gradient luôn tồn tại
```

### 2.2. Gumbel-Softmax là gì (ngắn gọn)

Vấn đề với discrete tokens: `argmax` không có gradient. Gumbel-Softmax giải quyết bằng cách replace `argmax` bằng soft approximation có gradient:

```python
# Gốc (không có gradient):
token = argmax(logits)

# Gumbel-Softmax (có gradient):
gumbel_noise = -log(-log(Uniform(0,1)))
token_soft = softmax((logits + gumbel_noise) / τ)
# τ = temperature: cao → uniform (diverse), thấp → one-hot (discrete)
```

**Straight-Through Estimator (STE)**: Dùng hard token cho input bước tiếp theo, nhưng gradient chạy qua soft token. Cho phép train end-to-end:

```python
token_soft = gumbel_softmax(logits, tau=τ, hard=False)  # cho Discriminator
token_hard = token_soft.detach().argmax(-1)              # cho next decoder step
# Forward: dùng token_hard (như thật)
# Backward: gradient flow qua token_soft (differentiable)
```

### 2.3. So sánh 3 phương án

| | REINFORCE (V1–V4) | Gumbel-Softmax | Warmup-Only |
|---|---|---|---|
| Framework | SeqGAN ✓ | SeqGAN ✓ | Không có D |
| Discriminator | WGAN-GP ✓ | WGAN-GP ✓ | Không có |
| Mode collapse | **Luôn xảy ra** | **Giải quyết** | N/A |
| Thesis compatibility | ✓ | ✓ | ✗ (thiếu D) |
| Độ phức tạp | Đã có sẵn | Thay ~50 dòng code | Đơn giản nhất |

**→ Chọn Gumbel-Softmax: giải quyết collapse + giữ nguyên SeqGAN framework.**

---

## PHẦN 3 — KIẾN TRÚC CHI TIẾT

### 3.1. Generator — ConditionalGumbelSeqGAN

Giữ nguyên kiến trúc V4 (`GeneratorBiLSTMEncoder`), chỉ thay output layer:

```python
class ConditionalGumbelGenerator(nn.Module):
    """
    Giữ từ V4: 2-layer BiLSTM encoder + 2-layer LSTM decoder
    Thay đổi: output dùng Gumbel-Softmax thay vì sample discrete token
    """
    vocab_size  = 434   # giữ từ V4 (delex_v2 function whitelist)
    embed_dim   = 256
    hidden_dim  = 512
    enc_layers  = 2
    dec_layers  = 2
    cond_dim    = 32    # attack_type (4) + db_engine (4) embedding
    
    def forward(self, condition, seq_len, temperature=1.0):
        # 1. Encode condition → initial decoder state
        cond_emb = self.condition_embed(condition)          # [B, cond_dim]
        h, c = self.init_hidden(cond_emb)                   # BiLSTM initial state
        
        soft_tokens = []
        hard_tokens = []
        x = self.embed(BOS_token)                           # [B, embed_dim]
        
        for t in range(seq_len):
            # LSTM decode step
            h, c = self.lstm_decoder(x, (h, c))
            logits = self.output_proj(h)                    # [B, vocab_size]
            
            # Gumbel-Softmax (THAY THẾ cho sample/REINFORCE)
            soft = F.gumbel_softmax(logits, tau=temperature, hard=False)
            hard = soft.detach().argmax(-1)                 # [B] — cho next step
            
            soft_tokens.append(soft)    # differentiable → Discriminator
            hard_tokens.append(hard)    # discrete → re-lex, reward, display
            
            x = self.embed(hard)        # straight-through: next input = hard token
        
        soft_seq = torch.stack(soft_tokens, dim=1)  # [B, T, V]
        hard_seq = torch.stack(hard_tokens, dim=1)  # [B, T]
        return soft_seq, hard_seq
```

**Temperature schedule:**
```
Phase 1 Warmup: τ = 1.0 (fixed, encourage exploration)
Phase 2 Adversarial: τ = max(0.5, 1.0 × exp(-0.00005 × step))
  → giảm dần từ 1.0 xuống 0.5 trong 14,000 steps
  → không để τ < 0.5 (dưới đó gradient vanish do quá hard)
```

### 3.2. Discriminator — WGAN-GP (giữ nguyên từ V4)

WGAN-GP đã được thầy Lâm confirm. Giữ nguyên kiến trúc, chỉ cần thay phần nhận input: bây giờ D nhận **soft token distribution** thay vì one-hot.

```python
class ConditionalWGANDiscriminator(nn.Module):
    """
    CNN Discriminator với WGAN-GP
    Input: [B, T, vocab_size] — real (one-hot) hoặc fake (Gumbel soft)
    Output: scalar score (không dùng sigmoid — Wasserstein distance)
    """
    
    def forward(self, token_seq, condition):
        # token_seq: [B, T, V] — works cho cả one-hot và soft distribution
        x = token_seq.transpose(1, 2)                   # [B, V, T] cho Conv1d
        
        # Multi-scale CNN (capture unigram, bigram, trigram patterns)
        feats = []
        for conv in self.convs:                         # kernel size 1, 2, 3
            f = F.relu(conv(x))
            f = F.max_pool1d(f, f.size(-1)).squeeze(-1) # [B, filters]
            feats.append(f)
        
        x = torch.cat(feats, dim=-1)                    # [B, total_filters]
        x = torch.cat([x, self.cond_embed(condition)], dim=-1)
        
        return self.linear(x)                           # [B, 1] — Wasserstein score
    
    def gradient_penalty(self, real_seq, fake_seq, condition):
        """WGAN-GP: enforce 1-Lipschitz qua gradient penalty"""
        B = real_seq.size(0)
        α = torch.rand(B, 1, 1).to(real_seq.device)
        interp = (α * real_seq + (1 - α) * fake_seq).requires_grad_(True)
        
        d_interp = self(interp, condition)
        grad = autograd.grad(
            outputs=d_interp, inputs=interp,
            grad_outputs=torch.ones_like(d_interp),
            create_graph=True, retain_graph=True
        )[0]
        gp = ((grad.norm(2, dim=(1,2)) - 1) ** 2).mean()
        return gp
```

### 3.3. Reward Function (đáp ứng câu hỏi thầy Lâm)

Giữ nguyên công thức từ V3, áp dụng cho **hard tokens** (sau re-lex):

```python
def compute_reward(hard_tokens, relex_dict, waf_oracle, db_sandbox, ast_tracker, ids_model):
    """
    Input:  hard_tokens [B, T] — discrete tokens từ Generator
    Output: reward [B] — scalar per sample
    """
    payloads = relex(hard_tokens, relex_dict)   # bước bắt buộc: delex → real SQL
    
    return (
        0.30 * waf_oracle.batch_check(payloads)        # OWASP CRS bypass
      + 0.25 * db_sandbox.batch_execute(payloads)       # SQL execution success
      + 0.20 * ast_tracker.batch_entropy(payloads)      # AST structural diversity
      + 0.15 * ids_model.batch_evasion(payloads)        # ML IDS evasion
      + 0.10 * novelty_score(payloads, buffer)          # Jaccard novelty
    )
```

**Reward dùng ở đâu trong training:**
```
Phase 1 (Warmup):    reward KHÔNG dùng → chỉ MLE loss + entropy reg
Phase 2 (Adversarial): D_score là reward signal chính
                        reward_fn bổ sung qua mixed loss (weight nhỏ hơn)
Phase 3 (Fine-tune): reward_fn là signal chính, D bị freeze
```

### 3.4. Training Loop — 3 Phases

```
Phase 1 — MLE Warmup (2,000 steps):
  Mục tiêu: G học SQL syntax từ dataset, không dùng D
  G_loss = CrossEntropy(logits, real_tokens) - 0.10 × H(logits)
  τ = 1.0 (fixed)
  Monitor: val_ppl ≤ 2.0, unique/64 > 50
  
  Khác V3: Dùng checkpoint MLE đã train (val_ppl=1.74) làm starting point
           → bỏ qua Phase 1, nhảy thẳng vào Phase 2 nếu cần nhanh

Phase 2 — Adversarial (12,000 steps):
  n_critic = 5 (train D 5 lần trước mỗi G step — standard WGAN)
  
  D step:
    real = sample từ dataset (one-hot)
    fake_soft, fake_hard = G(condition, τ)
    L_D = D(fake_soft) - D(real) + λ × GP(real, fake_soft)   [λ=10]
    update D

  G step:
    fake_soft, fake_hard = G(condition, τ)
    reward = compute_reward(fake_hard)         # reward từ real SQL
    L_G = -D(fake_soft)                        # adversarial loss (Wasserstein)
         - 0.05 × H(logits)                   # entropy regularization
         - 0.10 × reward                      # reward signal (weight nhỏ)
    update G
  
  τ = max(0.5, 1.0 × exp(-0.00005 × step))
  Monitor mỗi 100 steps: unique/64, H, cache_hit_rate
  
  Checkpoint: lưu mỗi 500 steps với metadata đầy đủ (step, τ, optimizer states)
  Resume flag: PHẢI có --resume để tránh lại lỗi V4

Phase 3 — Reward Fine-tuning (6,000 steps):
  Freeze D (không update)
  G_loss = -reward + 0.05 × H(logits)
  τ = 0.5 (fixed — gần discrete hơn)
  Dùng WAF thật (Docker ModSecurity) nếu có, dev_proxy nếu không
```

---

## PHẦN 4 — DATA PIPELINE (Bắt buộc làm trước model)

Root cause thực sự của mode collapse là **data**, không phải training:

| Vấn đề | Mức độ | Giải pháp |
|--------|--------|-----------|
| Delex xóa 100% function names (xmltype, pg_sleep...) | Critical | delex_v2 với function whitelist |
| Collision rate 71.89% (17,821 → 5,009 unique) | Critical | delex_v2 → 4.33% (đã proven) |
| Wrapper bias 53.64% (inner payload bị nuốt) | High | strip_wrapper.py |
| Gold data chỉ 662 rows | Medium | Hạ threshold 0.90 → 0.85 |

### 4.1. Pipeline 4 bước

```
combined_labeled_data.csv (~40k rows)
          ↓
  [1. TRIAGE]     triage.py
  Keep / Relabel / Drop
          ↓
  [2. RELABEL]    relabel.py + Claude subagent (chỉ khi A≠C)
  Gán sqli_type, db_engine, confidence
          ↓
  [3. TRANSFORM]  strip_wrapper.py → delex_v2.py
  Strip SELECT...WHERE wrapper, delex với function whitelist
          ↓
  [4. TIER]       tier_split.py → resample.py
  Gold (≥0.85) / Silver (≥0.70) → balanced 5,000–8,000 rows
```

### 4.2. Function whitelist (delex_v2) — quan trọng nhất

```python
FUNCTION_WHITELIST = {
    # Error-based (Oracle, MySQL)
    "xmltype", "extractvalue", "updatexml", "exp", "polygon",
    # Time-blind
    "sleep", "benchmark", "pg_sleep", "dbms_pipe", "randomblob", "waitfor",
    # Boolean-blind  
    "if", "ifnull", "coalesce", "elt", "field",
    # Union/String manipulation
    "group_concat", "concat", "concat_ws", "char", "ascii", "hex",
    "unhex", "substr", "substring", "mid", "left", "right",
    "instr", "locate", "length", "count", "version", "user",
    "database", "schema", "table_name", "column_name",
    # Control flow
    "case", "when", "then", "else", "end", "cast", "convert",
    # Information schema
    "information_schema", "sys", "mysql", "performance_schema",
}

# Kết quả đã đo: collision 71.89% → 4.33% (16× cải thiện)
```

### 4.3. Benign SQL (yêu cầu thầy Lâm — điểm #5)

```python
# generate_benign_sql.py — tạo ~2,000 benign queries
BENIGN_TEMPLATES = [
    "SELECT {col} FROM {table} WHERE {col} = {val}",
    "SELECT {col1}, {col2} FROM {table} WHERE {col} BETWEEN {v1} AND {v2}",
    "INSERT INTO {table} ({col1}, {col2}) VALUES ({v1}, {v2})",
    "UPDATE {table} SET {col} = {val} WHERE id = {id}",
    "DELETE FROM {table} WHERE {col} = {val}",
]
# Quy tắc: KHÔNG có SLEEP, UNION, OR '1'='1', comment (--), nested SELECT

# Dùng trong Discriminator training:
# real = SQLi payloads → label real
# benign + fake = benign SQL + G(output) → label fake
# D phân biệt real SQLi vs (benign + generated)
```

---

## PHẦN 5 — CẤU TRÚC CODE MỚI

```
GAN_SQLi/
├── data/
│   ├── raw/                            ← combined_labeled_data.csv
│   ├── processed/
│   │   ├── gold.csv                    ← ≥0.85 confidence (target >2,000 rows)
│   │   ├── silver.csv                  ← ≥0.70 confidence
│   │   ├── benign.csv                  ← generated benign SQL
│   │   ├── train.csv / val.csv         ← train/val split
│   │   └── tokenizer_vocab.json        ← 434 tokens (delex_v2)
│   └── pipeline/
│       ├── triage.py
│       ├── relabel.py
│       ├── strip_wrapper.py
│       ├── delex_v2.py                 ← function whitelist
│       ├── tier_split.py
│       ├── resample.py
│       └── generate_benign_sql.py
│
├── src/
│   ├── generator.py                    ← ConditionalGumbelGenerator (BiLSTM + Gumbel-ST)
│   ├── discriminator.py                ← ConditionalWGANDiscriminator (CNN + WGAN-GP)
│   ├── tokenizer.py                    ← SQLTokenizer (giữ từ V3)
│   ├── reward.py                       ← compute_reward (WAF+DB+AST+IDS+Novelty)
│   ├── waf_oracle.py                   ← ModSecurity interface
│   ├── db_sandbox.py                   ← SQLite execution sandbox
│   └── ast_tracker.py                  ← AST diversity metric
│
├── train.py                            ← 3-phase training (Warmup→Adv→Fine-tune)
├── evaluate.py                         ← 5-metric evaluation
├── generate.py                         ← Sampling từ checkpoint
│
├── configs/
│   ├── seqgan_gumbel.yaml              ← Main config
│   └── baselines.yaml                  ← MLE-only, CTGAN configs
│
├── checkpoints/                        ← auto-save mỗi 500 steps
├── eval/                               ← JSON results
└── logs/                               ← TensorBoard
```

**Files cần build theo thứ tự ưu tiên:**
```
Ngày 1 (Data — nền tảng, không thể bỏ):
  1. data/pipeline/triage.py
  2. data/pipeline/strip_wrapper.py
  3. data/pipeline/delex_v2.py           ← quan trọng nhất
  4. data/pipeline/tier_split.py + resample.py
  5. data/pipeline/generate_benign_sql.py

Ngày 2 (Model):
  6. src/tokenizer.py                    ← adapt từ V3 (nhỏ)
  7. src/generator.py                    ← Gumbel-Softmax thay REINFORCE
  8. src/discriminator.py                ← WGAN-GP (adapt từ V3/V4)
  9. src/reward.py                       ← adapt từ reward_v2.py (V3)
  10. configs/seqgan_gumbel.yaml

Ngày 3 (Training):
  11. train.py                           ← 3-phase loop + resume logic
  12. evaluate.py                        ← adapt từ eval/evaluate_v2.py
  13. generate.py                        ← adapt từ generate_v2.py

Ngày 4 (Eval + Slide):
  14. Chạy training + evaluation
  15. Build slide báo cáo thầy
```

---

## PHẦN 6 — SO SÁNH V3 vs V4 vs MỚI (Gumbel-SeqGAN)

| | V3 (REINFORCE) | V4 (8 fixes, crashed) | **Gumbel-SeqGAN (mới)** |
|--|--|--|--|
| Generator | LSTM | BiLSTM | BiLSTM ✓ |
| Gradient | REINFORCE | REINFORCE | **Gumbel-Softmax** ✓ |
| Mode collapse | Step ~2500 | N/A (crashed) | **Giải quyết** |
| Discriminator | WGAN-GP | WGAN-GP | WGAN-GP ✓ |
| Vocab | 89 tokens | 434 tokens | 434 tokens ✓ |
| Function whitelist | ✗ | ✓ | ✓ |
| Benign data | ✗ | ✓ | ✓ |
| Best composite | 0.471 | N/A | target >0.55 |
| Self-BLEU-3 | ~0.99 (collapse) | N/A | target <0.70 |
| Thesis valid | ✓ | ✓ | ✓ |

**Thay đổi thực tế so với V4**: Chỉ cần thay ~50 dòng trong `src/generator.py` (phần sampling + loss computation). Toàn bộ kiến trúc BiLSTM, WGAN-GP, 8 anti-collapse fixes, data pipeline đều giữ nguyên.

---

## PHẦN 7 — ĐÁNH GIÁ & BASELINE

### 7.1. Metrics (giữ nguyên V3)

```python
composite = 0.30 × owasp_bypass_rate
          + 0.25 × db_execution_rate
          + 0.20 × (ast_entropy / 5.0)
          + 0.15 × ids_evasion_rate
          + 0.10 × relex_uniqueness
```

Thêm cho Gumbel-SeqGAN:
```
Self-BLEU-3:     < 0.70 (target, V3 = 0.99)
Type accuracy:   > 70%  (conditional generation đúng attack type)
τ-diversity curve: diversity vs quality khi τ ∈ [0.5, 1.5]
```

### 7.2. Baseline cần có (yêu cầu thầy Lâm)

| Model | Mục đích | Nguồn |
|-------|---------|-------|
| MLE-only (V3 step2000) | Baseline đã có, composite=0.471 | Đã có checkpoint |
| CTGAN | Tabular baseline (thầy yêu cầu) | ctgan library |
| WGAN-GP text (standard) | Ablation: WGAN-GP không có Gumbel | Implement nhỏ |
| **Gumbel-SeqGAN (model của mình)** | **Main result** | Build mới |

---

## PHẦN 8 — CHUẨN BỊ CHO BUỔI GẶP THẦY LÂM (20/05)

### 8.1. Sơ đồ kiến trúc (đáp ứng nhận xét #1: "3 khối phải có kết nối")

```
┌─────────────────────────────────────────────────────────────┐
│                    SeqGAN + Gumbel-Softmax                   │
│                                                             │
│  [Attack Type]──┐                                           │
│  [DB Engine]────┤→ Condition Embed → BiLSTM Encoder         │
│                 │                         ↓                  │
│                 │              LSTM Decoder (step-by-step)   │
│                 │                         ↓                  │
│                 │              Gumbel-Softmax(logits, τ)     │
│                 │              ↙soft_tokens  ↘hard_tokens    │
│                 │              ↓              ↓              │
│                 │    ┌──────────────┐   ┌──────────┐        │
│                 │    │WGAN-GP Discr.│   │ Re-lex   │        │
│                 │    │  (CNN-based) │   │ (delex→  │        │
│                 │    │  D_score     │   │  real SQL)│        │
│                 │    └──────┬───────┘   └────┬─────┘        │
│                 │           │                ↓               │
│                 │    ┌──────┴──────────────────────┐        │
│                 └───→│  Reward = D_score +          │        │
│                      │  WAF_bypass + DB_exec +      │        │
│                      │  AST_entropy + IDS_evasion   │        │
│                      └───────────┬──────────────────┘        │
│                                  ↓                           │
│                          G_loss = -Reward                    │
│                          backprop qua soft_tokens            │
│                          (Gumbel-Softmax differentiable)     │
└─────────────────────────────────────────────────────────────┘
```

### 8.2. Trả lời câu hỏi thầy: "WAF score dùng làm gì?"

```
Thưa thầy:

Discriminator D học phân biệt real SQLi (từ dataset) với generated SQLi (từ G).
D cho ra W-distance score thay vì probability (WGAN-GP không dùng sigmoid).

WAF score hoạt động như sau:
  Phase 2 Adversarial: D là reward chính. D(fake) cao → G được reward cao.
    G học generate payload ngày càng khó phân biệt với real SQLi.
    WAF score đóng vai phụ (weight 0.10 trong mixed loss).

  Phase 3 Fine-tuning: WAF score là reward chính.
    G được fine-tune với reward = 0.30×WAF_bypass + 0.25×DB_exec + ...
    D bị freeze — không update nữa.
    G học bias generation về phía payload bypass được WAF thật sự.

Tóm lại: D dạy G "trông giống SQLi thật", WAF dạy G "bypass được WAF thật".
Hai signal bổ sung cho nhau, không thay thế nhau.
```

### 8.3. Thay đổi so với V3 (để trình bày với thầy)

```
Thay đổi kỹ thuật:
  1. REINFORCE → Gumbel-Softmax: giải quyết mode collapse gốc rễ
  2. BiLSTM encoder: capture context 2 chiều (theo gợi ý thầy)
  3. Benign SQL trong D training (theo yêu cầu thầy)
  4. delex_v2 với function whitelist: collision 71.89% → 4.33%
  5. WGAN-GP (thầy đã confirm)

Kết quả kỳ vọng so V3:
  Self-BLEU-3: 0.99 → <0.70  (mode collapse giải quyết)
  Unique/64:   6/64  → >40/64
  Composite:   0.471 → >0.50
```

---

## PHẦN 9 — ROADMAP 17–20/05

```
17/05 T7 (Hôm nay):
  ☐ AM: Data pipeline — triage + strip_wrapper + delex_v2 (4 giờ)
  ☐ PM: tier_split + generate_benign + verify (collision <15%) (3 giờ)

18/05 CN:
  ☐ AM: src/generator.py — ConditionalGumbelGenerator (BiLSTM + Gumbel-ST) (4 giờ)
  ☐ PM: src/discriminator.py (WGAN-GP), src/reward.py, configs/ (3 giờ)

19/05 T2:
  ☐ AM: train.py (3-phase loop + resume logic) (3 giờ)
  ☐ AM: MLE pretrain (2 phút/run) → load checkpoint → start adversarial
  ☐ PM: Adversarial training chạy ~2–3 giờ → evaluate (2 giờ)

20/05 T3:
  ☐ AM: Slide 7 trang (xem Section 8.3) (3 giờ)
  ☐ 14:00: Họp thầy

Plan B nếu training chưa xong 19/05:
  → Trình bày architecture + data pipeline results
  → Demo: collision rate 71.89% → 4.33% (có thể chạy live 5 phút)
  → Trình bày kế hoạch Gumbel-SeqGAN chi tiết
  → Dùng V3 step2000 numbers (composite=0.471) làm interim result
```

### Mục tiêu định lượng

| Metric | V3 step2000 (baseline) | Target Gumbel-SeqGAN |
|--------|----------------------|---------------------|
| Self-BLEU-3 | 0.9894 | **< 0.70** |
| Unique/64 adversarial | 6/64 | **> 40/64** |
| Composite (no-WAF) | 0.471 | **> 0.50** |
| OWASP bypass | 2.0% | **> 8%** |
| Type accuracy | N/A | **> 70%** |
| Relex uniqueness | 1.000 (warmup) | **> 0.80 (adversarial)** |

---

## PHẦN 10 — WINDOWS-SPECIFIC FIXES (bắt buộc từ đầu)

```python
# Đặt ở đầu MỌI script:
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# File I/O:
pd.read_csv(path, encoding='utf-8-sig')
pd.to_csv(path, encoding='utf-8-sig', index=False)

# Paths:
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

# Print/log: KHÔNG dùng emoji, dùng ASCII:
# ✓ → [OK], ✗ → [FAIL], ⚠ → [WARN], → thay bằng ->

# Checkpoint save (có resume):
torch.save({
    'step': step, 'phase': phase,
    'temperature': tau,
    'g_state': gen.state_dict(),
    'd_state': disc.state_dict(),
    'g_opt': g_opt.state_dict(),
    'd_opt': d_opt.state_dict(),
}, ckpt_path)
```

---

## MEMO CUỐI

> **Thay đổi duy nhất, tác động lớn nhất**: Thay ~50 dòng REINFORCE bằng Gumbel-Softmax  
> trong `generator.py`. Toàn bộ framework SeqGAN — Generator, Discriminator WGAN-GP,  
> Reward function, 3-phase training — giữ nguyên và hợp lệ với thesis.  
>  
> **Thứ tự ưu tiên tuyệt đối:**  
> 1. Data pipeline (delex_v2) — không có data tốt, model nào cũng collapse  
> 2. Generator Gumbel-Softmax — giải quyết root cause collapse  
> 3. Discriminator WGAN-GP — đã proven, adapt từ V3/V4  
> 4. Training + Eval — chạy và đo  
>  
> Deadline không thay đổi: 20/05 họp thầy lúc 2 giờ.

---

### 3.5. Implementation Delta từ V4 — chỉ thay ~60 dòng

Toàn bộ V4 giữ nguyên. Chỉ sửa 3 điểm:

**src/generator.py — thay sampling:**
```python
# XOA (REINFORCE):
# token_id = torch.multinomial(F.softmax(logits,-1), 1).squeeze(-1)
# log_prob  = F.log_softmax(logits,-1).gather(1, token_id.unsqueeze(-1)).squeeze(-1)
# log_probs.append(log_prob)

# THAY BANG (Gumbel-Softmax STE):
soft = F.gumbel_softmax(logits, tau=self.temperature, hard=False)  # [B,V]
hard = soft.detach().argmax(-1)                                     # [B]
soft_tokens.append(soft)   # -> Discriminator (differentiable)
hard_tokens.append(hard)   # -> re-lex, reward, next-step input
```

**train.py — thay G loss:**
```python
# XOA:
# pg_loss = -(log_probs * advantages).mean()
# g_loss  = pg_loss - entropy_coeff * entropy

# THAY BANG:
fake_soft = torch.stack(soft_tokens, dim=1)         # [B, T, V]
d_score   = discriminator(fake_soft, condition)     # backprop truc tiep
g_loss    = -d_score.mean()
          - entropy_coeff * entropy_of(fake_soft)
          - reward_coeff  * reward_fn(hard_tokens)
```

**train.py — them temperature schedule:**
```python
import math
def get_tau(step, phase):
    return 1.0 if phase == 'warmup' else max(0.5, math.exp(-5e-5 * step))
generator.temperature = get_tau(step, current_phase)
```

**Ket qua ky vong:**
- unique/64 tai adversarial: > 40 (so voi 6-7 cua V3)
- gradient_norm(G) khong collapse ve 0
- Self-BLEU-3 < 0.70

---

## PHAN 11 — HUONG 8: WAF-A-MoLE MUTATION AUGMENTATION

**Paper**: Demetrio et al. (2020) *"WAF-A-MoLE: Evading Web Application Firewalls through Adversarial Machine Learning"* — ACM SAC 2020

### Vi tri trong pipeline

Post-processing augmentation chay SAU khi G sinh payload. Zenodo dataset (3.79M rows)
co san truong `tamper_method` — ground-truth cua cac mutation techniques thuc te.
Dung de TRAIN mutation selector, khong chi random apply.

### 6 Mutation Rules

```python
import re, random, urllib.parse

MUTATIONS = {
    'space'    : lambda p: re.sub(r'\b(SELECT|UNION|AND|OR|WHERE)\b', r'\1 ', p),
    'comment'  : lambda p: p.replace(' ', '/**/'),
    'case'     : lambda p: ''.join(c.upper() if random.random() > .5
                                    else c.lower() for c in p),
    'urlencode': lambda p: urllib.parse.quote(p, safe='=<>(),-+'),
    'dbl_enc'  : lambda p: p.replace('%27', '%2527').replace('%20', '%2520'),
    'equiv'    : lambda p: p.replace('1=1', "'x'='x'")
                            .replace('OR ',  '|| ')
                            .replace('SLEEP(5)', 'SLEEP(0x5)'),
}

def mutate_and_score(payload, waf_oracle, n=20):
    candidates = []
    for _ in range(n):
        p = payload
        for op in random.choices(list(MUTATIONS.values()), k=random.randint(1, 3)):
            p = op(p)
        candidates.append(p)
    scores = waf_oracle.batch_check(candidates)
    return sorted(zip(candidates, scores), key=lambda x: -x[1])

def augment_replay_buffer(buffer, generator, waf_oracle):
    payloads = generator.generate(n=64)
    for payload in payloads:
        ranked = mutate_and_score(payload, waf_oracle)
        top    = [p for p, s in ranked if s > 0.7][:3]
        buffer.extend(top)
    return buffer[-2048:]
```

### Tich hop Zenodo tamper_method

Zenodo co 7 tamper methods co san: equaltolike, space2comment, randomcase,
charencode, charunicodeencode, between, greatest.

```python
ZENODO_TAMPER_MAP = {
    'equaltolike'      : 'equiv',
    'space2comment'    : 'comment',
    'randomcase'       : 'case',
    'charencode'       : 'urlencode',
    'charunicodeencode': 'dbl_enc',
    'between'          : 'equiv',
    'greatest'         : 'equiv',
}
```

Dung Zenodo lam "mutation training set": hoc mutation nao bypass WAF tot cho tung loai payload.

### Tich hop vao training loop

Moi 500 G steps (Phase 2 va 3): goi `augment_replay_buffer()`, lay 50% real data
+ 50% high-scoring mutants cho D training.

| Metric | Khong mutation | Co mutation |
|--------|---------------|-------------|
| OWASP bypass | 2-10% | **15-30%** |
| Code them | 0 | ~100 dong |

---

## PHAN 12 — HUONG 10: INFOGAN CONDITIONAL LOSS

**Paper**: Chen et al. (2016) *"InfoGAN: Interpretable Representation Learning
by Information Maximizing Generative Adversarial Nets"* — NeurIPS 2016

### Van de

Conditional embedding hien tai khong *enforce* G follow condition. G co the ignore
attack_type/db_engine sau vai decode steps, dan den type_accuracy thap (~45%).

### Q-Network (chia se CNN voi D)

```python
class QNetwork(nn.Module):
    def __init__(self, shared_cnn, hidden_dim=512):
        super().__init__()
        self.shared      = shared_cnn
        self.attack_head = nn.Linear(hidden_dim, 4)
        self.db_head     = nn.Linear(hidden_dim, 4)

    def forward(self, token_seq):
        feat = self.shared(token_seq)
        return self.attack_head(feat), self.db_head(feat)
```

### Loss function

```python
# G step (them InfoGAN term):
fake_soft        = generator(condition, tau)
d_score          = discriminator(fake_soft, condition)
q_atk, q_db     = Q(fake_soft)

q_loss = F.cross_entropy(q_atk, condition[:, 0]) \
       + F.cross_entropy(q_db,  condition[:, 1])

g_loss = -d_score.mean()
       - entropy_coeff * entropy_of(fake_soft)
       - reward_coeff  * reward_fn(hard_tokens)
       + 0.2 * q_loss                          # InfoGAN: phat neu ignore condition

# D step: shared encoder update -> Q duoc update gian tiep
```

### Expected improvement

| Metric | Khong InfoGAN | Co InfoGAN |
|--------|--------------|-----------|
| Type accuracy | ~45% | **>80%** |
| DB accuracy | ~30% | **>70%** |
| Code them | 0 | ~80 dong |

---

## PHAN 13 — NEWDATASET: 17 NGUON (14.6M ROWS)

**Thu muc**: `Asset/LabelData/NewDataSet/`
**Ngay tai**: 2026-05-17

### Priority Tier

**TIER 1 — Type-labeled, dung truc tiep:**

| Dataset | Rows | Labels | Key columns | Dung cho |
|---------|------|--------|-------------|---------|
| RbSQLi (Mendeley xz4d5zj5yw) | 10,190,450 | injection_type | sql_query, injection_type, vulnerability_status | Training chinh |
| Zenodo 17086037 | 3,792,161 | attack_technique, tamper_method | full_query, attack_technique, tamper_method | Training + Mutation |
| yogsec payloads | ~2,000 | 13 file theo type | txt files | Seed payloads |

**TIER 2 — Binary labeled, can type mapping:**

| Dataset | Rows | Action |
|---------|------|--------|
| Kaggle gambleryu | 158,007 | Pattern matching -> type |
| Kaggle sajid576 | 30,919 | Pattern matching -> type |
| Kaggle syedsaqlainhussain | 68,882 | Dedup roi type label |
| HttpParams (Morzeux) | 63,240 | Extract injection part + type |
| BCCC-SFU 2023 | 11,011 | Type label |

**TIER 3 — Bo qua hoac filter nang:**

| Dataset | Van de | Quyet dinh |
|---------|---------|-----------|
| Kaggle ayahkhaldi | Mixed natural language | Filter strict |
| HuggingFace sharegpt | Conversation format | Optional |
| GitHub ajinmathew | Duplicate sqliv5 | Skip |

### RbSQLi Type Mapping

```python
RBSQLI_MAP = {
    'Error-Based'    : 'error_based',
    'Boolean-Based'  : 'boolean_blind',
    'Time-Based'     : 'time_blind',
    'Union-Based'    : 'union_based',
    'None_Type'      : 'benign',
    'Stacked-Queries': None,
    'Out-of-Band'    : None,
}
# Chi lay: injection_type in map AND vulnerability_status == 'Yes'
# (tru benign: vulnerability_status == 'No')
```

### Zenodo Type + Tamper Mapping

```python
ZENODO_ATTACK_MAP = {
    'boolean-based blind': 'boolean_blind',
    'time-based blind'   : 'time_blind',
    'error-based'        : 'error_based',
    'UNION query-based'  : 'union_based',
    'stacked queries'    : None,
    'inline queries'     : None,
}
```

### Data Pipeline Moi (5 buoc)

```
Step 1 — DEDUP (dedup.py)
  SHA-256 hash cua payload.lower().strip()
  Expected: ~30% reduction (sqliv5 trung voi nhieu Kaggle sources)

Step 2 — TYPE MAPPING (map_types.py)
  RBSQLI_MAP + ZENODO_ATTACK_MAP truoc, fallback pattern matching
  Output: typed_payloads.csv (payload, sqli_type, db_engine, confidence, source)

Step 3 — STRIP WRAPPER + DELEX V2
  Giu nguyen tu curator skill (da proven: collision 71.89% -> 4.33%)

Step 4 — TIER SPLIT + BALANCE
  Gold  : confidence >= 0.85, cap 200 rows/type/db_engine
  Silver: confidence >= 0.70
  Target Gold: >10,000 rows (vs V3: 662 rows, tang 15x)

Step 5 — TRAIN/VAL/TEST SPLIT
  Train 70% / Val 15% / Test 15% (fixed set, khong touch khi train)
```

### Expected Dataset Size sau pipeline

| Tier | Source chinh | Expected rows |
|------|-------------|---------------|
| Gold | RbSQLi + Zenodo | **~15,000-20,000** |
| Silver | Kaggle + GitHub | ~30,000-50,000 |
| Total train | Gold + Silver | **~50,000-70,000** |
| Benign | gambleryu benign rows | ~10,000 |

So sanh voi V3: Gold 662 rows → **~15,000+ rows (22x nhieu hon)**
