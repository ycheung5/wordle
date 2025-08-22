from __future__ import annotations
from typing import Dict, Any
from uuid import uuid4
from fastapi import APIRouter, HTTPException

from wordle import Wordle
from .models import (
    CreateGameRequest, CreateGameResponse,
    GuessRequest, GuessResponse, GuessHistoryItem,
    StateResponse, RevealResponse, ServerConfig,
)
from .utils import score_symbols


def create_game_router(config: ServerConfig) -> APIRouter:
    """
    Returns an APIRouter that serves:
      POST   /games
      POST   /games/{game_id}/guess
      GET    /games/{game_id}
      GET    /games/{game_id}/reveal
    (The app will mount this under the /api prefix, preserving /api/games* paths.)
    """
    router = APIRouter(prefix="/games", tags=["games"])
    games: Dict[str, Dict[str, Any]] = {}

    @router.post("", response_model=CreateGameResponse, status_code=201)
    def create_game(req: CreateGameRequest):
        max_rounds = req.max_rounds or config.default_max_rounds
        game = Wordle(config.word_list, max_rounds=max_rounds, rng_seed=req.rng_seed or config.default_seed)
        gid = str(uuid4())
        games[gid] = {"engine": game, "history": []}
        return CreateGameResponse(
            game_id=gid,
            max_rounds=game.max_rounds,
            rounds_played=game.rounds_played,
            won=game.won,
            over=game.is_over(),
        )

    @router.post("/{game_id}/guess", response_model=GuessResponse)
    def make_guess(game_id: str, req: GuessRequest):
        if game_id not in games:
            raise HTTPException(status_code=404, detail="Game not found.")
        st = games[game_id]
        game: Wordle = st["engine"]
        if game.is_over():
            raise HTTPException(status_code=409, detail="Game is already over.")
        scores, err = game.check_guess(req.guess)
        if err is not None:
            raise HTTPException(status_code=400, detail=err)
        symbols = score_symbols(scores)
        st["history"].append({"guess": req.guess.upper(), "score": symbols})
        return GuessResponse(
            score=symbols,
            rounds_played=game.rounds_played,
            won=game.won,
            over=game.is_over(),
            history=[GuessHistoryItem(**h) for h in st["history"]],
        )

    @router.get("/{game_id}", response_model=StateResponse)
    def get_state(game_id: str):
        if game_id not in games:
            raise HTTPException(status_code=404, detail="Game not found.")
        st = games[game_id]
        game: Wordle = st["engine"]
        return StateResponse(
            max_rounds=game.max_rounds,
            rounds_played=game.rounds_played,
            won=game.won,
            over=game.is_over(),
            history=[GuessHistoryItem(**h) for h in st["history"]],
        )

    @router.get("/{game_id}/reveal", response_model=RevealResponse)
    def reveal(game_id: str):
        if game_id not in games:
            raise HTTPException(status_code=404, detail="Game not found.")
        st = games[game_id]
        game: Wordle = st["engine"]
        if not game.is_over():
            raise HTTPException(status_code=403, detail="Game is not over yet.")
        return RevealResponse(answer=game.answer)

    return router
