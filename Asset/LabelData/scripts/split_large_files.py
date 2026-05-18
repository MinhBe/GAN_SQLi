import csv
import time
from pathlib import Path

TARGET_BYTES = 90 * 1024 * 1024  # 90 MB hard cap per chunk
FILES = [
    Path("Asset/LabelData/Dataset Source/rbsqli_dataset.csv"),
    Path("Asset/LabelData/Dataset Source/zenodo_dataset.csv"),
    Path("Asset/LabelData/FinalDataSet/final_dataset.csv"),
]


def split_file(path: Path):
    print(f"\n=== {path.name}  ({path.stat().st_size / 1024**2:.0f} MB) ===")
    parent = path.parent
    stem = path.stem

    for existing in parent.glob(f"{stem}_*.csv"):
        existing.unlink()

    start = time.time()
    chunk_i = 1
    chunk_rows = 0
    total_rows = 0
    current_size = 0

    with open(path, "r", encoding="utf-8", errors="replace", newline="") as src:
        reader = csv.reader(src)
        header = next(reader)
        header_bytes = len(",".join(header).encode("utf-8")) + 1

        def open_chunk():
            p = parent / f"{stem}_{chunk_i}.csv"
            fh = open(p, "w", encoding="utf-8", newline="")
            w = csv.writer(fh)
            w.writerow(header)
            return p, fh, w

        out_path, out_fh, writer = open_chunk()
        current_size = header_bytes

        for row in reader:
            row_bytes = len(",".join(row).encode("utf-8")) + 1
            if current_size + row_bytes > TARGET_BYTES:
                out_fh.close()
                actual_mb = out_path.stat().st_size / 1024**2
                print(f"  -> {out_path.name}: {chunk_rows:,} rows ({actual_mb:.1f} MB)")
                chunk_i += 1
                chunk_rows = 0
                current_size = header_bytes
                out_path, out_fh, writer = open_chunk()

            writer.writerow(row)
            current_size += row_bytes
            chunk_rows += 1
            total_rows += 1

        out_fh.close()
        actual_mb = out_path.stat().st_size / 1024**2
        print(f"  -> {out_path.name}: {chunk_rows:,} rows ({actual_mb:.1f} MB)")

    elapsed = time.time() - start
    print(f"  Done: {total_rows:,} rows in {chunk_i} chunks ({elapsed:.0f}s)")


def main():
    for path in FILES:
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue
        split_file(path)
    print("\nAll done.")


if __name__ == "__main__":
    main()
