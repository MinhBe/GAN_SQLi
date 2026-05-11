import csv

rows = {}
with open('data/split_data_labeled_batch_3001_3500.csv', 'r') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows[int(r['id'])] = r

check_ids = [3025, 3028, 3037, 3040, 3048, 3065, 3074, 3077, 3085, 3097, 3108, 
             3112, 3122, 3130, 3142, 3170, 3173, 3175, 3198, 3200, 3207, 3208, 
             3213, 3215, 3223, 3237, 3258, 3274, 3282, 3290, 3293, 3302, 3309, 
             3313, 3317, 3331, 3332, 3333, 3343, 3346, 3361, 3365, 3390, 3401, 
             3402, 3448, 3457, 3459, 3474, 3485, 3488, 3493]

for rid in check_ids:
    r = rows[rid]
    print(f"{r['id']},{r['sqli_type']},{r['db_engine']},{r['confidence']}")
