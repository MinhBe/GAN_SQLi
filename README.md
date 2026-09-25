# CGR-SeqGAN clean replacement for `MinhBe/GAN_SQLi`

This package is the clean version I recommend for the current PostgreSQL Boolean SQLGAN corpus.
It keeps Branch A as a baseline, but makes Branch B the preferred path.

```text
Y1/Y2 accepted metadata -> CGR-SeqGAN core generator
                        -> metadata-aware static reward
                        -> Monte-Carlo rollout reward
                        -> accepted core candidates
                        -> Y3/Y4 representation renderers
                        -> static gate
                        -> optional local PostgreSQL sandbox validator
```

## What changed

- Replaced SeqGAN-lite whole-sequence reward with Monte-Carlo rollout reward.
- Added metadata-aware contracts from `seqgan_accepted_metadata.jsonl` / `attack_samples.csv`.
- Static validation now checks required tokens, skeleton overlap, representation compliance, safe scope, delimiter, quote, Boolean signal, and slot sanity.
- Generation now reports matched contract/cell fields when available.
- Y3/Y4 are renderers from accepted core payloads, not independent raw grammar learners.
- PostgreSQL validator has two modes: `safe_minimal` and `postgres_parse_readonly`.
- Tests are at public seams: validator, reward matching, renderers, rollout shape.

## Install

```bash
pip install -r requirements.txt
pip install -e .
pytest -q
```

## Branch B smoke run

```bash
python -m sqlgan_dual.experiment_b_core_renderers \
  --data /path/to/SQLGAN_PostgreSQL_Boolean_Attack_Corpus_V4_1_StaticTrainingCorpus.zip \
  --out ./runs/cgr_branch_b_smoke \
  --smoke --adv-epochs 1
```

## Full Branch B run

```bash
python -m sqlgan_dual.experiment_b_core_renderers \
  --data /path/to/SQLGAN_PostgreSQL_Boolean_Attack_Corpus_V4_1_StaticTrainingCorpus.zip \
  --out ./runs/cgr_branch_b \
  --surface validation \
  --mle-epochs 12 --d-epochs 4 --adv-epochs 4 \
  --adv-steps 100 --rollouts 4 \
  --batch-size 256 --generate-n 5000 --per-parent 2
```

## Single module

```bash
python -m sqlgan_dual.train_module \
  --data /path/to/V4_1.zip \
  --out ./runs/Y1_cgr \
  --module-id Y1_basic_boolean \
  --surface validation \
  --mle-epochs 12 --d-epochs 4 --adv-epochs 4 \
  --adv-steps 100 --rollouts 4
```

## Length audit before training

```bash
python -m sqlgan_dual.audit_length \
  --data /path/to/V4_1.zip \
  --out-json ./runs/length_audit.json \
  --surface validation --max-len 192
```

If `truncation_rate_at_max_len > 0`, raise `--max-len` before training.

## PostgreSQL sandbox validation

Run only against a disposable local database.

```bash
python validation/postgres_sandbox_validator.py \
  generated_static_scored.csv postgres_runtime.csv \
  --payload-column payload_raw \
  --mode postgres_parse_readonly
```

Do not claim runtime validity until this validator has run and the output is attached to the report.
