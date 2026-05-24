# 08 - Delex Template Leakage Audit

Scope: split overlap in normalized delex-template space. Raw payloads are intentionally omitted.

## Source Summary

| Source | Rows | Unique Templates | Duplicate Template Row Rate |
|---|---:|---:|---:|
| train | 1,652,331 | 77,804 | 0.9529 |
| dev | 165,836 | 26,899 | 0.8378 |
| test | 166,206 | 26,901 | 0.8381 |

## Pair Overlap

| Pair | Shared Templates | Left Rows On Shared | Right Rows On Shared | Left Rate | Right Rate |
|---|---:|---:|---:|---:|---:|
| train__dev | 26,899 | 1,522,182 | 165,836 | 0.9212 | 1.0000 |
| train__test | 26,901 | 1,523,763 | 166,206 | 0.9222 | 1.0000 |
| dev__test | 18,322 | 154,819 | 155,041 | 0.9336 | 0.9328 |

## All Three Splits

- Shared templates across train/dev/test: `18,322`
- train rows on all-three templates: `1,473,859` (`0.8920`)
- dev rows on all-three templates: `154,819` (`0.9336`)
- test rows on all-three templates: `155,041` (`0.9328`)

## Interpretation

- High dev/test overlap with train means token CE loss, novelty, and generated uniqueness can be inflated.
- If overlap is high, Phase 8 claims should use a new delex-template cluster split or explicitly scope old Phase 6 numbers as contaminated by template leakage.
- The JSON sidecar contains top shared template hashes for forensic tracing without exposing payload text.
