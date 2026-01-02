# coding: utf-8

import sqlite3
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import Request
from sqlmodel import Session

from pydantic import Field, StrictStr
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
        game_id: Annotated[StrictStr, Field(description="ID of the game to add to the voting")],
    ) -> None:
        """Attempt to add a game to the active voting by its ID"""
        ...
