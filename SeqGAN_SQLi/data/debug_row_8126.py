import csv, re

with open('split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['id'] == '8126':
            p = row['payload_norm'].lower()
            print(f"Payload: {p}")
            print(f"case when: {bool(re.search(r'case\s+when', p))}")
            print(f"rlike case: {bool(re.search(r'rlike\s*\(\s*select\s+case\s+when', p))}")
            print(f"if(: {bool(re.search(r'\bif\s*\(', p))}")
            print(f"iif(: {bool(re.search(r'\biif\s*\(', p))}")
            print(f"elt(: {bool(re.search(r'\belt\s*\(', p))}")
            print(f"simple bool: {bool(re.search(r'\d+\s*=\s*\d+', p))}")
            print(f"where cond: {bool(re.search(r'where\s+\d+\s*=', p))}")
            print(f"in select: {bool(re.search(r'in\s*\(\s*select', p))}")
            print(f"1=1: {bool(re.search(r'1\s*=\s*1', p))}")
            print(f"like compare: {bool(re.search(r"'[^']+'\s+like\s+'[^']+'", p))}")
            print(f"str compare: {bool(re.search(r"'[^']+'\s*=\s*'[^']*'", p))}")
            print("or quote:", bool(re.search(r"or\s+['\"]", p)))
            # Check for specific excerpt
            idx = p.find('in boolean')
            if idx >= 0:
                print(f"Context: {p[max(0,idx-20):idx+80]}")
            break
