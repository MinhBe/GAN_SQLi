# Week 5 Baseline Definitions

## Baselines

| Baseline | Role | Construction |
| --- | --- | --- |
| `template_rule` | Minimal seed/template baseline | Balanced sample from train-split teacher seed rows |
| `deterministic_mutation` | Simple mutation baseline | Deterministic operator families applied to train-split teacher seed rows |

## Operator Families

The mutation baseline records only operator family names in reports: case variation, spacing/comment-style separator variation, boolean-word variation, and quote encoding variation. Detailed payload text is not written to markdown reports or logs.

## Evaluation

Both baselines are evaluated through the same ModSecurity + OWASP CRS Docker path established by Week 4 real-WAF smoke testing.
