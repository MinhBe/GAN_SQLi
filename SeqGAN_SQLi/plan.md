# SeqGAN SQLi — Implementation Plan

## Context

Build a SeqGAN that generates SQL injection payloads and optimizes WAF evasion (ASR) via REINFORCE. Dataset (40,860 labeled payloads) lives at `Asset/LabelData/combined_labeled_data.csv`. **No code exists yet** — `SeqGAN_SQLi/` contains only `Guiding.md`. This plan turns `Guiding.md` §11 (proposed structure) into concrete, ordered work, grounded in what's actually in the CSV.

### What the codebase audit changed vs. the original draft

| Original draft assumption | Actual state |
|---|---|
| `payload_delex` column exists (re-use directly) | **Does NOT exist** in `combined_labeled_data.csv` (only documented for `master_unlabeled.csv`, which is also absent). De-lex must be implemented in Sprint 1. |
| Vocab ~150 tokens after de-lex | Measured: post-de-lex **20,590 unique** tokens. Top-200 covers 92% / top-500 covers ~94%. → Cap at **256 tokens + `<UNK>`**. |
| Tokenizer = SQL-aware, complex | `payload_norm` is **already space-tokenized** (e.g. `( __TIME__ )` has spaces). Tokenizer = `text.split()` + lowercase + de-lex pre-pass. |
| `__TIME__` is the de-lex placeholder we keep | Verified: only 10 rows contain `__TIME__`. All other literals (numbers, strings, hex) are still raw. |
| Expert demos: ~1,500–3,000 | Measured: **4,560** rows match `is_attack=True AND confidence ≥ 0.95`. |
| `IMPLEMENTATION_PLAN.md` / `SKILL_*.md` / `requirements.txt` exist | None of these exist in this repo — drop the references. |
| Stratified split is straightforward | 7 attack types have `<100` rows after Sprint 0 (e.g. `second_order=3`, `inline_query=8`). Need a `__minor__` bucket for splitting. |
| Payload length unspecified | Measured: avg=38, p95=170, max=217 space-tokens → set `max_len=180`. |

---

## Architecture

```
                     ┌───────────────────────────────┐
                     │ Generator π_θ                  │
                     │ LSTM 3-layer hidden=512 emb=128│──→ logits over V≈256
                     └──────────────┬────────────────┘
                                    │ multinomial sample a_t
                     ┌──────────────▼────────────────┐
                     │ SQLiEnv.step(a_t)              │
                     │ r=0 mid-trajectory             │
                     │ r=compute_reward(seq) at EOS   │
                     └──────────────┬────────────────┘
              ┌─────────────────────┴────────────────────┐
              ▼                                          ▼
    ┌──────────────────────┐                ┌────────────────────────┐
    │ RewardOracle         │                │ Discriminator D_φ      │
    │ syntax: sqlparse     │                │ TextCNN k=[3,4,5] f=128│
    │ bypass: dev-mode     │                │ Wasserstein (no σ)+GP  │
    │ length penalty       │                │                        │
    └──────────┬───────────┘                └──────────┬─────────────┘
               └──────────────────┬──────────────────────┘
                  r = 0.3·D + 0.5·r_bypass + 0.2·r_syntax − 0.01·len_pen
                                  │
                     ┌────────────▼─────────────┐
                     │ MCRollout K=16            │
                     │ Q(s_t,a_t)=1/K Σ R(τ^k)  │
                     └────────────┬─────────────┘
                     ┌────────────▼─────────────┐
                     │ ValueBaseline b_ψ(h_t)    │
                     │ MLP, EMA decay 0.95       │
                     │ A = Q − b                 │
                     └────────────┬─────────────┘
                       REINFORCE + grad clip 1.0
```

---

## Sprint 0 — Label Normalization

**Output:** `Asset/LabelData/master_labeled_data.csv`
**Script:** `SeqGAN_SQLi/data/normalize_labels.py`

