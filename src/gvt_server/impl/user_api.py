import datetime
import uuid
from typing import Annotated

from fastapi import Request, Response
from pydantic import StrictStr, Field
from sqlmodel import Session

from gvt_server.apis.user_api_base import BaseUserApi
from gvt_server.models.backend import UserSession


class UserApi(BaseUserApi):
    async def login_user(
            self,
            request: Request,
            session: Session,
            body: Annotated[StrictStr, Field(description="Desired user name")],
    ) -> str:
        new_id = uuid.uuid4().hex
        user_session = UserSession(id=new_id, user_name=body, login_time=datetime.datetime.now())
        session.add(user_session)
        session.commit()
        # if body.lower() not in {'cpprentice', 'thetout', 'digital'}:
        #     return Response('Login failed', status_code=400)
        return new_id
