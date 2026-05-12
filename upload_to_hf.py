"""
Upload SeqGAN SQLi checkpoints to Hugging Face Hub.
Usage:
    python upload_to_hf.py --token <HF_TOKEN> [--repo <repo_name>]
"""

import argparse
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo

HF_USERNAME = "MinhBe"  # đổi nếu username HF khác với GitHub

CHECKPOINTS = [
    # (local_path, path_in_repo)
    ("SeqGAN_SQLi/checkpoints/mle_best.pt",            "main/mle_best.pt"),
    ("SeqGAN_SQLi/checkpoints/mle_final.pt",           "main/mle_final.pt"),
    ("SeqGAN_SQLi/checkpoints/adv_final.pt",           "main/adv_final.pt"),
    ("SeqGAN_SQLi/checkpoints/adv_step1000.pt",        "main/adv_step1000.pt"),
    ("SeqGAN_SQLi/checkpoints/adv_step2000.pt",        "main/adv_step2000.pt"),
    ("SeqGAN_SQLi/checkpoints/adv_step3000.pt",        "main/adv_step3000.pt"),
    ("SeqGAN_SQLi/checkpoints/adv_step4000.pt",        "main/adv_step4000.pt"),
    ("SeqGAN_SQLi/checkpoints/adv_step5000.pt",        "main/adv_step5000.pt"),
    # error_based variant
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/mle_best.pt",     "error_based/mle_best.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/mle_final.pt",    "error_based/mle_final.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/adv_final.pt",    "error_based/adv_final.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/adv_step1000.pt", "error_based/adv_step1000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/adv_step2000.pt", "error_based/adv_step2000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/adv_step3000.pt", "error_based/adv_step3000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/adv_step4000.pt", "error_based/adv_step4000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based/adv_step5000.pt", "error_based/adv_step5000.pt"),
    # error_based_entropy variant
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based_entropy/adv_final.pt",    "error_based_entropy/adv_final.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based_entropy/adv_step1000.pt", "error_based_entropy/adv_step1000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based_entropy/adv_step2000.pt", "error_based_entropy/adv_step2000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based_entropy/adv_step3000.pt", "error_based_entropy/adv_step3000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based_entropy/adv_step4000.pt", "error_based_entropy/adv_step4000.pt"),
    ("SeqGAN_SQLi/SeqGAN_SQLi/checkpoints/error_based_entropy/adv_step5000.pt", "error_based_entropy/adv_step5000.pt"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=None, help="Hugging Face API token (hoặc để trống để nhập tương tác)")
    parser.add_argument("--repo", default="GAN_SQLi-checkpoints", help="Repo name on HF")
    parser.add_argument("--username", default=HF_USERNAME, help="HF username")
    args = parser.parse_args()

    token = args.token
    if not token:
        import getpass
        token = getpass.getpass("Paste HF token (https://huggingface.co/settings/tokens): ").strip()

    repo_id = f"{args.username}/{args.repo}"
    api = HfApi(token=token)

    print(f"Creating repo: {repo_id}")
    create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=token)

    total = len(CHECKPOINTS)
    for i, (local_path, repo_path) in enumerate(CHECKPOINTS, 1):
        if not os.path.exists(local_path):
            print(f"[{i}/{total}] SKIP (not found): {local_path}")
            continue
        size_mb = os.path.getsize(local_path) / 1024 / 1024
        print(f"[{i}/{total}] Uploading {local_path} ({size_mb:.0f}MB) -> {repo_path}")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"  Done.")

    print(f"\nAll done! View at: https://huggingface.co/{repo_id}")


if __name__ == "__main__":
    main()