| Old label | Count | New label |
|---|---|---|
| `boolean_based` | 1,820 | `boolean_blind` |
| `stacked_query` | 2 | `stacked_queries` |
| `ldap_injection` | 2 | `unknown` |
| `command_injection` | 1 | `rce` |

Steps:
1. Read `combined_labeled_data.csv` with `encoding='utf-8-sig'` (BOM present).
2. Apply remap.
3. Add columns:
   - `is_attack` ← `sqli_type != 'benign'`
   - `confidence_float` ← `float(confidence)` (parser test confirmed: 0 unparseable rows).
   - `attack_type_group` ← original sqli_type, but tiny types (`<100` rows: `polyglot`, `stacked_queries`, `generic`, `rce`, `comment_based`, `inline_query`, `second_order`) collapsed to `__minor__` — used only for stratified-split keys; original `sqli_type` is preserved.
4. Assert: `len(df) == 40,860` and every label is in the canonical 13-class taxonomy from `Knowledge_Transfer_SQLi_GAN.md` §6.

---

## Sprint 1 — Data Pipeline

**Files (under `SeqGAN_SQLi/data/`):**
```
prepare_seqgan_data.py       ← driver
tokenizer_vocab.json         (generated, ~256 entries)
train.csv  val.csv  test.csv (generated, 70/15/15, FROZEN test, seed=42)
expert_demos.csv             (generated, ~4,560 rows)
```

### De-lexicalization (regex pre-pass before `.split()`)

| Pattern | → Token |
|---|---|
| `'[^']*'` | `__STR__` |
| `"[^"]*"` | `__STR__` |
| `0x[0-9a-fA-F]+` | `__HEX__` |
| `\b\d+\.\d+\b` | `__FLOAT__` |
| `\b\d+\b` | `__INT__` |
| `__TIME__` (already in 10 rows) | unchanged |

Lowercase all, then `text.split()` to get tokens.

### Vocabulary

- Build counter on **train split only** (no leakage).
- Vocab = specials (`<PAD>`, `<SOS>`, `<EOS>`, `<UNK>`) + top-N most frequent → cap at **N=252** so total `vocab_size=256`.
- Audit metric to log: `% of tokens that are <UNK>` on val/test (expect ≤ 8% based on top-200 = 92% coverage).
- Round-trip test: for 100 random train rows, `decode(encode(x)) == x` after both go through de-lex (the de-lexed form is the canonical surface).

### Stratified split

