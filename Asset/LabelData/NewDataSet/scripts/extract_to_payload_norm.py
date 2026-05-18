import csv
import json
import os
import re
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ─── Paths ───────────────────────────────────────────────────────────────

BASE_DIR = Path("Asset/LabelData/NewDataSet")
OUTPUT_DIR = Path("Asset/LabelData/FinalDataSet")
OUTPUT_CSV = OUTPUT_DIR / "payload_norm.csv"
RECOVERY_MD = OUTPUT_DIR / "recovery1.md"
SOURCES_MD = OUTPUT_DIR / "DATASET_SOURCES.md"

RECOVERY_LOG = []


# ─── Normalization ───────────────────────────────────────────────────────

def normalize_payload(text):
    if not isinstance(text, str) or pd.isna(text):
        return ""
    try:
        text = urllib.parse.unquote(text)
    except Exception:
        pass
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ─── Helpers ─────────────────────────────────────────────────────────────

def write_rows(writer, rows_iter):
    count = 0
    for row in rows_iter:
        p = normalize_payload(row)
        if not p:
            continue
        writer.writerow([p])
        count += 1
    return count


def read_utf_fallback(path, **kwargs):
    try:
        return pd.read_csv(path, **kwargs)
    except (UnicodeDecodeError, UnicodeError):
        return pd.read_csv(path, encoding="utf-16", **kwargs)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ─── Source generators ───────────────────────────────────────────────────

def gen_rbsqli():
    path = BASE_DIR / "rbsqli_dataset.csv"
    if not path.exists():
        return
    try:
        for chunk in pd.read_csv(
            path, usecols=["sql_query"], chunksize=200_000
        ):
            for _, row in chunk.iterrows():
                payload = row["sql_query"]
                if pd.notna(payload):
                    yield payload
    except Exception as e:
        print(f"    [WARN] rbsqli error: {e}")


def gen_zenodo():
    path = BASE_DIR / "zenodo_dataset.csv"
    if not path.exists():
        return
    try:
        for chunk in pd.read_csv(path, usecols=["full_query"], chunksize=200_000):
            for _, row in chunk.iterrows():
                payload = row["full_query"]
                if pd.notna(payload):
                    yield payload
    except Exception as e:
        print(f"    [WARN] zenodo error: {e}")


def gen_github_http_params():
    dir_path = BASE_DIR / "github_http_params"
    if not dir_path.exists():
        return
    for f in sorted(dir_path.glob("*.csv")):
        try:
            df = pd.read_csv(f)
            if "payload" not in df.columns:
                continue
            sqli_rows = df[df["attack_type"].isin(["sqli", "norm"])]
            for _, row in sqli_rows.iterrows():
                yield row["payload"]
        except Exception:
            continue


def gen_github_yogsec():
    dir_path = BASE_DIR / "github_yogsec_payloads"
    if not dir_path.exists():
        return
    for f in sorted(dir_path.glob("*.txt")):
        if "README" in f.name:
            continue
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    yield line
        except OSError:
            print(f"    [SKIP] Defender blocked: {f.name}")
            continue


def gen_github_payloadbox():
    dir_path = BASE_DIR / "github_payloadbox"
    if not dir_path.exists():
        return
    targets = [
        "mssql-payloads.txt", "mysql-payloads.txt", "oracle-payloads.txt",
        "postgresql-payloads.txt", "sqlite-payloads.txt", "burp-intruder-payloads.txt",
    ]
    for fname in targets:
        path = dir_path / fname
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    yield line
        except OSError:
            print(f"    [SKIP] Defender blocked: {path.name}")
            continue


def gen_github_payloadsallthethings():
    sqli_dir = BASE_DIR / "github_payloadsallthethings" / "SQL Injection"
    if not sqli_dir.exists():
        return
    for f in sorted(sqli_dir.glob("*.md")):
        if f.name.lower() == "readme.md":
            continue
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            print(f"    [SKIP] Defender blocked: {f.name}")
            continue
        blocks = re.findall(r"```(?:sql)?\n(.*?)\n```", content, re.DOTALL)
        for block in blocks:
            for line in block.split("\n"):
                yield line
    intruder_dir = sqli_dir / "Intruder"
    if intruder_dir.exists():
        for f in sorted(intruder_dir.glob("*.txt")):
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        yield line
            except OSError:
                print(f"    [SKIP] Defender blocked: {f.name}")
                continue


