"""
delex_validator.py -- Measure delex domain gap in cascade labeler detection.

Compares detection rate between raw and delex payload states in the labeled output.
Also generates synthetic delex versions of raw payloads and checks if they still
get detected correctly, exposing delex-specific false negatives.

Usage:
    python Skill/label-sqli/scripts/delex_validator.py \
        --labeled Asset/LabelData/Testing/Testing_labeled.csv \
        [--report  delex_gap_report.txt]
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Delexification — convert raw payload to delex form
# ---------------------------------------------------------------------------

def delexify(payload: str) -> str:
    """
    Convert a raw payload to delex form:
      '5' → __INT__
      'admin' → __STR__
      5 → __INT__ (bare number)
      sleep(5) → sleep(__TIME__)
    Preserves SQL keywords and structure.
    """
    p = str(payload)
    # Time arguments in sleep/benchmark/pg_sleep/waitfor
    p = re.sub(r"(?<=\bsleep\s*\()\s*\d+(?:\.\d+)?", '__TIME__', p, flags=re.I)
    p = re.sub(r"(?<=\bbenchmark\s*\()\s*\d+", '__TIME__', p, flags=re.I)
    p = re.sub(r"(?<=\bpg_sleep\s*\()\s*\d+(?:\.\d+)?", '__TIME__', p, flags=re.I)
    # Quoted strings → __STR__
    p = re.sub(r"'[^']*'", '__STR__', p)
    p = re.sub(r'"[^"]*"', '__STR__', p)
    # Remaining bare integers → __INT__
    p = re.sub(r'\b\d+\b', '__INT__', p)
    return p


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_gap(df: pd.DataFrame) -> dict:
    """Compute detection rates by payload state."""
    if 'payload_state' not in df.columns:
        return {}

    results = {}
    for state in ('raw', 'normalized', 'delex'):
        mask = df['payload_state'] == state
        subset = df[mask]
        if len(subset) == 0:
            continue
        detected = (subset['label_source'] != 'tier4_ai_needed').sum()
        is_sqli  = subset['is_sqli'].sum() if 'is_sqli' in subset.columns else 0
        results[state] = {
            'total':    len(subset),
            'detected': int(detected),
            'detect_rate': round(detected / len(subset), 4),
            'is_sqli': int(is_sqli),
        }
    return results


def synthetic_delex_test(df: pd.DataFrame) -> dict:
    """
    Take raw payloads that were correctly labeled, delexify them,
    and run cascade labeler on the delex version. Report miss rate.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from cascade_labeler import label_payload
    except ImportError:
        return {'error': 'Could not import cascade_labeler'}

    payload_col = 'payload' if 'payload' in df.columns else None
    if payload_col is None:
        return {'error': 'No payload column in input'}

    # Sample max 500 raw rows that were gold-labeled (not tier4)
    raw_gold = df[
        (df.get('payload_state', pd.Series()) == 'raw') &
        (df.get('label_source', pd.Series()) != 'tier4_ai_needed') &
        (df.get('is_sqli', pd.Series()) == 1)
    ]
    sample = raw_gold.head(500)
    if len(sample) == 0:
        return {'error': 'No raw gold SQLi rows to test'}

    total = len(sample)
    missed = 0
    type_mismatch = 0

    for _, row in sample.iterrows():
        raw_payload  = str(row[payload_col])
        delex_form   = delexify(raw_payload)
        orig_label   = row.get('sqli_type')

        result = label_payload(delex_form)
        if result['label_source'] == 'tier4_ai_needed':
            missed += 1
        elif result['sqli_type'] != orig_label:
            type_mismatch += 1

    return {
        'tested':        total,
        'missed_delex':  missed,
        'miss_rate':     round(missed / max(total, 1), 4),
        'type_mismatch': type_mismatch,
        'mismatch_rate': round(type_mismatch / max(total, 1), 4),
    }


def write_report(gap: dict, delex_test: dict, output: Path) -> None:
    lines = [
        "# Delex Domain Gap Report",
        "",
        "## Detection Rate by Payload State",
        f"{'State':<15} {'Total':<8} {'Detected':<10} {'DetectRate':<12} {'is_sqli':<8}",
        "-" * 55,
    ]
    for state, stats in gap.items():
        lines.append(
            f"{state:<15} {stats['total']:<8,} {stats['detected']:<10,} "
            f"{stats['detect_rate']:<12.4f} {stats['is_sqli']:<8,}"
        )

    lines += [
        "",
        "## Synthetic Delex Test (raw → delex → relabel)",
    ]
    if 'error' in delex_test:
        lines.append(f"  Error: {delex_test['error']}")
    else:
        lines += [
            f"  Tested:           {delex_test['tested']:,} raw gold SQLi payloads",
            f"  Missed (tier4):   {delex_test['missed_delex']:,} ({delex_test['miss_rate']:.1%})",
            f"  Type mismatch:    {delex_test['type_mismatch']:,} ({delex_test['mismatch_rate']:.1%})",
            "",
            "  Miss rate < 5% → delex coverage OK",
            "  Miss rate 5-15% → add delex-specific patterns",
            "  Miss rate > 15% → significant domain gap, needs dedicated delex training",
        ]

    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f"[OK] Report written to: {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Measure delex domain gap in cascade labeler"
    )
    parser.add_argument('--labeled', required=True, help='Cascade output CSV')
    parser.add_argument('--report',  default=None,  help='Output report file (optional)')
    parser.add_argument('--no_synthetic', action='store_true',
                        help='Skip synthetic delex test (faster)')
    args = parser.parse_args()

    labeled_path = Path(args.labeled)
    if not labeled_path.exists():
        print(f"[FAIL] File not found: {labeled_path}")
        sys.exit(1)

    print(f"[INFO] Loading {labeled_path.name}...")
    df = pd.read_csv(labeled_path, encoding='utf-8-sig')
    print(f"[INFO] Loaded {len(df):,} rows")

    print("\n[INFO] Analyzing detection gap by payload state...")
    gap = analyze_gap(df)

    for state, stats in gap.items():
        flag = '[OK]' if stats['detect_rate'] >= 0.80 else '[WARN]'
        print(f"  {flag} {state:<12} detect_rate={stats['detect_rate']:.4f} "
              f"({stats['detected']:,}/{stats['total']:,})")

    delex_test = {}
    if not args.no_synthetic:
        print("\n[INFO] Running synthetic delex test (up to 500 rows)...")
        delex_test = synthetic_delex_test(df)
        if 'error' not in delex_test:
            flag = '[OK]' if delex_test['miss_rate'] < 0.05 else '[WARN]'
            print(f"  {flag} Delex miss rate: {delex_test['miss_rate']:.1%} "
                  f"({delex_test['missed_delex']}/{delex_test['tested']})")

    report_path = Path(args.report) if args.report else (
        labeled_path.parent / 'delex_gap_report.txt'
    )
    write_report(gap, delex_test, report_path)


if __name__ == '__main__':
    main()
