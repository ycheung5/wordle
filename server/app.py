from __future__ import annotations
from fastapi import FastAPI

from .models import ServerConfig  # keep type here
from .routes_game import create_game_router

# Re-export ServerConfig so existing imports (run_server.py) still work:
ServerConfig = ServerConfig  # noqa: F401


def create_app(config: ServerConfig) -> FastAPI:
    app = FastAPI(title="Wordle Server (Task 2)")

    # Mount /api/games* (same paths as before)
    app.include_router(create_game_router(config), prefix="/api")

    return app
