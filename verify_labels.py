import csv

# Check specific rows of interest
target_ids = ['13055', '13069', '13086', '13127', '13056', '13170', '13186', '13206', '13209', '13332', '13362', '13433']
results = {}
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_13001_14000.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['id'] in target_ids:
            results[row['id']] = row

for rid in target_ids:
    if rid in results:
        r = results[rid]
        print(f'{r["id"]}: {r["sqli_type"]}, {r["db_engine"]}, {r["confidence"]}')
    else:
        print(f'{rid}: NOT FOUND')

# Also verify specific payloads from the source data
print('\n--- Manual verification against source data ---')

# Load source payloads
source = {}
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        source[row[0]] = row[1]

# Check specific cases
checks = [
    ('13006', 'time_blind', 'mysql'),   # 1 and sleep(5) #
    ('13009', 'time_blind', 'oracle'),  # dbms_pipe.receive_message
    ('13011', 'union_based', 'generic'), # 1" union all select null,null,null
    ('13127', 'time_blind', 'mssql'),   # 1%" waitfor delay '0:0:5'
    ('13056', 'time_blind', 'postgresql'), # select pg_sleep(5)
    ('13055', 'boolean_blind', 'generic'), # rdb$database = Firebird -> generic
    ('13186', 'time_blind', 'oracle'), # dbms_lock.sleep (Oracle)
    ('13206', 'time_blind', 'mssql'),  # waitfor delay
    ('13209', 'time_blind', 'mysql'),  # BENCHMARK
]

print('\nSpot checks (expected vs actual):')
for rid, exp_type, exp_engine in checks:
    if rid in results:
        r = results[rid]
        t_ok = 'OK' if r['sqli_type'] == exp_type else f'MISMATCH (got {r["sqli_type"]})'
        e_ok = 'OK' if r['db_engine'] == exp_engine else f'MISMATCH (got {r["db_engine"]})'
        print(f'  id={rid}: type {exp_type} {t_ok}, engine {exp_engine} {e_ok}')
    else:
        print(f'  id={rid}: NOT IN RESULTS')
