"""
Full pipeline runner: Adversarial training → Generate → Evaluate → Report.
Chạy từ GAN_SQLi root:
  python -u SeqGAN_SQLi/run_full_pipeline.py
Log: SeqGAN_SQLi/pipeline.log
"""
import os
import sys
import time
import json
import subprocess
import datetime

ROOT_PROJ = os.path.dirname(os.path.abspath(__file__))   # SeqGAN_SQLi/
ROOT_WORK = os.path.dirname(ROOT_PROJ)                   # GAN_SQLi/
LOG_PATH = os.path.join(ROOT_PROJ, 'pipeline.log')

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────

def log(msg: str, also_print: bool = True):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    if also_print:
        print(line, flush=True)


def section(title: str):
    bar = '=' * 60
    log(bar)
    log(f"  {title}")
    log(bar)


# ──────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────

def run_step(name: str, cmd: list, timeout: int = None, cwd: str = ROOT_WORK) -> bool:
    """Run a command, stream output to both console and log file. Returns success."""
    log(f">> START: {name}")
    log(f"   cmd : {' '.join(cmd)}")
    t0 = time.time()
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            env={**os.environ, 'PYTHONUNBUFFERED': '1'},
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        with open(LOG_PATH, 'a', encoding='utf-8') as lf:
            for line in proc.stdout:
                line = line.rstrip('\n')
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                out = f"[{ts}]   {line}"
                print(out, flush=True)
                lf.write(out + '\n')
        proc.wait(timeout=timeout)
        elapsed = time.time() - t0
        if proc.returncode == 0:
            log(f"<< OK: {name}  ({elapsed:.0f}s)")
            return True
        else:
            log(f"<< FAIL: {name} (exit={proc.returncode}, {elapsed:.0f}s)")
            return False
    except subprocess.TimeoutExpired:
        proc.kill()
        log(f"<< TIMEOUT: {name}")
        return False
    except Exception as e:
        log(f"<< ERROR: {name} — {e}")
        return False


# ──────────────────────────────────────────────
# Pipeline steps
# ──────────────────────────────────────────────

def phase_adversarial():
    section("PHASE 1 — Adversarial RL Training (5k steps, fast config)")
    ok = run_step(
        "Adversarial training",
        [sys.executable, '-u',
         'SeqGAN_SQLi/train_adversarial.py',
         '--config', 'SeqGAN_SQLi/configs/seqgan_fast.yaml',
         '--mle_ckpt', 'SeqGAN_SQLi/checkpoints/mle_best.pt'],
        timeout=7200,  # 2-hour hard limit
    )
    if not ok:
        log("ERROR: Adversarial training failed. Aborting pipeline.")
        sys.exit(1)
    return ok


def phase_generate():
    section("PHASE 2 — Generate Samples (SeqGAN + Baselines)")

    # SeqGAN (adversarial)
    run_step(
        "Generate: SeqGAN (adv_final)",
        [sys.executable, '-u',
         'SeqGAN_SQLi/generate.py',
         '--ckpt', 'SeqGAN_SQLi/checkpoints/adv_final.pt',
         '--n_samples', '1000',
         '--out', 'eval_seqgan.csv'],
        timeout=300,
    )

    # MLE-only baseline
    run_step(
        "Generate: MLE-only baseline",
        [sys.executable, '-u',
         'SeqGAN_SQLi/generate.py',
         '--ckpt', 'SeqGAN_SQLi/checkpoints/mle_best.pt',
         '--n_samples', '1000',
         '--out', 'eval_mle.csv'],
        timeout=300,
    )

    # Template baseline
    run_step(
        "Generate: Template baseline",
        [sys.executable, '-u',
         'SeqGAN_SQLi/baselines/template_based.py',
         '--n_samples', '1000',
         '--out', 'eval_template.csv'],
        timeout=60,
    )


def phase_evaluate():
    section("PHASE 3 — Evaluate All Models")
    results = {}

    targets = [
        ('SeqGAN (adv)', 'eval_seqgan.csv'),
        ('MLE only',     'eval_mle.csv'),
        ('Template',     'eval_template.csv'),
    ]

    for name, csv_file in targets:
        csv_path = os.path.join(ROOT_WORK, csv_file)
        if not os.path.exists(csv_path):
            log(f"SKIP: {csv_file} not found")
            continue

        out_json = csv_file.replace('.csv', '_metrics.json')
        log(f"\n--- Evaluating: {name} ---")
        ok = run_step(
            f"Evaluate {name}",
            [sys.executable, '-u',
             'SeqGAN_SQLi/evaluate.py',
             '--input', csv_file,
             '--n_samples', '1000',
             '--out', out_json],
            timeout=600,
        )
        if ok and os.path.exists(os.path.join(ROOT_WORK, out_json)):
            with open(os.path.join(ROOT_WORK, out_json)) as f:
                results[name] = json.load(f)

    return results


def phase_report(results: dict):
    section("PHASE 4 — Comparison Report")
    if not results:
        log("No results to report.")
        return

    log("\n" + "=" * 72)
    log(f"{'Model':<22} {'ASR':>8} {'Syntax%':>10} {'Self-BLEU3':>12} {'N':>6}")
    log("-" * 72)

    mle_asr = None
    for name, m in results.items():
        asr = m.get('asr_mean', float('nan'))
        syn = m.get('syntax_rate', float('nan'))
        bleu = m.get('self_bleu_3', float('nan'))
        n = m.get('n_samples', 0)
        if name == 'MLE only':
            mle_asr = asr
        log(f"{name:<22} {asr:>7.1%} {syn:>10.1%} {bleu:>12.4f} {n:>6}")

    log("=" * 72)

    # Hard target check
    log("\n--- Hard Targets ---")
    seqgan = results.get('SeqGAN (adv)', {})
    seqgan_asr = seqgan.get('asr_mean', 0)
    seqgan_syn = seqgan.get('syntax_rate', 0)
    seqgan_bleu = seqgan.get('self_bleu_3', 1.0)

    if mle_asr is not None:
        delta = seqgan_asr - mle_asr
        status = "PASS" if delta >= 0.30 else "FAIL"
        log(f"ASR delta vs MLE:  {delta:+.1%}  (target >=+30pp)  [{status}]")
    log(f"Syntax validity:   {seqgan_syn:.1%}  (target >=90%)  [{'PASS' if seqgan_syn >= 0.9 else 'FAIL'}]")
    log(f"Self-BLEU-3:       {seqgan_bleu:.4f}  (target <0.60)  [{'PASS' if seqgan_bleu < 0.6 else 'FAIL'}]")

    # Save report
    report_path = os.path.join(ROOT_PROJ, 'timeline', 'eval_report.json')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump({'timestamp': datetime.datetime.now().isoformat(),
                   'results': results}, f, indent=2)
    log(f"\nReport saved: {report_path}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    # Clear old log
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(f"Pipeline started: {datetime.datetime.now()}\n")
        f.write(f"Working dir: {ROOT_WORK}\n\n")

    t_start = time.time()
    log("Pipeline: Adversarial Training -> Generate -> Evaluate -> Report")
    log(f"Log file: {LOG_PATH}")

    phase_adversarial()
    phase_generate()
    results = phase_evaluate()
    phase_report(results)

    elapsed = time.time() - t_start
    section(f"PIPELINE COMPLETE — Total time: {elapsed/60:.1f} min")
    log(f"Monitor: Get-Content SeqGAN_SQLi/pipeline.log -Tail 20")


if __name__ == '__main__':
    main()
