from typing import Annotated

from fastapi import Request, Response
from pydantic import StrictStr
from sqlmodel import Session, Field, select

from gvt_server.apis.voting_api_base import BaseVotingApi
from gvt_server.models.backend import VotingSessionBackend, GameBackend


class VotingApi(BaseVotingApi):
    async def add_game_to_voting(
            self,
            request: Request,
            session: Session,
            session_id: Annotated[StrictStr, Field(description="the ID of the session to add the game to")],
            game_id: Annotated[StrictStr, Field(description="ID of the game to add to the voting")],
    ) -> None:
        voting_session = session.exec(select(VotingSessionBackend).where(VotingSessionBackend.id == session_id)).first()
        if voting_session is None:
            return Response(status_code=404)
        game = session.exec(select(GameBackend).where(GameBackend.id == game_id)).first()
        if game is None:
            return Response(status_code=404)
        with session.begin():
            if not voting_session.try_to_add_game(game_id):
                return Response(status_code=400)
            session.add(voting_session)
            session.commit()

