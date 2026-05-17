# Function Whitelist for delex_v2

Functions in this whitelist are **preserved as-is** during de-lexicalization. All other identifiers are replaced with `__IDENT__`.

## Why preservation matters

The original delex replaced ALL function names with `__IDENT__`, which destroys 100% of the signal needed to distinguish SQLi types:
- `xmltype()` → `__IDENT__` (lost Oracle error-based signal)
- `pg_sleep()` → `__IDENT__` (lost PostgreSQL time-based signal)
- `extractvalue()` → `__IDENT__` (lost MySQL error signal)

After this loss, 71.89% of payloads collapse to the same delex form → mode collapse is inevitable.

## Whitelist (30 functions, organized by signal type)

### Time-blind signals (DB-exclusive)
```
sleep           — MySQL, MariaDB
pg_sleep        — PostgreSQL
waitfor         — MSSQL (keyword `WAITFOR DELAY '0:0:N'`)
benchmark       — MySQL (compute-heavy)
dbms_pipe       — Oracle (`dbms_pipe.receive_message`)
dbms_lock       — Oracle (`dbms_lock.sleep`)
randomblob      — SQLite (large blob = time delay)
```

### Error-based signals (DB-exclusive)
```
xmltype         — Oracle (XML cast error)
extractvalue    — MySQL (XPath error)
updatexml       — MySQL (XPath error)
exp             — MySQL (`EXP(~N)` overflow)
utl_inaddr      — Oracle (`utl_inaddr.get_host_address`, also OOB)
ctxsys          — Oracle (`ctxsys.drithsx.sn`)
```

### Out-of-band signals
```
load_file       — MySQL (file read)
utl_http        — Oracle (HTTP req)
xp_dirtree      — MSSQL (file listing)
xp_cmdshell     — MSSQL (shell exec, also stacked)
```

### Encoding / structural
```
chr             — Oracle/PostgreSQL (`chr(N)||chr(N)`)
char            — MSSQL/MySQL (`char(N)+char(N)`)
ord             — MySQL char→int
ascii           — generic
hex             — generic
unhex           — MySQL
concat          — generic
substring       — generic
substr          — Oracle/SQLite variant
```

### Boolean signals
```
elt             — MySQL (`ELT(N=N, payload)`)
rlike           — MySQL regex
if              — MySQL conditional
case            — generic conditional
```

### Casting
```
cast            — generic but tells structure
convert         — MSSQL/MySQL
```

### Identifiers worth preserving (not functions but DB-specific)
```
dual            — Oracle pseudo-table
information_schema  — MySQL/PostgreSQL metadata
sysobjects      — MSSQL metadata
sysdatabases    — MSSQL metadata
sqlite_master   — SQLite metadata
sys.all_tables  — Oracle metadata
rdb$fields      — Firebird metadata
rdb$types       — Firebird metadata
mysql.user      — MySQL admin table
```

## Replacement rules

For tokens **NOT** in whitelist:

| Pattern | Replacement |
|---------|-------------|
| Quoted strings: `'...'` or `"..."` | `__STR__` |
| Integer literals: `\b\d+\b` | `__INT__` |
| Hex literals: `0x[0-9a-fA-F]+` | `__HEX__` |
| Float: `\d+\.\d+` | `__FLOAT__` |
| Time intervals: `'0:0:N'` | `__TIME__` |
| Identifiers (not in whitelist): `[a-zA-Z_]\w*` | `__IDENT__` |
| SQL keywords (SELECT, FROM, WHERE, AND, OR, etc.) | preserve case-insensitive |

## Vocab size estimation

| Source | Tokens |
|--------|--------|
| SQL keywords (50): SELECT, FROM, WHERE, AND, OR, UNION, ALL, NULL, IS, NOT, BETWEEN, LIKE, IN, EXISTS, AS, JOIN, INNER, LEFT, RIGHT, OUTER, ON, GROUP, BY, HAVING, ORDER, ASC, DESC, LIMIT, OFFSET, INSERT, INTO, VALUES, UPDATE, SET, DELETE, CREATE, TABLE, INDEX, DROP, ALTER, ADD, COLUMN, PRIMARY, KEY, FOREIGN, REFERENCES, EXEC, CALL, CASE, WHEN, THEN, ELSE, END | 50 |
| Operators (15): `=`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`, `%`, `\|\|`, `&&`, `(`, `)` | 15 |
| Punctuation (8): `,`, `;`, `.`, `--`, `/*`, `*/`, `#` | 8 |
| Whitelisted functions/identifiers (above) | 32 |
| Special tokens: `__STR__`, `__INT__`, `__HEX__`, `__FLOAT__`, `__TIME__`, `__IDENT__`, `<PAD>`, `<SOS>`, `<EOS>`, `<UNK>` | 10 |
| **Total estimated vocab** | **~115-130** |

Cao hơn V3's 89 tokens (1.3x), nhưng diversity tăng nhiều hơn 10x.

## Edge cases

- `chr(60)||chr(58)||chr(113)` — `chr` is preserved, but the integer args become `__INT__` → result: `chr ( __INT__ ) || chr ( __INT__ ) || chr ( __INT__ )` — still distinguishable from xmltype + non-chr patterns.
- Quoted identifiers: `"users"` is a quoted identifier in PostgreSQL. We treat it as `__STR__` for simplicity (rare in attack payloads).
- Case sensitivity: All functions matched case-insensitive (`xmltype` and `XMLTYPE` both preserved as lowercase `xmltype`).
