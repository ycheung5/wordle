from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class CreateGameRequest(BaseModel):
    max_rounds: Optional[int] = Field(default=None, ge=1)
    rng_seed: Optional[int] = None

class CreateGameResponse(BaseModel):
    game_id: str
    max_rounds: int
    rounds_played: int
    won: bool
    over: bool

class GuessRequest(BaseModel):
    guess: str

class GuessHistoryItem(BaseModel):
    guess: str
    score: List[str]

class GuessResponse(BaseModel):
    score: List[str]
    rounds_played: int
    won: bool
    over: bool
    history: List[GuessHistoryItem]

class StateResponse(BaseModel):
    max_rounds: int
    rounds_played: int
    won: bool
    over: bool
    history: List[GuessHistoryItem]

class RevealResponse(BaseModel):
    answer: str

class ServerConfig(BaseModel):
    word_list: List[str]
    default_max_rounds: int = 6
    default_seed: Optional[int] = None
