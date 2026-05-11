"""Normalize sqli_type label names in combined_labeled_data.csv."""
import os
import pandas as pd

SRC = os.path.join(os.path.dirname(__file__), '..', '..', 'Asset', 'LabelData', 'combined_labeled_data.csv')
DST = SRC  # in-place

RENAME = {
    'boolean_based': 'boolean_blind',
    'stacked_query': 'stacked_queries',
}

def main():
    df = pd.read_csv(SRC)
    before = df['sqli_type'].value_counts().to_dict()
    df['sqli_type'] = df['sqli_type'].replace(RENAME)
    after = df['sqli_type'].value_counts().to_dict()
    df.to_csv(DST, index=False)
    print(f"Saved {len(df)} rows to {DST}")
    for old, new in RENAME.items():
        if old in before:
            print(f"  Renamed '{old}' ({before[old]}) -> '{new}' ({after.get(new, 0)})")

if __name__ == '__main__':
    main()
