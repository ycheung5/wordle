# Wordle — Interview Project (Tasks 1–4)

A clean Python implementation of Wordle with:

- **Task 1**: Local CLI game (fair host)
- **Task 2**: FastAPI server + Python CLI client
- **Task 3**: **Host-cheating** engine (Absurdle-style)
- **Task 4**: **Multiplayer** modes (`common` shared answer, `mutual` opponent-sets-secret)
- Windows & macOS/Linux instructions, tests, and modular server code

---

## Quick Start

### 1) Set up environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Run the CLI (Task 1 / Task 3)
```bash
# Fair (default)
python main.py --config config.json
# or without config:
python main.py --words data/words.txt --rounds 6 --seed 42

# Host-cheating (Task 3)
python main.py --mode cheat --config config.json
```
`config.json`
```json
{
  "word_list": "data/words.txt",
  "max_rounds": 6,
  "rng_seed": 42
}
```

### 3) Run the server (Task 2/4)
```bash
python run_server.py
# -> http://127.0.0.1:8000 (OpenAPI docs at /docs)
```

### 4) Use the client (Task 2)
```bash
# Play interactively (auto-creates a game)
python -m client.cli play

# Create only and print game id
python -m client.cli new

# Inspect a game
python -m client.cli state --game-id <uuid>
```

### 5) Tests
```bash
pytest -q
```

---

## Project Structure

```
wordle/                   # Core game logic
  __init__.py
  game.py                 # Scoring, validation, Wordle engine (Task 1)
  config.py               # JSON config loader
  host_cheating.py        # Absurdle-style engine (Task 3)

server/                   # FastAPI app (Task 2/4)
  __init__.py
  app.py                  # create_app() + router composition
  models.py               # Pydantic request/response models + ServerConfig
  utils.py                # helpers (e.g., score_symbols)
  routes_game.py          # /api/games endpoints
  # (optional future) routes_match.py for multiplayer endpoints

client/
  __init__.py
  cli.py                  # Simple requests-based client (Task 2)

data/
  words.txt               # 5-letter uppercase dictionary

tests/                    # Pytest suite
  test_game.py            # Task 1 engine tests
  test_host_cheating.py   # Task 3 logic tests
  test_server.py          # Task 2 API tests

run_server.py             # Reads server_config.json, starts FastAPI
server_config.json        # Server defaults (word list, rounds, seed)
requirements.txt
```

---

## API Overview

### Task 2 (Single-player)
- `POST /api/games` → create game  
  **201** returns `{ game_id, max_rounds, rounds_played, won, over }`
- `POST /api/games/{game_id}/guess` → make a guess  
  **400** invalid word; **409** if game over
- `GET /api/games/{game_id}` → current state (history, flags)
- `GET /api/games/{game_id}/reveal` → reveal after game ends (**403** if not over)

### Task 4 (Multiplayer, if enabled)
- `POST /api/matches` → create match `{ mode: "common"|"mutual", max_rounds, required_players }`
- `POST /api/matches/{id}/join` → join; returns `player_id`
- `POST /api/matches/{id}/secret` → set secret (mutual mode)
- `POST /api/matches/{id}/guess` → player guess
- `GET  /api/matches/{id}/state?player_id=...` → lobby + your board
- `GET  /api/matches/{id}/reveal` → final reveal when everyone is over

HTTP codes are used intentionally: **201/200/400/403/404/409**.

---

## Assumptions & Clarifications

- **Dictionary enforcement**: guesses must be exactly **5 English letters** and present in the configured word list.
- **Case**: input normalized to uppercase.
- **Reproducibility**: optional RNG seed controls answer selection (fair mode) and tie-breaks (cheat mode’s end-of-game pick).
- **Cheating logic**: select the feedback bucket with **fewest HITs**, then **fewest PRESENTs**; tie-break to **largest bucket**, then a stable pattern order.
- **Multiplayer modes**:
  - `common`: everyone races the **same** answer.
  - `mutual`: each player sets a secret; you guess your opponent’s secret.

---

## Decision Making & Trade-offs

- Reuse a **single scoring function** across engines to avoid duplication.
- Keep **one word list** for both answers and guesses (simple, consistent).  
  *(Optional future: separate “allowed guesses” list.)*
- **FastAPI + in-memory** state for deterministic evaluation.  
  *(Trade-off: not persistent across restarts.)*
- **Polling** endpoints for multiplayer (simpler than WebSockets).
- Modular server (`models`, `routes_*`, `app`) for maintainability.

---

## Code Quality & Organization

- Clear separation between engine, server, and client.
- Consistent naming: `Score.{HIT,PRESENT,MISS}`, `score_to_string`, `ServerConfig`.
- Tests cover engine, cheat logic, and API routes (`pytest` + FastAPI `TestClient`).

---

## Extending

- Add `routes_match.py` for multiplayer routing:
  ```python
  app.include_router(create_match_router(config), prefix="/api")
  ```
- Persist games in Redis or a DB (swap out in-memory dicts).
- Add Web UI or WebSockets for real-time updates.

---

## Requirements

```
fastapi>=0.110
uvicorn>=0.27
requests>=2.31
httpx>=0.27
pytest>=8.0.0
```

---

## License

For interview and evaluation use. Adapt freely as needed.
