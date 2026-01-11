from typing import Annotated, Union

from fastapi import Request, Response
from pydantic import StrictStr, StrictFloat, StrictInt
from sqlmodel import Session, Field, select

from gvt_logic.voting_session import handle_voting_session_update
from gvt_server.apis.voting_api_base import BaseVotingApi
from gvt_server.db_models import VotingSessionBackend, GameBackend, UserSession


class VotingApi(BaseVotingApi):
    async def add_game_to_voting(
            self,
            request: Request,
            session: Session,
            session_id: Annotated[StrictStr, Field(description="the ID of the session to add the game to")],
            user_id: Annotated[StrictStr, Field(description="the user that attempts to add the game")],
            game_id: Annotated[StrictStr, Field(description="ID of the game to add to the voting")],
    ) -> None:
        voting_session: VotingSessionBackend = session.exec(select(VotingSessionBackend).where(VotingSessionBackend.id == session_id)).first()
        if voting_session is None:
            return Response(status_code=404)
        user_session = UserSession.get_active_session(session, user_id)
        if user_session is None:
            return Response(status_code=404)
        game = session.exec(select(GameBackend).where(GameBackend.id == game_id)).first()
        if game is None:
            return Response(status_code=404)
        with session.begin(nested=True):
            if not voting_session.try_to_add_game(game_id, user_id, session):
                return Response(status_code=400)
            session.add(voting_session)
            session.commit()
        handle_voting_session_update(request)

    async def cast_vote(
            self,
            request: Request,
            session: Session,
            session_id: Annotated[StrictStr, Field(description="the ID of the session to cast the vote in")],
            user_id: Annotated[StrictStr, Field(description="the user that casts the vote")],
            game_id: Annotated[StrictStr, Field(description="the game the vote is cast for")],
            body: Annotated[StrictInt, Field(description="the value of the vote to be cast")],
    ) -> None | Response:
        voting_session: VotingSessionBackend | None = session.exec(
            select(VotingSessionBackend).where(VotingSessionBackend.id == session_id)).first()
        if voting_session is None:
            return Response(status_code=404)
        user_session = UserSession.get_active_session(session, user_id)
        if user_session is None:
            return Response(status_code=404)
        game: GameBackend | None = session.exec(select(GameBackend).where(GameBackend.id == game_id)).first()
        if game is None:
            return Response(status_code=404)
        if body not in [-1, 0, 1]:
            return Response(status_code=400)
        with session.begin(nested=True):
            voting_session.cast_vote(game_id, user_id, body, session)
            session.commit()
        handle_voting_session_update(request)
