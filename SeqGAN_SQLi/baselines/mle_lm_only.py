"""Baseline: generate from MLE-only checkpoint (no RL)."""
import os
import sys
import subprocess

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_samples', type=int, default=1000)
    parser.add_argument('--out', default='eval_mle.csv')
    parser.add_argument('--ckpt', default='checkpoints/mle_best.pt')
    args = parser.parse_args()

    subprocess.run([
        sys.executable,
        os.path.join(ROOT, 'generate.py'),
        '--ckpt', args.ckpt,
        '--n_samples', str(args.n_samples),
        '--out', args.out,
    ], check=True, cwd=os.path.join(ROOT, '..'))


if __name__ == '__main__':
    main()
