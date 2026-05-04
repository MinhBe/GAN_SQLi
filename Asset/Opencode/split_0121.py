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

start_batch = 121
num_batches = 10
start_row = 3600

combined = pd.read_csv(os.path.join(RESULTS_DIR, f"result_batch_{start_batch:04d}.csv"), header=None, names=['row_index','sqli_type','db_engine','confidence','reasoning'])

for batch_num in range(start_batch, start_batch + num_batches):
    batch_data = combined[combined['row_index'] >= start_row + (batch_num - start_batch) * 30]
    batch_data = batch_data[batch_data['row_index'] < start_row + (batch_num - start_batch + 1) * 30]
    
    results_list = []
    for _, row in batch_data.iterrows():
        results_list.append([int(row['row_index']), row['sqli_type'], row['db_engine'], row['confidence'], row['reasoning']])
    
    if len(results_list) > 0:
        save_batch_results(batch_num, results_list)
        print(f"Batch {batch_num}: {len(results_list)} rows")

completed = list(range(1, 131))
progress = {
    "worker": "Opencode",
    "total_batches": 1382,
    "completed_batches": completed,
    "failed_batches": [],
    "last_completed": 130,
    "status": "in_progress",
    "last_updated": "2026-05-03 19:55:00",
    "rows_completed": 3900,
    "rows_total": 41459
}

with open(PROGRESS_FILE, "w") as f:
    json.dump(progress, f, indent=2)

print(f"Done! Updated progress to batch 0130")