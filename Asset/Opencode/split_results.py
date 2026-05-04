import pandas as pd
import os
import json

RESULTS_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
PROGRESS_FILE = r"C:\Users\Admin\Documents\GAN\Asset\Opencode\progress.json"

def save_batch_results(batch_num, start_row, results_list):
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

# Read all results from combined file
combined = pd.read_csv(os.path.join(RESULTS_DIR, "result_batch_0081.csv"))

# Split into 10 batches (batch 0081-0090)
start_row = 2400
for batch_num in range(81, 91):
    batch_data = combined[combined['row_index'] >= start_row + (batch_num - 81) * 30]
    batch_data = batch_data[batch_data['row_index'] < start_row + (batch_num - 81 + 1) * 30]
    
    results_list = []
    for _, row in batch_data.iterrows():
        results_list.append([row['row_index'], row['sqli_type'], row['db_engine'], row['confidence'], row['reasoning']])
    
    if len(results_list) > 0:
        save_batch_results(batch_num, start_row, results_list)
        print(f"Batch {batch_num}: {len(results_list)} rows")

# Update progress
progress = {
    "worker": "Opencode",
    "total_batches": 1382,
    "completed_batches": list(range(1, 91)),
    "failed_batches": [],
    "last_completed": 90,
    "status": "in_progress",
    "last_updated": "2026-05-03 19:35:00",
    "rows_completed": 2700,
    "rows_total": 41459
}

with open(PROGRESS_FILE, "w") as f:
    json.dump(progress, f, indent=2)

print("Done! Updated progress to batch 0090")