# V5.1 PostgreSQL Boolean Probe Validator

This validator is defensive/offline and does not claim real-world exploitation. It validates predicate-only payloads in a PostgreSQL sandbox using:

```sql
SELECT CASE WHEN (<payload>) THEN TRUE ELSE FALSE END;
SELECT CASE WHEN ((<payload>) OR TRUE) THEN TRUE ELSE FALSE END;
SELECT CASE WHEN ((<payload>) AND FALSE) THEN TRUE ELSE FALSE END;
```

Recommended usage:

```bash
PG_DSN=postgresql://postgres:postgres@localhost:5432/postgres \
python Dataset/validation/postgres_boolean_probe_validator.py \
  Dataset/C_generated_candidates/Y1_basic_boolean/generated_candidates.csv \
  y1_runtime_results.csv --auto-payload-column
```

Column policy with `--auto-payload-column`:

- Y1/Y2: `payload_raw` or `payload_stripped`
- Y3: `payload_decoded` first
- Y4: `payload_normalized` first

Runtime status in this dataset remains `not_run` until this script is executed against a sandbox.
