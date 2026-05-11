import argparse
import csv
import logging
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classifier import classify, ClassifyResult
from llm_client import classify_via_llm


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("labeler")

OUTPUT_FIELDS = ["row_index", "payload_norm", "sqli_type", "db_engine",
                 "confidence", "reasoning", "label_source"]


def read_csv(path: str) -> tuple[list[dict], list[str]]:
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


def write_csv(path: str, rows: list[dict], fieldnames: list[str]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_single_payload(payload: str, use_llm: bool = False,
                           llm_provider: str = "gemini",
                           api_key: str = "") -> ClassifyResult:
    result = classify(payload)
    if result and result.confidence < 0.7 and use_llm:
        llm_result = classify_via_llm(payload, provider=llm_provider, api_key=api_key)
        if llm_result:
            result = llm_result
    return result


def label_row(row: dict, mode: str, use_llm: bool,
              llm_provider: str, api_key: str) -> dict:
    payload = row.get("payload_norm", "")
    if not payload:
        row["sqli_type"] = row.get("sqli_type", "unknown")
        row["db_engine"] = row.get("db_engine", "unknown")
        row["confidence"] = row.get("confidence", "0.50")
        row["reasoning"] = row.get("reasoning", "Empty payload")
        row["label_source"] = "pass-through"
        return row

    current_type = row.get("sqli_type", "").strip()
    try:
        current_conf = float(row.get("confidence", 0))
    except (ValueError, TypeError):
        current_conf = 0.0

    if mode == "unlabeled" and current_type:
        row["label_source"] = "existing"
        return row
    if mode == "low-confidence" and (not current_type or current_conf >= 0.7):
        row["label_source"] = "existing"
        return row
    if mode == "out-of-taxonomy" and current_type in {"", "unknown"}:
        pass
    elif mode == "out-of-taxonomy" and current_type:
        from shared.taxonomy import VALID_TYPES, NORMALIZE_MAP
        if current_type in VALID_TYPES and current_type not in NORMALIZE_MAP:
            row["label_source"] = "existing"
            return row

    result = process_single_payload(payload, use_llm, llm_provider, api_key)
    if result:
        row["sqli_type"] = result.sqli_type
        row["db_engine"] = result.db_engine
        row["confidence"] = str(result.confidence)
        row["reasoning"] = result.reasoning
        row["label_source"] = "llm" if (use_llm and result.confidence < 0.7
                                         and current_conf < 0.7) else "rule-based"
    else:
        row["sqli_type"] = row.get("sqli_type", "unknown")
        row["db_engine"] = row.get("db_engine", "unknown")
        row["confidence"] = row.get("confidence", "0.50")
        row["reasoning"] = row.get("reasoning", "Classification failed")
        row["label_source"] = "fallback"

    return row


def cmd_label(args):
    rows, fieldnames = read_csv(args.input)
    logger.info("Loaded %d rows from %s", len(rows), args.input)

    supported_modes = {"all", "low-confidence", "out-of-taxonomy", "unlabeled"}
    mode = args.mode or "all"

    updated = []
    for row in rows:
        updated.append(label_row(row, mode, args.llm_fallback,
                                 args.llm_provider, args.api_key))

    output_fields = fieldnames
    if "label_source" not in output_fields:
        output_fields = output_fields + ["label_source"]

    write_csv(args.output, updated, output_fields)
    logger.info("Wrote %d rows to %s", len(updated), args.output)


def cmd_single(args):
    result = process_single_payload(args.payload, args.llm_fallback,
                                    args.llm_provider, args.api_key)
    if result:
        print(f"sqli_type:   {result.sqli_type}")
        print(f"db_engine:   {result.db_engine}")
        print(f"confidence:  {result.confidence}")
        print(f"reasoning:   {result.reasoning}")
    else:
        print("Classification failed")
        sys.exit(1)


def cmd_batch(args):
    batches_dir = Path(args.batches_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_files = list(batches_dir.glob("*.csv"))
    logger.info("Found %d batch files in %s", len(csv_files), batches_dir)

    def process_file(csv_path: Path):
        rows, fieldnames = read_csv(str(csv_path))
        updated = []
        for row in rows:
            updated.append(label_row(row, "all", args.llm_fallback,
                                     args.llm_provider, args.api_key))
        output_path = results_dir / f"labeled_{csv_path.name}"
        output_fields = fieldnames[:]
        for f in OUTPUT_FIELDS:
            if f not in output_fields:
                output_fields.append(f)
        write_csv(str(output_path), updated, output_fields)
        return csv_path.name

    n_workers = args.workers or 1
    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        results = list(pool.map(process_file, csv_files))

    logger.info("Processed %d batch files", len(results))


def main():
    parser = argparse.ArgumentParser(description="SQLi Labeler")
    sub = parser.add_subparsers(dest="command", required=True)

    p_label = sub.add_parser("label", help="Label/re-label CSV")
    p_label.add_argument("input", help="Input CSV path")
    p_label.add_argument("--mode", choices=["all", "low-confidence", "out-of-taxonomy", "unlabeled"],
                        default="all", help="Labeling mode")
    p_label.add_argument("--llm-fallback", action="store_true", help="Use LLM when confidence < 0.7")
    p_label.add_argument("--llm-provider", default="gemini", help="LLM provider (gemini/openai)")
    p_label.add_argument("--api-key", default="", help="API key for LLM")
    p_label.add_argument("--output", "-o", required=True, help="Output CSV path")

    p_single = sub.add_parser("single", help="Label single payload")
    p_single.add_argument("payload", help="Payload string to classify")
    p_single.add_argument("--llm-fallback", action="store_true")
    p_single.add_argument("--llm-provider", default="gemini")
    p_single.add_argument("--api-key", default="")

    p_batch = sub.add_parser("batch", help="Label batch files in directory")
    p_batch.add_argument("batches_dir", help="Directory with batch CSV files")
    p_batch.add_argument("results_dir", help="Output directory for results")
    p_batch.add_argument("--workers", type=int, default=1, help="Parallel workers")
    p_batch.add_argument("--llm-fallback", action="store_true")
    p_batch.add_argument("--llm-provider", default="gemini")
    p_batch.add_argument("--api-key", default="")

    args = parser.parse_args()
    if args.command == "label":
        cmd_label(args)
    elif args.command == "single":
        cmd_single(args)
    elif args.command == "batch":
        cmd_batch(args)


if __name__ == "__main__":
    main()