def gen_github_fuzzdb():
    base = BASE_DIR / "github_fuzzdb" / "attack" / "sql-injection"
    if not base.exists():
        return
    for subdir in ["detect", "exploit", "payloads-sql-blind"]:
        d = base / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.txt")):
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        yield line
            except OSError:
                print(f"    [SKIP] Defender blocked: {f.name}")
                continue


def gen_bccc_sfu():
    path = BASE_DIR / "bccc_sfu" / "BCCC-SFU-SQLInj-2023.csv"
    if not path.exists():
        return
    try:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            yield row["Data"]
    except Exception as e:
        print(f"    [WARN] bccc_sfu error: {e}")


def gen_gist_johntroony():
    path = BASE_DIR / "gist_johntroony" / "Troony_SQLi_Payloads.txt"
    if not path.exists():
        return
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                yield line
    except OSError:
        print(f"    [SKIP] Defender blocked: {path.name}")


def gen_github_ajinmathew():
    dir_path = BASE_DIR / "github_ajinmathew"
    if not dir_path.exists():
        return
    for f in sorted(dir_path.glob("*.csv")):
        try:
            df = read_utf_fallback(f)
            if "Sentence" not in df.columns or "Label" not in df.columns:
                continue
            sqlis = df[df["Label"] == 1]
            for _, row in sqlis.iterrows():
                yield row["Sentence"]
        except Exception:
            continue


def gen_github_sqliv5():
    dir_path = BASE_DIR / "github_sqliv5"
    if not dir_path.exists():
        return
    for fname in ["sqli.csv", "sqliv2.csv"]:
        path = dir_path / fname
        if not path.exists():
            continue
        try:
            df = read_utf_fallback(path)
            if "Sentence" in df.columns and "Label" in df.columns:
                sqlis = df[df["Label"] == 1]
                for _, row in sqlis.iterrows():
                    yield row["Sentence"]
        except Exception:
            continue
    csv3 = dir_path / "SQLiV3.csv"
    if csv3.exists():
        try:
            df = pd.read_csv(csv3, header=None)
            if len(df.columns) >= 2:
                for _, row in df.iterrows():
                    if str(row[1]).strip() == "1":
                        yield row[0]
        except Exception:
            pass
    for fname in ["SQLiV3.json", "SQLiV3_clean.json", "SQLiV4.json", "SQLiV5.json"]:
        path = dir_path / fname
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "pattern" in item:
                        yield item["pattern"]
        except Exception:
            continue


def gen_github_csic_ecml():
    path = (
        BASE_DIR / "github_csic_ecml_combined" / "CSVData" / "csic_ecml_final.csv"
    )
    if not path.exists():
        return
    try:
        df = pd.read_csv(path)
        if "Class" not in df.columns:
            return
        anomalies = df[df["Class"] == "Anomalous"]
        for _, row in anomalies.iterrows():
            gq = row.get("GET-Query", "")
            pd_val = row.get("POST-Data", "")
            raw = gq if pd.notna(gq) and str(gq).strip() else pd_val
            if pd.notna(raw):
                yield raw
    except Exception as e:
        print(f"    [WARN] csic_ecml error: {e}")


def gen_kaggle_sources():
    kaggle_base = BASE_DIR / "kaggle"
    if not kaggle_base.exists():
        return
    for root, _, files in os.walk(kaggle_base):
        for file in files:
            if not file.endswith(".csv"):
                continue
            path = Path(root) / file
            try:
                df = read_utf_fallback(path)
                p_col = None
                for c in ["Query", "Sentence", "sql_query"]:
                    if c in df.columns:
                        p_col = c
                        break
                if p_col is None or "Label" not in df.columns:
                    continue
                sqlis = df[df["Label"] == 1]
                for _, row in sqlis.iterrows():
                    yield row[p_col]
            except Exception:
                continue


