# Timeline

This file records the work completed in this chat and anchors the moved artifacts now stored under this `Timeline` directory.

## 2026-05-29

### Step 1 - PayloadsAllTheThings Teacher Seed

- Created the initial recovery workflow.
- Downloaded PayloadsAllTheThings online.
- Processed SQL Injection Intruder files.
- Generated source card, seed inventory, normalized CSV, teacher resource report, and rule-baseline definition.
- Recorded commit `e961fef231d8327bae83b563fab50aec2e6b77c0`.
- Result: 1465 normalized rows, 1359 unique hashes, 106 duplicate rows by hash.

### Step 2 - HttpParamsDataset Teacher Source

- Downloaded HttpParamsDataset online.
- Selected `payload_full.csv` as the primary source.
- Filtered SQLi rows and generated normalized CSV, inventory, source card, report, baseline definition, and combined corpus.
- Recorded commit `926670a710283f87c05b554680facf3f9530548c`.
- Result: 10852 SQLi rows, 10852 unique hashes, 0 duplicate rows by hash.

### Step 3 - SQLiV3 Mirror Teacher Source

- Downloaded SQLiV3 mirror online.
- Selected `SQLiV3_clean.json` as the clean source.
- Filtered `type=sqli` records and refreshed the combined corpus.
- Recorded commit `486e182221e48d2cadab63edc217dfd46eb67405`.
- Result: 11347 SQLi rows, 11288 unique hashes, 59 duplicate rows by hash.
- Combined corpus after three sources: 23664 rows, 23082 unique hashes, 582 duplicate rows by hash.

### Week 1 Completion

- Completed the PayloadsAllTheThings teacher-resource artifacts.
- Added license, scope, taxonomy coverage, operator families, duplicate risk, dual-use risk, and baseline status.
- Clarified that PayloadsAllTheThings is a teacher seed and taxonomy source, not a paper-original dataset.

### Week 2 Completion

- Screened seven urgent papers.
- Created seven paper cards.
- Created paper inventory, resource inventory, and teacher-vs-paper mapping tables.
- Fixed the phase-1 role order: teacher resource first, evaluator/baseline next, GSQLi reproduction after that.

### Drift-Audit Companion

- Created `TRAJECTORY_AUDIT.md` as a companion to `RECOVERY.md`.
- Defined read order, ground-truth counts, drift checks, verification commands, and review triggers.

### Move To Timeline

- Moved all generated artifacts from the temporary working artifact root into this `Timeline` directory.
- Preserved the existing artifact structure:
  - `Data`
  - `Reports`
  - `Reproduction`
  - `Scripts`
  - `Survey`
  - `RECOVERY.md`
  - `TRAJECTORY_AUDIT.md`
- Added this `TIMELINE.md` file to summarize the work performed.

## Current Status

- Current phase: Dasari 2025 CWGAN-GP `partial_smoke` reproduction completed (artifact contract verified) under Survey + tiered reproduction evidence (see `Timeline/guiding.md`).
- Last completed step: Dasari CWGAN-GP smoke run completed with fallback mirror data; WAF-A-MoLE remains FROZEN at `threshold_reached=0`.
- Review verdict on the smoke run: process discipline PASS (full artifact contract, honest fallback labeling, no exact claim, no payload leakage, fixed seed); evidence value NOT YET EVIDENCE (detection-uplift is within noise and synthetic quality is unmeasured).
- Current WAF-A-MoLE claim: reproduction attempt completed with `threshold_reached=0`; this is not evasion success; do not invest further.
- Contribution reframed: from "evaluation protocol" to "survey with reproduction evidence".
- Teacher code = PayloadsAllTheThings = already reproduced in Week 1; no remaining debt.
- Next step: measure the existing synthetic samples through the shared evaluator (validity / uniqueness / novelty / diversity) to decide whether a fuller Dasari run is worth doing.
- Not yet completed: Dasari reproduction EVIDENCE (smoke done but not yet evidence), GSQLi conceptual reproduction, Lu 2022 operator augmentation, final comparison table, survey write-up.

## Current Next Actions