- Stratify on `attack_type_group` (so tiny types share a bucket and don't blow up split sizes).
- 70/15/15 with `seed=42`. Test set written once and never re-generated.
- Each split keeps `payload_norm`, `payload_delex` (computed), `sqli_type` (original), `is_attack`, `confidence_float`, `db_engine`.

### Expert demos

- Filter from train only: `is_attack AND confidence_float >= 0.95` → expected ~3.2k of the 4,560 (rough 70% of total).
- Saved separately for ×3.0 upweight in MLE pretraining.

### Verification

```bash
python SeqGAN_SQLi/data/prepare_seqgan_data.py --verify
# Expected output (numbers approximate within stratification rounding):
# train=28,602  val=6,129  test=6,129
# vocab_size=256  unk_rate_val=~6%  round_trip=100/100 OK
# expert_demos=~3,200 (from train split)
# max_len_p99 ≈ 200  (we'll truncate at 180)
```

---

## Sprint 2 — Model Code

```
SeqGAN_SQLi/
├── src/
│   ├── tokenizer.py
│   ├── generator.py
│   ├── discriminator.py
│   ├── env.py
│   ├── reward.py
│   ├── rollout.py
│   ├── baseline.py
│   ├── losses.py
│   ├── scheduled_sampling.py
│   └── utils.py
├── configs/
│   ├── seqgan_default.yaml
│   └── seqgan_ablation.yaml
└── requirements.txt    (torch, sqlparse, pyyaml, tqdm, tensorboard, pandas, numpy, nltk)
```

| File | Class / fn | Critical signature / detail |
|---|---|---|
| `tokenizer.py` | `SQLiTokenizer` | `encode(s)→List[int]`, `decode(ids)→str`; loads `tokenizer_vocab.json`; uses regex de-lex from Sprint 1, then `.split()` |
| `generator.py` | `GeneratorLSTM` | embed 128, LSTM 3×512, dropout 0.2; `forward(ids, hidden=None)→(logits, hidden)`; `sample(B, max_len, temperature=1.0, sos=<SOS>)→(ids[B,T], log_probs[B,T], hiddens[B,T,H])` |
| `discriminator.py` | `DiscriminatorCNN` | TextCNN k=[3,4,5] f=128 → linear → scalar (no sigmoid); `gradient_penalty(real, fake)→Tensor` |
| `env.py` | `SQLiEnv` | `reset()→state`, `step(a)→(state, r, done)` (r=0 unless EOS or `len==max_len`), `compute_reward(seq)→{syntax, bypass, d_score, total}` |
| `reward.py` | `RewardOracle` | `syntax_check(payload)`: sqlparse → `1` if parses, `0` otherwise; `bypass_check(payload, sqli_type)`: dev-mode proxy returns `0.1` if non-benign else `0.0` (placeholder; real WAF integration in future iteration); `length_penalty(seq)`: `0.01 * max(0, len-MIN_LEN)/max_len` |
| `rollout.py` | `MCRollout` | `estimate_q(prefix_ids, hidden, env, K=16, max_len)→Tensor[B, T]`; pads B×K rollouts as a single (B·K, L) batch through generator for speed |
| `baseline.py` | `ValueBaseline` | MLP `H→64→1`; `update(q_target, h)` MSE; EMA target with decay 0.95 |
| `losses.py` | functions | `reinforce_loss(log_probs, advantages, mask)`, `wgan_gp_loss(d_real, d_fake, gp, lambda_gp=10)`, `mle_loss(logits, targets, sample_weights)` |
| `scheduled_sampling.py` | `ScheduledSampler` | `epsilon(step) = min(1.0, step / 5000)`; `mix(gt_token, pred_token, eps)` |
| `utils.py` | helpers | `set_seed`, `save_checkpoint`, `load_checkpoint`, `get_device`, `setup_logging` |

### `configs/seqgan_default.yaml`
```yaml
data:
  train_csv: SeqGAN_SQLi/data/train.csv
  val_csv:   SeqGAN_SQLi/data/val.csv
  test_csv:  SeqGAN_SQLi/data/test.csv
  expert_csv: SeqGAN_SQLi/data/expert_demos.csv
  vocab:     SeqGAN_SQLi/data/tokenizer_vocab.json
  max_len:   180
generator:    {embed_dim: 128, hidden_dim: 512, num_layers: 3, dropout: 0.2}
discriminator: {kernel_sizes: [3,4,5], num_filters: 128, embed_dim: 128}
reward:       {lambda_d: 0.3, lambda_bypass: 0.5, lambda_syntax: 0.2, length_penalty: 0.01, min_len: 4}
rollout:      {K: 16}
baseline:     {ema_decay: 0.95, hidden: 64}
training:
  mle:  {epochs: 10, lr: 1.0e-3, batch_size: 64, grad_clip: 1.0, expert_upweight: 3.0, ss_ramp_steps: 5000, early_stop_patience: 3}
  adv:  {total_steps: 50000, lr_g: 1.0e-4, lr_d: 1.0e-4, batch_size: 64, d_steps_per_g: 5, lambda_gp: 10, eval_every: 1000}
seed: 42
```

`seqgan_ablation.yaml` overrides for: (a) no advantage (baseline=0), (b) λ shaping disabled, (c) no scheduled sampling.

---

## Sprint 3 — MLE Pre-training

**File:** `SeqGAN_SQLi/pretrain_mle.py`

1. Load train + expert_demos (concat with weights: train rows = 1.0, expert rows = 3.0 — used as per-sample weights inside cross-entropy via `weight` argument or manual reduction).
2. Teacher forcing for first `ss_ramp_steps` then ScheduledSampling mix.
3. Adam(lr=1e-3, β=(0.5, 0.999)), `grad_clip=1.0`, `batch_size=64`.
4. Validate val perplexity each epoch; save best to `checkpoints/mle_best.pt`; early stop patience=3.

**Smoke gate:** val perplexity drops monotonically across the first 3 epochs; no NaN.

---

## Sprint 4 — Adversarial RL

**File:** `SeqGAN_SQLi/train_adversarial.py`

Per global step:
1. Sample batch B=64 from G; capture `log_probs` and `hidden_states` along the trajectory.
2. `MCRollout.estimate_q` → Q-values (B, T).
3. Baseline forward → b(s_t); `advantage = Q − b` (detached for G grad).
4. G loss: `−mean(log_probs · advantage · mask)`; backward; clip 1.0; `optG.step()`.
5. D loop ×5: real batch from train, fake batch from G; WGAN-GP loss with λ_gp=10; `optD.step()`.
6. Baseline MSE update on Q targets.
7. Every `eval_every` (1000 steps): generate 200 val samples → log `mean_reward`, `syntax_rate`, `ASR_val_proxy`, `‖∇G‖`.

**Reward-hacking guard:** if `syntax_rate < 0.5` at step 5,000 → bump `lambda_syntax: 0.2 → 0.4`, log the change.

**Output:** `checkpoints/adv_final.pt` and `checkpoints/adv_best.pt` (by `mean_reward` on val proxy).

---

## Sprint 5 — Evaluation & Baselines

```
SeqGAN_SQLi/
├── generate.py       ← CLI: --ckpt, --n_samples, --temperature, --out
├── evaluate.py       ← CLI: --input → metrics JSON
└── baselines/
    ├── template_based.py    # samples templates from train, randomly fills __PLACEHOLDER__ with realistic literals
    ├── mle_lm_only.py       # loads mle_best.pt, sample only
    └── seqgan_vanilla.py    # uses raw Q (no advantage), no shaping
```

### Metrics

| Metric | Definition | Pass |
|---|---|---|
| ASR_proxy | `r_bypass==0.1` rate (until real WAF lands) | SeqGAN+adv > MLE-only + 30 pp |
| Syntax validity | `sqlparse(p) parses && len(p)>=4` | ≥ 90% |
| Self-BLEU-3 | NLTK on 1,000 samples | < 0.60 |
| Validity × ASR | composite gate | both must pass |

### Statistical rigor
- N=1000 samples per model; ≥3 seeds.
- Bootstrap CI n=10,000 for ASR and Self-BLEU-3.
- Report mean ± std and p-values vs. MLE-only.

### Run
```bash
python SeqGAN_SQLi/generate.py --ckpt SeqGAN_SQLi/checkpoints/adv_final.pt \
    --n_samples 1000 --out eval_samples.csv
python SeqGAN_SQLi/evaluate.py --input eval_samples.csv \
    --baseline_mle SeqGAN_SQLi/checkpoints/mle_best.pt --seeds 3
```

---

## Dependency order

```
Sprint 0  ──►  Sprint 1  ──►  Sprint 2  ──►  Sprint 3  ──►  Sprint 4  ──►  Sprint 5
normalize     prepare data    code+configs    MLE pretrain    REINFORCE      eval+baselines
labels        + vocab         (parallel ok    mle_best.pt     adv_final.pt   ASR/validity/
master CSV    train/val/test  with Sprint 1   ─────────►      ─────────►     Self-BLEU
              expert_demos    after tokenizer
                              is designed)
```

---

## Critical files — at a glance

| Path | Role |
|---|---|
| `Asset/LabelData/combined_labeled_data.csv` | Source dataset (read-only, 40,860 rows) |
| `SeqGAN_SQLi/Guiding.md` | Architecture reference (already exists; do not modify) |
| `Asset/LabelData/master_labeled_data.csv` | Sprint 0 output (new) |
| `SeqGAN_SQLi/data/normalize_labels.py` | Sprint 0 (new) |
| `SeqGAN_SQLi/data/prepare_seqgan_data.py` | Sprint 1 (new) |
| `SeqGAN_SQLi/data/{train,val,test,expert_demos}.csv` | Sprint 1 outputs (new) |
| `SeqGAN_SQLi/data/tokenizer_vocab.json` | Sprint 1 output (new) |
| `SeqGAN_SQLi/src/{tokenizer,generator,discriminator,env,reward,rollout,baseline,losses,scheduled_sampling,utils}.py` | Sprint 2 (new) |
| `SeqGAN_SQLi/configs/seqgan_default.yaml` + `seqgan_ablation.yaml` | Sprint 2 (new) |
| `SeqGAN_SQLi/requirements.txt` | Sprint 2 (new): torch, sqlparse, pyyaml, tqdm, tensorboard, pandas, numpy, nltk |
| `SeqGAN_SQLi/pretrain_mle.py` | Sprint 3 (new) |
| `SeqGAN_SQLi/train_adversarial.py` | Sprint 4 (new) |
| `SeqGAN_SQLi/checkpoints/{mle_best,adv_best,adv_final}.pt` | Sprints 3–4 outputs |
| `SeqGAN_SQLi/{generate,evaluate}.py` | Sprint 5 (new) |
| `SeqGAN_SQLi/baselines/{template_based,mle_lm_only,seqgan_vanilla}.py` | Sprint 5 (new) |

---

## Per-sprint verification

| Sprint | Smoke check | Pass condition |
|---|---|---|
| 0 | `python SeqGAN_SQLi/data/normalize_labels.py` | Output CSV has 40,860 rows; every `sqli_type` in canonical taxonomy |
| 1 | `python SeqGAN_SQLi/data/prepare_seqgan_data.py --verify` | Splits ≈28,602 / 6,129 / 6,129; vocab_size=256; UNK rate ≤8%; round-trip 100/100 |
| 2 | `pytest SeqGAN_SQLi/tests/` (small smoke tests in same PR) | `GeneratorLSTM(B=4).sample(...).shape == (4, 180)`; `DiscriminatorCNN(ids).shape == (4,)`; `SQLiEnv.step(action)` returns `(state, 0.0, False)` mid-trajectory |
| 3 | `python pretrain_mle.py --epochs 1 --max_steps 100` | Loss strictly decreasing on the smoke window; no NaN; checkpoint saved |
| 4 | `python train_adversarial.py --max_steps 100` | No NaN; G/D losses logged; baseline updates without dimension errors |
| 5 | `python evaluate.py --input <generated_10_samples.csv>` | All metrics print; JSON well-formed |

---

## Out of scope (explicit non-goals for this plan)

- Real ModSecurity Docker WAF integration (Guiding.md §8 mentions; left as future iteration — `bypass_check` ships as a dev-mode proxy).
- Multi-WAF reward (Guiding.md §15).
- Conditional generation `G(z, attack_type)` (future).
- Cross-approach comparison with VAE-GAN / Gumbel-Softmax (future, on the same frozen test set).



.gitignore updated để loại các file generated lớn (*.pt, train.csv/val.csv/test.csv/expert_demos.csv/master_labeled_data.csv — đều regenerate được).

Commit: e271635 — "Add SeqGAN SQLi implementation (Sprints 0–5)"

Không tạo PR vì repo này không có git remote và gh CLI chưa cài. Khi nào setup remote (e.g. GitHub) thì git push -u origin seqgan-sqli-implementation rồi tạo PR.

Để chạy full training:

pip install -r SeqGAN_SQLi/requirements.txt
python SeqGAN_SQLi/data/normalize_labels.py
python SeqGAN_SQLi/data/prepare_seqgan_data.py --verify
python SeqGAN_SQLi/pretrain_mle.py             # ~10 epochs
python SeqGAN_SQLi/train_adversarial.py --mle_ckpt SeqGAN_SQLi/checkpoints/mle_best.pt
python SeqGAN_SQLi/generate.py --ckpt SeqGAN_SQLi/checkpoints/adv_final.pt --n_samples 1000 --out eval_samples.csv
python SeqGAN_SQLi/evaluate.py --input eval_sa