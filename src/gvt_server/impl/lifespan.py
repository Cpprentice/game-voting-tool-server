import contextlib

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from gvt_db.db import database_startup, SessionDependency
from gvt_logic.user_session import handle_user_session
from gvt_logic.voting_session import create_new_voting_session
from gvt_server.models.backend import UserSession

origins = [
    "*"
]


# Theoretically, FastAPI supports the lifespan context manager, but that does not allow adding routes and middlewares,
#  because the app is already started. So this mimics this behavior at an earlier stage
def before_app_start(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.websocket('/ws/{user_id}')
    async def websocket_endpoint(websocket: WebSocket, session: SessionDependency, user_id: str):
        await websocket.accept()
        user = session.exec(select(UserSession).where(UserSession.id == user_id)).first()
        if user is None:
            await websocket.close(401, 'User session not recognized')
        else:
            await handle_user_session(websocket, user_id)
        # while True:
        #     data = await websocket.receive_text()
        #     await websocket.send_text(f'Message text was: {data}')

    database_startup()
    create_new_voting_session()
