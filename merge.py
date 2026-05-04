import pandas as pd
import numpy as np
import os
import glob

VALID_TYPES = [
    "union_based", "error_based", "boolean_blind", "time_blind", 
    "heavy_query", "stacked_queries", "out_of_band", "auth_bypass", 
    "second_order", "rce", "polyglot", "lateral", "benign", "unknown"
]

def main():
    output_dir = 'outputs'
    output_files = sorted(glob.glob(os.path.join(output_dir, "output_*.csv")))
    
    if not output_files:
        print("No output files found in outputs/!")
        return
    
    print(f"Merging {len(output_files)} files...")
    all_dfs = []
    for f in output_files:
        df = pd.read_csv(f)
        all_dfs.append(df)
        
    master_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Total rows after merge: {len(master_df)}")
    
    # 3. Dedup lần cuối trên payload_norm
    print("Final deduplication on payload_norm...")
    master_df['norm_hash'] = master_df['payload_norm'].str.lower().str.strip()
    master_df = master_df.drop_duplicates(subset=['norm_hash'])
    master_df = master_df.drop(columns=['norm_hash'])
    
    # 4. Tạo cột payload_delex nếu chưa có
    # (Đã có từ prepare.py nhưng đảm bảo)
    if 'payload_delex' not in master_df.columns:
        # Import from prepare if needed or just re-run logic
        import re
        def delexicalize(s):
            if not isinstance(s, str): return ""
            s = re.sub(r"'[^']*'", '<STR>', s)
            s = re.sub(r'"[^"]*"', '<STR>', s)
            s = re.sub(r'\b\d+\.?\d*\b', '<NUM>', s)
            s = re.sub(r'\b(users|admin|accounts|members|login)\b', '<TABLE>', s, flags=re.IGNORECASE)
            s = re.sub(r'\b(username|password|email|id|name)\b', '<COL>', s, flags=re.IGNORECASE)
            return s
        master_df['payload_delex'] = master_df['payload_norm'].apply(delexicalize)

    # 5. Validate schema
    print("Validating schema...")
    mandatory_cols = [
        'payload_raw', 'payload_norm', 'payload_delex', 
        'label', 'is_obfuscated', 'sqli_type', 'confidence'
    ]
    
    missing = [c for c in mandatory_cols if c not in master_df.columns]
    if missing:
        print(f"WARNING: Missing mandatory columns: {missing}")
    
    # Data integrity checks
    master_df['label'] = master_df['label'].fillna(1).astype(int) # Default to 1 if missing? instruction says label is 0/1
    master_df['is_obfuscated'] = master_df['is_obfuscated'].astype(bool)
    
    # sqli_type check
    master_df['sqli_type'] = master_df['sqli_type'].fillna('unknown')
    invalid_types = master_df[~master_df['sqli_type'].isin(VALID_TYPES)]
    if not invalid_types.empty:
        print(f"WARNING: Found {len(invalid_types)} rows with invalid sqli_type. Setting to 'unknown'.")
        master_df.loc[~master_df['sqli_type'].isin(VALID_TYPES), 'sqli_type'] = 'unknown'
        
    # Flag mâu thuẫn
    flag_1 = master_df[(master_df['label'] == 1) & (master_df['sqli_type'] == "benign")]
    flag_2 = master_df[(master_df['label'] == 0) & (master_df['sqli_type'] != "benign") & (master_df['sqli_type'] != "unknown")]
    
    print(f"Flagged label=1 but sqli_type='benign': {len(flag_1)}")
    print(f"Flagged label=0 but sqli_type!='benign': {len(flag_2)}")
    
    # Export
    output_path = 'master_sqli.csv'
    master_df.to_csv(output_path, index=False)
    print(f"Final dataset exported to {output_path}")
    
    # 7. Final Report
    print("\n--- FINAL CONSOLIDATED REPORT ---")
    print(f"Total rows: {len(master_df)}")
    
    print("\nsqli_type Distribution (%):")
    print(master_df['sqli_type'].value_counts(normalize=True) * 100)
    
    print("\ndb_engine Distribution (%):")
    if 'db_engine' in master_df.columns:
        print(master_df['db_engine'].value_counts(normalize=True) * 100)
    
    print("\nLabel Distribution (%):")
    print(master_df['label'].value_counts(normalize=True) * 100)
    
    print("\nObfuscation Distribution (%):")
    print(master_df['is_obfuscated'].value_counts(normalize=True) * 100)
    
    print(f"\nAverage Confidence: {master_df['confidence'].mean():.4f}")
    
    unknown_pct = (master_df['sqli_type'] == 'unknown').mean() * 100
    print(f"Unknown sqli_type: {unknown_pct:.2f}%")
    
    print(f"Total flagged contradictions: {len(flag_1) + len(flag_2)}")

if __name__ == "__main__":
    main()