1. Measure synthetic quality first (cheapest, decides everything):
   - Run the 79 non-empty synthetic samples through `Reproduction/configs/evaluation_config.yaml`.
   - Record validity / uniqueness / novelty / diversity.
   - If validity is near zero, that is itself a valid survey finding (matches the discrete-text-GAN limitation in `2212.11119v1.md`).
2. Resolve Dasari official data status:
   - Place official Kaggle `sqli.csv` at `Timeline/Data/raw/dasari_2025/sqli.csv` if available.
   - Place `Modified SQL Dataset.csv` at `Timeline/Data/raw/dasari_2025/Modified SQL Dataset.csv` if available.
   - Record URL, license/snapshot or download date; otherwise formally declare partial with SQLiV3 replacement.
3. Only if step 1 shows promise, rerun Dasari CWGAN-GP with a fuller bounded configuration:
   - Keep checkpoint + config + log + metrics.
   - epochs 100-300, critic_steps 5, fixed TF-IDF vectorizer, XGBoost classifier, >=3 seeds with a noise band.
   - Add synthetic quality metrics; keep report claim as `partial` unless the official data snapshot is confirmed.
4. Fix `Reports/04a_dasari_cwgangp_reproduction.md`: add a caveat that the uplift is not statistically meaningful (~1 sample) and synthetic validity is not yet measured.
5. After Dasari is stable, continue in order:
   - Le 2024 GSQLi conceptual/partial reproduction.
   - Lu 2022 mutation/tamper operator augmentation.
   - Unified comparison table (keep augmentation/detection and evasion as separate metric groups).
   - Survey write-up with failure analysis and limitations.

## Resume Files

Before continuing, read:

1. `Timeline/guiding.md`
2. `Timeline/RECOVERY.md`
3. `Timeline/TRAJECTORY_AUDIT.md`
4. `Timeline/TIMELINE.md`
5. `Timeline/Reports/00_teacher_resource_inventory.md`
6. `Timeline/Reports/01_paper_screening.md`
7. `Timeline/Survey/tables/paper_inventory.csv`
8. `Timeline/Survey/tables/teacher_vs_paper_mapping.csv`
9. `Timeline/Reports/02_dataset_inventory.md`
10. `Timeline/Data/splits/split_rule.md`
11. `Timeline/Reports/03_baseline_results.md`
12. `Timeline/Reports/03d_wafamole_original_guided_long_report.md`
13. `Timeline/Reproduction/results/wafamole_original_guided_long_metrics.csv`
14. `Timeline/Reports/04a_dasari_cwgangp_reproduction.md`
15. `Timeline/Reproduction/results/dasari_cwgangp_metrics.csv`
16. `Timeline/Data/manifests/dasari_cwgangp_source_status.md`

## Notes

- The moved artifacts preserve their internal structure, but older reports may still mention paths using the previous `GAN/...` relative form.
- For new work, write artifacts under `Timeline` unless instructed otherwise.


### Week 3 Completion

- Consolidated dataset/source inventory.
- Created `Timeline/Data/manifests/dataset_inventory.csv`.
- Created `Timeline/Data/manifests/source_cards.md`.
- Created `Timeline/Reports/02_dataset_inventory.md`.
- Created exact-hash split rule and split assignment files under `Timeline/Data/splits`.
- Split counts: train 18516, validation 2274, test 2292 unique hashes.
- Combined corpus remains 23664 rows, 23082 unique hashes, 582 duplicate rows by hash.


### Week 4 Completion

- Created `Timeline/Reproduction/configs/evaluation_config.yaml`.
- Created split-aware evaluator smoke test over 45 samples.
- Wrote `Timeline/Reproduction/results/evaluator_smoke_test.md`.
- Wrote `Timeline/Reproduction/results/evaluator_smoke_metrics.csv`.
- Wrote `Timeline/Reproduction/results/evaluator_smoke_samples.csv`.
- Wrote `Timeline/Reproduction/logs/waf_smoke_test.log`.
- Validity hits: 45; needs review: 0.
- Local WAF-rule smoke blocked 27 and allowed 18.
- Real WAF engine is still not configured; do not treat local rule-smoke as final WAF ASR/FNR.


