from __future__ import annotations
import argparse
import pathlib
from wordle import Wordle, load_word_list, score_to_string
from wordle.config import load_config
from wordle.host_cheating import HostCheatingWordle


def build_game(args):
    # Resolve config/CLI into words, max_rounds, seed
    if args.config:
        cfg = load_config(args.config)
        words = load_word_list(cfg.word_list)
        max_rounds = cfg.max_rounds
        rng_seed = cfg.rng_seed
    else:
        words = load_word_list(args.words)
        max_rounds = args.rounds
        rng_seed = args.seed

    # Select engine
    if args.mode == "cheat":
        return HostCheatingWordle(words, max_rounds=max_rounds, rng_seed=rng_seed)
    return Wordle(words, max_rounds=max_rounds, rng_seed=rng_seed)


def main():
    parser = argparse.ArgumentParser(description="Wordle CLI (Task 1 + Task 3)")
    parser.add_argument(
        "--mode",
        choices=["fair", "cheat"],
        default="fair",
        help="fair = normal Wordle; cheat = host-cheating (Absurdle-style)",
    )
    parser.add_argument("--config", type=pathlib.Path, help="Path to JSON config file.")
    parser.add_argument(
        "--words",
        type=pathlib.Path,
        default=pathlib.Path("data/words.txt"),
        help="Path to word list file (one 5-letter word per line).",
    )
    parser.add_argument("--rounds", type=int, default=6, help="Max rounds (default: 6).")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility.")
    args = parser.parse_args()

    game = build_game(args)

    mode_label = "Host-cheating" if args.mode == "cheat" else "Fair"
    print(f"Welcome to Wordle! Mode: {mode_label}")
    print(f"Max rounds: {game.max_rounds}")

    while not game.is_over():
        guess = input("Enter a 5-letter guess: ").strip()
        scores, err = game.check_guess(guess)
        if err:
            print(f"Error: {err}")
            continue
        print(score_to_string(scores))
        if game.won:
            print("You guessed it! 🎉")
            break

    if not game.won:
        # In cheat mode, the engine decides the answer at the end; in fair mode it's fixed from start.
        print(f"Game over! The word was: {game.answer}")


if __name__ == "__main__":
    main()