def gen_benign_complex():
    sources = [
        BASE_DIR / "spider" / "spider_eval_benign.csv",
        BASE_DIR / "spider" / "gretelai_synthetic_sql.csv",
        BASE_DIR / "huggingface" / "sql_create_context_benign.csv",
    ]
    for path in sources:
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
            if "query" in df.columns:
                for _, row in df.iterrows():
                    yield row["query"]
            elif "Sentence" in df.columns:
                for _, row in df.iterrows():
                    yield row["Sentence"]
        except Exception:
            continue


def gen_auto_discover():
    EXCLUDE_FILE_NAMES = {
        "readme.md", "license", "license.md", "contributing.md",
        "dataset_sources.md", "additional_sources_candidates.md",
        "anubis.pdf", ".gitignore", "mkdocs.yml", "custom.css",
        "disclaimer.md", "security.md",
    }
    EXCLUDE_DIRS = {
        "scripts", "github_wafamole", "github_csic_2010",
        "github_rbsqli", "github_spider_data", "zenodo",
    }
    EXCLUDE_EXT = {".md", ".json", ".ipynb", ".pdf", ".jpg", ".jpeg",
                   ".png", ".gif", ".svg", ".css", ".yml", ".yaml",
                   ".lock", ".arff", ".py", ".woff2"}

    known = set()
    for entry in BASE_DIR.rglob("*"):
        if entry.is_file():
            known.add(str(entry.resolve()))

    for root, dirs, files in os.walk(BASE_DIR):
        root_parts = Path(root).parts
        if any(ex in root_parts for ex in EXCLUDE_DIRS):
            continue
        for file in files:
            f_lower = file.lower()
            if f_lower in EXCLUDE_FILE_NAMES:
                continue
            ext = Path(file).suffix.lower()
            if ext in EXCLUDE_EXT:
                continue
            path = Path(root) / file
            if str(path.resolve()) in known:
                continue
            if ext == ".csv":
                try:
                    df = pd.read_csv(path, nrows=3)
                    p_col = None
                    for c in df.columns:
                        c_lower = c.lower()
                        if any(k in c_lower for k in
                               ["payload", "query", "sentence", "data", "text", "sql"]):
                            p_col = c
                            break
                    if p_col is None:
                        continue
                    for chunk in pd.read_csv(path, chunksize=100_000):
                        for _, r in chunk.iterrows():
                            yield r[p_col]
                except Exception:
                    continue
            elif ext == ".txt":
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        for line in fh:
                            yield line
                except OSError:
                    continue


# ─── Recovery / Sources MD ───────────────────────────────────────────────

def write_recovery_checkpoint():
    # Separate source entries from the TOTAL entry
    sources_log = [e for e in RECOVERY_LOG if e["name"] != "TOTAL"]
    total_log = [e for e in RECOVERY_LOG if e["name"] == "TOTAL"]

    total_rows = sum(e["rows"] for e in sources_log)
    started = sources_log[0]["start"] if sources_log else ""
    completed = total_log[0]["end"] if total_log else (sources_log[-1]["end"] if sources_log else "")

    header = "# Recovery Checkpoint 1\n\n"
    header += f"**Started:** {started}\n"
    if completed:
        header += f"**Completed:** {completed}\n"
    header += f"**Output:** `{OUTPUT_CSV}`\n\n"
    header += "| # | Source | File | Rows | Time | Status |\n"
    header += "|---|--------|------|-----:|------|--------|\n"
    rows_str = ""
    for i, entry in enumerate(sources_log, 1):
        rows_str += (
            f"| {i} | {entry['name']} | {entry['file']} "
            f"| {entry['rows']:,} | {entry['end']} | {entry['status']} |\n"
        )
    footer = f"\n**Total rows extracted:** {total_rows:,}\n"
    footer += f"**Output size:** ~{max(total_rows * 40 / 1024 / 1024, 1):.0f} MB (est.)\n"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RECOVERY_MD, "w", encoding="utf-8") as f:
        f.write(header + rows_str + footer)


