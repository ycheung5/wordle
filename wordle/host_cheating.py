from __future__ import annotations
from typing import List, Tuple, Dict
import random

from .game import Wordle, Score, normalize_word

class HostCheatingWordle:
    """
    Absurdle-style host: no fixed answer at start.
    After each guess, keep the bucket of candidates that:
      1) minimizes #HIT, then
      2) minimizes #PRESENT,
      3) tie-break: keep the largest bucket (hardest),
      4) final tie-break: deterministic on pattern.
    """
    def __init__(self, word_list: List[str], max_rounds: int = 6, rng_seed: int | None = None):
        if max_rounds <= 0:
            raise ValueError("max_rounds must be positive.")
        self.all_words = [normalize_word(w) for w in word_list]
        if not self.all_words:
            raise ValueError("word_list must not be empty.")

        self.max_rounds = max_rounds
        self.rounds_played = 0
        self.won = False
        self.answer: str | None = None  # set when game ends (win/lose)
        self.rng = random.Random(rng_seed)

        self._candidates: List[str] = self.all_words[:]   # remaining consistent answers
        self.history: List[Tuple[str, List[Score]]] = []  # (guess, score)

    def _validate_guess(self, guess: str) -> str:
        g = normalize_word(guess)
        if g not in self.all_words:
            raise ValueError("Invalid word: not in word list.")
        return g

    def _choose_bucket(self, guess: str) -> Tuple[List[Score], List[str]]:
        """Partition candidates by feedback pattern and choose the 'worst' bucket."""
        partitions: Dict[Tuple[int, int, Tuple[int, ...]], List[str]] = {}
        pattern_map: Dict[Tuple[int, int, Tuple[int, ...]], List[Score]] = {}

        for ans in self._candidates:
            scores = Wordle._score_internal(ans, guess)
            hits = sum(s is Score.HIT for s in scores)
            presents = sum(s is Score.PRESENT for s in scores)
            # Encode Score to ints for a stable last tie-break (MISS=0,PRESENT=1,HIT=2)
            enc = tuple(0 if s is Score.MISS else (1 if s is Score.PRESENT else 2) for s in scores)
            key = (hits, presents, enc)
            partitions.setdefault(key, []).append(ans)
            pattern_map[key] = scores

        # Min hits, then min presents, then *largest* bucket, then lexicographic pattern
        best_key = min(
            partitions.keys(),
            key=lambda k: (k[0], k[1], -len(partitions[k]), k[2])
        )
        return pattern_map[best_key], partitions[best_key]

    def check_guess(self, guess: str):
        try:
            g = self._validate_guess(guess)
        except ValueError as e:
            return None, str(e)

        self.rounds_played += 1
        scores, bucket = self._choose_bucket(g)
        self._candidates = bucket
        self.history.append((g, scores))

        if all(s is Score.HIT for s in scores):
            # Forced to reveal: the only consistent answer is the guess.
            self.won = True
            self.answer = g

        # If game is over by round limit but not won, pick any consistent answer
        if self.is_over() and not self.won:
            self.answer = self.rng.choice(self._candidates) if self._candidates else g

        return scores, None

    def is_over(self) -> bool:
        return self.won or self.rounds_played >= self.max_rounds
