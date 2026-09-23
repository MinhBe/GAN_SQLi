# Kaggle Run Guide

## Upload

1. Upload `gansqli_rebuild_mvp.zip` lên Kaggle Notebook hoặc Dataset riêng.
2. Giải nén và cài dependencies:

```python
!unzip -q /kaggle/input/<your-upload>/gansqli_rebuild_mvp.zip -d /kaggle/working/
%cd /kaggle/working/gansqli_rebuild_mvp
!pip install -q -r requirements.txt
!pip install -q -e .
```

## Run

```python
DATASET_CSV = '/kaggle/input/<dataset>/<file>.csv'
!python scripts/run_mvp.py --config configs/experiment_mvp.yaml --input $DATASET_CSV --out /kaggle/working/runs/mvp
```

## Output cần review

```text
/kaggle/working/runs/mvp/baseline/metrics.json
/kaggle/working/runs/mvp/candidates/candidates_gated.csv
/kaggle/working/runs/mvp/selected/selected_novelty.csv
```

Kaggle API chính thức hỗ trợ `datasets`, `competitions`, `kernels/notebooks` và dùng credential `kaggle.json` hoặc token; không commit credential vào repo.
