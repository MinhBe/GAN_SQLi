import csv
import re

# ── helpers ──────────────────────────────────────────────────────────────────

def load_rows(path, id_min, id_max):
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        header = [c.strip('" ') for c in header]
        rows = []
        for row in reader:
            d = {header[i]: row[i] for i in range(len(header))}
            rid = int(d['id'])
            if id_min <= rid <= id_max:
                rows.append(d)
    return rows

# ── classification logic ────────────────────────────────────────────────────

def classify(norm_raw):
    """Return (sqli_type, db_engine, confidence) for a payload."""
    n = norm_raw.lower()
    markers = {}  # type -> list of (engine_hint, confidence)

    # ── 1. error-based ──────────────────────────────────────────────────
    err = []

    # Oracle error-based (unambiguous)
    if re.search(r'xmltype', n):
        err.append(('oracle', 1.00))
    if re.search(r'ctxsys', n):
        err.append(('oracle', 1.00))
    if re.search(r'dbms_utility', n):
        err.append(('oracle', 1.00))
    if re.search(r'utl_inaddr', n):
        err.append(('oracle', 1.00))

    # MySQL error-based: floor/rand group by
    if re.search(r'\bfloor\s*\(', n) and re.search(r'rand\s*\(', n) and re.search(r'\bgroup\s+by\b', n):
        err.append(('mysql', 1.00))

    # MySQL error-based: exp(~(select...))
    if re.search(r'\bexp\s*\(\s*~', n):
        err.append(('mysql', 1.00))

    # MySQL error-based: extractvalue (with procedure analyse or concat hex)
    if re.search(r'extractvalue\s*\(', n):
        if re.search(r'procedure\s+analyse', n) or re.search(r'concat\s*\(\s*0x', n):
            err.append(('mysql', 1.00))
        else:
            err.append(('mysql', 0.85))

    # MySQL error-based: updatexml
    if re.search(r'updatexml\s*\(', n):
        if re.search(r'concat\s*\(\s*0x', n):
            err.append(('mysql', 1.00))
        else:
            err.append(('mysql', 0.85))

    # MySQL error-based: double/overflow (row() > count(*))
    if re.search(r'row\s*\(', n) and re.search(r'>\s*\(\s*select\s+count\s*\(\s*\*\s*\)', n):
        err.append(('mysql', 1.00))

    # PostgreSQL error-based: ::numeric or ::int
    if re.search(r'::\s*numeric\b', n) or re.search(r'::\s*int\b', n):
        err.append(('postgresql', 1.00))

    # MSSQL error-based: convert(int, ...)
    if re.search(r'convert\s*\(\s*int\b', n):
        err.append(('mssql', 1.00))

    if err:
        # Take first error type found (but prefer the one with highest confidence)
        best = max(err, key=lambda x: x[1])
        # If multiple engines, prefer the one appearing first in payload
        engine = best[0]
        conf = best[1]
        return ('error_based', engine, conf)

    # ── 2. union-based ──────────────────────────────────────────────────
    if re.search(r'\bunion\b', n):
        # Detect engine from other hints
        engine = detect_engine(n)
        return ('union_based', engine, 1.00 if engine != 'generic' else 0.85)

    # ── 3. time-blind ───────────────────────────────────────────────────
    time = []

    # Oracle time
    if re.search(r'dbms_lock\.sleep', n) or re.search(r'user_lock\.sleep', n):
        time.append(('oracle', 1.00))
    # MySQL time: sleep( (not dbms_lock.sleep)
    if re.search(r'(?<!dbms_lock\.)(?<!user_lock\.)\bsleep\s*\(', n):
        time.append(('mysql', 1.00))
    # MySQL time: benchmark(
    if re.search(r'benchmark\s*\(', n):
        time.append(('mysql', 1.00))
    # PostgreSQL time
    if re.search(r'pg_sleep', n):
        time.append(('postgresql', 1.00))
    # MSSQL time
    if re.search(r'waitfor\s+delay', n):
        time.append(('mssql', 1.00))
    # SQLite time
    if re.search(r'randomblob\s*\(', n):
        time.append(('sqlite', 1.00))

    if time:
        best = max(time, key=lambda x: x[1])
        return ('time_blind', best[0], best[1])

    # ── 4. boolean-blind (default) ──────────────────────────────────────
    engine = detect_engine(n)
    conf = confidence_boolean(n, engine)
    return ('boolean_blind', engine, conf)


