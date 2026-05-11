"""
Re-label REJECT rows from critic results using only rule-based logic (no LLM API).

Usage:
    python relabeler.py <critic_results.csv> <original_labeled.csv> --output relabeled.csv

This module:
  1. Reads critic verdicts + corrections
  2. Applies critic-suggested sqli_type corrections for priority conflicts
  3. Runs improved classifier on remaining C3 signal-absent rows
  4. Produces clean output with label_source tracking
"""

import argparse
import csv
import json
import logging
import sys
import importlib.util
from pathlib import Path
from collections import defaultdict

BASE = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, BASE)
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import classifier via importlib (directory has hyphen)
spec = importlib.util.spec_from_file_location("classifier",
    str(Path(__file__).resolve().parent / "classifier.py"))
classifier_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier_mod)
classify = classifier_mod.classify
ClassifyResult = classifier_mod.ClassifyResult

# Import shared modules directly (Skill/ is on sys.path)
from shared.taxonomy import VALID_TYPES, NORMALIZE_MAP, TYPE_PRIORITY
from shared.patterns import SIGNAL_PATTERNS, DB_SIGNATURES, ATTACK_KEYWORDS


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("relabeler")


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for i, row in enumerate(reader):
            cleaned = {}
            for k, v in row.items():
                key = k.strip().strip('"').strip("'")
                cleaned[key] = v
            if "row_index" not in cleaned or not cleaned["row_index"]:
                cleaned["row_index"] = str(i)
            rows.append(cleaned)
        fieldnames = reader.fieldnames or []
        fieldnames = [f.strip().strip('"').strip("'") for f in fieldnames]
        if "row_index" not in fieldnames:
            fieldnames = ["row_index"] + fieldnames
    return rows, fieldnames


def write_csv(path, rows, fieldnames):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def apply_correction_from_critic(row):
    """Apply correction_json from critic if available."""
    cj = row.get("correction_json", "")
    if not cj:
        return row, "no-correction-json"

    try:
        correction = json.loads(cj)
    except json.JSONDecodeError:
        return row, "parse-error"

    action = correction.get("action", "")
    suggested_type = correction.get("sqli_type", "")
    suggested_db = correction.get("db_engine", "")

    if action == "re-label" and suggested_type:
        row["sqli_type"] = suggested_type
        row["label_source"] = "critic-correction-type"
        if suggested_db:
            row["db_engine"] = suggested_db
        return row, f"corrected-to-{suggested_type}"

    if suggested_type:
        row["sqli_type"] = suggested_type
        row["label_source"] = "critic-correction-type"
        if suggested_db:
            row["db_engine"] = suggested_db
        return row, f"corrected-to-{suggested_type}"

    if action == "re-label or reduce confidence":
        return row, "needs-classifier"

    return row, "no-action"


def has_attack_keywords(payload):
    """Check if payload contains any attack keywords."""
    lower = payload.lower()
    return any(kw in lower for kw in ATTACK_KEYWORDS)


def detect_best_type(payload):
    """Run priority chain + fallback heuristics to find best type."""
    lower = payload.lower()

    # Priority chain P1-P12
    type_scores = {}
    for type_name, patterns in SIGNAL_PATTERNS.items():
        score = sum(1 for p in patterns if p.search(payload))
        if score > 0:
            priority = TYPE_PRIORITY.get(type_name, 99)
            type_scores[type_name] = {"score": score, "priority": priority}

    if type_scores:
        best = min(type_scores.items(),
                   key=lambda x: (x[1]["priority"], -x[1]["score"]))
        return best[0]

    return None


def detect_best_db(payload):
    for db, signatures in DB_SIGNATURES.items():
        for sig in signatures:
            if sig.search(payload):
                return db
    return "generic"


def relabel_via_classifier(row):
    """Run improved rule-based classifier on a row."""
    payload = row.get("payload_norm", "")
    if not payload:
        row["label_source"] = "empty-payload"
        return row

    result = classify(payload)
    if result and result.sqli_type not in ("unknown", "benign"):
        row["sqli_type"] = result.sqli_type
        row["db_engine"] = result.db_engine
        row["confidence"] = str(result.confidence)
        row["reasoning"] = result.reasoning
        row["label_source"] = "relabel-classifier"
        return row

    # Fallback: check attack keywords
    if has_attack_keywords(payload):
        best_type = detect_best_type(payload)
        if best_type:
            db = detect_best_db(payload)
            row["sqli_type"] = best_type
            row["db_engine"] = db
            row["confidence"] = "0.75"
            row["reasoning"] = f"Fallback: attack keywords detected, best match {best_type}"
            row["label_source"] = "relabel-keyword-fallback"
            return row

    # No attack signals found
    row["sqli_type"] = "benign"
    row["db_engine"] = "unknown"
    row["confidence"] = "0.60"
    row["reasoning"] = "No attack signals detected after re-label"
    row["label_source"] = "relabel-benign-fallback"
    return row


def main():
    parser = argparse.ArgumentParser(
        description="Re-label REJECT rows from critic using rule-based logic")
    parser.add_argument("critic_results", help="critic_results.csv from Step 4")
    parser.add_argument("--output", "-o", required=True, help="Output CSV path")
    parser.add_argument("--diff", help="Optional diff report path")
    args = parser.parse_args()

    rows, fieldnames = read_csv(args.critic_results)
    logger.info("Loaded %d rows from %s", len(rows), args.critic_results)

    stats = defaultdict(int)
    change_log = []

    for row in rows:
        original_type = row.get("sqli_type", "")
        original_db = row.get("db_engine", "")
        verdict = row.get("verdict", "")

        if verdict != "REJECT":
            row["label_source"] = row.get("label_source", "pass-through")
            continue

        row, action = apply_correction_from_critic(row)
        stats[action] += 1

        if action in ("no-correction-json", "no-action", "needs-classifier"):
            row = relabel_via_classifier(row)
            stats[f"after-classifier-{row.get('sqli_type', '?')}"] += 1

        new_type = row.get("sqli_type", "")
        new_db = row.get("db_engine", "")
        if new_type != original_type:
            change_log.append({
                "row_index": row.get("row_index", "?"),
                "field": "sqli_type",
                "old": original_type,
                "new": new_type,
                "reason": row.get("label_source", "?"),
            })
        if new_db != original_db:
            change_log.append({
                "row_index": row.get("row_index", "?"),
                "field": "db_engine",
                "old": original_db,
                "new": new_db,
                "reason": row.get("label_source", "?"),
            })

    output_fields = [f for f in fieldnames if f not in ("verdict", "critic_evidence", "correction_json")]
    if "label_source" not in output_fields:
        output_fields = output_fields + ["label_source"]

    cleaned = [{k: v for k, v in r.items() if k in output_fields} for r in rows]
    write_csv(args.output, cleaned, output_fields)
    logger.info("Wrote %d rows to %s", len(rows), args.output)

    if args.diff:
        diff_fields = ["row_index", "field", "old", "new", "reason"]
        write_csv(args.diff, change_log, diff_fields)
        logger.info("Wrote %d changes to %s", len(change_log), args.diff)

    print("\n=== Re-label Stats ===")
    for action, count in sorted(stats.items()):
        print(f"  {action}: {count}")
    print(f"\n  Total changes logged: {len(change_log)}")


if __name__ == "__main__":
    main()
