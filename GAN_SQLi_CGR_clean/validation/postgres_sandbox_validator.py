#!/usr/bin/env python3
"""Local PostgreSQL Boolean predicate validator.

Runs only against a disposable local PostgreSQL database. It validates parse and
runtime behavior of Boolean predicate candidates; it does not validate exploit
success against an application.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

EFFECT_TOKENS = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|COPY|TRUNCATE|GRANT|REVOKE|EXEC|EXECUTE|CALL|DO|PG_SLEEP)\b|;", re.I)
COMMENT_RE = re.compile(r"/\*.*?\*/|--.*?$", re.S | re.M)
SELECT_RE = re.compile(r"\bSELECT\b", re.I)


def allowed_by_mode(payload: str, mode: str) -> tuple[bool, str]:
    if EFFECT_TOKENS.search(payload):
        return False, "forbidden_effect_construct"
    if mode == "safe_minimal":
        if COMMENT_RE.search(payload):
            return False, "comment_not_allowed_in_safe_minimal"
        if SELECT_RE.search(payload):
            return False, "select_not_allowed_in_safe_minimal"
    elif mode != "postgres_parse_readonly":
        return False, "unknown_mode"
    return True, ""


def validate_payload(payload: str, *, mode: str = "safe_minimal", psql_cmd: str = "psql", timeout: float = 1.0) -> dict:
    ok, reason = allowed_by_mode(payload, mode)
    if not ok:
        return {"postgres_parse_valid": False, "postgres_runtime_valid": False, "runtime_error_class": reason}
    sql = "SET statement_timeout='200ms'; SET lock_timeout='100ms'; SET search_path=pg_temp; SELECT CASE WHEN (" + payload + ") THEN TRUE ELSE FALSE END;"
    try:
        cp = subprocess.run([psql_cmd, "-X", "-q", "-v", "ON_ERROR_STOP=1", "-c", sql], text=True, capture_output=True, timeout=timeout)
        ok = cp.returncode == 0
        err = "" if ok else (cp.stderr.strip().split("\n")[-1][:160] if cp.stderr else "psql_error")
        return {"postgres_parse_valid": ok, "postgres_runtime_valid": ok, "runtime_error_class": err}
    except subprocess.TimeoutExpired:
        return {"postgres_parse_valid": False, "postgres_runtime_valid": False, "runtime_error_class": "timeout"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv")
    ap.add_argument("output_csv")
    ap.add_argument("--payload-column", default="validation_payload_v4")
    ap.add_argument("--mode", choices=["safe_minimal", "postgres_parse_readonly"], default="safe_minimal")
    ap.add_argument("--psql-cmd", default="psql")
    args = ap.parse_args(argv)
    inp, out = Path(args.input_csv), Path(args.output_csv)
    with inp.open(newline="", encoding="utf-8") as f, out.open("w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fields = list(r.fieldnames or []) + ["postgres_parse_valid_runtime", "postgres_runtime_valid_runtime", "runtime_error_class_runtime", "validator_mode"]
        w = csv.DictWriter(g, fieldnames=fields)
        w.writeheader()
        for row in r:
            res = validate_payload(row.get(args.payload_column, "") or "", mode=args.mode, psql_cmd=args.psql_cmd)
            row.update({"postgres_parse_valid_runtime": res["postgres_parse_valid"], "postgres_runtime_valid_runtime": res["postgres_runtime_valid"], "runtime_error_class_runtime": res["runtime_error_class"], "validator_mode": args.mode})
            w.writerow(row)

if __name__ == "__main__":
    main()
