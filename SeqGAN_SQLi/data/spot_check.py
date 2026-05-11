import csv

# Spot check labels against payloads
with open('split_data.csv', 'r', encoding='utf-8-sig') as f:
    data = {int(row['id']): row['payload_norm'] for row in csv.DictReader(f) if 6001 <= int(row['id']) <= 8000}

with open('split_data_labeled_batch_6001_8000.csv', 'r') as f:
    labels = {int(row['id']): row for row in csv.DictReader(f)}

# Check specific ids
check_ids = [6001,6002,6003,6004,6005,6007,6008,6011,6014,6016,6017,6020]
for rid in check_ids:
    if rid in labels and rid in data:
        l = labels[rid]
        p = data[rid][:150]
        print(f'ID {rid}: {l["sqli_type"]:15s} | {l["db_engine"]:12s} | conf={l["confidence"]} | {p}')

print("\n--- First 20 lines of output ---")
with open('split_data_labeled_batch_6001_8000.csv', 'r') as f:
    for i, row in enumerate(csv.DictReader(f)):
        if i < 20:
            print(f'{row["id"]},{row["sqli_type"]},{row["db_engine"]},{row["confidence"]}')
