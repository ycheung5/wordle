from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Iterable
import random
import pathlib

class Score(Enum):
    HIT = auto()      # correct letter, correct spot
    PRESENT = auto()  # letter exists in answer but at different spot
    MISS = auto()     # letter not in answer

def score_to_string(score_row: Iterable[Score]) -> str:
    """
    Represent a score row using assignment's symbols:
    O = Hit, ? = Present, _ = Miss
    """
    m = {Score.HIT: "O", Score.PRESENT: "?", Score.MISS: "_"}
    return "".join(m[s] for s in score_row)

def normalize_word(w: str) -> str:
    w = w.strip().upper()
    if not w or len(w) != 5 or not w.isalpha():
        raise ValueError("Each word must be exactly 5 English letters.")
    return w

def load_word_list(path: str | pathlib.Path) -> List[str]:
    """Load a word list file with one word per line (case-insensitive)."""
    p = pathlib.Path(path)
    words: List[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        w = normalize_word(line)
        words.append(w)
    if not words:
        raise ValueError("Word list is empty.")
    return words

@dataclass
class WordleConfig:
    max_rounds: int = 6
    word_list: List[str] | None = None
    rng_seed: int | None = None  # useful for tests / reproducibility

class Wordle:
    """
    Core Wordle game engine implementing Task 1 (single-player, local).

    Usage:
        game = Wordle(word_list=words, max_rounds=6)
        score, err = game.check_guess("PLANT")
    """
    def __init__(self, word_list: List[str], max_rounds: int = 6, rng_seed: int | None = None):
        if max_rounds <= 0:
            raise ValueError("max_rounds must be positive.")
        if not word_list:
            raise ValueError("word_list must not be empty.")
        self.word_list = [normalize_word(w) for w in word_list]
        self.max_rounds = max_rounds
        self.rng = random.Random(rng_seed)
        self.answer: str = self.rng.choice(self.word_list)
        self.rounds_played: int = 0
        self.won: bool = False

    def _validate_guess(self, guess: str) -> str:
        g = normalize_word(guess)
        if g not in self.word_list:
            raise ValueError("Invalid word: not in word list.")
        return g

    @staticmethod
    def _score_internal(answer: str, guess: str) -> List[Score]:
        # Wordle duplicate-letter handling:
        # First mark all hits, then for remaining letters compute PRESENT counts using frequency.
        result = [Score.MISS] * 5
        answer_list = list(answer)
        guess_list = list(guess)

        # First pass: mark HITs and remove matched chars.
        for i in range(5):
            if guess_list[i] == answer_list[i]:
                result[i] = Score.HIT
                answer_list[i] = None
                guess_list[i] = None

        # Count remaining letters in answer
        freq = {}
        for ch in answer_list:
            if ch is not None:
                freq[ch] = freq.get(ch, 0) + 1

        # Second pass: PRESENT if available in remaining frequency
        for i in range(5):
            ch = guess_list[i]
            if ch is not None and freq.get(ch, 0) > 0:
                result[i] = Score.PRESENT
                freq[ch] -= 1

        return result

    def check_guess(self, guess: str) -> Tuple[List[Score], None] | Tuple[None, str]:
        """Validate guess, update game state, and return per-letter scores.

        Returns:
            (scores, None) on success,
            (None, error_message) on validation failure.
        """
        try:
            g = self._validate_guess(guess)
        except ValueError as e:
            return None, str(e)

        self.rounds_played += 1
        scores = self._score_internal(self.answer, g)
        if g == self.answer:
            self.won = True
        return scores, None

    def is_over(self) -> bool:
        return self.won or self.rounds_played >= self.max_rounds
