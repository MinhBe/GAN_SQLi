# WAF-A-MoLE Original Reproduction Policy

## Decision

From this point forward, WAF-A-MoLE reproduction work must try the original-faithful runtime first. Fallbacks such as operator-only mutation, regenerated classifiers, or custom WAF-oracle adapters are allowed only after the original-faithful attempt has a written blocker.

## Original-Faithful Defaults

| Component | Default |
| --- | --- |
| Code source | `Timeline/Reproduction/external/WAF-A-MoLE` |
| Code commit | `4a2cb9438f874ec0d09acaa04402174cc6334880` |
| Dataset source | `Timeline/Reproduction/external/wafamole-dataset` |
| Dataset commit | `b8f0118b8586f8b069ac980b3909970838f69d5e` |
| Python | `3.7.x`, matching the upstream README badge |
| Primary sklearn target | `scikit-learn==0.21.1`, matching bundled pickle warnings from the current runtime |
| CLI/API | Upstream `wafamole evade` / `EvasionEngine`, without modifying upstream package code |
| First model probes | Bundled example models under `wafamole/models/custom/example_models` |
| Reporting | No raw payload text in markdown reports or logs |

## Claim Rules

- Claim `full_guided_wafamole_reproduction` only if a bundled or original-style classifier loads, classifies, and runs at least one guided `EvasionEngine.evaluate` attempt.
- Claim `partial_original_runtime_reproduction` if the original-faithful container loads/classifies bundled models but guided search is too slow or times out.
- Claim `blocked_original_runtime` if the legacy container cannot be built or bundled models still cannot load/classify.
- Keep `operator_only_sqlfuzzer` separate from WAF-A-MoLE guided reproduction.
