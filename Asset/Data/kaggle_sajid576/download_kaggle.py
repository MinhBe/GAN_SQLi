"""
Download sajid576/sql-injection-dataset from Kaggle.
Requires: kaggle API key at ~/.kaggle/kaggle.json
  Get it from: https://www.kaggle.com/settings → API → Create New Token
"""
import os
import sys
import shutil

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import kagglehub
    from kagglehub import KaggleDatasetAdapter
    import pandas as pd
except ImportError:
    print("Missing packages. Run: pip install kagglehub pandas")
    sys.exit(1)

print("Downloading sajid576/sql-injection-dataset ...")
df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "sajid576/sql-injection-dataset",
    "",
)

out_path = os.path.join(OUTPUT_DIR, "sql_injection_dataset.csv")
df.to_csv(out_path, index=False)
print(f"Saved {len(df)} rows → {out_path}")
print(f"Columns: {list(df.columns)}")
print(df.head(3))
