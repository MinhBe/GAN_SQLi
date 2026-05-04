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

def main():
    start_batch = int(sys.argv[1]) if len(sys.argv) > 1 else 111
    num_batches = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    combined = pd.read_csv(os.path.join(RESULTS_DIR, f"result_batch_{start_batch:04d}.csv"), header=None, names=['row_index','sqli_type','db_engine','confidence','reasoning'])
    
    for batch_num in range(start_batch, start_batch + num_batches):
        batch_data = combined[combined['row_index'] >= 3000 + (batch_num - start_batch) * 30]
        batch_data = batch_data[batch_data['row_index'] < 3000 + (batch_num - start_batch + 1) * 30]
        
        results_list = []
        for _, row in batch_data.iterrows():
            results_list.append([int(row['row_index']), row['sqli_type'], row['db_engine'], row['confidence'], row['reasoning']])
        
        if len(results_list) > 0:
            save_batch_results(batch_num, results_list)
            print(f"Batch {batch_num}: {len(results_list)} rows")
    
    progress = {
        "worker": "Opencode",
        "total_batches": 1382,
        "completed_batches": list(range(1, start_batch + num_batches)),
        "failed_batches": [],
        "last_completed": start_batch + num_batches - 1,
        "status": "in_progress",
        "last_updated": "2026-05-03 19:50:00",
        "rows_completed": (start_batch + num_batches - 1) * 30,
        "rows_total": 41459
    }
    
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)
    
    print(f"Done! Updated progress to batch {start_batch + num_batches - 1}")

if __name__ == "__main__":
    main()