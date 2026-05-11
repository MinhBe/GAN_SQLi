import csv, re

with open('split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rid = row['id']
        if rid in ('8002', '8005', '8014', '8024', '8027'):
            p = row['payload_norm'].lower()
            print(f"\nRow {rid}:")
            print(f"  Has char+: {bool(re.search(r'char\s*\(\d+\)\s*\+', p))}")
            print(f"  Has rlike: {bool(re.search(r'rlike', p))}")
            print(f"  Has hash_end: {bool(re.search(r'#\s*$', p))}")
            print(f"  Has in boolean mode: {bool(re.search(r'in\s+boolean\s+mode', p))}")
            print(f"  Has floor(rand: {bool(re.search(r'floor\s*\(\s*rand\s*\(', p))}")
            print(f"  Has convert(int: {bool(re.search(r'convert\s*\(\s*int\s*,', p))}")
            print(f"  Has case when: {bool(re.search(r'case\s+when', p))}")
            print(f"  Has union: {bool(re.search(r'union\s+(?:all\s+)?select', p))}")
            # Check for short context
            idx = p.find('char')
            if idx >= 0:
                print(f"  char context: ...{p[max(0,idx-10):idx+60]}...")
