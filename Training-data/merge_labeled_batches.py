import argparse
import csv
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("merge_labeled_batches")

OUTPUT_FIELDS = ["row_index", "payload_norm", "sqli_type", "db_engine",
                 "confidence", "reasoning", "label_source"]


def merge_batches(input_dir: str, output: str):
    input_path = Path(input_dir)
    csv_files = sorted(input_path.glob("labeled_*.csv"))
    logger.info("Found %d labeled batch files in %s", len(csv_files), input_dir)

    all_rows = []
    for fpath in csv_files:
        with open(fpath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned = {}
                for k, v in row.items():
                    key = k.strip().strip('"').strip("'")
                    cleaned[key] = v if v else ""
                all_rows.append(cleaned)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    logger.info("Wrote %d merged rows to %s", len(all_rows), output)


def main():
    parser = argparse.ArgumentParser(description="Merge labeled batch CSVs")
    parser.add_argument("--input-dir", required=True, help="Directory with labeled_*.csv files")
    parser.add_argument("--output", "-o", required=True, help="Output merged CSV path")
    args = parser.parse_args()
    merge_batches(args.input_dir, args.output)


if __name__ == "__main__":
    main()
