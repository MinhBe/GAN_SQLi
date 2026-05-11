import csv
import re

with open('SeqGAN_SQLi/data/split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    header = [c.strip('" ') for c in header]
    rows = []
    for row in reader:
        row_dict = {header[i]: row[i] for i in range(len(header))}
        if 12001 <= int(row_dict['id']) <= 14000:
            rows.append(row_dict)

norms = [(r['id'], r['payload_norm']) for r in rows]

# Check overlap: dual + ::
dual_and_cast = [(rid, n[:120]) for rid, n in norms if 'dual' in n.lower() and '::' in n]
print(f'dual + :: overlap: {len(dual_and_cast)}')
for rid, n in dual_and_cast[:3]:
    print(f'  ID={rid}: {n}')

# Check overlap: elt + :: 
elt_and_cast = [(rid, n[:120]) for rid, n in norms if re.search(r'\belt\s*\(', n, re.I) and '::' in n]
print(f'\nelt + :: overlap: {len(elt_and_cast)}')
for rid, n in elt_and_cast[:3]:
    print(f'  ID={rid}: {n}')

# Check overlap: elt + dual
elt_and_dual = [(rid, n[:120]) for rid, n in norms if re.search(r'\belt\s*\(', n, re.I) and 'dual' in n.lower()]
print(f'\nelt + dual overlap: {len(elt_and_dual)}')
for rid, n in elt_and_dual[:3]:
    print(f'  ID={rid}: {n}')

# Check rows with only # (MySQL) without dual
hash_no_dual = [(rid, n[:120]) for rid, n in norms if '#' in n and 'dual' not in n.lower()]
print(f'\n# without dual: {len(hash_no_dual)}')

# Check rows with -- without dual
dash_no_dual = [(rid, n[:120]) for rid, n in norms if '--' in n and 'dual' not in n.lower() and '::' not in n and '#' not in n]
print(f'\n-- without dual/::/#: {len(dash_no_dual)}')
for rid, n in dash_no_dual[:5]:
    print(f'  ID={rid}: {n}')

# Check how many rows have xmltype AND :: - overlap
xml_and_pg = [(rid, n[:120]) for rid, n in norms if 'xmltype' in n.lower() and '::' in n]
print(f'\nxmltype + :: overlap: {len(xml_and_pg)}')

# Check rows with no engine-specific markers at all
no_engine = []
for rid, n in norms:
    nl = n.lower()
    has_engine = any(x in nl for x in ['dual', '::', 'elt(', 'mysql', 'rlike', 'regexp', 'procedure analyse', 
                                        'in boolean mode', 'benchmark(', '#', 'char(.*)+'])
    # Check mssql + concat
    if re.search(r"char\s*\(.*\)\s*\+", n, re.I):
        has_engine = True
    if not has_engine:
        no_engine.append((rid, n[:120]))
print(f'\nNo engine markers: {len(no_engine)}')
for rid, n in no_engine[:5]:
    print(f'  ID={rid}: {n}')
