import csv

# Check union_based samples
with open('split_data.csv', 'r', encoding='utf-8-sig') as f:
    data = {r['id']: r['payload_norm'] for r in csv.DictReader(f)}

with open('split_data_labeled_8001_10000.csv', 'r') as f:
    reader = csv.DictReader(f)
    union_rows = [r for r in reader if r['sqli_type'] == 'union_based']

print(f"Total union_based: {len(union_rows)}")
print("Sample union_based rows:")
for r in union_rows[:25]:
    pid = r['id']
    payload = data.get(pid, '')
    print(f"  {pid}: {r['db_engine']}, {r['confidence']} | {payload[:100]}...")
