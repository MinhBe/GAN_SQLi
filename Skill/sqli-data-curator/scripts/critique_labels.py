"""critique_labels.py — Triage existing labels into Keep/Relabel/Drop.

Given combined_labeled_data.csv, classify each row:
  - DROP   : type in {ldap_injection, command_injection, second_order, inline_query,
                      comment_based, rce, generic}, OR payload < 5 chars,
                      OR signal absent + confidence high (likely mislabel)
  - RELABEL: type=unknown, OR reasoning < 20 chars, OR confidence < 0.70,
             OR rule-based check disagrees with current label
  - KEEP   : passes all checks → use as-is

Output: <input>_triaged.csv with `verdict` column added.
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from label_payload import source_a_rule_based, TYPE_PRIORITY, SQLI_TYPES

# Types to drop entirely (user decision: 134 rows, 0.3% of data)
DROP_TYPES = {
    "ldap_injection", "command_injection", "second_order", "inline_query",
    "comment_based", "rce", "generic",
}

# Types to relabel (still SQLi but uncertain)
RELABEL_TRIGGERS = {"unknown"}

MIN_REASONING_LEN = 20
MIN_CONFIDENCE = 0.70
MIN_PAYLOAD_LEN = 5


def critique_row(row: dict) -> dict:
    """Return verdict dict: {verdict, reasons[], suggested_type, suggested_db}."""
    payload = str(row.get("payload_norm", "") or "")
    cur_type = str(row.get("sqli_type", "") or "")
    cur_db = str(row.get("db_engine", "") or "")
    cur_reasoning = str(row.get("reasoning", "") or "")
    try:
        cur_conf = float(row.get("confidence", 0.0))
    except (TypeError, ValueError):
        cur_conf = 0.0

    reasons = []
    suggested_type = cur_type
    suggested_db = cur_db

    # DROP rules
    if cur_type in DROP_TYPES:
        return {
            "verdict": "DROP",
            "reasons": [f"type '{cur_type}' is in drop-list (user decision)"],
            "suggested_type": cur_type,
            "suggested_db": cur_db,
        }
    if len(payload.strip()) < MIN_PAYLOAD_LEN:
        return {
            "verdict": "DROP",
            "reasons": [f"payload too short ({len(payload.strip())} chars)"],
            "suggested_type": cur_type,
            "suggested_db": cur_db,
        }

    # RELABEL rules
    if cur_type in RELABEL_TRIGGERS:
        reasons.append(f"type='{cur_type}' needs verification")
    if len(cur_reasoning.strip()) < MIN_REASONING_LEN:
        reasons.append(f"reasoning too short ({len(cur_reasoning.strip())} chars)")
    if cur_conf < MIN_CONFIDENCE:
        reasons.append(f"confidence too low ({cur_conf:.2f})")

    # Rule-based check: does source A agree?
    rule_result = source_a_rule_based(payload)
    if rule_result.sqli_type != cur_type and cur_type != "benign":
        # Conflict — but only flag if priority of rule is HIGHER (stronger) than current
        rule_pri = TYPE_PRIORITY.get(rule_result.sqli_type, 99)
        cur_pri = TYPE_PRIORITY.get(cur_type, 99)
        if rule_pri < cur_pri:
            reasons.append(
                f"rule-check disagrees: rule says '{rule_result.sqli_type}' "
                f"(P{rule_pri}) but labeled '{cur_type}' (P{cur_pri})"
            )
            suggested_type = rule_result.sqli_type
            suggested_db = rule_result.db_engine

    # Benign with attack keyword → DROP or RELABEL
    if cur_type == "benign":
        ATTACK_KEYWORDS = ["union", "sleep", "pg_sleep", "waitfor", "benchmark",
                           "extractvalue", "updatexml", "xp_cmdshell", "load_file",
                           "xmltype", "dbms_pipe", " or 1=1", " and 1=1", "admin'"]
        pl_lower = payload.lower()
        for kw in ATTACK_KEYWORDS:
            if kw in pl_lower:
                reasons.append(f"benign payload contains '{kw}' (likely false negative)")
                suggested_type = rule_result.sqli_type
                suggested_db = rule_result.db_engine
                break

    if reasons:
        return {
            "verdict": "RELABEL",
            "reasons": reasons,
            "suggested_type": suggested_type,
            "suggested_db": suggested_db,
        }

    return {
        "verdict": "KEEP",
        "reasons": [],
        "suggested_type": cur_type,
        "suggested_db": cur_db,
    }


def critique_batch(df) -> list:
    return [critique_row(row.to_dict()) for _, row in df.iterrows()]


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import pandas as pd

    parser = argparse.ArgumentParser(description="Triage labels: Keep/Relabel/Drop")
    parser.add_argument("--input", required=True, help="Input CSV")
    parser.add_argument("--output", required=True, help="Output CSV with verdict")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.limit:
        df = df.head(args.limit).copy()

    print(f"Critiquing {len(df)} rows...")
    results = critique_batch(df)

    df["verdict"] = [r["verdict"] for r in results]
    df["critique_reasons"] = ["; ".join(r["reasons"]) for r in results]
    df["suggested_type"] = [r["suggested_type"] for r in results]
    df["suggested_db"] = [r["suggested_db"] for r in results]

    df.to_csv(args.output, index=False)

    print(f"\nWrote {len(df)} rows to {args.output}")
    print(f"\n=== VERDICT DISTRIBUTION ===")
    counts = df["verdict"].value_counts()
    for v, c in counts.items():
        print(f"  {v:<10} {c:6d} ({c/len(df):6.2%})")
    print(f"\n=== TOP RELABEL REASONS ===")
    relabel_df = df[df["verdict"] == "RELABEL"]
    if len(relabel_df) > 0:
        from collections import Counter
        all_reasons = []
        for r in relabel_df["critique_reasons"]:
            all_reasons.extend([x.strip() for x in str(r).split(";") if x.strip()])
        for reason, count in Counter(all_reasons).most_common(10):
            # Strip specific numbers for grouping
            reason_grouped = re.sub(r"\(\d+(\.\d+)?\s*(chars|\)).*", r"(...)", reason)[:80]
            print(f"  {count:5d}  {reason_grouped}")
