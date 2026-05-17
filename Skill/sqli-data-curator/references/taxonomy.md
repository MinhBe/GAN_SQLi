# SQLi Taxonomy v2 — 12 types (merged from original 18)

After analyzing `combined_labeled_data.csv` (40,860 rows), we keep the 10 types with ≥100 attack rows and drop 6 long-tail types (134 rows total, 0.3% of data).

## Kept Types (10 + benign + unknown_for_review)

| Type | Priority | Attack rows | Signal examples |
|------|----------|-------------|-----------------|
| `union_based`        | 7 | 2,236 | `UNION SELECT`, `UNION ALL SELECT` |
| `time_blind`         | 5 | 2,391 | `SLEEP()`, `pg_sleep()`, `WAITFOR DELAY`, `BENCHMARK()`, `dbms_pipe.receive_message`, `randomblob()` |
| `error_based`        | 4 | 8,663 | `xmltype()`, `extractvalue()`, `updatexml()`, `cast(... as int)`, `utl_inaddr.get_host_address` |
| `out_of_band`        | 6 | 610 | `load_file()`, `utl_http.request`, `xp_dirtree`, DNS-exfil patterns |
| `stacked_queries`    | 8 | 43 + merged | `; INSERT`, `; UPDATE`, `; DROP`, `; EXEC`, `xp_cmdshell` |
| `boolean_blind`      | 3 | 4,531 + merged | `AND 1=1`, `OR 1=2`, `RLIKE`, `ELT()`, `IF(... THEN ... ELSE ...)` |
| `auth_bypass`        | 2 | 1,193 | `admin' --`, `' OR '1'='1` near login |
| `heavy_query`        | 4 | 1,296 | `generate_series`, large cartesian joins, recursive CTE |
| `polyglot`           | 9 | 51 | Multi-context payload (XSS + SQLi mixed) |
| `benign`             | 1 | 19,669 | Valid SQL without injection signals |

**Priority** = numerical weight for conflict resolution. Lower priority is "stronger" signal — a payload matching multiple types is labeled with the lowest-numbered priority. Example: a payload with both `SLEEP()` (P5=time_blind) and `UNION SELECT` (P7=union_based) → `time_blind` wins.

## Dropped Types (134 rows, 0.3%)

User decision: DROP all rows with these types (do not relabel, do not merge):

```
ldap_injection      (2 rows)   — out of SQLi scope
command_injection   (1 row)    — out of SQLi scope
second_order        (3 rows)   — requires multi-request context
inline_query        (8 rows)   — ambiguous category
comment_based       (10 rows)  — too vague signal
rce                 (10 rows)  — covered by stacked_queries via xp_cmdshell
generic             (19 rows)  — uninformative
unknown             (124 rows) — sent to relabel, NOT dropped, if it has clear signal
```

Note: `unknown` is special — re-run through 3-source labeler. If still uncertain → drop. Don't auto-drop the 124 rows.

## DB Engine Taxonomy (9 engines kept)

| Engine | Attack rows | Exclusive signatures |
|--------|-------------|---------------------|
| `oracle`     | 9,141 | `xmltype`, `dual`, `utl_inaddr`, `dbms_pipe`, `ctxsys`, `all_tables`, `rownum`, `chr(N)||chr(N)` |
| `generic`    | 23,024 | (no DB-specific functions — keep as-is) |
| `mysql`      | 4,840 | `extractvalue`, `updatexml`, `sleep`, `benchmark`, `information_schema`, `concat`, `elt`, `rlike` |
| `postgresql` | 1,896 | `pg_sleep`, `pg_database`, `string_agg`, `cast(... as int)`, `generate_series` |
| `mssql`      | 1,081 | `xp_cmdshell`, `WAITFOR DELAY`, `sysobjects`, `sysdatabases`, `master..` |
| `firebird`   | 396   | `rdb$`, `gen_id`, `rdb$fields` |
| `sqlite`     | 275   | `randomblob`, `sqlite_master`, `like('a','a')` |
| `db2`        | 204   | `sysibm.systables`, `current schema` |
| `unknown`    | 3     | (drop) |

## Type × DB Holes (need synthetic augmentation)

After resampling, fill these cells with ≥ 50 synthetic rows each:

| Type × DB | Current rows | Action |
|-----------|--------------|--------|
| `error_based × sqlite` | 0 | Augment: `randomblob`-based error |
| `auth_bypass × mssql` | 0 | Augment: `WAITFOR` + admin pattern |
| `union_based × sqlite` | 0 | Augment: `UNION SELECT name, sql FROM sqlite_master` |
| `out_of_band × sqlite` | 0 | Augment: `randomblob` + dns probe (rare in practice → low priority) |

## Reasoning Quality Requirement

Every label MUST have reasoning ≥ 50 chars that:
1. Names the **specific token/function** from payload (not just "matches pattern")
2. Mentions **DB engine signature** if applicable
3. Explains **WHY** the type chosen (not just "looks like X")

**Good**: `"pg_sleep(N) confirms PostgreSQL time-based blind; the 'OR' boolean context after makes it true-branch sleep"`

**Bad** (will be FLAGGED): `"time blind"`, `"xmltype for Oracle"`, `"union_select"` — all reused 800+ times in current data.
