# coding: utf-8

import sqlite3
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import Request

from pydantic import StrictStr
from typing import Any, List, Optional
from gvt_server.models.game import Game


class BaseGameApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseGameApi.subclasses = BaseGameApi.subclasses + (cls,)
    async def create_game(
        self,
        request: Request,
        connection: sqlite3.Connection,
        game: Optional[Game],
    ) -> Game:
        """Add a new game from a data record"""
        ...


    async def create_game_from_steam(
        self,
        request: Request,
        connection: sqlite3.Connection,
        body: Optional[StrictStr],
    ) -> Game:
        """Scrapes the steam store for data"""
        ...


    async def get_games(
        self,
        request: Request,
        connection: sqlite3.Connection,
    ) -> List[Game]:
        """Receive game list"""
        ...
