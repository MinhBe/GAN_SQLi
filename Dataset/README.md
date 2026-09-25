# SQLGAN PostgreSQL Boolean C-SeqGAN V5.1 Coverage-Fixed Bootstrap Corpus

This dataset is a defensive, synthetic, ruleset-conditioned PostgreSQL Boolean predicate corpus. It is **payload-only / no-context** and does not claim real-world exploitation.

## Status

- Schema complete: yes
- Ruleset contracts: 4000 total, 1000/module
- Y1/Y2 full MLE coverage: yes, via `cseqgan_train_full_coverage.jsonl`
- Candidate rows: bootstrap from V4.1, not newly model-generated
- Match source for current candidates: `source_assigned`
- Runtime/execution proof: `not_run`
- AI evaluator loop: placeholder, not run

## Key changes from V5

1. Fixed missing `required_tokens` for SIMILAR TO and `?` rulesets.
2. Replaced duplicate slot schema IDs with module-unique IDs such as `SLOT_Y1_R001_C01`.
3. Added structured slot schemas with family/operator/slot constraints.
4. Added minimal shape-only seed rows for Y1/Y2 rulesets missing accepted-static examples.
5. Added full-coverage MLE training files for Y1/Y2.
6. Added `match_source=source_assigned` and `candidate_generation_status=bootstrap_from_v4_1_not_model_generated`.
7. Updated validator to choose payload columns by module.

## Training file policy

- Use `cseqgan_train_full_coverage.jsonl` for MLE shape exposure across all rulesets.
- Use `cseqgan_train.jsonl` as reward-positive accepted-static data.
- Do not treat minimal seeds as runtime-valid or reward-positive.

## Runtime policy

Run `Dataset/validation/postgres_boolean_probe_validator.py` against a local PostgreSQL sandbox before claiming parse/runtime/behavior validity.
