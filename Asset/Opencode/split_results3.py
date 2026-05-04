import pandas as pd
import os
import json

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

combined = pd.read_csv(os.path.join(RESULTS_DIR, "result_batch_0101.csv"), header=None, names=['row_index','sqli_type','db_engine','confidence','reasoning'])

start_row = 3000
for batch_num in range(101, 111):
    batch_data = combined[combined['row_index'] >= start_row + (batch_num - 101) * 30]
    batch_data = batch_data[batch_data['row_index'] < start_row + (batch_num - 101 + 1) * 30]
    
    results_list = []
    for _, row in batch_data.iterrows():
        results_list.append([int(row['row_index']), row['sqli_type'], row['db_engine'], row['confidence'], row['reasoning']])
    
    if len(results_list) > 0:
        save_batch_results(batch_num, results_list)
        print(f"Batch {batch_num}: {len(results_list)} rows")

progress = {
    "worker": "Opencode",
    "total_batches": 1382,
    "completed_batches": list(range(1, 111)),
    "failed_batches": [],
    "last_completed": 110,
    "status": "in_progress",
    "last_updated": "2026-05-03 19:45:00",
    "rows_completed": 3300,
    "rows_total": 41459
}

with open(PROGRESS_FILE, "w") as f:
    json.dump(progress, f, indent=2)

print("Done! Updated progress to batch 0110")