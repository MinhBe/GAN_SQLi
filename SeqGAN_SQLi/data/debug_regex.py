import csv, re

with open('split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['id'] in ('8002', '8005'):
            p = row['payload_norm'].lower()
            # Exact match test
            test_str = "char ( 113 ) +char ( 113 )"
            pattern = r'char\s*\(\d+\)\s*\+'
            print(f"Test string: '{test_str}'")
            print(f"Pattern: r'{pattern}'")
            print(f"Match: {bool(re.search(pattern, test_str))}")
            
            # More precise
            idx = p.find('char')
            chunk = p[idx:idx+60]
            print(f"Chunk: '{chunk}'")
            for i, c in enumerate(chunk):
                print(f"  [{i}] = '{c}' (ord={ord(c)})")
            
            print(f"Has char+ (raw): {bool(re.search(pattern, p))}")
            break
