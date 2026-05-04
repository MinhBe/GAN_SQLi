import pandas as pd
import os
import json
import sys

RESULTS_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
PROGRESS_FILE = r"C:\Users\Admin\Documents\GAN\Asset\Opencode\progress.json"

def save_batch_results(batch_num, results_list):
    output_file = os.path.join(RESULTS_DIR, f"result_batch_{batch_num:04d}.csv")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("row_index,sqli_type,db_engine,confidence,reasoning\n")
        for r in results_list:
            row_idx = r[0]
            sqli_type = r[1]
            db_engine = r[2]
            confidence = r[3]
            reasoning = r[4].replace('"', '""')
            f.write(f"{row_idx},{sqli_type},{db_engine},{confidence},{reasoning}\n")
    return True

def split_results(start_batch, num_batches):
    """Split results từ start_batch với num_batches batches"""
    all_files = sorted([f for f in os.listdir(RESULTS_DIR) if f.startswith('result_batch_') and f.endswith('.csv')])
    
    for fname in all_files:
        fpath = os.path.join(RESULTS_DIR, fname)
        try:
            df = pd.read_csv(fpath, header=None, names=['row_index','sqli_type','db_engine','confidence','reasoning'])
        except:
            continue
        
        batch_num = int(fname.replace('result_batch_', '').replace('.csv', ''))
        
        if batch_num < start_batch or batch_num >= start_batch + num_batches:
            continue
        
        if len(df) > 31:
            start_row = int(df['row_index'].min())
            results_list = []
            for _, row in df.iterrows():
                results_list.append([int(row['row_index']), row['sqli_type'], row['db_engine'], row['confidence'], row['reasoning']])
            
            original_file = fpath
            new_files = {}
            for r in results_list:
                batch_idx = (r[0] - start_row) // 30 + start_batch
                if batch_idx not in new_files:
                    new_files[batch_idx] = []
                new_files[batch_idx].append(r)
            
            for bn, rl in new_files.items():
                if bn >= start_batch and bn < start_batch + num_batches:
                    save_batch_results(bn, rl)
                    print(f"Batch {bn}: {len(rl)} rows")

def main():
    if len(sys.argv) < 3:
        print("Usage: python split_all.py <start_batch> <num_batches>")
        print("  split_all.py 81 10   → split batch 81-90")
        sys.exit(1)
    
    start_batch = int(sys.argv[1])
    num_batches = int(sys.argv[2])
    
    print(f"Splitting batch {start_batch} to {start_batch + num_batches - 1}...")
    split_results(start_batch, num_batches)
    print("Done!")

if __name__ == "__main__":
    main()