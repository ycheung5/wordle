from __future__ import annotations
import argparse
import pathlib

def validate_words(path: str | pathlib.Path) -> int:
    p = pathlib.Path(path)
    bad = []
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        w = line.strip()
        if not w:
            continue
        if not w.isalpha() or len(w) != 5:
            bad.append((i, w))
    if bad:
        print("Invalid entries:")
        for i, w in bad:
            print(f"  line {i}: '{w}'")
        return 1
    print("All words valid.")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Validate a Wordle word list (5-letter alpha words).")
    ap.add_argument("path", type=pathlib.Path)
    args = ap.parse_args()
    raise SystemExit(validate_words(args.path))
