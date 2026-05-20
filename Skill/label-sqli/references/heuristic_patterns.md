# Heuristic Patterns — label-sqli

Patterns used by `heuristic_scorer.py`. More permissive than OWASP.
Handles obfuscated payloads that OWASP misses.

---

## Extra Time-Blind Patterns

```python
r'\bif\s*\(\s*\d+\s*=\s*\d+\s*,\s*sleep'   # IF(1=1,sleep(5),0)
r'\bcase\s+when\s+.+sleep\s*\('             # CASE WHEN 1=1 THEN SLEEP(5)
r"'\s*;\s*(?:exec|execute)\s+xp_"           # '; EXEC xp_cmdshell (MSSQL time via shell)
```

---

## Extra Boolean-Blind Patterns

```python
r"'\s+or\s+['\"]?\w+['\"]?\s*like\s*'%"    # ' OR x LIKE '%
r'\bif\s*\(\s*\(\s*select\b'               # IF((SELECT count(*)...)
r'\bexists\s*\(\s*select\b'               # EXISTS(SELECT 1 FROM...) blind check
r"' or ''='"                               # ' or ''='
r"admin'--"                                # auth bypass pattern
r"'\s+--\s*$"                              # ' -- (trailing comment after quote)
```

---

## Extra Union-Based Patterns

```python
r'union.{0,5}select.{0,30}(?:null|0x|char\()'  # UNION SELECT NULL/hex/char
r'order\s+by\s+\d+\b'                           # ORDER BY 1 (column count probing)
r'group\s+by\s+\d+\s*having\b'                 # GROUP BY 1 HAVING (error trigger)
```

---

## Extra Error-Based Patterns

```python
r'\bgeometrycollection\s*\('    # MySQL geometry error
r'\blinestring\s*\('            # MySQL geometry error
r'\bmultipoint\s*\('            # MySQL geometry error
r'\bpolygon\s*\('               # MySQL geometry error
r'\butl_inaddr\b'               # Oracle UTL_INADDR DNS leak
r'\bctxsys\b'                   # Oracle CTXSYS privilege escalation
```

---

## Structural Signals

Structural analysis detects injection context beyond keyword matching.

### Quote Imbalance
```python
count = payload.count("'") - payload.count("\\'")
if count % 2 != 0:  # Odd unescaped quotes → likely injection
    return 0.70     # High imbalance score
elif count > 0:
    return 0.30     # Even quotes, still some signal
```

### SQL Terminator at End
```
--\s*$      # SQL line comment: score 0.85
#\s*$       # MySQL hash comment: score 0.80
/\*.*\*/\s*$  # Block comment: score 0.75
;\s*$       # Statement terminator: score 0.60
```

**Usage**: Structural signals provide bonus to type scores when injection context detected.
`structural_bonus = structural_score * 0.10 if base_type_score > 0 else 0.0`

---

## Obfuscation-Aware Matching

When `detect_comment_injection()` or `detect_encoding_obfuscation()` scores > 0.70
AND base type detector = 0.0 AND heuristic extra pattern matches → give partial credit:

```python
obf_bonus = obf_score * 0.50
```

This handles payloads like `UN/**/ION SEL/**/ECT NULL--` that OWASP misses.

---

## Heuristic vs OWASP Comparison

| Aspect | OWASP | Heuristic |
|--------|-------|-----------|
| Pattern source | OWASP Guide v4.2 | Empirical + structural |
| Obfuscation | Not handled | Comment-strip + retry |
| Structural signals | No | Quote imbalance, terminator |
| Extra patterns | No | 20+ extra patterns |
| Recall | ~60-70% | ~85-90% |
| Precision | ~90-95% | ~75-85% |

**Disagreement rate**: ~25-35% of payloads where OWASP and Heuristic disagree.
These get sent to AI review (Claude Haiku).

---

## Obfuscation Detection Thresholds

| Detector | Pattern | Score |
|---------|---------|-------|
| comment_injection | `\w+\s*/\*[^*]*\*/\s*\w+` | 0.85 |
| comment_injection | `/*!50000` (MySQL version) | 0.90 |
| comment_injection | `/\*\*/` (empty comment) | 0.80 |
| case_variation | keyword with mixed case ratio 0.1-0.9 | 0.80 |
| encoding_obfuscation | `0x[0-9a-f]{4,}` | 0.85 |
| encoding_obfuscation | `char(\d+,...)` | 0.80 |
| encoding_obfuscation | `unhex(` | 0.85 |
| encoding_obfuscation | `%[0-9a-f]{2}` (URL encoding) | 0.60 |

---

*For OWASP canonical patterns, see owasp_patterns.md*
