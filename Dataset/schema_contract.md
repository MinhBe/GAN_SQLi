# V5.1 Schema Contract

The corpus is ruleset-conditioned. A generated row must carry both target and matched structure metadata.

Required candidate columns include:

- `target_ruleset_id`, `target_root_id`, `target_structure_cell_id`, `target_module_id`
- `payload_raw`, `payload_normalized`, `payload_decoded`, `payload_hash`
- `matched_ruleset_id`, `matched_structure_cell_id`, `match_source`
- `ruleset_match_score`, `skeleton_match_score`, `slot_match_score`, `required_token_match_score`
- `r_ruleset`, `r_skeleton`, `r_slot`, `r_coverage`, `p_duplicate`, `p_near_duplicate`
- `delimiter_valid`, `quote_valid`, `boolean_signal_valid`, `slot_sanity_valid`, `static_error_class`
- `postgres_parse_valid`, `postgres_runtime_valid`, `semantic_behavior_valid`, `truth_match`

Current bootstrap rows use `match_source=source_assigned`; future model outputs should use `algorithmic_match` or `ai_reviewed_match`.
