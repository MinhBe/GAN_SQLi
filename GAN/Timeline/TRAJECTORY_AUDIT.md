# Trajectory Audit

Purpose: this file is the companion to `Timeline/RECOVERY.md`. Use it before continuing work to check whether the project is still following the planned phase-1 trajectory, whether artifacts contradict each other, and whether any step needs review before moving on.

## Read Order

Read these files in order (read `Timeline/guiding.md` first as the chosen direction):

1. `Timeline/guiding.md`
2. `Timeline/RECOVERY.md`
3. `Timeline/Reports/00_teacher_resource_inventory.md`
4. `Timeline/Reports/01_paper_screening.md`
5. `Timeline/Data/manifests/payloadsallthethings_sqli_source_card.md`
6. `Timeline/Survey/tables/paper_inventory.csv`
7. `Timeline/Survey/tables/resource_inventory.csv`
8. `Timeline/Survey/tables/teacher_vs_paper_mapping.csv`
9. `Timeline/Data/manifests/dataset_inventory.csv`
10. `Timeline/Data/splits/split_rule.md`
11. `Timeline/Data/manifests/teacher_seed_inventory.csv`
12. `Timeline/Reproduction/baselines/payloadsallthethings_rule_baseline.md`
13. `Timeline/Reproduction/configs/evaluation_config.yaml`
14. `Timeline/Reproduction/results/evaluator_smoke_test.md`
15. `Timeline/Reproduction/logs/waf_smoke_test.log`
16. `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`
17. `Timeline/Reproduction/results/real_waf_smoke_test.md`
18. `Timeline/Reproduction/logs/real_waf_smoke_test.log`
19. `Timeline/Reproduction/configs/week5_baseline_config.yaml`
20. `Timeline/Reproduction/results/baseline_metrics.csv`
21. `Timeline/Reports/03_baseline_results.md`
22. `Timeline/Reproduction/results/wafamole_smoke_metrics.csv`
23. `Timeline/Reports/03b_wafamole_smoke_report.md`
24. `Timeline/Reproduction/original_repro/WAFAMOLE_ORIGINAL_REPRO_POLICY.md`
25. `Timeline/Reproduction/results/wafamole_original_runtime_metrics.csv`
26. `Timeline/Reports/03c_wafamole_original_runtime_report.md`
27. `Timeline/Reproduction/configs/wafamole_original_guided_long_config.yaml`
28. `Timeline/Reproduction/results/wafamole_original_guided_long_metrics.csv`
29. `Timeline/Reports/03d_wafamole_original_guided_long_report.md`
30. `Timeline/Reports/04a_dasari_cwgangp_reproduction.md`
31. `Timeline/Reproduction/results/dasari_cwgangp_metrics.csv`
32. `Timeline/Reproduction/results/dasari_cwgangp_detection_uplift.csv`
33. `Timeline/Data/manifests/dasari_cwgangp_source_status.md`

If the task concerns dataset/source inventory, also read:

1. `Timeline/Data/manifests/httpparams_sqli_inventory.csv`
2. `Timeline/Data/manifests/sqliv3_sqli_inventory.csv`
3. `Timeline/Data/manifests/httpparamsdataset_sqli_source_card.md`
4. `Timeline/Data/manifests/sqliv3_sqli_source_card.md`
5. `Timeline/Reports/01_httpparams_teacher_resource_inventory.md`
6. `Timeline/Reports/02_sqliv3_teacher_resource_inventory.md`

If the task concerns reproducibility or generated data, also read:

1. `Timeline/Scripts/build_payloadsallthethings_teacher_seed.py`
2. `Timeline/Scripts/build_httpparams_teacher_seed.py`
3. `Timeline/Scripts/build_sqliv3_teacher_seed.py`
4. `Timeline/Scripts/build_week1_week2_artifacts.py`

## Current Trajectory

