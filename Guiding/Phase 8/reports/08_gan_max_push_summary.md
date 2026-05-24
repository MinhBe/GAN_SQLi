# 08 - GAN Max Push Summary

Date: 2026-05-22

## Objective

Push the GAN branch as far as possible under the local hardware constraint:

- GPU: RTX 3050 Laptop 6GB
- RAM: 20GB

The goal is not to prove MLE is best. The thesis requirement is to use GAN for SQLi, so Phase 8 keeps GAN as the experimental center while retaining baselines for scientific comparison.

## Change Implemented

`phase08_06_paired_surgery_gan.py` now supports wider surgery action spaces:

| Slot mode | Editable positions |
|---|---|
| `placeholder` | Only delex placeholders such as `__NUM__`, `__STR__`, `__TIME__`, `__COMMENT__` |
| `local` | Placeholder + local operators/comment/connective tokens |
| `aggressive` | Local slots + technique-bearing tokens such as union/select/sleep/extractvalue/updatexml |

New launchers:

- `run_phase08_paired_surgery_gan_max_local.ps1`
- `run_phase08_paired_surgery_gan_max_aggressive.ps1`

## Main Result

The previous H5' GAN was stable but too close to anchor-only. Opening the surgery action space changed that.

| Model / Run | Slot mode | Novel vs train template | Batch template duplicate | Technique hint | Detector bypass proxy | Notes |
|---|---|---:|---:|---:|---:|---|
| Anchor-only full-lite | placeholder | 0.3125 | 0.4250 | 0.8346 | 0.1050 | Strong reconstruction, low novelty |
| Mutation-engine full-lite | rule-based | 0.6925 | 0.1925 | 0.8296 | 0.1000 | Strong non-learned novelty baseline |
| H5' adv015 sampled | placeholder | 0.1750 | 0.3900 | 0.8346 | not scored in core detector batch | Best old H5' before action expansion |
| H5' max local | local | 0.5950 | 0.2550 | 0.7744 | 0.1525 | Large GAN novelty jump |
| H5' max aggressive | aggressive | 0.8050 | 0.1725 | 0.6767 | 0.2325 | Best GAN run so far; beats mutation-engine on novelty and detector-bypass proxy |

## Training Stability

Both max runs completed on RTX 3050 6GB without OOM.

H5' max local:

- Steps: 2000
- Batch size: 64
- Mixed precision: True
- D accuracy latest: 0.8203
- Dev slot accuracy: 0.8296
- Sample unique ratio: 0.7450

H5' max aggressive:

- Steps: 2000
- Batch size: 64
- Mixed precision: True
- D accuracy latest: 0.7500
- Dev slot accuracy: 0.8093
- Sample unique ratio: 0.8275

## Interpretation

This is the strongest GAN evidence so far.

The earlier placeholder-only H5' failed to move far from anchor-only. The aggressive action space shows that the adversarial surgery setup can create substantially more novel templates and higher detector-bypass proxy than:

- anchor-only supervised infill
- mutation-engine baseline
- earlier H5' placeholder-only variants

The cost is lower conditioning hint rate, especially for boolean_blind and error_based. This is expected because aggressive surgery edits tokens that are also used by the heuristic condition detector.

## Evasion Axis Status

Evasion is now measured by a deterministic offline detector proxy:

```text
phase08_07_detector_evasion_score.py
```

This is still not a live WAF result. Do not claim real WAF bypass yet. The current claim is bounded:

```text
Paired masked surgery GAN with expanded action space improves delex-template novelty and detector-proxy bypass under the Phase 8 evaluator, while remaining trainable on 6GB VRAM.
```

## Held-Out Classifier Oracle Update

Implemented a stronger offline classifier oracle:

```text
phase08_08_heldout_classifier_oracle.py
```

The oracle trains on the Phase 8 train split, chooses its detection threshold on the dev split with a benign-FPR target, audits quality on the held-out test split, and writes evaluator-compatible CSV files.

Oracle quality:

- Train rows used: `174,956`
- Test accuracy: `0.9999`
- Test SQLi recall: `1.0000`
- Test benign FPR: `0.0190`
- Test ROC-AUC/AP: `1.0000` / `1.0000`

Classifier-oracle result on the same core generated sample batch:

| Model | Novel vs train template | Signature-proxy bypass | Classifier-oracle bypass |
|---|---:|---:|---:|
| Anchor-only full-lite | `0.3125` | `0.1050` | `0.0050` |
| Mutation-engine full-lite | `0.6925` | `0.1000` | `0.0000` |
| H5' max local | `0.5950` | `0.1525` | `0.0000` |
| H5' max aggressive | `0.8050` | `0.2325` | `0.0050` |

Updated interpretation: the GAN max-aggressive result remains the best novelty result, and it still beats the deterministic signature proxy, but it does not currently beat a held-out learned classifier oracle. The defensible claim is now bounded to novelty plus weak signature-proxy evasion. Strong evasion remains an open gate.

## Recommended Next Step

The held-out classifier oracle is now implemented and shows that current samples do not evade a strong learned detector. The next step is to improve H5' against that oracle without sacrificing structural validity:

1. Anchor-only full-lite
2. Mutation-engine full-lite
3. H5' max local
4. H5' max aggressive

The next scientific gate should require the best GAN run to maintain useful validity while improving novelty and classifier-oracle evasion, not novelty alone.
