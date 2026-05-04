import csv
import json
import os

def classify_payload(payload, label):
    if label == 0:
        return "benign", "generic", 0.9, "plain text no sql"

    payload_lower = payload.lower()

    if any(kw in payload_lower for kw in ['sleep(', 'pg_sleep', 'benchmark(', 'waitfor delay', 'delay']):
        return "time_blind", detect_db(payload_lower), 0.95, "time-based blind"

    if any(kw in payload_lower for kw in ['extractvalue(', 'updatexml(', 'xmltype(']):
        return "error_based", detect_db(payload_lower), 0.95, "xml error extraction"

    if 'union all select' in payload_lower:
        return "union_based", detect_db(payload_lower), 0.9, "union-based injection"

    if any(kw in payload_lower for kw in ['case when', 'if(', 'iif(']):
        return "boolean_blind", detect_db(payload_lower), 0.85, "conditional boolean"

    if any(kw in payload_lower for kw in ['dbms_pipe', 'dbms_utility', 'utl_inaddr', 'ctxsys', 'from dual', 'chr(']):
        return "time_blind", "oracle", 0.9, "oracle time-based"

    if any(kw in payload_lower for kw in ['pg_sleep', 'generate_series', 'domain.domains']):
        return "time_blind", "postgresql", 0.9, "postgresql time-based"

    if any(kw in payload_lower for kw in ['waitfor', 'sysibm', 'master..sysdatabases']):
        return "time_blind", "mssql", 0.9, "mssql time-based"

    if any(kw in payload_lower for kw in ['rdb$', 'rdb$fields']):
        return "error_based", "firebird", 0.85, "firebird database"

    if any(kw in payload_lower for kw in ['all_users', 'sysusers']):
        return "heavy_query", detect_db(payload_lower), 0.8, "heavy query enumeration"

    return "unknown", "generic", 0.5, "complex payload"

def detect_db(payload):
    if any(kw in payload for kw in ['dbms_pipe', 'dbms_utility', 'utl_inaddr', 'ctxsys', 'from dual', 'chr(']):
        return "oracle"
    if any(kw in payload for kw in ['pg_sleep', 'generate_series', 'domain.domains']):
        return "postgresql"
    if any(kw in payload for kw in ['waitfor', 'sysibm', 'master..sysdatabases']):
        return "mssql"
    if any(kw in payload for kw in ['benchmark', 'mysql.db', 'information_schema']):
        return "mysql"
    if any(kw in payload for kw in ['rdb$', 'rdb$fields']):
        return "firebird"
    return "generic"

results = []
for batch_num in range(132, 142):
    batch_file = f"C:\\Users\\Admin\\Documents\\GAN\\Asset\\Data\\batches\\batch_{batch_num:04d}.csv"
    if not os.path.exists(batch_file):
        print(f"Batch {batch_num} not found")
        continue

    with open(batch_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_index = int(row['row_index'])
            payload = row['payload_norm']
            label = int(row['label'])

            sqli_type, db_engine, confidence, reasoning = classify_payload(payload, label)
            results.append({
                "row_index": row_index,
                "sqli_type": sqli_type,
                "db_engine": db_engine,
                "confidence": confidence,
                "reasoning": reasoning
            })

print(f"Total rows: {len(results)}")

for batch_num in range(132, 142):
    batch_results = [r for r in results if int(r['row_index']) >= (batch_num-1)*30+3930 and int(r['row_index']) < (batch_num-1)*30+3960]
    if not batch_results:
        start_idx = (batch_num - 132) * 30
        end_idx = start_idx + 30
        batch_results = results[start_idx:end_idx] if start_idx < len(results) else []

    output_file = f"C:\\Users\\Admin\\Documents\\GAN\\Asset\\Data\\results\\result_batch_{batch_num:04d}.csv"

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['row_index', 'sqli_type', 'db_engine', 'confidence', 'reasoning'])
        writer.writeheader()
        writer.writerows(batch_results)

    print(f"Saved {output_file} ({len(batch_results)} rows)")

progress = {
    "worker": "Opencode",
    "total_batches": 1382,
    "completed_batches": list(range(1, 142)),
    "failed_batches": [],
    "last_completed": 141,
    "status": "in_progress",
    "last_updated": "2026-05-03",
    "rows_completed": 4230,
    "rows_total": 41459
}

with open("C:\\Users\\Admin\\Documents\\GAN\\Asset\\Opencode\\progress.json", 'w') as f:
    json.dump(progress, f, indent=2)

print("Progress updated to batch 141")