### Week 4 Real WAF Smoke Completion

- Created `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`.
- Reran the 45-sample evaluator smoke set against ModSecurity + OWASP CRS in Docker.
- Wrote `Timeline/Reproduction/results/real_waf_smoke_test.md`.
- Wrote `Timeline/Reproduction/results/real_waf_smoke_metrics.csv`.
- Wrote `Timeline/Reproduction/results/real_waf_smoke_samples.csv`.
- Real WAF blocked 41, allowed 4, and errored 0.
- Payload text was not written to reports or logs.


### Week 5 Baseline Completion

- Created `Timeline/Reproduction/configs/week5_baseline_config.yaml`.
- Created `Timeline/Reproduction/baselines/week5_baseline_definitions.md`.
- Evaluated template/rule and deterministic mutation baselines through ModSecurity + OWASP CRS Docker.
- `deterministic_mutation`: samples 60, blocked 36, allowed 24, errors 0.
- `template_rule`: samples 60, blocked 43, allowed 17, errors 0.
- Wrote `Timeline/Reproduction/results/baseline_metrics.csv`.
- Wrote `Timeline/Reproduction/results/baseline_samples.csv`.
- Wrote `Timeline/Reports/03_baseline_results.md`.
- Payload text was not written to markdown reports or logs.


### WAF-A-MoLE Smoke / Failure Completion

- Cloned WAF-A-MoLE code at `4a2cb9438f874ec0d09acaa04402174cc6334880`.
- Cloned wafamole-dataset at `b8f0118b8586f8b069ac980b3909970838f69d5e`.
- Counted wafamole-dataset rows: attacks 1286863, sane 1000217.
- Probed 9 bundled example models; 0 loaded/classified and 9 failed under the current runtime.
- Ran operator-only SqlFuzzer smoke through ModSecurity + OWASP CRS Docker: samples 40, blocked 23, allowed 17, errors 0.
- Wrote `Timeline/Reports/03b_wafamole_smoke_report.md`.
- Full guided WAF-A-MoLE reproduction remains blocked until a compatible model runtime is created or models are regenerated.


### WAF-A-MoLE Original Runtime Completion

- Added `Timeline/Reproduction/original_repro/WAFAMOLE_ORIGINAL_REPRO_POLICY.md`.
- Added legacy Docker runtime using Python 3.7.4 and scikit-learn 0.21.1.
- Built Docker image `gan-sqli-wafamole-legacy:py37`.
- Ran original runtime probe without modifying upstream WAF-A-MoLE code.
- Runtime versions confirmed: numpy 1.16.4, scipy 1.3.0, scikit-learn 0.21.1, joblib 0.13.2, sqlparse 0.3.0, networkx 2.3, click 7.0, Keras 2.2.4, TensorFlow 1.14.0.
- Bundled model probe: 5 loaded/classified, 4 failed.
- Guided engine smoke ran, but threshold was not reached in the short smoke run.
- Current claim: `guided_engine_smoke_no_evasion`, not evasion success.
- Wrote `Timeline/Reports/03c_wafamole_original_runtime_report.md`.


### WAF-A-MoLE Original Guided Long Run

- Continued original-faithful WAF-A-MoLE reproduction in Docker image `gan-sqli-wafamole-legacy:py37`.
- Ran bundled model guided attempts with max_rounds 200, round_size 20, timeout 120s, threshold 0.5.
- Models total: 5; guided attempted: 4; threshold reached: 0; skipped initial-below-threshold: 1; failed: 0.
- Wrote `Timeline/Reproduction/results/wafamole_original_guided_long_results.csv`.
- Wrote `Timeline/Reproduction/results/wafamole_original_guided_long_metrics.csv`.
- Wrote `Timeline/Reports/03d_wafamole_original_guided_long_report.md`.
- Payload text was not written to reports or logs.


### Direction Narrowing To Survey + Tiered Reproduction

