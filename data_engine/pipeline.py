"""
Pipeline — Orchestrator cho toàn bộ data engine.
Flow: Load → Normalize → Classify → Dedup → Split
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))

from loaders import load_all_sources
from normalizer import normalize_batch
from classifier import classify_batch, MLClassifier
from deduplicator import full_dedup_pipeline
from splitter import run_splitter

from config import OUTPUT_DIR, STATS_DIR


def run_pipeline(step: str = "all", input_path: str = None):
    """Chạy toàn bộ hoặc một bước của pipeline."""
    start_time = time.time()
    steps_run = []

    if step == "all":
        steps = ["load", "normalize", "classify", "dedup", "split"]
    else:
        steps = [step]

    samples = []

    for current_step in steps:
        print(f"\n{'='*60}")
        print(f"  STEP: {current_step.upper()}")
        print(f"{'='*60}\n")

        if current_step == "load":
            samples = load_all_sources()
            steps_run.append("load")

        elif current_step == "normalize":
            if not samples:
                print("[ERROR] Không có data. Chạy step 'load' trước.")
                return
            samples = normalize_batch(samples)
            steps_run.append("normalize")

        elif current_step == "classify":
            if not samples:
                print("[ERROR] Không có data. Chạy step 'load' trước.")
                return
            samples = classify_batch(samples)
            steps_run.append("classify")

        elif current_step == "dedup":
            if not samples:
                print("[ERROR] Không có data. Chạy step 'load' trước.")
                return
            samples = full_dedup_pipeline(samples)
            steps_run.append("dedup")

        elif current_step == "split":
            if not samples:
                print("[ERROR] Không có data. Chạy step 'load' trước.")
                return
            stats = run_splitter(samples)
            steps_run.append("split")

            elapsed = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"  PIPELINE COMPLETE")
            print(f"{'='*60}")
            print(f"  Steps run: {', '.join(steps_run)}")
            print(f"  Total samples processed: {len(samples)}")
            print(f"  Time: {elapsed:.1f}s")
            print(f"  Output: {OUTPUT_DIR}")
            print(f"{'='*60}\n")
            return

    if step != "split":
        print(f"\n[+] Pipeline step '{step}' complete. {len(samples)} samples in memory.")
        print(f"    Chạy 'python pipeline.py --step split' để export kết quả.")


def main():
    parser = argparse.ArgumentParser(description="SQLi Data Engine Pipeline")
    parser.add_argument(
        "--step",
        choices=["all", "load", "normalize", "classify", "dedup", "split"],
        default="all",
        help="Pipeline step to run (default: all)",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to additional input file/directory",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  SQLi DATA ENGINE — PIPELINE")
    print("=" * 60)
    print(f"  Step: {args.step}")
    if args.input:
        print(f"  Additional input: {args.input}")
    print("=" * 60)

    run_pipeline(step=args.step, input_path=args.input)


if __name__ == "__main__":
    main()
