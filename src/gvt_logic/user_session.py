import asyncio
import datetime

from fastapi import WebSocket
from sqlmodel import select
from starlette.websockets import WebSocketState

from gvt_db.db import get_session
from gvt_logic.connections import websocket_list
from gvt_logic.voting_session import get_active_voting_session, handle_voting_session_update
from gvt_server.db_models import UserSession
from gvt_server.models.voting_session_message import VotingSessionMessage
from gvt_server.models.websocket_message import WebsocketMessage


def close_user_session(user_id: str):
    session = next(get_session())
    user_session = session.exec(select(UserSession).where(UserSession.id == user_id)).one()
    user_session.logout_time = datetime.datetime.now()
    session.add(user_session)
    session.commit()
    session.close()


async def ping_listener(websocket: WebSocket, user_id: str):
    try:
        while True:
            text = await websocket.receive_json()
            session = next(get_session())
            user_session = session.exec(select(UserSession).where(UserSession.id == user_id)).one()
            user_session.last_alive_time = datetime.datetime.now()
            session.add(user_session)
            session.commit()
            session.close()
    except Exception as e:
        _ = 42
        print(f'ping_listener exception: {e}')
        close_user_session(user_id)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        if websocket in websocket_list:
            websocket_list.remove(websocket)
        if len(websocket_list) > 0:
            handle_voting_session_update(websocket_list[0])


async def ping_loop(websocket: WebSocket, user_id: str):
    try:
        while True:
            await asyncio.sleep(5)
            await websocket.send_json('ping')
    except Exception as e:
        print(f'ping_loop exception: {e}')
        close_user_session(user_id)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        if websocket in websocket_list:
            websocket_list.remove(websocket)
        if len(websocket_list) > 0:
            handle_voting_session_update(websocket_list[0])


async def handle_user_session(websocket: WebSocket, user_id: str):
    websocket_list.append(websocket)
    try:
        active_session = get_active_voting_session(websocket)
        active_session_string = active_session.model_dump_json(by_alias=True)
        await websocket.send_text(active_session_string)
    except Exception as e:
        print(f'Failed to send initial session state: {e}')
        close_user_session(user_id)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        if websocket in websocket_list:
            websocket_list.remove(websocket)
        return
    ping_task = asyncio.create_task(ping_loop(websocket, user_id))
    await ping_listener(websocket, user_id)
    ping_task.cancel()
