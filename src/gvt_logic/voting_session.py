import asyncio
import datetime
import uuid
from venv import create

from sqlmodel import select, Session

from gvt_db.db import get_session
from gvt_logic.connections import websocket_list
from gvt_logic.util import UrlFactory
from gvt_server.db_models import VotingSessionBackend
from gvt_server.models.game_votes import GameVotes
from gvt_server.models.voting_session import VotingSession


def create_new_voting_session():
    session = next(get_session())
    voting_session = VotingSessionBackend(id=uuid.uuid4().hex, start_time=datetime.datetime.now())
    session.add(voting_session)
    session.commit()


def get_active_voting_session_backend(session: Session) -> VotingSessionBackend:
    active_voting_session: VotingSessionBackend = session.exec(
        select(VotingSessionBackend)
        .order_by(VotingSessionBackend.start_time.desc())
        .limit(1)
    ).one()
    return active_voting_session
    # return active_voting_session.get_voting_session(url_factory, session)


def get_active_voting_session(url_factory: UrlFactory) -> VotingSession:
    session = next(get_session())
    return get_active_voting_session_backend(session).get_voting_session(url_factory, session)


async def _handle_voting_session_update(url_factory: UrlFactory):
    session = next(get_session())
    active_voting_session = get_active_voting_session_backend(session)
    if active_voting_session.is_resolved(session, url_factory):
        await broadcast_voting_state(active_voting_session.get_voting_session(url_factory, session))
        await broadcast_voting_result(active_voting_session.result(session, url_factory))
        session.close()
        create_new_voting_session()
        await broadcast_voting_state(get_active_voting_session(url_factory))
    else:
        await broadcast_voting_state(active_voting_session.get_voting_session(url_factory, session))


def handle_voting_session_update(url_factory: UrlFactory):
    asyncio.create_task(_handle_voting_session_update(url_factory))


async def broadcast_voting_state(state: VotingSession):
    await asyncio.gather(*(
        websocket.send_text(state.model_dump_json(by_alias=True))
        for websocket in websocket_list
    ))


async def broadcast_voting_result(result: list[GameVotes]):
    await asyncio.gather(*(
        websocket.send_json([
            game_votes.model_dump(by_alias=True)
            for game_votes in result
        ])
        for websocket in websocket_list
    ))