- Week 1: teacher resource first, using PayloadsAllTheThings SQL Injection.
- Week 2: screen seven urgent papers and map them against the teacher resource.
- Week 3: dataset/source inventory and exact-hash split rule completed.
- Week 4: evaluator smoke and real WAF smoke completed.
- Week 5: minimum template/rule and deterministic mutation baselines completed with real-WAF metrics.
- WAF-A-MoLE original-faithful runtime established: Python 3.7.4, scikit-learn 0.21.1, bundled model probe works for 5 of 9 models.
- WAF-A-MoLE original guided long run completed: guided attempts ran for 4 models, `threshold_reached=0`, and no WAF-A-MoLE evasion success may be claimed.
- Direction narrowed: deliverable is a survey with reproduction evidence, not an evaluation protocol contribution. See `Timeline/guiding.md`.
- Teacher code = PayloadsAllTheThings = already reproduced in Week 1; no remaining debt.
- "All papers" means cover all core papers at tiered reproduction levels (exact/partial/conceptual/cite-only), not full reproduction of every paper.
- WAF-A-MoLE is FROZEN at `threshold_reached=0`; no further runtime/round investment.
- Dasari 2025 CWGAN-GP partial smoke run completed the first runnable paper reproduction. It used fallback mirror data and must not be treated as exact reproduction.
- Dasari smoke review verdict: process discipline PASS, but NOT YET EVIDENCE. Uplift is within noise (~1 sample), generator is effectively untrained, and synthetic quality was not measured through the shared evaluator.
- Next trajectory step: measure the existing synthetic samples through the shared evaluator (validity/uniqueness/novelty/diversity) FIRST; then resolve official Dasari data status; then a fuller bounded Dasari run only if synthetic quality shows promise; then GSQLi conceptual, then Lu 2022 operators, then comparison table and survey write-up.

## Key Ground Truth

- Primary teacher source: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- PayloadsAllTheThings commit: `e961fef231d8327bae83b563fab50aec2e6b77c0`
- HttpParams source: `https://github.com/Morzeux/HttpParamsDataset`
- HttpParams commit: `926670a710283f87c05b554680facf3f9530548c`
- SQLiV3 mirror source: `https://github.com/nidnogg/sqliv5-dataset`
- SQLiV3 mirror commit: `486e182221e48d2cadab63edc217dfd46eb67405`
- PayloadsAllTheThings rows: 1465
- HttpParams SQLi rows: 10852
- SQLiV3 mirror SQLi rows: 11347
- Combined rows: 23664
- Combined unique payload hashes: 23082
- Combined duplicate rows by payload hash: 582
- Paper cards expected: 7
- Paper inventory rows expected: 7
- Teacher-paper mapping rows expected: 7

- Split counts: train 18516, validation 2274, test 2292 unique hashes
- Evaluator smoke samples: 45 with local WAF-rule blocked 27 and allowed 18
- Real WAF smoke samples: 45 with ModSecurity+CRS blocked 41 and allowed 4
- Week 5 baseline rows: 120 across template_rule and deterministic_mutation
- WAF-A-MoLE operator smoke rows: 40 with blocked 23 and allowed 17
- WAF-A-MoLE original runtime: 5/9 bundled models loaded/classified; guided smoke OK 1; threshold reached 0
- WAF-A-MoLE original guided long run: models total 5, guided attempted 4, threshold reached 0, skipped initial-below-threshold 1, failed 0
- WAF-A-MoLE claim rule: only rows with `status=threshold_reached` count as guided evasion success
- Dasari CWGAN-GP smoke run: `partial_smoke`, source status `fallback_mirror_not_exact`, prepared rows 3936, train/validation/test 3134/384/418, synthetic samples 80, synthetic non-empty 79
- Dasari detection uplift smoke: char TF-IDF logistic regression F1 real-only 0.9393; real+synthetic 0.9435
- Dasari official Kaggle `sqli.csv`: missing locally
- Dasari `Modified SQL Dataset.csv`: missing locally
- Dasari smoke evidence status: NOT YET EVIDENCE; uplift within noise, synthetic validity unmeasured, generator effectively untrained

## Drift Checks

Check for these signs before continuing:

