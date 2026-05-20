"""
rule_refiner.py -- Analyze Tier 3/4 payloads and propose new detector rules.

Usage:
    python Skill/label-sqli/scripts/rule_refiner.py \
        --report Asset/LabelData/Testing/Testing_labeled_needs_ai_report.csv \
        --output rule_suggestions.txt \
        [--top_n 30]

Input CSV must have columns: label_source, payload (or payload_norm).
Output: ranked list of SQL fragments + proposed regex patterns.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# SQL keywords to track in ngram extraction
_SQL_KEYWORDS = {
    'select', 'union', 'insert', 'update', 'delete', 'drop', 'truncate',
    'where', 'from', 'having', 'order', 'group', 'by', 'limit', 'offset',
    'sleep', 'benchmark', 'waitfor', 'delay', 'execute', 'immediate',
    'declare', 'cast', 'convert', 'char', 'ascii', 'substr', 'substring',
    'concat', 'extractvalue', 'updatexml', 'xmltype', 'utl_inaddr',
    'pg_sleep', 'xp_cmdshell', 'openrowset', 'load_file', 'outfile',
    'information_schema', 'sysobjects', 'sqlite_master',
    'or', 'and', 'not', 'in', 'like', 'between', 'exists', 'null',
    'true', 'false', 'case', 'when', 'then', 'else', 'end',
}

_COMMENT_PAT = re.compile(r'--[^\n]*|#[^\n]*|/\*.*?\*/', re.DOTALL)
_SPACE_PAT   = re.compile(r'\s+')


def _tokenize(payload: str) -> list:
    """Extract SQL-relevant tokens from payload."""
    p = _COMMENT_PAT.sub(' ', str(payload).lower())
    p = re.sub(r"'[^']*'|\"[^\"]*\"", ' __STR__ ', p)
    p = re.sub(r'\b\d+\b', ' __N__ ', p)
    tokens = re.findall(r'[\w@_]+|[()=<>!;,]', p)
    return [t for t in tokens if t in _SQL_KEYWORDS or t.startswith('@') or t in {'__STR__', '__N__'}]


def _ngrams(tokens: list, n: int) -> list:
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def _to_regex(fragment: str) -> str:
    """Convert a space-separated token sequence to a regex pattern."""
    parts = []
    for tok in fragment.split():
        if tok == '__STR__':
            parts.append(r"""(?:'[^']*'|"[^"]*")""")
        elif tok == '__N__':
            parts.append(r'\d+')
        elif re.match(r'^\w+$', tok):
            parts.append(r'\b' + re.escape(tok) + r'\b')
        else:
            parts.append(re.escape(tok))
    return r'\s+'.join(parts)


def analyze(report_csv: Path, top_n: int = 30) -> list:
    """
    Load tier4_ai_needed rows, extract SQL ngrams, rank by frequency.
    Returns list of (fragment, count, proposed_regex).
    """
    import pandas as pd

    df = pd.read_csv(report_csv, encoding='utf-8-sig')

    # Identify payload column
    payload_col = None
    for col in ('payload', 'payload_norm'):
        if col in df.columns:
            payload_col = col
            break
    if payload_col is None:
        print(f"[FAIL] No 'payload' or 'payload_norm' column in {report_csv.name}")
        sys.exit(1)

    # Filter to tier4 only
    tier4_mask = df.get('label_source', pd.Series()) == 'tier4_ai_needed'
    tier4 = df[tier4_mask][payload_col].astype(str).tolist()
    print(f"[INFO] Analyzing {len(tier4):,} tier4_ai_needed payloads...")

    counter: Counter = Counter()
    for payload in tier4:
        tokens = _tokenize(payload)
        for n in (1, 2, 3):
            counter.update(_ngrams(tokens, n))

    results = []
    for fragment, count in counter.most_common(top_n * 3):
        # Skip single trivial tokens
        words = fragment.split()
        if len(words) == 1 and words[0] in ('or', 'and', '__N__', '__STR__'):
            continue
        coverage_pct = round(count / max(len(tier4), 1) * 100, 1)
        proposed = _to_regex(fragment)
        results.append((fragment, count, coverage_pct, proposed))
        if len(results) >= top_n:
            break

    return results


def write_report(results: list, tier4_total: int, output: Path) -> None:
    lines = [
        "# Rule Refiner — Pattern Suggestions",
        f"# Tier 4 payloads analyzed: {tier4_total:,}",
        f"# Top {len(results)} patterns ranked by frequency",
        "",
        f"{'Rank':<5} {'Count':<7} {'Coverage%':<11} {'Fragment':<35} Proposed Regex",
        "-" * 110,
    ]
    for rank, (fragment, count, pct, regex) in enumerate(results, 1):
        lines.append(f"{rank:<5} {count:<7} {pct:<11.1f} {fragment:<35} r'{regex}'")

    lines += [
        "",
        "# How to use:",
        "# 1. Pick patterns with coverage > 5% and 2+ tokens",
        "# 2. Add to _TIER2_BOOL_PATTERNS or _TIER2_ERROR_PATTERNS in detectors_v2.py",
        "# 3. Re-run: python run_labeling.py --input ... --output ... --detector_only --benchmark",
        "# 4. Check Tier 4 % decreased; if delta < 100 rows, stop the loop",
    ]

    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f"[OK] Report written to: {output}")


def main():
    parser = argparse.ArgumentParser(description="Propose new detector rules from Tier 4 payloads")
    parser.add_argument('--report', required=True, help='needs_ai_report CSV')
    parser.add_argument('--output', required=True, help='Output text report file')
    parser.add_argument('--top_n',  type=int, default=30, help='Top N patterns to report')
    args = parser.parse_args()

    report_path = Path(args.report)
    output_path = Path(args.output)

    if not report_path.exists():
        print(f"[FAIL] Report not found: {report_path}")
        sys.exit(1)

    import pandas as pd
    df = pd.read_csv(report_path, encoding='utf-8-sig')
    tier4_total = (df.get('label_source', pd.Series()) == 'tier4_ai_needed').sum()

    results = analyze(report_path, top_n=args.top_n)
    write_report(results, tier4_total, output_path)


if __name__ == '__main__':
    main()
