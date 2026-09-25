from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PAD = "<PAD>"
BOS = "<BOS>"
EOS = "<EOS>"
UNK = "<UNK>"
SPECIALS = [PAD, BOS, EOS, UNK]


@dataclass
class CharCodec:
    stoi: dict[str, int]
    itos: list[str]
    max_len: int

    @classmethod
    def fit(cls, texts: Iterable[str], max_len: int | None = None, min_freq: int = 1) -> "CharCodec":
        texts = [str(t) for t in texts if str(t)]
        if not texts:
            raise ValueError("Cannot fit tokenizer on an empty corpus")
        counts: dict[str, int] = {}
        for text in texts:
            for ch in text:
                counts[ch] = counts.get(ch, 0) + 1
        chars = sorted(ch for ch, n in counts.items() if n >= min_freq)
        itos = SPECIALS + chars
        stoi = {ch: i for i, ch in enumerate(itos)}
        max_len = int(max_len or (max(len(t) for t in texts) + 2))
        return cls(stoi=stoi, itos=itos, max_len=max_len)

    @property
    def pad_id(self) -> int:
        return self.stoi[PAD]

    @property
    def bos_id(self) -> int:
        return self.stoi[BOS]

    @property
    def eos_id(self) -> int:
        return self.stoi[EOS]

    @property
    def unk_id(self) -> int:
        return self.stoi[UNK]

    @property
    def vocab_size(self) -> int:
        return len(self.itos)

    def encode(self, text: str) -> list[int]:
        ids = [self.bos_id] + [self.stoi.get(ch, self.unk_id) for ch in str(text)] + [self.eos_id]
        ids = ids[: self.max_len]
        if ids[-1] != self.eos_id:
            ids[-1] = self.eos_id
        return ids + [self.pad_id] * (self.max_len - len(ids))

    def decode(self, ids: Iterable[int]) -> str:
        out: list[str] = []
        for raw in ids:
            i = int(raw)
            if i == self.eos_id:
                break
            if i in (self.pad_id, self.bos_id):
                continue
            if 0 <= i < len(self.itos):
                out.append(self.itos[i])
        return "".join(out)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps({"stoi": self.stoi, "itos": self.itos, "max_len": self.max_len}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "CharCodec":
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(stoi={k: int(v) for k, v in obj["stoi"].items()}, itos=list(obj["itos"]), max_len=int(obj["max_len"]))
