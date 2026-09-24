from sqlgan_dual.validators import static_validate
from sqlgan_dual.renderers import render_one


def test_static_validate_basic_boolean():
    v = static_validate("32 = 32")
    assert v.final_accept
    assert v.boolean_signal_valid


def test_reject_broken_keyword_scope():
    v = static_validate("313 BET ENT BETWEE 2606 AND 5541")
    assert not v.final_accept


def test_y3_roundtrip():
    r = render_one("32 = 32", derived_level="Y3", recipe_id="T_Y3_URL_FULL")
    assert r.roundtrip_valid
    assert r.semantic_preserved


def test_y4_roundtrip():
    r = render_one("32 = 32", derived_level="Y4", recipe_id="T_Y4_TAB_SPACE")
    assert r.roundtrip_valid
    assert r.semantic_preserved