def detect_engine(n):
    """Detect SQL engine from payload hints."""
    n = n.lower()
    hints = []

    # Strong Oracle indicators
    if re.search(r'xmltype|ctxsys|dbms_utility|utl_inaddr', n):
        hints.append(('oracle', 10))
    if re.search(r'\bdual\b', n):
        hints.append(('oracle', 8))

    # Strong MySQL indicators
    if re.search(r'procedure\s+analyse', n):
        hints.append(('mysql', 10))
    if re.search(r'\bin\s+boolean\s+mode\b', n):
        hints.append(('mysql', 9))
    if re.search(r'\brlike\b', n):
        hints.append(('mysql', 8))
    if re.search(r'\belt\s*\(', n):
        hints.append(('mysql', 7))
    if re.search(r'benchmark\s*\(', n):
        hints.append(('mysql', 7))
    if re.search(r'(?<!dbms_lock\.)(?<!user_lock\.)\bsleep\s*\(', n):
        hints.append(('mysql', 7))
    if re.search(r'\bextractvalue\s*\(', n):
        hints.append(('mysql', 6))
    if re.search(r'\bupdatexml\s*\(', n):
        hints.append(('mysql', 6))
    if re.search(r'#', n):
        hints.append(('mysql', 4))

    # Strong PostgreSQL indicators
    if re.search(r'::\s*text\b', n) or re.search(r'::\s*numeric\b', n) or re.search(r'::\s*int\b', n):
        hints.append(('postgresql', 10))
    if re.search(r'pg_sleep', n):
        hints.append(('postgresql', 9))

    # MSSQL indicators
    if re.search(r'convert\s*\(\s*int\b', n):
        hints.append(('mssql', 10))
    if re.search(r'waitfor\s+delay', n):
        hints.append(('mssql', 9))
    if re.search(r"char\s*\(.*?\)\s*\+", n):
        hints.append(('mssql', 6))

    # SQLite indicators
    if re.search(r'randomblob\s*\(', n):
        hints.append(('sqlite', 9))

    if not hints:
        return 'generic'

    # Return highest score engine
    hints.sort(key=lambda x: -x[1])
    return hints[0][0]


def confidence_boolean(n, engine):
    """Determine confidence for boolean-blind payloads."""
    n = n.lower()

    # Strong boolean patterns = higher confidence
    strong = 0

    # case when (explicit boolean inference)
    if re.search(r'\bcase\s+when\b', n):
        strong += 2
    # if( condition, ... )
    if re.search(r'\bif\s*\(', n):
        strong += 2
    # rlike / regexp
    if re.search(r'\brlike\b', n):
        strong += 2
    # explicit comparison with and/or
    if re.search(r'\band\b.*=.*=|\bor\b.*=.*=', n):
        strong += 1
    # like pattern
    if re.search(r'\blike\b', n):
        strong += 1
    # elt( (MySQL boolean)
    if re.search(r'\belt\s*\(', n):
        strong += 1
    # chr( / char( for data extraction
    if re.search(r'\bchr\s*\(', n) or re.search(r'\bchar\s*\(', n):
        strong += 1
    # as / subquery
    if re.search(r'\bas\s+\w+\s+where', n):
        strong += 1

    if strong >= 4:
        return 1.00
    elif strong >= 2:
        return 0.85
    else:
        return 0.70


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    src = 'SeqGAN_SQLi/data/split_data.csv'
    dst = 'SeqGAN_SQLi/data/split_data_labeled_12001_14000.csv'
    rows = load_rows(src, 12001, 14000)

    out = [['id', 'sqli_type', 'db_engine', 'confidence']]
    for r in rows:
        sqli_type, db_engine, confidence = classify(r['payload_norm'])
        out.append([r['id'], sqli_type, db_engine, f'{confidence:.2f}'])

    with open(dst, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(out)

    print(f'Written {len(out) - 1} labeled rows to {dst}')

    # Summary
    from collections import Counter
    types = Counter()
    engines = Counter()
    confs = Counter()
    for row in out[1:]:
        types[row[1]] += 1
        engines[row[2]] += 1
        confs[row[3]] += 1
    print('\n--- sqli_type ---')
    for k, v in types.most_common():
        print(f'  {k}: {v}')
    print('\n--- db_engine ---')
    for k, v in engines.most_common():
        print(f'  {k}: {v}')
    print('\n--- confidence ---')
    for k, v in confs.most_common():
        print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
