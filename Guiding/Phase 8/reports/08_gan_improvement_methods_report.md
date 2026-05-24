# 08 - GAN Improvement Methods Report

Date: 2026-05-23

Scope: implementation and evaluation of the Phase 8 GAN-improvement methods after the first held-out classifier-oracle result showed that H5' max-aggressive had high novelty but weak learned-detector evasion.

Raw payload text is intentionally omitted.

## Methods Implemented

### 1. Constrained H5' slot mode

Files:

- `phase08_06_paired_surgery_gan.py`
- `run_phase08_paired_surgery_gan_constrained.ps1`

Change:

- Added `--slot-mode constrained`.
- Added context-aware slot selection.
- Added constrained logits so each editable token can only sample from a compatible token group.
- Goal: reduce arbitrary aggressive token edits and improve structural validity.

Result:

- Training completed on RTX 3050 6GB.
- Constrained mode improved technique hint compared with max-aggressive, but lost too much novelty and did not improve classifier-oracle evasion.
- This is useful as an ablation, not the best current branch.

### 2. GAN candidate pool sampler

Files:

- `phase08_09_gan_candidate_sampler.py`
- `run_phase08_gan_candidate_sampler_max_aggressive.ps1`

Change:

- Loaded the existing H5' max-aggressive checkpoint.
- Generated a larger stochastic candidate pool from dev frames.
- Candidate pool size: `8,000`.

Purpose:

- Test whether the H5' distribution already contains better samples than the original one-sample-per-frame output.
- Enable post-generation selection before changing training loss.

### 3. Classifier-oracle reranker

Files:

- `phase08_10_classifier_oracle_rerank.py`
- `run_phase08_classifier_oracle_rerank_max_aggressive.ps1`
- `run_phase08_classifier_oracle_rerank_max_aggressive_attack_only.ps1`

Change:

- Reads generated candidates plus classifier-oracle CSV scores.
- Applies guardrails:
  - optional novel-only
  - optional balanced-delimiter-only
  - optional technique-hint-only
  - optional technique exclusion, especially `benign`
- Selects top candidates by a multi-objective utility score.
- Writes both JSONL samples and evaluator-compatible classifier-oracle CSV.

Important correction:

- The first rerank variant selected `107` benign rows and reached classifier-oracle bypass `0.1700`.
- That result is diagnostic only and must not be used as the main attack-generator claim.
- The attack-only rerank excludes `benign` and is the valid comparison.

### 4. Oracle-aware mutation/search

Files:

- `phase08_11_oracle_aware_search.py`
- `run_phase08_oracle_aware_search_attack_balanced_novel.ps1`

Change:

- Starts from the attack-only reranked GAN candidates.
- Generates bounded text-level variants.
- Trains the same held-out classifier oracle.
- Scores all variants.
- Keeps candidates that pass novelty/balanced/attack-only guardrails.

Purpose:

- Test whether light oracle-aware post-processing can find lower-score candidates without breaking the evaluator gates.

## Main Comparison

| Source | Samples | Balanced delimiter | Novel vs train | Batch dup | Technique hint | Signature-proxy bypass | Classifier-oracle bypass | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| H5' max-aggressive | 400 | `0.2225` | `0.8050` | `0.1725` | `0.6767` | `0.2325` | `0.0050` | Baseline best GAN novelty before improvements |
| H5' constrained | 400 | `0.2225` | `0.5175` | `0.3500` | `0.8321` | `0.1100` | `0.0000` | Ablation; not better overall |
| Rerank attack balanced+novel | 400 | `1.0000` | `1.0000` | `0.0000` | `0.4775` | `0.3775` | `0.0025` | Strong novelty/validity, weak conditioning |
| Rerank attack balanced+novel+hint | 245 | `1.0000` | `1.0000` | `0.2204` | `1.0000` | `0.2531` | `0.0000` | Clean conditioning, fewer samples, no learned evasion |
| Oracle-aware search | 400 | `1.0000` | `1.0000` | `0.0000` | `0.9950` | `0.1525` | `0.0050` | Best balanced post-generation branch |

## Interpretation

The improvements successfully fixed two weaknesses of raw H5' max-aggressive:

- Structural sanity: balanced delimiter rate rose from `0.2225` to `1.0000`.
- Novelty cleanliness: novel-vs-train reached `1.0000` with `0.0000` batch template duplication in the best post-generation branches.

The strongest usable branch is currently:

```text
oracle-aware search over attack-only balanced+novel H5' candidates
```

It gives:

- balanced delimiter rate: `1.0000`
- novel-vs-train template rate: `1.0000`
- batch duplicate rate: `0.0000`
- technique hint rate: `0.9950`
- signature-proxy bypass: `0.1525`
- classifier-oracle bypass: `0.0050`

The main limitation remains:

```text
No implemented method has materially improved learned classifier-oracle evasion.
```

Therefore the defensible claim is:

```text
Expanded-action H5' plus guarded reranking/search can recover clean novelty and structural validity, but the learned held-out classifier oracle still detects almost all attack-only generated samples.
```

## What This Means For The Thesis

Use H5' max-aggressive to show that GAN action-space expansion improves novelty.

Use oracle-aware search to show that the pipeline can clean up the GAN output:

- remove train-template duplicates
- remove batch duplicates
- enforce balanced delimiters
- restore technique hints

Do not claim strong evasion against learned detectors.

The stronger result is now a bounded partial-positive:

```text
GAN helps produce a diverse candidate distribution; evaluator-aware post-processing selects a cleaner novelty frontier; learned-oracle evasion remains unsolved.
```

## Recommended Next Gate

The next step should not be another unbounded GAN training run.

The next useful gate is one of:

1. Add a real WAF/libinjection/ModSecurity-style oracle and compare the same selected branches.
2. Add a stronger SQLi validity oracle beyond balanced delimiters and technique hints.
3. If learned-oracle evasion remains required, train an oracle-aware generator only after adding hard validity constraints, because unconstrained evasion pressure can reward broken payloads.

