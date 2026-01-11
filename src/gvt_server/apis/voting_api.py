# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from gvt_server.apis.voting_api_base import BaseVotingApi
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
from pydantic import Field, StrictInt, StrictStr
from typing import Any
from typing_extensions import Annotated

from gvt_db.db import SessionDependency

router = APIRouter()

ns_pkg = gvt_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/voting-session/{session_id}/participant/{user_id}/games/{game_id}",
    responses={
        200: {"description": "game added successfully"},
        400: {"description": "game could not be added"},
        404: {"description": "game could not be found"},
    },
    tags=["voting"],
    summary="Attempt to add a game to the voting",
    response_model_by_alias=True,
)
async def add_game_to_voting(
    request: Request,
    session: SessionDependency,
    session_id: Annotated[StrictStr, Field(description="the ID of the session to add the game to")] = Path(..., description="the ID of the session to add the game to"),
    user_id: Annotated[StrictStr, Field(description="the user that attempts to add the game")] = Path(..., description="the user that attempts to add the game"),
    game_id: Annotated[StrictStr, Field(description="ID of the game to add to the voting")] = Path(..., description="ID of the game to add to the voting"),
) -> None:
    """Attempt to add a game to the active voting by its ID"""
    if not BaseVotingApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVotingApi.subclasses[0]().add_game_to_voting(request, session, session_id, user_id, game_id)


@router.post(
    "/voting-session/{session_id}/participant/{user_id}/games/{game_id}/vote",
    responses={
        200: {"description": "vote cast successfully"},
        400: {"description": "vote could not be cast"},
        404: {"description": "session, user, or game could not be found"},
    },
    tags=["voting"],
    summary="Set a voting value",
    response_model_by_alias=True,
)
async def cast_vote(
    request: Request,
    session: SessionDependency,
    session_id: Annotated[StrictStr, Field(description="the ID of the session to cast the vote in")] = Path(..., description="the ID of the session to cast the vote in"),
    user_id: Annotated[StrictStr, Field(description="the user that casts the vote")] = Path(..., description="the user that casts the vote"),
    game_id: Annotated[StrictStr, Field(description="the game the vote is cast for")] = Path(..., description="the game the vote is cast for"),
    body: Annotated[StrictInt, Field(description="the value of the vote to be cast")] = Body(None, description="the value of the vote to be cast"),
) -> None:
    """Set your voting value for a specific game in a specific session"""
    if not BaseVotingApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVotingApi.subclasses[0]().cast_vote(request, session, session_id, user_id, game_id, body)
