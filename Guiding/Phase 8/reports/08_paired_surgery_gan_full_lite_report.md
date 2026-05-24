# 08 - H5' Paired Surgery GAN Pilot Report

Scope: adversarial slot-surgery pilot, not full-sequence GAN.

## Hardware-Aware Config

- Device: `cuda`
- CUDA available: `True`
- Train rows used: `300,000`
- Dev rows used: `25,000`
- Batch size: `64`
- Max steps: `1500`
- Max len: `96`
- Embed/hidden/D-hidden: `64` / `128` / `128`
- Mixed precision: `True`
- Anchor init: `{'loaded': True, 'path': 'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Guiding\\Phase 8\\checkpoints\\surgery_baselines_full_lite\\anchor_only_latest.pt', 'matched_keys': 11, 'total_keys': 11}`

## Latest Metrics

- Step: `1500`
- Loss D: `1.344191`
- Loss G: `0.050507`
- Loss anchor: `0.010494`
- Loss adversarial: `0.800566`
- Slot entropy: `0.007648`
- D accuracy: `0.5391`
- D frozen on latest step: `False`
- Dev slot loss: `0.077669`
- Dev slot accuracy: `0.9870`
- Sample unique ratio: `0.5725`
- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\paired_surgery_gan_full_lite\paired_surgery_gan_samples.jsonl`

## Gate

- Compare this report against anchor-only and mutation-engine under `phase08_03_evaluator_contract.py`.
- Continue H5' only if adversarial training improves validity/novelty/evasion over anchor-only, not merely over full-sequence Gumbel.
