# Phase 5 Artifact Manifest

> Preparation date: 2026-05-22  
> Status: prepared only. Full labeling has not been run by this preparation step.  
> Contract: all Phase 5 scripts, launchers, logs, progress files, outputs, reports, and summaries stay under `Guiding/Phase 5`.

## Input

Phase 5 reads the cleaned Phase 4 full foundation from:

```text
Guiding/Phase 4/outputs/full/phase04_payload_foundation.parquet
```

Required input columns:

```text
row_id
payload_working
payload_delex_v5
lane
split
near_dup_cluster_id
delex_collision_key
duplicate_count
```

## Prepared Structure

```text
Guiding/Phase 5/
  phase05_full_label_system.py
  run_phase05_full.ps1
  run_phase05_full.cmd
  PHASE5_ARTIFACT_MANIFEST.md
  Tổng kết Phase 5.md
  outputs/
    full/
    sanity/
  logs/
  reports/
```

## Labeling Mode

Default execution is detector-only and offline. The wrapper imports:

```text
Skill/label-sqli/scripts/cascade_labeler.py
```

No API or network review is called by the prepared script.

## Full Outputs

When the full launcher is run, these files are written to:

```text
Guiding/Phase 5/outputs/full/
```

Expected files:

```text
phase05_labeled.parquet
gold.parquet
silver.parquet
bronze.parquet
review_queue.parquet
verified_dev.parquet
verified_test.parquet
label_distribution.json
conflict_summary.json
```

## Reports

When a run completes, reports are written to:

```text
Guiding/Phase 5/reports/
```

Expected files:

```text
05_full_label_system_report.md
05_label_distribution.md
05_conflict_report.md
05_gold_quality_report.md
```

The top-level summary is:

```text
Guiding/Phase 5/Tổng kết Phase 5.md
```

## Logs And Progress

Full launcher logs:

```text
Guiding/Phase 5/logs/phase05_full_run.log
Guiding/Phase 5/logs/phase05_full_run.err.log
Guiding/Phase 5/logs/phase05_full_progress.json
```

Direct sanity runs with `--limit` default to:

```text
Guiding/Phase 5/outputs/sanity/
Guiding/Phase 5/logs/phase05_sanity_progress.json
```

## Commands

Compile check:

```powershell
python -m py_compile "Guiding\Phase 5\phase05_full_label_system.py"
```

Future sanity run:

```powershell
python -u -B "Guiding\Phase 5\phase05_full_label_system.py" --limit 10000
```

Future full run:

```powershell
Guiding\Phase 5\run_phase05_full.cmd
```

## Path Guardrails

The prepared Phase 5 script defaults to internal paths only:

```text
Guiding/Phase 5/outputs/full
Guiding/Phase 5/outputs/sanity
Guiding/Phase 5/logs
Guiding/Phase 5/reports
```

It does not default to `data/phase05` or root-level `reports`.

The wrapper also rejects `--out-dir`, `--report-dir`, `--log-dir`, or `--progress-file` values that resolve outside `Guiding/Phase 5`.
