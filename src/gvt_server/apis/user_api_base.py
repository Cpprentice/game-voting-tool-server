# coding: utf-8

import sqlite3
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import Request
from sqlmodel import Session

from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated


class BaseUserApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUserApi.subclasses = BaseUserApi.subclasses + (cls,)
    async def login_user(
        self,
        request: Request,
        session: Session,
        body: Annotated[StrictStr, Field(description="Desired user name")],
    ) -> str:
        """"""
        ...
