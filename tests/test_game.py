import pathlib
import pytest
from wordle import Wordle, Score, score_to_string, load_word_list

DATA = pathlib.Path(__file__).resolve().parents[1] / "data" / "words.txt"
WORDS = load_word_list(DATA)

def test_normalize_and_load_words():
    assert "HELLO" in WORDS
    assert all(len(w) == 5 and w.isalpha() for w in WORDS)

def test_game_setup_and_answer_reproducible():
    g1 = Wordle(WORDS, max_rounds=6, rng_seed=42)
    g2 = Wordle(WORDS, max_rounds=6, rng_seed=42)
    assert g1.answer == g2.answer

def test_invalid_max_rounds():
    with pytest.raises(ValueError):
        Wordle(WORDS, max_rounds=0)

def test_invalid_guess_length():
    game = Wordle(WORDS, max_rounds=6, rng_seed=1)
    scores, err = game.check_guess("TOO LONG")
    assert scores is None and "exactly 5" in err

def test_invalid_guess_non_alpha():
    game = Wordle(WORDS, max_rounds=6, rng_seed=1)
    scores, err = game.check_guess("ab1!@")
    assert scores is None and "exactly 5" in err

def test_invalid_guess_not_in_list():
    game = Wordle(WORDS, max_rounds=6, rng_seed=1)
    scores, err = game.check_guess("ZZZZZ")
    assert scores is None and "not in word list" in err

def test_scoring_hit_present_miss():
    # Force answer to known word using seed
    game = Wordle(["APPLE", "PEACH", "GRAPE"], max_rounds=6, rng_seed=0)
    # With seed 0, pick a deterministic answer. We don't rely on specific word; we check relative scoring:
    answer = game.answer
    # Craft a guess with same letters in wrong spots (where possible)
    if answer == "APPLE":
        guess = "PEACH"  # A,P,P,L,E vs P,E,A,C,H -> expect some PRESENTs
        scores, err = game.check_guess(guess)
        assert err is None
        # Check no crashes and length 5
        assert len(scores) == 5
    else:
        # generic smoke
        scores, err = game.check_guess(answer)
        assert err is None
        assert all(s is Score.HIT for s in scores)

def test_duplicate_letter_logic():
    # Include BOTH the answer and the guess in the allowed dictionary
    game = Wordle(["PLANT", "ALARM"], max_rounds=6, rng_seed=1)
    game.answer = "PLANT"

    scores, err = game.check_guess("ALARM")
    assert err is None

    s = score_to_string(scores)
    # P L A N T
    # A L A R M
    # -> _ O O _ _
    assert s == "_OO__"

def test_win_and_game_over():
    game = Wordle(["APPLE"], max_rounds=2, rng_seed=1)
    game.answer = "APPLE"
    scores, err = game.check_guess("APPLE")
    assert err is None
    assert game.won
    assert game.is_over()

def test_lose_and_game_over():
    game = Wordle(["APPLE", "PEACH"], max_rounds=2, rng_seed=1)
    game.answer = "APPLE"
    scores, err = game.check_guess("PEACH")
    assert err is None
    assert not game.won
    assert not game.is_over()
    scores, err = game.check_guess("PEACH")
    assert game.is_over()
