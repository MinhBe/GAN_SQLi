# Validation

This artifact contains static validation and a PostgreSQL sandbox validator script.

Important boundary: PostgreSQL parse/runtime validation has not been executed here. Fields `postgres_parse_valid_v4`, `postgres_runtime_valid_v4`, and `semantic_behavior_valid_v4` intentionally remain `not_run`.

Run `postgres_sandbox_validator.py` against a disposable local PostgreSQL database before claiming executable rate. After runtime validation, create `accepted_runtime_valid.csv` from rows that pass PostgreSQL parse/runtime behavior.
