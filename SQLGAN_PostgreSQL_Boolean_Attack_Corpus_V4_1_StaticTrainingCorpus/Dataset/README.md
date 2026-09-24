# SQLGAN PostgreSQL Boolean Attack Corpus V4.1 Static Training Corpus

This is a patched successor to V4. It should be described as a **static-training candidate corpus**, not a PostgreSQL-runtime-confirmed executable corpus.

Core fixes:
1. Each module now has `seqgan_accepted_corpus.txt` and `seqgan_accepted_metadata.jsonl`; these contain only rows accepted by the static SeqGAN gate.
2. `seqgan_attack_corpus.txt` is retained as the raw candidate view and must not be used for normal SeqGAN training.
3. Y3/Y4 now have explicit parent lineage fields: `parent_sample_id`, `parent_module_level`, `payload_before_transform`, `transform_recipe_id`, `roundtrip_valid`, `structure_preserved`, and `semantic_preserved`.
4. `legacy_literal_metric` naming has been replaced by `slot_sanity`; the score measures slot constraint fit, not real-world traffic distribution.
5. PostgreSQL parse/runtime fields remain `not_run`; use `validation/postgres_sandbox_validator.py` before claiming executable rate.

Recommended training input: `Dataset/A_generator_attack_corpus/<module>/seqgan_accepted_corpus.txt`.
