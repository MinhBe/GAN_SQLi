import csv
import random

# Load source data
source = {}
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if 13001 <= int(row[0]) <= 14000:
            source[row[0]] = row[1]

# Load labels
labels = {}
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_13001_14000.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        labels[row['id']] = row

# Random verification
ids = list(source.keys())
random.seed(42)
sample = random.sample(ids, 20)

print("Random sample verification:")
print()
for sid in sorted(sample, key=int):
    payload = source[sid]
    label = labels[sid]
    payload_short = payload[:120] + '...' if len(payload) > 120 else payload
    print(f'id={sid}: {label["sqli_type"]}, {label["db_engine"]}, {label["confidence"]}')
    print(f'  payload: {payload_short}')
    print()
