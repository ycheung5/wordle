from __future__ import annotations
import pathlib, json
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Reuse loader from your engine
from wordle import load_word_list
from server.app import create_app, ServerConfig

def load_server_config(config_path: str | pathlib.Path) -> ServerConfig:
    p = pathlib.Path(config_path)
    data = json.loads(p.read_text(encoding="utf-8"))
    words = load_word_list(data.get("word_list", "data/words.txt"))
    default_max_rounds = int(data.get("default_max_rounds", 6))
    default_seed = data.get("default_seed", None)
    return ServerConfig(word_list=words, default_max_rounds=default_max_rounds, default_seed=default_seed)

if __name__ == "__main__":
    cfg = load_server_config("server_config.json")
    app = create_app(cfg)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
