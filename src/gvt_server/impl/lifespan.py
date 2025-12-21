import contextlib

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware


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

    @app.websocket('/ws')
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'Message text was: {data}')
