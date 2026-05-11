import csv

with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_13001_14000.csv') as f:
    reader = csv.DictReader(f)
    rows = {r['id']: r for r in reader}

targets = ['13086', '13209', '13069', '13055', '13127', '13056', '13170', '13186', '13206', '13332', '13362', '13433']
for t in targets:
    if t in rows:
        r = rows[t]
        print(f'{t}: {r["sqli_type"]}, {r["db_engine"]}, {r["confidence"]}')
    else:
        print(f'{t}: NOT FOUND')
