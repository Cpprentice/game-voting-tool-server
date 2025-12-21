import sqlite3
import uuid
from typing import Annotated

from fastapi import Request, Response
from pydantic import StrictStr, Field

from gvt_server.apis.user_api_base import BaseUserApi


class UserApi(BaseUserApi):
    async def login_user(
            self,
            request: Request,
            connection: sqlite3.Connection,
            body: Annotated[StrictStr, Field(description="Desired user name")],
    ) -> str:

        if body.lower() not in {'cpprentice', 'thetout', 'digital'}:
            return Response('Login failed', status_code=400)
        return str(uuid.uuid4().hex)
