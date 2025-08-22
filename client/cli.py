from __future__ import annotations
import argparse
import requests
import sys

DEFAULT_BASE = "http://127.0.0.1:8000"

def cmd_new(args):
    base = args.base_url or DEFAULT_BASE
    payload = {}
    if args.max_rounds:
        payload["max_rounds"] = args.max_rounds
    if args.seed is not None:
        payload["rng_seed"] = args.seed
    r = requests.post(f"{base}/api/games", json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(data["game_id"])

def show_score(score):
    print("".join(score))

def cmd_play(args):
    base = args.base_url or DEFAULT_BASE
    gid = args.game_id
    if not gid:
        r = requests.post(
            f"{base}/api/games",
            json={"max_rounds": args.max_rounds, "rng_seed": args.seed},
            timeout=10,
        )
        r.raise_for_status()
        gid = r.json()["game_id"]
        print(f"[New game] id={gid}")

    while True:
        s = requests.get(f"{base}/api/games/{gid}", timeout=10)
        if s.status_code == 404:
            print("Game not found.", file=sys.stderr)
            return 1
        st = s.json()
        if st["over"]:
            break

        guess = input("Enter 5-letter guess: ").strip()
        resp = requests.post(f"{base}/api/games/{gid}/guess", json={"guess": guess}, timeout=10)
        if resp.status_code == 400:
            print(f"Error: {resp.json()['detail']}")
            continue
        if resp.status_code == 409:
            print("Game is already over.")
            break
        resp.raise_for_status()
        data = resp.json()
        show_score(data["score"])
        if data["won"]:
            print("You guessed it!")
            break

    # reveal the answer if game is over
    rev = requests.get(f"{base}/api/games/{gid}/reveal", timeout=10)
    if rev.status_code == 403:
        print("Game not over yet.")
    elif rev.status_code == 200:
        print(f"Answer: {rev.json()['answer']}")
    else:
        print("Unable to reveal.")

def cmd_state(args):
    base = args.base_url or DEFAULT_BASE
    gid = args.game_id
    r = requests.get(f"{base}/api/games/{gid}", timeout=10)
    r.raise_for_status()
    print(r.json())

def main():
    ap = argparse.ArgumentParser(description="Wordle client for Task 2 (server-play).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_new = sub.add_parser("new", help="Create a new game and print its ID.")
    ap_new.add_argument("--base-url", help="Server base URL")
    ap_new.add_argument("--max-rounds", type=int, default=None)
    ap_new.add_argument("--seed", type=int, default=None)
    ap_new.set_defaults(func=cmd_new)

    ap_play = sub.add_parser("play", help="Play a game by ID (or create a new one).")
    ap_play.add_argument("--base-url", help="Server base URL")
    ap_play.add_argument("--game-id", help="Existing game id; if omitted a new game is created")
    ap_play.add_argument("--max-rounds", type=int, default=None)
    ap_play.add_argument("--seed", type=int, default=None)
    ap_play.set_defaults(func=cmd_play)

    ap_state = sub.add_parser("state", help="Get game state by ID.")
    ap_state.add_argument("--base-url", help="Server base URL")
    ap_state.add_argument("--game-id", required=True)
    ap_state.set_defaults(func=cmd_state)

    args = ap.parse_args()
    raise SystemExit(args.func(args))

if __name__ == "__main__":
    main()
