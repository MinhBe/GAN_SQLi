#!/usr/bin/env python3
"""
Pipeline Orchestrator — SQLi labeling pipeline (rule-based, no LLM API).

Usage:
    python pipeline_run.py [--data-dir ASSET/LabelData] [--skill-dir Skill]

Steps:
    1. Validate + normalize existing labels
    2a. Re-label low-confidence rows (rule-based)
    2b. Fix out-of-taxonomy rows
    3. Label remaining unlabeled rows
    4. Critic review v1 (8 checks)
    5. Re-label REJECT rows using critic corrections + improved classifier
    6. Critic review v2 (final verification)
    7. Export master dataset (PASS + FLAG)
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("pipeline")


def run_step(step_num: int, description: str, cmd: list[str]) -> bool:
    logger.info("=== Step %d: %s ===", step_num, description)
    logger.info("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                logger.info("  %s", line)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Step %d failed with exit code %d", step_num, e.returncode)
        if e.stderr:
            for line in e.stderr.strip().split("\n"):
                logger.error("  %s", line)
        return False


def main():
    parser = argparse.ArgumentParser(description="SQLi Labeling Pipeline")
    parser.add_argument("--data-dir", default="Asset/LabelData",
                       help="Directory containing combined_labeled_data.csv")
    parser.add_argument("--skill-dir", default="Skill",
                       help="Directory containing skill modules")
    parser.add_argument("--input", help="Input CSV path (default: <data-dir>/combined_labeled_data.csv)")
    parser.add_argument("--llm-fallback", action="store_true",
                       help="Use LLM for ambiguous cases")
    parser.add_argument("--llm-provider", default="gemini")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--audit-sample", type=int, default=500)
    parser.add_argument("--start-step", type=int, default=1,
                       help="Start from step N (1-7)")
    parser.add_argument("--end-step", type=int, default=7,
                       help="End at step N (1-7)")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    skill_dir = Path(args.skill_dir)

    input_csv = args.input or str(data_dir / "combined_labeled_data.csv")

    steps = [
        {
            "num": 1,
            "desc": "Validate + normalize labels",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-label-validator" / "validator.py"),
                "normalize", input_csv,
                "--output", str(data_dir / "step1_validated.csv"),
                "--corrections", str(data_dir / "step1_corrections.csv"),
            ],
        },
        {
            "num": 2,
            "desc": "Re-label low-confidence rows (rule-based)",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-labeler" / "labeler.py"),
                "label", str(data_dir / "step1_validated.csv"),
                "--mode", "low-confidence",
                "--output", str(data_dir / "step2a_relabeled.csv"),
            ],
        },
        {
            "num": 3,
            "desc": "Fix out-of-taxonomy + fill unlabeled rows",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-labeler" / "labeler.py"),
                "label", str(data_dir / "step2a_relabeled.csv"),
                "--mode", "out-of-taxonomy",
                "--output", str(data_dir / "step3_unlabeled_filled.csv"),
            ],
        },
        {
            "num": 4,
            "desc": "Critic review v1 (8 checks + benign audit)",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-label-critic" / "critic.py"),
                "review", str(data_dir / "step3_unlabeled_filled.csv"),
                "--extended-checks", "confidence,structure,historical",
                "--audit-sample", str(args.audit_sample),
                "--output-dir", str(data_dir / "critic_output"),
            ],
        },
        {
            "num": 5,
            "desc": "Re-label REJECT rows (critic corrections + classifier)",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-labeler" / "relabeler.py"),
                str(data_dir / "critic_output" / "critic_results.csv"),
                "--output", str(data_dir / "step5_relabeled.csv"),
                "--diff", str(data_dir / "step5_diff.csv"),
            ],
        },
        {
            "num": 6,
            "desc": "Critic review v2 (final verification)",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-label-critic" / "critic.py"),
                "review", str(data_dir / "step5_relabeled.csv"),
                "--extended-checks", "confidence,structure,historical",
                "--audit-sample", str(args.audit_sample),
                "--output-dir", str(data_dir / "critic_output_v2"),
            ],
        },
        {
            "num": 7,
            "desc": "Export master dataset",
            "cmd": [
                sys.executable, str(skill_dir / "sqli-label-critic" / "critic.py"),
                "export-master", str(data_dir / "critic_output_v2" / "critic_results.csv"),
                "--output", str(data_dir / "master_labeled_data.csv"),
            ],
        },
    ]

    for step in steps:
        if step["num"] < args.start_step or step["num"] > args.end_step:
            continue
        if not run_step(step["num"], step["desc"], step["cmd"]):
            logger.error("Pipeline failed at step %d. Aborting.", step["num"])
            sys.exit(1)

    logger.info("=== Pipeline completed successfully ===")
    logger.info("Master dataset: %s/master_labeled_data.csv", data_dir)


if __name__ == "__main__":
    main()
