# Wrapper Patterns — Strip rules

53.64% of attack payloads in `combined_labeled_data.csv` start with `select * from users WHERE username = "..."`. This is **dataset wrapping**, not part of the actual SQLi attack. The real attack is the INNER content.

After delex, wrapper becomes `select * from __IDENT__ where __IDENT__ = __STR__` for all 9,559 payloads — they look identical. This causes mode collapse.

## Wrapper patterns to detect & strip

### Pattern W1: Single-quote wrapper
```regex
^\s*select\s+\*\s+from\s+\w+\s+where\s+\w+\s*=\s*'(.*)'\s*$
```
**Example input**: `select * from users WHERE username = '1' OR 1=1--'`
**Inner payload**: `1' OR 1=1--`

### Pattern W2: Double-quote wrapper
```regex
^\s*select\s+\*\s+from\s+\w+\s+where\s+\w+\s*=\s*"(.*)"\s*$
```
**Example input**: `select * from users WHERE username = "1) AND pg_sleep(5)--"`
**Inner payload**: `1) AND pg_sleep(5)--`

### Pattern W3: Concat wrapper (multi-arg)
Some payloads wrap with concatenated where clauses:
```regex
^\s*select\s+\*\s+from\s+\w+\s+where\s+\w+\s*=\s*"([^"]+)"\s+(and|or)\s+\w+\s*=\s*"([^"]+)"\s*$
```
**Example input**: `select * from users WHERE username = "1" or username = "-1' UNION SELECT NULL--"`
**Inner payload**: Take the LONGER part (the one containing the actual payload).

## When NOT to strip

Don't strip if:
- The query doesn't start with `select * from <table> where <col> =`
- The "inner" part is empty after stripping
- The inner part is shorter than 5 chars (probably empty wrapper, not actual attack)
- The "inner" part is identical to the wrapper (no actual injection inside)

## Output columns after stripping

For each row, produce TWO payload columns:

| Column | Content |
|--------|---------|
| `payload_norm` | Original full payload (kept for evaluate.py + WAF testing) |
| `payload_inner` | Stripped INNER payload (used for delex + GAN training) |

If no wrapper detected, `payload_inner = payload_norm`.

## Verification metric

After stripping, run check:
```
% rows with payload_inner ≠ payload_norm = should be ~53.64% (matches wrapper bias)
% rows with len(payload_inner) > len(payload_norm) = should be 0 (sanity)
Mean inner length vs mean norm length = should be ~30-50% shorter
```

## Edge case: nested wrappers

Some payloads have nested wrappers:
```
select * from users WHERE username = "select * from users WHERE username = '...'"
```
→ Apply stripping recursively up to 3 levels deep.

## Why this matters for GAN

Before stripping:
- 53% of training data starts with `select * from __IDENT__ where __IDENT__ =`
- G learns to ALWAYS output this prefix → wastes capacity on wrapper instead of attack patterns
- D learns to score "long prefix + short payload" as real → fake_attack_only_short doesn't get reward

After stripping:
- G focuses on the ACTUAL attack content (which varies widely)
- D learns attack-specific signals, not wrapper boilerplate
- Diversity in delex space jumps from 5,009 → expected 8,000+ unique patterns
