# coding: utf-8

import sqlite3
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import Request

from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated


class BaseImageApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseImageApi.subclasses = BaseImageApi.subclasses + (cls,)
    async def get_image(
        self,
        request: Request,
        connection: sqlite3.Connection,
        game_id: Annotated[StrictStr, Field(description="ID of the game to get the image for")],
    ) -> None:
        """Receive the requested image from the database"""
        ...
