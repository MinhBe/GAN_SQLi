# 08 - H5' Paired Surgery GAN Pilot Report

Scope: adversarial slot-surgery pilot, not full-sequence GAN.

## Hardware-Aware Config

- Device: `cuda`
- CUDA available: `True`
- Train rows used: `300,000`
- Dev rows used: `25,000`
- Batch size: `64`
- Max steps: `2000`
- Max len: `96`
- Slot mode: `aggressive`
- Embed/hidden/D-hidden: `64` / `128` / `192`
- Mixed precision: `True`
- Anchor init: `{'loaded': True, 'path': 'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Guiding\\Phase 8\\checkpoints\\surgery_baselines_full_lite\\anchor_only_latest.pt', 'matched_keys': 11, 'total_keys': 11}`

## Latest Metrics

- Step: `2000`
- Loss D: `1.041628`
- Loss G: `0.835538`
- Loss anchor: `0.493073`
- Loss adversarial: `1.548558`
- Slot entropy: `0.057521`
- D accuracy: `0.7500`
- D frozen on latest step: `False`
- Dev slot loss: `0.866331`
- Dev slot accuracy: `0.8093`
- Sample unique ratio: `0.8275`
- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\paired_surgery_gan_max_aggressive\paired_surgery_gan_samples.jsonl`

## Gate

- Compare this report against anchor-only and mutation-engine under `phase08_03_evaluator_contract.py`.
- Continue H5' only if adversarial training improves validity/novelty/evasion over anchor-only, not merely over full-sequence Gumbel.
