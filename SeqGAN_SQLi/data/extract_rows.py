import csv

with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        rows.append(row)
        if len(rows) >= 1000:
            break

for row in rows:
    print(f"{row['id']}|{row['payload_norm']}")
