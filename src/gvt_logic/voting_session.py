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
from gvt_server.models.voting_cancellation_message import VotingCancellationMessage
from gvt_server.models.voting_result_message import VotingResultMessage
from gvt_server.models.voting_session import VotingSession
from gvt_server.models.voting_session_message import VotingSessionMessage
from gvt_server.models.websocket_message_type import WebsocketMessageType


def create_new_voting_session():
    session = next(get_session())
    voting_session = VotingSessionBackend(id=uuid.uuid4().hex, start_time=datetime.datetime.now())
    session.add(voting_session)
    session.commit()


def close_active_voting_session(was_cancelled: bool, session: Session):
    voting_session = get_active_voting_session_backend(session)
    now = datetime.datetime.now()
    if was_cancelled:
        voting_session.cancel_time = now
    else:
        voting_session.finish_time = now
    session.add(voting_session)


def get_active_voting_session_backend(session: Session) -> VotingSessionBackend:
    active_voting_session: VotingSessionBackend = session.exec(
        select(VotingSessionBackend)
        .order_by(VotingSessionBackend.start_time.desc())
        .limit(1)
    ).one()
    return active_voting_session
    # return active_voting_session.get_voting_session(url_factory, session)


def get_active_voting_session(url_factory: UrlFactory) -> VotingSessionMessage:
    session = next(get_session())
    return get_active_voting_session_backend(session).get_voting_session(url_factory, session)


async def _handle_voting_session_update(url_factory: UrlFactory):
    session = next(get_session())
    active_voting_session = get_active_voting_session_backend(session)
    active_voting_session_frontend_message = active_voting_session.get_voting_session(url_factory, session)
    if active_voting_session.is_resolved(session, url_factory):
        await broadcast_voting_state(active_voting_session_frontend_message)
        await broadcast_voting_result(active_voting_session.result(session, url_factory))
        close_active_voting_session(False, session)
        session.close()
        create_new_voting_session()
        await broadcast_voting_state(get_active_voting_session(url_factory))
    elif active_voting_session.needs_reset(session):
        cancellation_message = VotingCancellationMessage(
            type=WebsocketMessageType.CANCELLATION,
            body=active_voting_session_frontend_message.body.reset_votes
        )
        close_active_voting_session(True, session)
        session.close()
        await broadcast_voting_cancellation(cancellation_message)
        create_new_voting_session()
        await broadcast_voting_state(get_active_voting_session(url_factory))
    else:
        await broadcast_voting_state(active_voting_session.get_voting_session(url_factory, session))


def handle_voting_session_update(url_factory: UrlFactory):
    asyncio.create_task(_handle_voting_session_update(url_factory))


async def broadcast_voting_state(state: VotingSessionMessage):
    dump = state.model_dump_json(by_alias=True)
    await asyncio.gather(*(
        websocket.send_text(dump)
        for websocket in websocket_list
    ))

async def broadcast_voting_result(result: VotingResultMessage):
    dump = result.model_dump_json(by_alias=True)
    await asyncio.gather(*(
        websocket.send_text(dump)
        for websocket in websocket_list
    ))

async def broadcast_voting_cancellation(cancellation: VotingCancellationMessage):
    dump = cancellation.model_dump_json(by_alias=True)
    await asyncio.gather(*(
        websocket.send_text(dump)
        for websocket in websocket_list
    ))
