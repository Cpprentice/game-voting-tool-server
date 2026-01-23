# coding: utf-8

import sqlite3
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import Request
from sqlmodel import Session

from pydantic import Field, StrictInt, StrictStr
from typing import Any
from typing_extensions import Annotated


class BaseVotingApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseVotingApi.subclasses = BaseVotingApi.subclasses + (cls,)
    async def add_game_to_voting(
        self,
        request: Request,
        session: Session,
        session_id: Annotated[StrictStr, Field(description="the ID of the session to add the game to")],
        user_id: Annotated[StrictStr, Field(description="the user that attempts to add the game")],
        game_id: Annotated[StrictStr, Field(description="ID of the game to add to the voting")],
    ) -> None:
        """Attempt to add a game to the active voting by its ID"""
        ...


    async def cast_vote(
        self,
        request: Request,
        session: Session,
        session_id: Annotated[StrictStr, Field(description="the ID of the session to cast the vote in")],
        user_id: Annotated[StrictStr, Field(description="the user that casts the vote")],
        game_id: Annotated[StrictStr, Field(description="the game the vote is cast for")],
        body: Annotated[StrictInt, Field(description="the value of the vote to be cast")],
    ) -> None:
        """Set your voting value for a specific game in a specific session"""
        ...


    async def set_reset_vote(
        self,
        request: Request,
        session: Session,
        session_id: Annotated[StrictStr, Field(description="the ID of the session to add the game to")],
        user_id: Annotated[StrictStr, Field(description="the user that attempts to add the game")],
        body: Annotated[StrictInt, Field(description="the value of the vote to be cast")],
    ) -> None:
        """Players can indicate if they want to reset or re-roll the voting session a majority triggers that accordingly."""
        ...
