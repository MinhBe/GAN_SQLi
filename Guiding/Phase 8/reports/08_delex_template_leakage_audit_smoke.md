# 08 - Delex Template Leakage Audit

Scope: split overlap in normalized delex-template space. Raw payloads are intentionally omitted.

## Source Summary

| Source | Rows | Unique Templates | Duplicate Template Row Rate |
|---|---:|---:|---:|
| train | 50,000 | 18,235 | 0.6353 |
| dev | 50,000 | 15,550 | 0.6890 |
| test | 50,000 | 15,464 | 0.6907 |

## Pair Overlap

| Pair | Shared Templates | Left Rows On Shared | Right Rows On Shared | Left Rate | Right Rate |
|---|---:|---:|---:|---:|---:|
| train__dev | 10,600 | 38,868 | 41,138 | 0.7774 | 0.8228 |
| train__test | 10,581 | 38,786 | 41,204 | 0.7757 | 0.8241 |
| dev__test | 11,270 | 43,498 | 43,552 | 0.8700 | 0.8710 |

## All Three Splits

- Shared templates across train/dev/test: `8,116`
- train rows on all-three templates: `34,670` (`0.6934`)
- dev rows on all-three templates: `37,352` (`0.7470`)
- test rows on all-three templates: `37,386` (`0.7477`)

## Interpretation

- High dev/test overlap with train means token CE loss, novelty, and generated uniqueness can be inflated.
- If overlap is high, Phase 8 claims should use a new delex-template cluster split or explicitly scope old Phase 6 numbers as contaminated by template leakage.
- The JSON sidecar contains top shared template hashes for forensic tracing without exposing payload text.
