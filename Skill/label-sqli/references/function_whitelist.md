# Function Whitelist — label-sqli

These SQL functions/identifiers must be PRESERVED during delexicalization (delex_v2).
They carry attack type signal and DB engine signal that is critical for GAN conditioning.

Replacing these with generic tokens (e.g., __FUNC__) destroys the discriminative signal
the model needs to learn attack-type-specific syntax.

---

## Time-Blind Functions (preserve exactly)

```
sleep           SLEEP           pg_sleep        PG_SLEEP
benchmark       BENCHMARK       waitfor         WAITFOR
dbms_pipe       DBMS_PIPE       dbms_lock       DBMS_LOCK
randomblob      RANDOMBLOB
```

---

## Error-Based Functions (preserve exactly)

```
extractvalue    EXTRACTVALUE    updatexml       UPDATEXML
xmltype         XMLTYPE         floor           FLOOR
rand            RAND            exp             EXP
utl_inaddr      UTL_INADDR      ctxsys          CTXSYS
geometrycollection  linestring  multipoint      polygon
```

---

## Union/Boolean Functions (preserve exactly)

```
union           UNION           select          SELECT
substr          SUBSTR          substring       SUBSTRING
mid             MID             ascii           ASCII
ord             ORD             char            CHAR
concat          CONCAT          group_concat    GROUP_CONCAT
```

---

## Out-of-Band / File Functions (preserve exactly)

```
load_file       LOAD_FILE       into outfile    INTO OUTFILE
utl_http        UTL_HTTP        utl_file        UTL_FILE
xp_cmdshell     XP_CMDSHELL     openrowset      OPENROWSET
pg_read_file    PG_READ_FILE    pg_ls_dir       PG_LS_DIR
load_extension  LOAD_EXTENSION
```

---

## Encoding Functions (preserve exactly)

```
unhex           UNHEX           hex             HEX
convert         CONVERT         cast            CAST
nchar           NCHAR           charindex       CHARINDEX
```

---

## DB-Specific Identifiers (preserve exactly)

```
# MySQL
information_schema  @@version   @@datadir   group_concat    ifnull  elt

# PostgreSQL
string_agg      array_to_string     pg_sleep    pg_read_binary_file

# Oracle
dual            rownum      connect by  all_tables  v$instance  all_columns

# MSSQL
sys.objects     sys.columns     sysobjects  syscolumns  @@servername  stuff

# SQLite
sqlite_master   sqlite_temp_master  sqlite_version
```

---

## Replacement Rules (for non-whitelisted tokens)

| Token type | Replacement |
|-----------|-------------|
| String literals | `__STR__` |
| Integer literals | `__INT__` |
| Hex literals (0x...) | `__HEX__` |
| Column/table names | `__IDENT__` |
| Database names | `__DBNAME__` |

---

## Estimated Vocabulary Size

After delex with this whitelist:
- ~115–130 unique tokens
- Function preservation rate: >= 95% (quality gate)
- Collision rate: <= 4.33% (quality gate — critical: run strip_wrapper BEFORE delex)

**CRITICAL ORDER**: `strip_wrapper()` MUST run BEFORE `delex_v2()`.
If reversed: collision rate jumps from 4.33% to 40.18% (empirically measured).

---

*Updated: 2026-05-18 for label-sqli v1.0*
