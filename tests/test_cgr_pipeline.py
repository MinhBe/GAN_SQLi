import torch

from sqlgan_dual.validators import static_validate
from sqlgan_dual.reward import score_payload
from sqlgan_dual.renderers import render_one
from sqlgan_dual.models import Generator, Discriminator
from sqlgan_dual.tokenizer import CharCodec
from sqlgan_dual.rollout import Rollout


def test_required_tokens_strict_rejects_missing_contract_token():
    contract = {"required_tokens": "AND"}
    v = static_validate("32 = 32", contract, strict_required=True)
    assert not v.final_accept
    assert not v.required_tokens_valid


def test_required_tokens_strict_accepts_matching_contract_token():
    contract = {"required_tokens": "AND =", "structure_signature": "<NUM> = <NUM> AND <NUM> = <NUM>"}
    v = static_validate("32 = 32 AND 9 = 9", contract, strict_required=True)
    assert v.final_accept
    assert v.required_tokens_valid


def test_reward_uses_best_matching_contract():
    contracts = [
        {"required_tokens": "LIKE", "structure_signature": "<STR> LIKE <STR>"},
        {"required_tokens": "AND =", "structure_signature": "<NUM> = <NUM> AND <NUM> = <NUM>"},
    ]
    r = score_payload("32 = 32 AND 9 = 9", contracts)
    assert r.matched_contract_index == 1
    assert r.reward > 0.8


def test_y3_and_y4_renderers_preserve_normalized_parent():
    y3 = render_one("32 = 32 AND 9 = 9", "Y3", "T_Y3_URL_FULL")
    y4 = render_one("32 = 32 AND 9 = 9", "Y4", "T_Y4_COMMENT_SPACE")
    assert y3.roundtrip_valid and y3.semantic_preserved
    assert y4.roundtrip_valid and y4.semantic_preserved


def test_rollout_reward_shape_smoke():
    texts = ["1 = 1", "2 = 2 AND 3 = 3"]
    codec = CharCodec.fit(texts, max_len=16)
    gen = Generator(codec.vocab_size, emb_dim=8, hidden_dim=16, pad_id=codec.pad_id)
    disc = Discriminator(codec.vocab_size, emb_dim=8, channels=8, pad_id=codec.pad_id)
    seq = torch.tensor([codec.encode("1 = 1")[1:]], dtype=torch.long)
    rollout = Rollout(gen)
    rewards = rollout.rewards(seq, disc, codec, contracts=[{"required_tokens": "="}], n_rollout=1)
    assert rewards.shape == seq.shape
    assert torch.isfinite(rewards).all()