| Check | Expected state | Review if |
| --- | --- | --- |
| Recovery phase | Dasari CWGAN-GP partial smoke started after WAF-A-MoLE freeze and Week 5 baseline | It claims selected GSQLi reproduction, full GAN training, or final comparison already completed |
| Teacher-first rule | PayloadsAllTheThings remains the first resource | A report treats HttpParams or SQLiV3 as the initial teacher source |
| Paper screening | Exactly seven urgent papers are screened | Paper count is not seven or labels differ from the plan |
| Dataset identity | PayloadsAllTheThings is a seed/replacement corpus | It is described as a paper-original dataset |
| GSQLi role | Le 2024 is the priority-2 conceptual/partial reproduction after Dasari CWGAN-GP | It is treated as already reproduced, trained, or started before Dasari without an explicit reason |
| Baseline status | Week 5 minimum baselines have real-WAF metrics | Reports claim final comparison metrics before selected GSQLi reproduction exists |
| Payload exposure | Reports contain taxonomy and counts only | Detailed payload strings appear in markdown reports |
| Path hygiene | Current artifacts are stored under `Timeline/...` | Reports include local absolute paths or unrelated offline-source markers |
| WAF-A-MoLE claim | Guided long run is recorded as no evasion success because `threshold_reached=0` | Work claims WAF-A-MoLE evasion success before threshold-reaching guided artifacts exist |
| WAF-A-MoLE frozen | WAF-A-MoLE stays at `threshold_reached=0`, no further runs | New WAF-A-MoLE runtime/round runs appear after the freeze decision |
| Dasari source status | Current Dasari artifact is `partial_smoke` using fallback mirror data | It is claimed as exact reproduction before official Kaggle snapshot and modified dataset are recorded |
| Dasari evidence status | Smoke run is recorded as NOT YET EVIDENCE | The detection-uplift number is presented as a real augmentation gain, or synthetic quality is still unmeasured when Dasari is called reproduced |
| Contribution framing | Deliverable is a survey with reproduction evidence | A report treats "evaluation protocol" as the main contribution |
| Teacher code status | PayloadsAllTheThings reproduction is complete (Week 1) | Work reopens teacher-code reproduction as if still pending, or treats PayloadsAllTheThings as runnable model code |
| Reproduction tiering | Each core paper carries an explicit tier (exact/partial/conceptual/cite-only) | A paper is claimed fully reproduced without its tier and evidence, or every paper is forced to full reproduction |
| Next step | Measure Dasari synthetic quality through the shared evaluator first, then resolve official data, then a fuller bounded run, then GSQLi conceptual, then Lu 2022 operators, then comparison table | Work starts a fuller Dasari run before synthetic quality is measured, or starts unrelated GAN training/final comparison before Dasari/GSQLi reproductions exist |

## Commands For Verification

Use these checks from the directory that contains `Timeline`:

```powershell
python -X utf8 -c "import csv; print(sum(1 for _ in csv.DictReader(open('Timeline/Survey/tables/paper_inventory.csv', encoding='utf-8'))))"
python -X utf8 -c "import csv; print(sum(1 for _ in csv.DictReader(open('Timeline/Survey/tables/teacher_vs_paper_mapping.csv', encoding='utf-8'))))"
python -X utf8 -c "import csv,collections; rows=list(csv.DictReader(open('Timeline/Data/processed/teacher_seed_sqli_normalized_combined.csv', encoding='utf-8'))); c=collections.Counter(r['normalized_sha256'] for r in rows); print(len(rows)); print(len(c)); print(sum(v-1 for v in c.values() if v>1))"
python -X utf8 -c "from pathlib import Path; slash=chr(47); bs=chr(92); toks=[chr(58)+bs,slash+'Users'+slash,slash+'home'+slash,'Doc'+'uments'+bs,'Doc'+'uments'+slash]; roots=['Timeline/RECOVERY.md','Timeline/TRAJECTORY_AUDIT.md','Timeline/TIMELINE.md','Timeline/Reports','Timeline/Data/manifests','Timeline/Data/splits','Timeline/Reproduction/baselines','Timeline/Survey','Timeline/Scripts']; bad=[]; [bad.append(str(p)) for r in roots for p in ([Path(r)] if Path(r).is_file() else Path(r).rglob('*')) if p.is_file() and any(t in p.read_text(encoding='utf-8', errors='ignore') for t in toks)]; print('\n'.join(bad))"
```

Expected command results:

- `paper_inventory.csv`: 7 rows
- `teacher_vs_paper_mapping.csv`: 7 rows
- Combined corpus: 23664 rows, 23082 unique hashes, 582 duplicate rows
- Path hygiene scan: no matches

## Review Triggers

Stop and review before continuing if any of these occur:

- A new artifact claims a GAN model was trained without checkpoint, config, logs, and metrics.
- A report claims final WAF/ASR/FNR results from local rule-smoke instead of `real_waf_smoke_*` artifacts.
- A markdown report prints detailed bypass payload strings.
- A source is added without source URL, commit/hash or retrieval timestamp.
- Any generated artifact depends on a non-`GAN` local path for reproducibility.
- Week 4 outputs are skipped: evaluator config, evaluator smoke result, local WAF note, and real-WAF smoke result.
- WAF-A-MoLE evasion success is claimed from skipped initial-below-threshold rows instead of `status=threshold_reached`.
- A new WAF-A-MoLE run is started after the freeze decision instead of keeping `threshold_reached=0`.
- A paper is claimed reproduced without an explicit tier (exact/partial/conceptual/cite-only) and supporting evidence.
- The deliverable is described as an "evaluation protocol" contribution instead of a survey with reproduction evidence.
- Dasari smoke artifacts are cited as exact reproduction despite `fallback_mirror_not_exact`.
- The Dasari detection-uplift number is presented as a meaningful augmentation gain despite being within noise.
- A fuller Dasari training run is started before synthetic quality is measured through the shared evaluator.

## Last Updated

`2026-05-29T17:05:00+07:00`