def generate_sources_md():
    sources_log = [e for e in RECOVERY_LOG if e["name"] != "TOTAL"]
    total = sum(e["rows"] for e in sources_log)
    now_str = now()
    md = "# FinalDataSet - Sources Summary\n\n"
    md += f"**Generated:** {now_str}\n"
    md += f"**Output file:** `payload_norm.csv`\n"
    md += f"**Total rows:** {total:,}\n"
    md += f"**Total sources:** {len(sources_log)}\n\n"
    md += "| # | Source | File(s) | Rows | Status |\n"
    md += "|---|--------|---------|-----:|--------|\n"
    for i, entry in enumerate(sources_log, 1):
        md += (
            f"| {i} | {entry['name']} | {entry['file']} "
            f"| {entry['rows']:,} | {entry['status']} |\n"
        )
    md += f"\n| **Total** | | | **{total:,}** | |\n\n"
    md += "---\n"
    md += f"*Auto-generated by `extract_to_payload_norm.py` at {now_str}*\n"
    with open(SOURCES_MD, "w", encoding="utf-8") as f:
        f.write(md)


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    csv.field_size_limit(10 * 1024 * 1024)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output -> {OUTPUT_CSV}")
    print(f"Recovery -> {RECOVERY_MD}")
    print()

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["payload_norm"])

        sources = [
            ("RbSQLi", "rbsqli_dataset.csv", gen_rbsqli),
            ("Zenodo", "zenodo_dataset.csv", gen_zenodo),
            ("Github HTTP Params", "github_http_params/", gen_github_http_params),
            ("Github Yogsec", "github_yogsec_payloads/", gen_github_yogsec),
            ("Github Payloadbox", "github_payloadbox/", gen_github_payloadbox),
            ("PayloadsAllTheThings", "github_payloadsallthethings/", gen_github_payloadsallthethings),
            ("Github FuzzDB", "github_fuzzdb/", gen_github_fuzzdb),
            ("BCCC-SFU", "bccc_sfu/", gen_bccc_sfu),
            ("Gist johntroony", "gist_johntroony/", gen_gist_johntroony),
            ("Github ajinmathew", "github_ajinmathew/", gen_github_ajinmathew),
            ("Github sqliv5", "github_sqliv5/", gen_github_sqliv5),
            ("CSIC-ECML", "github_csic_ecml_combined/", gen_github_csic_ecml),
            ("Kaggle sources", "kaggle/", gen_kaggle_sources),
            ("Benign complex", "spider/ + huggingface/", gen_benign_complex),
            ("Auto-discover", "catch-all", gen_auto_discover),
        ]

        total_rows = 0
        overall_start = now()

        for name, file_desc, gen_func in sources:
            start_t = time.time()
            start_str = now()
            print(f"[{start_str}] Processing: {name} ...", end="", flush=True)
            count = write_rows(writer, gen_func())
            elapsed = time.time() - start_t
            end_str = now()
            status = "OK" if count > 0 else "SKIP"
            print(f" {count:,} rows ({elapsed:.1f}s) [{status}]")
            RECOVERY_LOG.append({
                "name": name,
                "file": file_desc,
                "rows": count,
                "start": start_str,
                "end": end_str,
                "status": status,
            })
            total_rows += count
            write_recovery_checkpoint()

    overall_end = now()
    RECOVERY_LOG.append({
        "name": "TOTAL",
        "file": "",
        "rows": total_rows,
        "start": overall_start,
        "end": overall_end,
        "status": "DONE",
    })
    write_recovery_checkpoint()
    generate_sources_md()

    print()
    print("=" * 50)
    print(f"COMPLETED")
    print(f"  Total rows: {total_rows:,}")
    print(f"  Output: {OUTPUT_CSV}")
    print(f"  Recovery: {RECOVERY_MD}")
    print(f"  Sources: {SOURCES_MD}")
    print("=" * 50)


if __name__ == "__main__":
    main()
