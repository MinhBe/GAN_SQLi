# Cargo Hi5 notebooks

Use these notebooks when the runtime clones `MinhBe/GAN_SQLi` and runs inside a Cargo/Kaggle-like notebook environment.

- `01_cargo_hi5_branch_a_four_modules.ipynb`: Branch A baseline. Trains Y1/Y2/Y3/Y4 independently.
- `02_cargo_hi5_branch_b_cgr_core_renderers.ipynb`: Branch B recommended path. Trains Y1/Y2 CGR core generators, then renders Y3/Y4.

Both notebooks:

1. clone the repository fresh,
2. install dependencies,
3. run `pytest -q`,
4. auto-detect dataset location,
5. detect available CUDA GPUs,
6. run a smoke test first,
7. run the full configuration if smoke passes,
8. write outputs under `/kaggle/working/sqlgan_runs` when available, otherwise `./sqlgan_runs`.

Set `RUN_FULL = False` in the first config cell if you only want smoke validation.
