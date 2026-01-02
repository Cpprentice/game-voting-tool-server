# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from gvt_server.apis.game_api_base import BaseGameApi
import gvt_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
    Request
)

from gvt_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from gvt_server.models.game import Game

from gvt_db.db import SessionDependency

router = APIRouter()

ns_pkg = gvt_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/games",
    responses={
        200: {"model": Game, "description": "successful operation"},
        400: {"description": "Invalid input or game id already taken"},
        422: {"description": "Validation exception"},
    },
    tags=["game"],
    summary="Attempt to add a new game",
    response_model_by_alias=True,
)
async def create_game(
    request: Request,
    session: SessionDependency,
    game: Optional[Game] = Body(None, description=""),
) -> Game:
    """Add a new game from a data record"""
    if not BaseGameApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGameApi.subclasses[0]().create_game(request, session, game)


@router.post(
    "/games/from-steam",
    responses={
        200: {"model": Game, "description": "successful operation"},
        400: {"description": "Invalid input or game id already taken"},
        422: {"description": "Validation exception"},
    },
    tags=["game"],
    summary="Attempt to add a game from a steam id",
    response_model_by_alias=True,
)
async def create_game_from_steam(
    request: Request,
    session: SessionDependency,
    body: Optional[StrictStr] = Body(None, description=""),
) -> Game:
    """Scrapes the steam store for data"""
    if not BaseGameApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGameApi.subclasses[0]().create_game_from_steam(request, session, body)


@router.get(
    "/games",
    responses={
        200: {"model": List[Game], "description": "successful operation"},
    },
    tags=["game"],
    summary="Get list of supported games",
    response_model_by_alias=True,
)
async def get_games(
    request: Request,
    session: SessionDependency,
) -> List[Game]:
    """Receive game list"""
    if not BaseGameApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGameApi.subclasses[0]().get_games(request, session, )
