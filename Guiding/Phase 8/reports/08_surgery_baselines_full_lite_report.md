# 08 - Surgery Baselines Report

Scope: pre-H5' baselines only. Anchor-only uses CE reconstruction; mutation-engine is non-learned.

## Hardware-Aware Config

- Device: `cuda`
- CUDA available: `True`
- Train rows used: `300,000`
- Dev rows used: `25,000`
- Batch size: `64`
- Max steps: `1000`
- Max len: `96`
- Embed/hidden: `64` / `128`
- Mixed precision: `True`

## Anchor-Only

- Final step: `1000`
- Final train loss: `0.017805`
- Dev slot loss: `0.085824`
- Dev slot accuracy: `0.9821`
- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\surgery_baselines_full_lite\anchor_only_samples.jsonl`
- Unique ratio: `0.5750`

## Mutation Engine

- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\surgery_baselines_full_lite\mutation_engine_samples.jsonl`
- Unique ratio: `0.8175`

## Next Gate

Run `phase08_03_evaluator_contract.py` on both sample files before H5'. H5' should only be trained after these baselines are visible in the same validity/novelty/evasion table.
