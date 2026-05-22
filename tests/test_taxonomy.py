import json

from gumbel_sqli.taxonomy import (
    apply_action,
    detect_actions,
    make_action_frame,
    reconstruct_payload,
)


def test_detector_finds_required_families():
    payload = "UnIoN SELECT char(65) FROM users WHERE id=0x31 AND name='bob' -- x %27"
    families = {hit["family"] for hit in detect_actions(payload)}
    assert "literal" in families
    assert "operator" in families
    assert "comment" in families
    assert "encoding" in families
    assert "function" in families
    assert "keyword_variant" in families
    assert "whitespace" in families
    assert "tamper_candidate" in families


def test_round_trip_reconstructs_original_payload():
    payload = "\" or pg_sleep ( __TIME__ ) --"
    frame = make_action_frame(payload)
    assert reconstruct_payload(frame["template"], frame["slots_json"]) == payload
    assert json.loads(frame["slots_json"])


def test_action_mutation_stays_action_level():
    payload = "select * from users where id = 1 and name = 'a'"
    mutated = apply_action(payload, "keyword_split")
    assert mutated != payload
    assert "/**/" in mutated
