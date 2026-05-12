"""
Upload SeqGAN SQLi dataset, checkpoints, và eval results lên Hugging Face Hub.

Usage:
    python upload_to_hf.py --token <HF_TOKEN> [--repo <repo_name>] [--skip_ckpt]
"""

import argparse
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo

HF_USERNAME = "MinhBe"

# ── Checkpoints ──────────────────────────────────────────────────────────────
# Format: (local_path, path_in_repo)
CHECKPOINTS = [
    # V2 — MLE pretrain
    ("SeqGAN_SQLi/checkpoints/v2/mle_best.pt",          "v2/mle_best.pt"),
    ("SeqGAN_SQLi/checkpoints/v2/mle_final.pt",         "v2/mle_final.pt"),
    # V2 — Adversarial (key steps)
    ("SeqGAN_SQLi/checkpoints/v2/adv_step1000.pt",      "v2/adv_step1000.pt"),
    ("SeqGAN_SQLi/checkpoints/v2/adv_step2000.pt",      "v2/adv_step2000.pt"),
    ("SeqGAN_SQLi/checkpoints/v2/adv_final.pt",         "v2/adv_final.pt"),
    # V3 — Entropy regularization (key steps)
    ("SeqGAN_SQLi/checkpoints/v3/adv_step1000.pt",      "v3/adv_step1000.pt"),
    ("SeqGAN_SQLi/checkpoints/v3/adv_step2000.pt",      "v3/adv_step2000.pt"),   # BEST
    ("SeqGAN_SQLi/checkpoints/v3/adv_step12000.pt",     "v3/adv_step12000.pt"),
    ("SeqGAN_SQLi/checkpoints/v3/adv_final.pt",         "v3/adv_final.pt"),
]

# ── Dataset & eval artifacts ──────────────────────────────────────────────────
EXTRA_FILES = [
    # Dataset V2
    ("SeqGAN_SQLi/data/v2/train.csv",                   "data/v2/train.csv"),
    ("SeqGAN_SQLi/data/v2/val.csv",                     "data/v2/val.csv"),
    ("SeqGAN_SQLi/data/v2/test.csv",                    "data/v2/test.csv"),
    ("SeqGAN_SQLi/data/v2/tokenizer_vocab.json",        "data/v2/tokenizer_vocab.json"),
    ("SeqGAN_SQLi/data/v2/type_mapping.json",           "data/v2/type_mapping.json"),
    ("SeqGAN_SQLi/data/relex_dictionary.json",          "data/relex_dictionary.json"),
    # Eval results (with & without WAF)
    ("SeqGAN_SQLi/eval/results_v3/v3_adv_step2000.json",     "eval/v3_step2000_nowaf.json"),
    ("SeqGAN_SQLi/eval/results_v3/v3_adv_step2000_waf.json", "eval/v3_step2000_waf.json"),
    # Generated samples (best model)
    ("SeqGAN_SQLi/eval/samples_v3/v3_adv_step2000.csv",      "samples/v3_best_500.csv"),
    # Timeline summary
    ("SeqGAN_SQLi/timeline/IMPROVEMENTS_SUMMARY.md",         "IMPROVEMENTS_SUMMARY.md"),
]


def upload_files(api, repo_id, files, label):
    total = len(files)
    skipped = 0
    for i, (local_path, repo_path) in enumerate(files, 1):
        if not os.path.exists(local_path):
            print(f"[{i}/{total}] SKIP (not found): {local_path}")
            skipped += 1
            continue
        size_mb = os.path.getsize(local_path) / 1024 / 1024
        print(f"[{i}/{total}] {label}: {local_path} ({size_mb:.1f}MB) -> {repo_path}")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=repo_id,
            repo_type="model",
        )
    return total - skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token",    default=None, help="HF API token")
    parser.add_argument("--repo",     default="GAN_SQLi-SeqGAN", help="Repo name")
    parser.add_argument("--username", default=HF_USERNAME)
    parser.add_argument("--skip_ckpt", action="store_true", help="Skip checkpoint upload (data/eval only)")
    args = parser.parse_args()

    token = args.token
    if not token:
        import getpass
        token = getpass.getpass("Paste HF token (https://huggingface.co/settings/tokens): ").strip()

    repo_id = f"{args.username}/{args.repo}"
    api = HfApi(token=token)

    print(f"Creating repo: {repo_id}")
    create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=token,
                private=False)

    if not args.skip_ckpt:
        n = upload_files(api, repo_id, CHECKPOINTS, "CKPT")
        print(f"\nCheckpoints uploaded: {n}/{len(CHECKPOINTS)}")

    n = upload_files(api, repo_id, EXTRA_FILES, "FILE")
    print(f"Extra files uploaded: {n}/{len(EXTRA_FILES)}")

    print(f"\nDone! View at: https://huggingface.co/{repo_id}")


if __name__ == "__main__":
    main()
