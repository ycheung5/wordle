from wordle.host_cheating import HostCheatingWordle
from wordle import Wordle, Score

def _counts(scores):
    return sum(s is Score.HIT for s in scores), sum(s is Score.PRESENT for s in scores)

def test_minimizes_hits_then_presents():
    words = ["APPLE", "ALLEY", "APPLY", "GRAPE", "PEACH", "ALARM"]  # add ALARM
    game = HostCheatingWordle(words, max_rounds=6, rng_seed=0)
    scores, err = game.check_guess("ALARM")
    assert err is None

    mins = min(_counts(Wordle._score_internal(ans, "ALARM")) for ans in words)
    assert _counts(scores) == mins

def test_candidates_remain_consistent_with_history():
    words = ["APPLE", "ALLEY", "APPLY", "GRAPE", "PEACH"]
    g = HostCheatingWordle(words, max_rounds=6, rng_seed=0)
    g.check_guess("ALARM")
    g.check_guess("PEACH")
    # Every remaining candidate must reproduce every past feedback
    for cand in g._candidates:
        for guess, scores in g.history:
            assert Wordle._score_internal(cand, guess) == scores

def test_win_when_only_candidate():
    g = HostCheatingWordle(["APPLE"], max_rounds=6)
    scores, err = g.check_guess("APPLE")
    assert err is None
    assert all(s is Score.HIT for s in scores)
    assert g.won and g.is_over()
    assert g.answer == "APPLE"

def test_loss_picks_consistent_answer():
    g = HostCheatingWordle(["APPLE", "PEACH"], max_rounds=1, rng_seed=0)
    scores, err = g.check_guess("APPLE")
    assert err is None
    assert g.is_over()
    if not g.won:
        # Chosen answer must be consistent with the history feedbacks
        ans = g.answer
        assert ans in ["APPLE", "PEACH"]
        for guess, scores in g.history:
            assert Wordle._score_internal(ans, guess) == scores
