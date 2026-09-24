# GAN_SQLi full replacement package — GRADFIX

Use this package when you want to replace the GitHub repository completely.

## What to upload to GitHub
Upload the CONTENTS of this folder to the root of `MinhBe/GAN_SQLi`.
Do not upload this folder as a nested directory.

The root should contain:

- `sqlgan_dual/`
- `A_generator_attack_corpus/`
- `B_random_forest_feature_dataset/`
- `C_llm_hard_cases/`
- `validation/`
- `metrics/`
- `notebooks/`
- `requirements.txt`
- `pyproject.toml`
- `README.md`
- `README_TRAINING_GRADFIX.md`
- `dataset_manifest.json`

## Kaggle notebooks to use
Use only these two notebooks:

- `01_kaggle_branch_a_four_module_dual_t4_selfcontained_GRADFIX.ipynb`
- `02_kaggle_branch_b_core_renderer_dual_t4_selfcontained_GRADFIX.ipynb`

Discard older notebook versions: `FIXED`, `DATAFALLBACK`, `JOBFIX`, and non-GRADFIX notebooks.

## What is fixed

- Self-contained toolkit fallback.
- Dataset fallback: zip input or cloned repo folder.
- Subprocess `PYTHONPATH` propagation.
- PyTorch in-place gradient error in adversarial training.

## Data status

This repository still uses the V4.1 static training corpus. PostgreSQL runtime validation is not yet claimed.
