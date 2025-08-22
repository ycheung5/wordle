from __future__ import annotations
import json
import pathlib
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    max_rounds: int
    word_list: pathlib.Path
    rng_seed: Optional[int] = None

def load_config(path: str | pathlib.Path) -> Config:
    p = pathlib.Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if "max_rounds" not in data or "word_list" not in data:
        raise ValueError("Config must include 'max_rounds' and 'word_list'.")
    return Config(
        max_rounds=int(data["max_rounds"]),
        word_list=pathlib.Path(data["word_list"]),
        rng_seed=data.get("rng_seed", None),
    )
