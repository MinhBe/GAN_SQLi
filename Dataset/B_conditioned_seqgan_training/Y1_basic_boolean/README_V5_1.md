# Y1_basic_boolean C-SeqGAN Training Files (V5.1)

- `cseqgan_train.jsonl`: accepted-static rows only; reward-positive eligible.
- `cseqgan_ruleset_seed_minimal.jsonl`: one shape-only seed for rulesets missing accepted rows. These rows are `usable_for_mle=true` but `usable_for_reward_positive=false`.
- `cseqgan_train_full_coverage.jsonl`: recommended MLE bootstrap file; accepted-static rows plus minimal seeds, covering 1000/1000 rulesets.

Runtime status remains `not_run`; these files do not claim exploitability or PostgreSQL runtime success.