- Reviewed the three Timeline files against `Mục tiêu đề tài` and clarified the real goal with the user.
- Confirmed deliverable = a survey whose empirical evidence is reproducing teacher code and the papers.
- Clarified "teacher code" = PayloadsAllTheThings (already reproduced in Week 1; no remaining debt).
- Clarified "all papers" = cover all core papers at tiered reproduction levels, not full reproduction of every paper.
- Reframed the contribution from "evaluation protocol" to "survey with reproduction evidence".
- Froze WAF-A-MoLE at `threshold_reached=0`; no further runtime/round investment.
- Set the reproduction order: Dasari 2025 CWGAN-GP (run for real) -> GSQLi conceptual -> Lu 2022 operators -> comparison table -> survey write-up.
- Created `Timeline/guiding.md` as the chosen operational direction and updated `RECOVERY.md`, `TIMELINE.md`, and `TRAJECTORY_AUDIT.md`.


### Dasari 2025 CWGAN-GP Partial Smoke Start

- Fixed the stale GSQLi drift check: GSQLi is priority 2 after Dasari, not the first reproduction target.
- Added `Timeline/Scripts/run_dasari_cwgangp_reproduction.py`.
- Ran `dasari_cwgangp_smoke_v1` with a CWGAN-GP character-level smoke implementation.
- Selected source: `Timeline/Data/raw/sqliv5-dataset/sqli.csv` as `fallback_mirror_not_exact`.
- Official Kaggle `sqli.csv` and `Modified SQL Dataset.csv` are missing locally, so this is not exact reproduction.
- Prepared rows: 3936; train 3134, validation 384, test 418.
- Synthetic samples: 80; non-empty 79; unique synthetic hashes 78.
- Detection uplift smoke F1: real-only 0.9393; real+synthetic 0.9435.
- Wrote config, prepared data, checkpoint, metrics, detection uplift, synthetic samples, data status, log, and report artifacts.
- Updated dataset inventory/source cards with Dasari official-missing and fallback-used source status.


### Dasari Smoke Review

- Reviewed the Dasari smoke run for process discipline and evidence value.
- Process discipline: PASS. Full artifact contract (config, checkpoint, log, metrics, report), honest `fallback_mirror_not_exact` labeling, no exact claim, no payload leakage, fixed seed, real CWGAN-GP code (not a stub).
- Evidence value: NOT YET EVIDENCE. Recorded these known issues:
  - Detection uplift is within noise: test 418 rows, precision 1.0000 in both runs, F1 gain equals roughly one extra correctly-classified sample; one seed, one split.
  - Generator is effectively untrained (epochs 1, critic_steps 1, ~24 batches; `last_generator_loss=-0.004982`); synthetic samples are likely low-validity character noise.
  - Synthetic quality (validity / novelty / diversity) was not measured through the shared evaluator.
  - Uplift comparison refits a separate TF-IDF vectorizer for the augmented model; representation must be held fixed.
  - The run uses its own hash split (`dasari-cwgangp-v1:`), not the canonical `split_rule`.
- Reset the next step to: measure synthetic quality through the shared evaluator first, before any fuller training run.
- Updated `RECOVERY.md`, `TIMELINE.md`, and `TRAJECTORY_AUDIT.md` to reflect this verdict and the reprioritized next steps.
- Payload text was not written to markdown reports or logs.


### Current Checkpoint - After Dasari Smoke

- Timestamp: `2026-05-29T16:23:58+07:00`.
- Current stage: after Dasari 2025 CWGAN-GP `partial_smoke`.
- What has been reached:
  - Survey direction is locked.
  - Teacher code reproduction is complete.
  - Evaluator/split/baseline infrastructure is complete.
  - WAF-A-MoLE is frozen at honest failure result `threshold_reached=0`.
  - Dasari reproduction path has a runnable smoke implementation and complete artifact contract.
- What this does not prove yet:
  - It is not exact Dasari reproduction.
  - It does not use official Kaggle `sqli.csv` locally yet.
  - It does not use `Modified SQL Dataset.csv` locally yet.
  - The observed F1 uplift is smoke evidence only, not final thesis evidence.
- Immediate next work:
  - Prefer resolving official Dasari data first.
  - If official data cannot be obtained quickly, run a fuller `partial` Dasari experiment on the fallback source and state the limitation explicitly.
