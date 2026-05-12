"""
generate_best.py — Quick generate từ warmup-trained model tốt nhất.

Usage:
  python SeqGAN_SQLi/generate_best.py --n 1000 --out output.csv
  python SeqGAN_SQLi/generate_best.py --n 500 --type 0   # error_based only
  python SeqGAN_SQLi/generate_best.py --n 500 --type 1   # boolean_blind only
"""
import argparse
import subprocess
import sys
from pathlib import Path

BEST_CKPT = "SeqGAN_SQLi/checkpoints/v3/adv_step2000.pt"
CONFIG    = "SeqGAN_SQLi/configs/seqgan_v3.yaml"

# Attack type IDs
TYPE_MAP = {0: "error_based", 1: "boolean_blind", 2: "time_blind", 3: "union_based"}


def main():
    parser = argparse.ArgumentParser(description="Generate từ V3 warmup-trained model")
    parser.add_argument("--n", type=int, default=1000, help="Số lượng samples")
    parser.add_argument("--out", default="generated_payloads.csv", help="Output CSV")
    parser.add_argument("--type", type=int, default=None, choices=[0, 1, 2, 3],
                        help="Attack type: 0=error_based 1=boolean_blind 2=time_blind 3=union_based")
    parser.add_argument("--ckpt", default=BEST_CKPT, help="Override checkpoint path")
    args = parser.parse_args()

    ckpt = Path(args.ckpt)
    if not ckpt.exists():
        print(f"ERROR: checkpoint not found: {ckpt}")
        print("  Run train_adversarial_v3.py first, or check path.")
        sys.exit(1)

    type_label = TYPE_MAP.get(args.type, "all types") if args.type is not None else "all types (random)"
    print(f"Model  : {ckpt}")
    print(f"Samples: {args.n}")
    print(f"Type   : {type_label}")
    print(f"Output : {args.out}")
    print()

    cmd = [
        sys.executable, "SeqGAN_SQLi/generate_v2.py",
        "--config", CONFIG,
        "--ckpt", str(ckpt),
        "--n_samples", str(args.n),
        "--out", args.out,
    ]
    if args.type is not None:
        cmd += ["--attack_type", str(args.type)]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
