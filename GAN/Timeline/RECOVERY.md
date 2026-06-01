# Recovery

- Current phase: Dasari 2025 CWGAN-GP `partial_smoke` reproduction completed under Survey + tiered reproduction evidence (see `Timeline/guiding.md`)
- Last completed step: Dasari CWGAN-GP smoke run completed (artifact contract verified) with fallback mirror data; WAF-A-MoLE remains FROZEN at `threshold_reached=0`
- Next exact step: Measure the existing synthetic samples through the shared evaluator (validity / uniqueness / novelty / diversity) to decide whether a fuller Dasari run is worth doing
- Review verdict on the smoke run:
  - Process discipline: PASS (full artifact contract, honest fallback labeling, no exact claim, no payload leakage, fixed seed).
  - Evidence value: NOT YET EVIDENCE. The detection-uplift table is within noise and the synthetic quality is unmeasured.
- Direction note:
  - Contribution reframed from "evaluation protocol" to "survey with reproduction evidence".
  - Teacher code = PayloadsAllTheThings = already reproduced in Week 1 (taxonomy + rule/mutation baseline); no remaining debt.
  - "All papers" = cover all core papers at TIERED reproduction levels (exact/partial/conceptual/cite-only), not full reproduction of every paper.
  - Evaluator/splits/baselines built in Week 1-5 are now measurement TOOLS for the reproductions, not the main contribution.
- Reproduction tiers (see `Timeline/guiding.md` section 3):
  - Dasari 2025 CWGAN-GP: partial -> exact (run for real, Kaggle data) — priority 1; current artifact is `partial_smoke` using fallback mirror data, not exact
  - Le 2024 GSQLi: conceptual/partial (no open code/data) — priority 2
  - Lu 2022 GAN SQLi: conceptual (data not public)
  - Demetrio 2020 WAF-A-MoLE: FROZEN at `threshold_reached=0`
  - Goodfellow / WGAN-GP / DCGAN / Text GAN survey / BERT-GAN: cite-only or related-work
- WAF-A-MoLE results (frozen):
  - Models total: 5
  - Guided attempted: 4
  - Threshold reached: 0
  - Skipped initial-below-threshold: 1
  - Failed: 0
  - Runtime: Docker image `gan-sqli-wafamole-legacy:py37`, max_rounds 200, round_size 20, timeout 120s, threshold 0.5
- Dasari CWGAN-GP smoke results:
  - Run id: `dasari_cwgangp_smoke_v1`
  - Reproduction level: `partial_smoke`
  - Source status: `fallback_mirror_not_exact` (SQLiV5/SQLiV3 mirror `sqli.csv`, not Dasari's Kaggle data)
  - Prepared rows: 3936 (label 0: 2999, label 1: 937)
  - Train/validation/test rows: 3134 / 384 / 418
  - Synthetic samples: 80; non-empty: 79; unique hashes: 78
  - Detection uplift smoke F1: real-only 0.9393; real+synthetic 0.9435
  - Official Kaggle `sqli.csv`: missing locally
  - `Modified SQL Dataset.csv`: missing locally
- Known issues to fix before this counts as Dasari reproduction evidence:
  - Uplift is within noise: test set is 418 rows, precision is 1.0000 in both, and the F1 gain equals roughly one extra correctly-classified sample; one seed, one split. Do NOT present it as "augmentation helps".
  - Generator is effectively untrained (epochs 1, critic_steps 1, ~24 batches; `last_generator_loss=-0.004982`); synthetic samples are likely low-validity character noise.
  - Synthetic quality (validity / novelty / diversity) was NOT measured through the shared evaluator.
  - Uplift comparison refits a separate TF-IDF vectorizer for the augmented model; representation must be held fixed for a fair comparison.
  - The run uses its own hash split (`dasari-cwgangp-v1:`), not the canonical `split_rule`; reconcile or document.
- Prioritized next steps:
  1. Run the 79 synthetic samples through `Reproduction/configs/evaluation_config.yaml` to get validity/uniqueness/novelty/diversity. If validity is near zero, that is itself a valid survey finding (matches the discrete-text-GAN limitation).
  2. Resolve official Dasari data status: place Kaggle `sqli.csv` + `Modified SQL Dataset.csv` under `Data/raw/dasari_2025/` with URL and download date, or formally declare partial with SQLiV3 replacement.
  3. If step 1 shows promise, run ONE fuller bounded training: epochs 100-300, critic_steps 5, fixed vectorizer, XGBoost classifier, >=3 seeds with a noise band, plus synthetic quality metrics.
  4. Add a caveat to `Reports/04a_dasari_cwgangp_reproduction.md` stating the uplift is not statistically meaningful and synthetic validity is not yet measured.
  5. After Dasari is stable: Le 2024 GSQLi conceptual, then Lu 2022 operators, then unified comparison table (keep augmentation/detection and evasion as separate metric groups), then survey write-up.
- Claim rule:
  - Only rows with `status=threshold_reached` count as WAF-A-MoLE evasion success.
  - Rows skipped because the initial payload was already below threshold are not guided evasion successes.
  - No method is claimed "trained" or "reproduced" without checkpoint, config, logs, and metrics.
  - A smoke run that satisfies the artifact contract is NOT yet reproduction evidence until synthetic quality and an interpretable result exist.
