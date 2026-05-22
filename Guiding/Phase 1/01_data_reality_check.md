# 01 — Data Reality Check Report

**Total rows processed:** 12,753,953

## Lane Distribution

| Lane | Name | Count | % |
|---|---|---:|---:|
| N | normalized-like | 12,749,451 | 99.96% |
| R | raw/encoded-like | 2,744 | 0.02% |
| D | delexed-like | 116 | 0.0% |
| X | mixed-state | 173 | 0.0% |
| M | malformed | 1,469 | 0.01% |

## Examples per Lane

### Lane N — normalized-like
- `create user name identified by pass123 temporary tablespace temp default tablespace users;`
- `AND 1 = utl_inaddr.get_host_address ( ( SELECT DISTINCT ( table_name ) FROM ( SELECT DISTINCT ( table_name ) , ROWNUM AS`
- `select * from users where id = '1' or @ @1 = 1 union select 1,version ( ) -- 1'`

### Lane R — raw/encoded-like
- `INSERT INTO airport (ident, type, name, wikipedia_link, continent) VALUES ("US-3411","closed", "Fazenda Santa Helena I A`
- `UPDATE airport SET wikipedia_link = "https://translate.google.com/translate?hl=en&sl=es&u=https://es.wikipedia.org/wiki/`
- `SELECT id FROM airports WHERE scheduled_service = "no" AND name LIKE "%pFh0ozNoP0N7S0TWKyTR%" OR name LIKE "%Ea5HUs644za`

### Lane D — delexed-like
- `" or pg_sleep ( __TIME__ ) --`
- `) ) or pg_sleep ( __TIME__ ) --`
- `" ) or sleep ( __TIME__ ) = "`

### Lane X — mixed-state
- `1 or pg_sleep ( __TIME__ ) --`
- `1 ) ) or pg_sleep ( __TIME__ ) --`
- `1 ) or sleep ( __TIME__ ) #`

### Lane M — malformed
- ` or 3 = 3 --`
- `â or 3 = 3 --`
- `â or 1 = 1 --`

## Notes

- `recoverability_score`, `relex_potential`, `db_eval_potential` are **soft heuristics only**.
- Do NOT use them as hard gates before manual audit validation.
- See `reports/01_audit_samples.csv` for stratified manual review.