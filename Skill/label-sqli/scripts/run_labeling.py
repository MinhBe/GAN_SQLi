import sys
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
run_labeling.py -- CLI orchestrator for label-sqli (4-tier cascade architecture)

Two-pass pipeline:
  Pass 1: Script cascade (Tier 1→2→3→benign) labels ~75-85% of rows
          Use --detector_only to stop here and export a needs_ai_report.csv
  Pass 2: low_confidence + tier4 rows → AI chat review (batched, optional)
  Merge:  AI results override script labels for reviewed rows

Usage:
    python run_labeling.py --input raw.csv --output labeled.csv --detector_only
    python run_labeling.py --input raw.csv --output labeled.csv --dry_run
    python run_labeling.py --input raw.csv --output labeled.csv --ai_cap 5000
"""

import argparse
import time
import json
import random
from pathlib import Path

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from cascade_labeler import label_batch, VALID_TYPES, VALID_ENGINES
from ai_reviewer import review_batch

CHECKPOINT_EVERY = 10_000


def _ckpt(output: Path, step: str) -> Path:
    return output.parent / f".ckpt2_{output.stem}_{step}.parquet"


def _load_ckpt(path: Path) -> 'pd.DataFrame | None':
    if path.exists():
        print(f"[INFO] Resuming from checkpoint: {path.name}")
        return pd.read_parquet(path)
    return None


def _save_ckpt(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=False)
    print(f"[INFO] Checkpoint saved: {path.name} ({len(df):,} rows)")


# ===========================================================================
# PASS 1: Script cascade
# ===========================================================================

def pass1_cascade(df: pd.DataFrame, payload_col: str,
                  output_path: Path) -> pd.DataFrame:
    """Run cascade labeler on all rows. Returns result DataFrame."""
    ckpt = _ckpt(output_path, 'pass1')
    cached = _load_ckpt(ckpt)
    if cached is not None:
        return cached

    payloads = df[payload_col].astype(str).tolist()
    n = len(payloads)
    print(f"[INFO] Pass 1 (cascade) on {n:,} rows...")
    t0 = time.time()

    all_results = []
    for i in range(0, n, CHECKPOINT_EVERY):
        chunk = payloads[i:i + CHECKPOINT_EVERY]
        all_results.extend(label_batch(chunk, progress_every=CHECKPOINT_EVERY))
        elapsed = time.time() - t0
        rate = (i + len(chunk)) / elapsed if elapsed > 0 else 0
        eta = (n - i - len(chunk)) / rate if rate > 0 else 0
        print(f"[INFO] Pass 1: {i+len(chunk):,}/{n:,} rows "
              f"({rate:.0f} rows/s, ETA {eta/60:.1f} min)")

    result = pd.DataFrame(all_results)
    _save_ckpt(result, ckpt)
    return result


# ===========================================================================
# COVERAGE MONITOR: detect sparse cells after Pass 1
# ===========================================================================

def coverage_report(result_df: pd.DataFrame) -> dict:
    """
    Count rows per (sqli_type, db_engine) cell.
    Returns {(type, engine): count} for all 20 cells.
    """
    TYPES   = ['time_blind', 'boolean_blind', 'union_based', 'error_based', 'benign']
    ENGINES = ['mysql', 'postgres', 'oracle', 'mssql', 'sqlite', 'unknown']
    counts  = {}
    pivot   = result_df[result_df['sqli_type'].notna()].groupby(
        ['sqli_type', 'db_engine']).size()
    for t in TYPES:
        for e in ENGINES:
            counts[(t, e)] = int(pivot.get((t, e), 0))
    return counts


def log_coverage(counts: dict, sparse_threshold: int = 20) -> list:
    TYPES   = ['time_blind', 'boolean_blind', 'union_based', 'error_based', 'benign']
    ENGINES = ['mysql', 'postgres', 'oracle', 'mssql', 'sqlite', 'unknown']
    sparse  = [(t, e) for t in TYPES for e in ENGINES
               if counts.get((t, e), 0) < sparse_threshold]
    print(f"\n[INFO] Coverage: {len(counts) - len(sparse)}/20 cells dense "
          f"(>= {sparse_threshold} rows)")
    if sparse:
        print(f"[WARN] {len(sparse)} sparse cells:")
        for t, e in sparse:
            print(f"  {t} x {e}: {counts.get((t,e), 0)} rows")
    else:
        print("[OK] All 20 cells dense")
    return sparse


# ===========================================================================
# DETECTOR-ONLY REPORT: export needs-AI candidates without calling AI
# ===========================================================================

def _export_needs_ai_report(result_df: 'pd.DataFrame', payloads: list, output_path: Path) -> None:
    """Export rows needing AI review to a separate CSV after Pass 1 completes."""
    mask = result_df['needs_ai'] | (result_df['confidence'] < 0.70)
    candidates = result_df[mask].copy()
    payload_col_vals = [payloads[i] for i in candidates.index]
    candidates.insert(0, 'payload', payload_col_vals)
    report_path = output_path.parent / f"{output_path.stem}_needs_ai_report.csv"
    candidates.to_csv(report_path, encoding='utf-8-sig', index=True, index_label='original_row')
    pct = len(candidates) / max(len(result_df), 1) * 100
    print(f"[INFO] Needs-AI report: {len(candidates):,} rows ({pct:.1f}%) → {report_path.name}")


# ===========================================================================
# PASS 2: AI review for low-confidence + sparse cells
# ===========================================================================

def select_ai_candidates(result_df: pd.DataFrame, payloads: list,
                          cell_counts: dict, ai_cap: int,
                          sparse_threshold: int = 20,
                          high_conf_sample_pct: float = 0.10) -> list:
    """
    Select indices for AI review:
    1. All needs_ai=True rows (tier4 + low_confidence tier3)
    2. Random sample of high-confidence rows (cross-check per Agrasp_2024)
    3. Cap at ai_cap total
    """
    needs_ai_idx = result_df.index[result_df['needs_ai'] == True].tolist()

    # High-confidence sample for cross-checking
    high_conf = result_df[
        (result_df['confidence'] >= 0.85) &
        (result_df['needs_ai'] == False)
    ]
    sample_n = int(len(high_conf) * high_conf_sample_pct)
    if sample_n > 0:
        random.seed(42)
        sample_idx = random.sample(high_conf.index.tolist(), min(sample_n, len(high_conf)))
    else:
        sample_idx = []

    combined = list(set(needs_ai_idx + sample_idx))

    # Cap
    if len(combined) > ai_cap:
        random.seed(42)
        combined = random.sample(combined, ai_cap)
        print(f"[WARN] AI candidates {len(needs_ai_idx)+len(sample_idx):,} > cap {ai_cap:,}")
        print(f"[INFO] Sampled {ai_cap:,} rows for AI review")
    else:
        print(f"[INFO] AI candidates: {len(needs_ai_idx):,} needs_ai "
              f"+ {len(sample_idx):,} high-conf sample = {len(combined):,} total")

    return sorted(combined)


def apply_ai_results(result_df: pd.DataFrame, ai_results: dict,
                     high_conf_ai_idx: set) -> pd.DataFrame:
    """
    Merge AI results back into result_df.
    For high-confidence cross-check rows: if AI disagrees, flag but keep AI label.
    Preserves script prediction in label_agreement column (#6 double-score).
    """
    df = result_df.copy()
    if 'ai_conflict' not in df.columns:
        df['ai_conflict'] = False
    if 'label_agreement' not in df.columns:
        df['label_agreement'] = ''

    conflict_count = 0
    for idx, ai in ai_results.items():
        ai_type = ai.get('sqli_type')
        ai_eng  = ai.get('db_engine', 'unknown')
        ai_conf = float(ai.get('confidence', 0.72))

        if ai_type not in VALID_TYPES:
            ai_type = None
        if ai_eng not in VALID_ENGINES:
            ai_eng = 'unknown'

        if ai_type is None:
            continue

        # Cross-check: did AI disagree with high-confidence script label?
        if idx in high_conf_ai_idx:
            orig_type = df.at[idx, 'sqli_type']
            if orig_type != ai_type:
                df.at[idx, 'ai_conflict'] = True
                conflict_count += 1

        # Double-score: record script vs AI agreement (#6)
        script_type = df.at[idx, 'script_sqli_type'] if 'script_sqli_type' in df.columns else df.at[idx, 'sqli_type']
        df.at[idx, 'label_agreement'] = 'agree' if ai_type == script_type else 'disagree'

        df.at[idx, 'sqli_type']    = ai_type
        df.at[idx, 'db_engine']    = ai_eng
        df.at[idx, 'confidence']   = ai_conf
        df.at[idx, 'label_source'] = 'tier4_ai'
        df.at[idx, 'tier']         = ('gold' if ai_conf >= 0.85 else
                                       'silver' if ai_conf >= 0.70 else 'bronze')
        df.at[idx, 'needs_ai']     = False

    if conflict_count > 0:
        conflict_rate = conflict_count / max(len(high_conf_ai_idx), 1)
        flag = "[WARN]" if conflict_rate > 0.15 else "[OK]"
        print(f"{flag} AI cross-check: {conflict_count}/{len(high_conf_ai_idx)} "
              f"conflicts ({conflict_rate:.1%}) on high-confidence rows")
        if conflict_rate > 0.15:
            print("  → High conflict rate: consider reviewing Tier 1/2 patterns")

    return df


# ===========================================================================
# BENCHMARK + GOLD SET (#9 stop condition)
# ===========================================================================

def _compute_benchmark(df: pd.DataFrame) -> dict:
    """Compute coverage and entropy metrics for iteration stop-condition."""
    import math
    t4 = (df['label_source'] == 'tier4_ai_needed').sum()
    labeled = df[df['sqli_type'].notna() & (df['sqli_type'] != 'benign')]
    counts = labeled['sqli_type'].value_counts().to_dict()
    total  = sum(counts.values())
    H = (-sum((c / total) * math.log2(c / total) for c in counts.values())
         if total > 0 else 0.0)
    return {
        'total':      len(df),
        'tier4':      int(t4),
        'tier4_pct':  round(t4 / max(len(df), 1) * 100, 2),
        'entropy':    round(H, 4),
        'type_counts': counts,
    }


def _save_benchmark_log(bm: dict, output_path: Path) -> None:
    """Append benchmark result to benchmark_log.jsonl next to output file."""
    import json, time as _time
    log_path = output_path.parent / 'benchmark_log.jsonl'
    entry = {'timestamp': _time.strftime('%Y-%m-%dT%H:%M:%S'), **bm}
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    print(f"[INFO] Benchmark logged → {log_path.name}")
    print(f"       Tier4={bm['tier4_pct']}%  H={bm['entropy']:.4f} bits  "
          f"types={bm['type_counts']}")


def precision_at_gold(df: pd.DataFrame, gold_path: Path) -> float:
    """
    Compute precision against human-labeled gold set.
    Gold CSV must have columns: payload (or same payload_col), sqli_type.
    Returns fraction of gold payloads where script prediction matches human label.
    """
    gold = pd.read_csv(gold_path, encoding='utf-8-sig')
    if 'payload' not in gold.columns or 'sqli_type' not in gold.columns:
        print(f"[WARN] gold_set must have 'payload' and 'sqli_type' columns — skipping")
        return float('nan')
    payload_col = 'payload' if 'payload' in df.columns else df.columns[0]
    merged = gold.merge(
        df[[payload_col, 'sqli_type']].rename(columns={payload_col: 'payload'}),
        on='payload', suffixes=('_gold', '_pred')
    )
    if len(merged) == 0:
        print(f"[WARN] No overlapping payloads between gold set and labeled output")
        return float('nan')
    correct = (merged['sqli_type_gold'] == merged['sqli_type_pred']).sum()
    prec = round(correct / len(merged), 4)
    print(f"[INFO] Precision@Gold: {correct}/{len(merged)} = {prec:.4f} "
          f"({prec*100:.1f}%) on {len(gold)} gold rows")
    return prec


# ===========================================================================
# SUMMARY
# ===========================================================================

def _print_summary(result_df: pd.DataFrame) -> None:
    n = len(result_df)
    print("\n" + "=" * 60)
    print("LABELING v2 SUMMARY")
    print("=" * 60)
    print(f"Total rows: {n:,}")

    if 'sqli_type' in result_df.columns:
        print("\nType distribution:")
        for t, c in result_df['sqli_type'].value_counts().items():
            print(f"  {str(t):<22} {c:>8,}  ({c/n*100:.1f}%)")

    if 'label_source' in result_df.columns:
        print("\nLabel source (tier distribution):")
        for s, c in result_df['label_source'].value_counts().items():
            print(f"  {str(s):<25} {c:>8,}  ({c/n*100:.1f}%)")

    if 'confidence' in result_df.columns:
        conf = result_df['confidence']
        print(f"\nConfidence: mean={conf.mean():.3f}, median={conf.median():.3f}, "
              f"min={conf.min():.3f}, max={conf.max():.3f}")

    if 'payload_state' in result_df.columns:
        print("\nPayload state:")
        for s, c in result_df['payload_state'].value_counts().items():
            print(f"  {str(s):<12} {c:>8,}  ({c/n*100:.1f}%)")

    ai_conflict = result_df.get('ai_conflict', pd.Series([False]*n))
    if ai_conflict.sum() > 0:
        print(f"\n[WARN] AI conflict flags: {ai_conflict.sum():,} rows")

    print("=" * 60)


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="label-sqli v2: Cascade script-first labeler"
    )
    parser.add_argument('--input',       required=True,  help='Input CSV')
    parser.add_argument('--output',      required=True,  help='Output CSV')
    parser.add_argument('--payload_col', default='payload', help='Payload column name')
    parser.add_argument('--work_dir',    default=None,   help='Dir for AI prompt/response files')
    parser.add_argument('--batch_size',  type=int, default=50, help='Payloads per AI batch')
    parser.add_argument('--ai_cap',      type=int, default=5_000,
                        help='Max rows sent to AI (default 5000)')
    parser.add_argument('--sparse_threshold', type=int, default=20,
                        help='Cell count below which it is sparse (default 20)')
    parser.add_argument('--dry_run',       action='store_true',
                        help='Mock AI labels, no chat interaction')
    parser.add_argument('--detector_only', action='store_true',
                        help='Run Pass 1 only. Exports *_needs_ai_report.csv then exits '
                             'without any AI calls.')
    parser.add_argument('--benchmark',     action='store_true',
                        help='Compute and log coverage/entropy metrics after labeling')
    parser.add_argument('--gold_set',      default=None,
                        help='Path to human-labeled gold CSV for Precision@Gold check')
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[FAIL] Input not found: {input_path}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir = args.work_dir or str(output_path.parent / "chat_review_v2")

    print(f"[INFO] Loading {input_path.name}...")
    df = pd.read_csv(input_path, encoding='utf-8-sig')
    print(f"[INFO] Loaded {len(df):,} rows, columns: {list(df.columns)}")

    if args.payload_col not in df.columns:
        print(f"[FAIL] Column '{args.payload_col}' not found. "
              f"Available: {list(df.columns)}")
        sys.exit(1)

    payloads = df[args.payload_col].astype(str).tolist()
    t_start  = time.time()

    # ---- Pass 1: Script cascade ----
    result_df = pass1_cascade(df, args.payload_col, output_path)

    # ---- Coverage report ----
    cell_counts = coverage_report(result_df)
    sparse_cells = log_coverage(cell_counts, args.sparse_threshold)

    # ---- Detector-only mode: skip Pass 2 entirely ----
    if args.detector_only:
        _export_needs_ai_report(result_df, payloads, output_path)
        original_cols = [c for c in df.columns if c != args.payload_col]
        final_df = pd.concat([
            df[[args.payload_col]].reset_index(drop=True),
            result_df.reset_index(drop=True),
            df[original_cols].reset_index(drop=True) if original_cols else pd.DataFrame(),
        ], axis=1)
        final_df.to_csv(output_path, encoding='utf-8-sig', index=False)
        elapsed = time.time() - t_start
        print(f"\n[OK] Output written to: {output_path}")
        print(f"[OK] Total time: {elapsed/60:.1f} min ({len(df)/elapsed:.0f} rows/s)")
        print("[INFO] --detector_only mode: Pass 2 skipped.")
        _print_summary(result_df)
        if args.benchmark:
            bm = _compute_benchmark(result_df)
            _save_benchmark_log(bm, output_path)
        if args.gold_set:
            precision_at_gold(final_df, Path(args.gold_set))
        return

    # ---- Pass 2: AI review ----
    ckpt2 = _ckpt(output_path, 'pass2')
    ai_results_df = _load_ckpt(ckpt2)

    if ai_results_df is None:
        ai_idx = select_ai_candidates(
            result_df, payloads, cell_counts,
            ai_cap=args.ai_cap,
            sparse_threshold=args.sparse_threshold,
        )

        if ai_idx:
            print(f"\n[INFO] Pass 2: AI review for {len(ai_idx):,} rows...")
            ai_results = review_batch(
                payloads=payloads,
                disagreement_indices=ai_idx,
                work_dir=work_dir,
                batch_size=args.batch_size,
                budget_cap=args.ai_cap,
                dry_run=args.dry_run,
            )
        else:
            print("[INFO] Pass 2: No rows need AI review — all labeled by script")
            ai_results = {}

        # Serialize ai_results for checkpoint
        ai_records = [{'_ai_idx': k, **v} for k, v in ai_results.items()]
        ai_results_df = pd.DataFrame(ai_records) if ai_records else pd.DataFrame(
            columns=['_ai_idx', 'sqli_type', 'db_engine', 'confidence', 'reasoning'])
        _save_ckpt(ai_results_df, ckpt2)
    else:
        ai_results = {
            int(row['_ai_idx']): {
                'sqli_type':  row.get('sqli_type', 'boolean_blind'),
                'db_engine':  row.get('db_engine', 'unknown'),
                'confidence': float(row.get('confidence', 0.72)),
                'reasoning':  row.get('reasoning', ''),
            }
            for _, row in ai_results_df.iterrows()
        }
        print(f"[INFO] Loaded {len(ai_results):,} AI results from checkpoint")

    # Identify which high-conf rows were sent for cross-check
    high_conf_ai_idx = set()
    if not args.dry_run:
        high_conf_ai_idx = {
            idx for idx in ai_results.keys()
            if idx < len(result_df) and result_df.at[idx, 'confidence'] >= 0.85
               and not result_df.at[idx, 'needs_ai']
        }

    # ---- Merge AI results ----
    if ai_results:
        result_df = apply_ai_results(result_df, ai_results, high_conf_ai_idx)

    # ---- Build final CSV ----
    original_cols = [c for c in df.columns if c != args.payload_col]
    final_df = pd.concat([
        df[[args.payload_col]].reset_index(drop=True),
        result_df.reset_index(drop=True),
        df[original_cols].reset_index(drop=True) if original_cols else pd.DataFrame(),
    ], axis=1)

    final_df.to_csv(output_path, encoding='utf-8-sig', index=False)

    elapsed = time.time() - t_start
    print(f"\n[OK] Output written to: {output_path}")
    print(f"[OK] Total time: {elapsed/60:.1f} min ({len(df)/elapsed:.0f} rows/s)")

    _print_summary(result_df)


if __name__ == '__main__':
    main()
