import csv, sys
csv.field_size_limit(2**31-1)
with open('SeqGAN_SQLi/data/split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        rid = int(row['id'])
        if 3501 <= rid <= 6000:
            payload = row['payload_norm'].replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            rows.append(f"{rid}|{payload}")
    with open('C:\\Users\\BoPC\\.local\\share\\opencode\\tool-output\\payloads_3501_6000.txt', 'w', encoding='utf-8') as out:
        out.write('id | payload_norm\n')
        out.write('\n'.join(rows))
    print(f'Extracted {len(rows)} rows')
