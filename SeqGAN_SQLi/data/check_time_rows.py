import csv

# Check time_blind samples
with open('split_data_labeled_8001_10000.csv', 'r') as f:
    reader = csv.DictReader(f)
    time_rows = []
    for row in reader:
        if row['sqli_type'] == 'time_blind':
            time_rows.append(row)
            if len(time_rows) > 15:
                break

for r in time_rows:
    print(f"{r['id']}: {r['db_engine']}, {r['confidence']}")

print()

# Check a few sqlite rows
with open('split_data_labeled_8001_10000.csv', 'r') as f:
    reader = csv.DictReader(f)
    sqlite_rows = []
    for row in reader:
        if row['db_engine'] == 'sqlite':
            sqlite_rows.append(row)
            if len(sqlite_rows) > 5:
                break

for r in sqlite_rows:
    print(f"{r['id']}: {r['sqli_type']}, {r['confidence']}")

print()

# Check for any rows that still say union_based but shouldn't
with open('split_data_labeled_8001_10000.csv', 'r') as f:
    reader = csv.DictReader(f)
    suspicious = []
    for row in reader:
        if row['sqli_type'] == 'union_based':
            suspicious.append(row['id'])
    print(f"Total union_based: {len(suspicious)}")
