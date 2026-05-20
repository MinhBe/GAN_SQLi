# SQLi Taxonomy — label-sqli

## 4 Attack Types (Primary)

| Type | Priority | Key Signals | Example |
|------|---------|------------|---------|
| `union_based` | 7 | UNION SELECT, ORDER BY N-- | `' UNION SELECT NULL,NULL--` |
| `time_blind` | 5 | SLEEP(), BENCHMARK(), WAITFOR, pg_sleep() | `' AND SLEEP(5)--` |
| `error_based` | 4 | extractvalue, updatexml, xmltype, floor(rand()) | `' AND extractvalue(1,concat(0x7e,version()))--` |
| `boolean_blind` | 3 | OR 1=1, AND 1=2, substring comparisons | `' OR '1'='1` |
| `benign` | 1 | None of the above, max attack score < 0.20 | `admin` |

**Note**: Priority only matters for tiebreaking when multiple types score similarly.
Multi-dimensional payload → `is_complex=True`, primary = argmax.

---

## 5 DB Engines

| Engine | Key Exclusive Functions | Confidence Signal |
|--------|------------------------|-------------------|
| `mysql` | SLEEP(), BENCHMARK(), GROUP_CONCAT(), LOAD_FILE(), INTO OUTFILE, @@version | High exclusivity |
| `postgres` | pg_sleep(), pg_read_file(), $$ dollar-quoting, ::integer cast | Very high exclusivity |
| `oracle` | xmltype(), FROM DUAL, dbms_pipe, utl_http, ROWNUM, v$instance | Very high exclusivity |
| `mssql` | WAITFOR DELAY, xp_cmdshell, OPENROWSET, sys.objects, @@servername | Very high exclusivity |
| `sqlite` | randomblob(), sqlite_master, sqlite_version(), load_extension() | Very high exclusivity |
| `unknown` | Fallback when no engine signature found | — |

---

## 20-Cell Matrix (type × engine)

This is what the GAN model learns. Each cell needs >= 50 rows minimum (gold tier: >= 200).

```
                mysql  postgres  oracle  mssql  sqlite  unknown
time_blind       +++     +++      ++      +++     +       +
boolean_blind    +++     ++       ++      ++      +       ++
union_based      +++     ++       ++      ++      +       ++
error_based      +++     +        +++     +       -       +
```

**Sparse cells** (historically hard to fill):
- `error_based × oracle`: xmltype-based attacks, rare in public datasets
- `error_based × sqlite`: SQLite has limited error-based techniques
- `time_blind × sqlite`: randomblob() rarely seen in wild payloads
- `union_based × oracle`: Oracle syntax (ROWNUM) rarely used in injection datasets

---

## Multi-dimensional Payloads

A payload scoring >= 0.40 in 2+ attack types → `is_complex = True`.

Examples:
- `admin' AND sleep(5) OR 1=1--` → time_blind=0.95, boolean_blind=0.90, is_complex=True
- `' UNION SELECT extractvalue(1,user())--` → union_based=0.92, error_based=0.95, is_complex=True

**Training impact**: complex payloads contribute to BOTH type cells. Count them once under primary type.

---

## Confidence Thresholds

| Threshold | Meaning | Action |
|-----------|---------|--------|
| >= 0.85 | Gold label | Include in gold training set |
| 0.70–0.84 | Silver label | Include in silver training set |
| 0.55–0.69 | Bronze label | Exclude from training |
| < 0.55 | Unlabeled / low confidence | Drop row |

---

## Obfuscation Types

| Type | Detector | Description |
|------|---------|-------------|
| Comment injection | `detect_comment_injection()` | `UN/**/ION`, `/*!50000SELECT*/` |
| Case variation | `detect_case_variation()` | `SeLeCt`, `UnIoN` |
| URL encoding | `detect_encoding_obfuscation()` | `%27 OR %271%27%3D%271` |
| Hex encoding | `detect_encoding_obfuscation()` | `0x27 OR 0x31=0x31` |
| Char encoding | `detect_encoding_obfuscation()` | `char(39) OR char(49)=char(49)` |

**Obfuscation handling**: Heuristic scorer strips comments and retries pattern match.
OWASP scorer does NOT handle obfuscation → disagreement → AI review.

---

*Updated: 2026-05-18 for label-sqli v1.0*
