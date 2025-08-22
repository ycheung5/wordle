from __future__ import annotations
from typing import List
from wordle import Score

def score_symbols(scores: List[Score]) -> List[str]:
    mapping = {Score.HIT: "O", Score.PRESENT: "?", Score.MISS: "_"}
    return [mapping[s] for s in scores]
