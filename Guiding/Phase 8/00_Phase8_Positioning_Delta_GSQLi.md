# Phase 8 - Scientific Positioning and Delta vs GSQLi

Date: 2026-05-22

## Decision

Phase 8 does not continue full-sequence Gumbel training. The Phase 6 Gumbel work is frozen as an engineering smoke test and as negative evidence for full-sequence adversarial training on discrete SQLi tokens.

The scientific center of Phase 8 is conditional surgery:

- H2: discriminator-as-scorer / reranker, with benign rows used as negative evidence in the scorer/evaluator side.
- Anchor: supervised conditional masked infill, used as the non-adversarial surgery baseline.
- H5': paired masked slot-surgery GAN, evaluated only after the representation, split, and evaluator contracts are fixed.

## Target Construct

A generated payload is useful only if it satisfies all primary axes:

1. Validity: after rehydration and insertion into a controlled context template, the payload remains syntactically/behaviorally SQLi-relevant.
2. Novelty: the payload is not an exact or near copy of train data in raw or delex/template space.
3. Evasion: the payload bypasses a held-out detector or WAF-like oracle while preserving attack intent.

Technique conditioning is a secondary diagnostic. It is not the dependent variable.

## Delta vs GSQLi

GSQLi is close prior art: it uses a conditional GAN to emit mutation actions, applies them through a payload transformer, and evaluates bypass behavior against WAF/classifier oracles. Phase 8 must therefore avoid claiming "GAN + mutation/surgery for SQLi" as novel by itself.

The defensible delta is:

| Axis | GSQLi-like prior art | Phase 8 target |
|---|---|---|
| Generation unit | Mutation actions over existing payloads | Hybrid conditional surgery: safe mutation actions plus masked slot infill where new local content is required |
| Conditioning | Mutation-vector style syntactic features | Technique + DB-family + obfuscation/state features, subject to ablation |
| Data scale | Small public SQLi corpora in the analysis notes | Phase 5 full corpus, after delex-template leakage audit |
| Evaluator | WAF/classifier bypass reports | Separated validity, novelty, and held-out evasion axes with meta-eval calibration |
| Baselines | Prior paper baselines | Internal comparison against MLE, anchor-only infill, mutation-engine baseline, H2 rerank, and H5' |
| Reproducibility | Risk of best-run reporting | Multi-seed or stratified vertical-slice confidence intervals within compute budget |

If Phase 8 cannot show this delta empirically, H5' should be downgraded and the thesis should emphasize H2/evaluator/dataset/negative-result contributions.

## Evaluation Contract

Do not use the following as primary gates:

- keyword-only `syntax_validity_rate`
- token-level CE validation loss
- discriminator score alone
- technique keyword hints alone

Use them only as debug signals.

Primary gates:

1. Delex-template leakage audit passes, or the report explicitly scopes claims to a contaminated split.
2. Error-based representation audit determines whether error-based is kept in the main task or moved to diagnostic appendix.
3. Evaluator meta-eval reports agreement between automatic labels and manually reviewed payloads.
4. Anchor-only is evaluated before H5'.
5. H5' is considered useful only if it improves validity-novelty-evasion over anchor-only and mutation-engine baselines, not merely over full-sequence Gumbel.

## Pre-registered Interpretation

- If anchor-only wins: the result is not a failure. The claim becomes that supervised conditional surgery is stronger than adversarial surgery under the current oracle.
- If H2 rerank improves anchor/MLE samples: the GAN-related contribution is a scorer/reranker rather than a generator.
- If H5' wins: claim a bounded improvement for paired conditional surgery under the held-out evaluator, not a universal result for SQLi GANs.
- If no generator beats retrieval/mutation: the scientific result is that the corpus plus constrained transformations dominate learned generation on this task.

## Immediate Implementation Order

1. Audit leakage in delex-template space across train/dev/test.
2. Audit `error_based` raw to delex to decide whether `delex_v2` is required and whether `error_based` remains in the main task.
3. Build evaluator contract and smoke implementation.
4. Re-score existing Phase 6 MLE and attack-only outputs using the new evaluator.
5. Implement anchor-only and mutation-engine baselines before H5'.

