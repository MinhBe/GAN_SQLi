# Y3_encoded_boolean SeqGAN training files

Use `seqgan_accepted_corpus.txt` and `seqgan_accepted_metadata.jsonl` for SeqGAN training.
Do not use `seqgan_attack_corpus.txt` for training unless you intentionally want raw candidates, because it includes rows excluded by the static gate.

Accepted static rows: 5436 / 6000.
PostgreSQL parse/runtime validation has not been run in this artifact; runtime fields intentionally remain `not_run`.
