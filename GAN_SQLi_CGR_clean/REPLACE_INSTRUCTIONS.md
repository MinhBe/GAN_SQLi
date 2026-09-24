# Replacement instructions

Copy these paths into the repository root, replacing existing files with the same names:

```text
sqlgan_dual/
validation/postgres_sandbox_validator.py
README.md
requirements.txt
pyproject.toml
tests/
```

Do not delete the dataset directories. This package expects the existing corpus layout:

```text
A_generator_attack_corpus/Y1_basic_boolean/...
A_generator_attack_corpus/Y2_boolean_variation/...
A_generator_attack_corpus/Y3_encoded_boolean/...
A_generator_attack_corpus/Y4_obfuscated_boolean/...
```

Recommended validation after replacement:

```bash
pip install -e .
pytest -q
python -m sqlgan_dual.experiment_b_core_renderers --data . --out ./runs/smoke --smoke --adv-epochs 1
```
