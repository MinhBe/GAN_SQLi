import csv

# Load current output
labeled = {}
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data_labeled_batch_12001_13000.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        labeled[row[0]] = row

# Check all the pg_sleep payloads
print("=== pg_sleep payloads ===")
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_12001_13000.csv', 'r', encoding='utf-8-sig') as f:
    for line in f:
        if 'pg_sleep' in line.lower():
            parts = line.split(',')
            pid = parts[0].strip('"')
            if pid in labeled:
                lbl = labeled[pid]
                print(f'ID {pid}: {lbl[1]}/{lbl[2]}/{lbl[3]}')

print("\n=== benchmark() payloads ===")
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_12001_13000.csv', 'r', encoding='utf-8-sig') as f:
    for line in f:
        if 'benchmark' in line.lower():
            parts = line.split(',')
            pid = parts[0].strip('"')
            if pid in labeled:
                lbl = labeled[pid]
                print(f'ID {pid}: {lbl[1]}/{lbl[2]}/{lbl[3]}')

print("\n=== ID 12667 ===")
if '12667' in labeled:
    lbl = labeled['12667']
    print(f'ID 12667: {lbl[1]}/{lbl[2]}/{lbl[3]}')
