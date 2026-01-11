import asyncio
import datetime
import uuid
from typing import Annotated

from fastapi import Request, Response
from pydantic import StrictStr, Field
from sqlmodel import Session

from gvt_logic.voting_session import handle_voting_session_update
from gvt_server.apis.user_api_base import BaseUserApi
from gvt_server.db_models import UserSession


class UserApi(BaseUserApi):
    async def login_user(
            self,
            request: Request,
            session: Session,
            body: Annotated[StrictStr, Field(description="Desired user name")],
    ) -> str:
        active_sessions = UserSession.get_active_sessions(session)
        print(len(active_sessions))
        if body in [active_session.user_name for active_session in active_sessions]:
            return Response('', status_code=400)
        new_id = uuid.uuid4().hex
        login_time = datetime.datetime.now()
        user_session = UserSession(id=new_id, user_name=body, login_time=login_time, last_alive_time=login_time)
        session.add(user_session)
        session.commit()
        handle_voting_session_update(request)
        return new_id
