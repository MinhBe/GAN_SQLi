"""
eval/run_eval_pipeline_v2.py — Post-training V2 evaluation pipeline.

Runs after adversarial training completes:
  1. Generate samples from each checkpoint
  2. Run 5-metric evaluate_v2 on each
  3. Compare results → comparison.csv + comparison.md

Usage (from GAN_SQLi root):
  python SeqGAN_SQLi/eval/run_eval_pipeline_v2.py [--no_waf] [--n_samples 500]
"""
import argparse
import json
import os
import subprocess
import sys
import time
import datetime
from pathlib import Path

ROOT_WORK = Path(__file__).parent.parent.parent  # GAN_SQLi/
ROOT_PROJ = ROOT_WORK / "SeqGAN_SQLi"
CKPT_DIR = ROOT_PROJ / "checkpoints" / "v2"
RESULTS_DIR = ROOT_PROJ / "eval" / "results"
SAMPLES_DIR = ROOT_PROJ / "eval" / "samples"
IDS_DIR = ROOT_PROJ / "eval" / "ids_classifier"
CONFIG = ROOT_PROJ / "configs" / "seqgan_v2.yaml"
LOG_PATH = ROOT_PROJ / "eval" / "eval_pipeline.log"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: list, timeout: int = 600, name: str = "") -> bool:
    log(f">> {name or ' '.join(cmd[:3])}")
    t0 = time.time()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(ROOT_WORK),
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    with open(LOG_PATH, "a", encoding="utf-8") as lf:
        for line in proc.stdout:
            out = f"    {line.rstrip()}"
            print(out, flush=True)
            lf.write(out + "\n")
    proc.wait(timeout=timeout)
    elapsed = time.time() - t0
    ok = proc.returncode == 0
    log(f"<< {'OK' if ok else 'FAIL'} ({elapsed:.0f}s)")
    return ok


def discover_checkpoints() -> list:
    """Find all V2 checkpoints in order: mle_best, adv_step*, adv_final."""
    ckpts = []

    mle = CKPT_DIR / "mle_best.pt"
    if mle.exists():
        ckpts.append(("v2_mle", str(mle)))

    step_files = sorted(
        CKPT_DIR.glob("adv_step*.pt"),
        key=lambda p: int(p.stem.replace("adv_step", "")),
    )
    for p in step_files:
        step = p.stem.replace("adv_step", "")
        ckpts.append((f"v2_step{step}", str(p)))

    final = CKPT_DIR / "adv_final.pt"
    if final.exists():
        ckpts.append(("v2_refined", str(final)))

    return ckpts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no_waf", action="store_true")
    parser.add_argument("--n_samples", type=int, default=500)
    parser.add_argument("--ids_dir", default=str(IDS_DIR))
    args = parser.parse_args()

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(f"V2 Eval Pipeline started: {datetime.datetime.now()}\n\n")

    log(f"WAF: {'disabled' if args.no_waf else 'enabled'}")
    log(f"Samples per checkpoint: {args.n_samples}")

    ckpts = discover_checkpoints()
    if not ckpts:
        log("ERROR: No V2 checkpoints found in " + str(CKPT_DIR))
        sys.exit(1)

    log(f"Checkpoints found: {[n for n, _ in ckpts]}")

    for model_name, ckpt_path in ckpts:
        log(f"\n{'='*60}")
        log(f"Evaluating: {model_name}")
        log(f"{'='*60}")

        samples_csv = str(SAMPLES_DIR / f"{model_name}.csv")
        out_json = str(RESULTS_DIR / f"{model_name}.json")

        # Step 1: Generate
        gen_cmd = [
            sys.executable, "-u", "SeqGAN_SQLi/generate_v2.py",
            "--config", str(CONFIG),
            "--ckpt", ckpt_path,
            "--n_samples", str(args.n_samples),
            "--out", samples_csv,
        ]
        ok = run(gen_cmd, timeout=300, name=f"Generate {model_name}")
        if not ok:
            log(f"SKIP evaluate for {model_name} (generate failed)")
            continue

        # Step 2: Evaluate
        eval_cmd = [
            sys.executable, "-u", "SeqGAN_SQLi/eval/evaluate_v2.py",
            "--samples_csv", samples_csv,
            "--out_json", out_json,
            "--config", str(CONFIG),
            "--ids_dir", args.ids_dir,
        ]
        if args.no_waf:
            eval_cmd.append("--no_waf")

        run(eval_cmd, timeout=900, name=f"Evaluate {model_name}")

    # Step 3: Compare
    log("\n" + "=" * 60)
    log("Comparing all results...")
    compare_cmd = [
        sys.executable, "-u", "SeqGAN_SQLi/eval/compare_results.py",
        "--results_dir", str(RESULTS_DIR),
        "--out_csv", str(ROOT_PROJ / "eval" / "comparison.csv"),
        "--out_md", str(ROOT_PROJ / "eval" / "comparison.md"),
    ]
    run(compare_cmd, timeout=60, name="Compare results")

    log(f"\nDone. Results in {RESULTS_DIR}")
    log(f"Summary: {ROOT_PROJ / 'eval' / 'comparison.md'}")


if __name__ == "__main__":
    main()
