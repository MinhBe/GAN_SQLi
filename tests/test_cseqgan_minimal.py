import json
from pathlib import Path

from sqlgan_dual.cseqgan_data import split_conditioned_text, make_prefix
from sqlgan_dual.reward_v2 import score_payload_v2


def test_split_conditioned_text():
    text = "<RULE=RS_Y1_R001_C01><CELL=PG_BOOL_R001_C01><FAMILY=comparison_numeric> 32 = 32"
    prefix, payload = split_conditioned_text(text)
    assert prefix == "<RULE=RS_Y1_R001_C01><CELL=PG_BOOL_R001_C01><FAMILY=comparison_numeric>"
    assert payload == "32 = 32"


def test_reward_v2_prefers_target_ruleset_and_slots():
    contract = {
        "ruleset_id": "RS_Y1_R053_C01",
        "structure_cell_id": "PG_BOOL_R053_C01",
        "ruleset_family": "array_operator",
        "semantic_family": "array_operator",
        "required_tokens": "ARRAY|&&",
        "skeleton_reference": "ARRAY[INT_LIST] && ARRAY[INT_LIST]",
        "slot_schema_json": json.dumps({
            "slots": [
                {"name": "left", "type": "int_array_literal"},
                {"name": "operator", "type": "operator_set", "allowed_values": ["&&"]},
                {"name": "right", "type": "int_array_literal"},
            ]
        }),
    }
    good = "<RULE=RS_Y1_R053_C01><CELL=PG_BOOL_R053_C01><FAMILY=array_operator> ARRAY[1,2] && ARRAY[2,3]"
    bad = "<RULE=RS_Y1_R006_C01><CELL=PG_BOOL_R006_C01><FAMILY=comparison_text> 'a' = 'a'"
    rg = score_payload_v2(good, contract)
    rb = score_payload_v2(bad, contract)
    assert rg.ruleset_score == 1.0
    assert rg.slot_score >= 0.9
    assert rg.reward > rb.reward
    assert rb.off_ruleset is True


def test_make_prefix():
    assert make_prefix("R", "C", "F") == "<RULE=R><CELL=C><FAMILY=F>"
