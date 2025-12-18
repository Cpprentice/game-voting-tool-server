import sqlite3
from typing import Annotated

from fastapi import Request, Response
from pydantic import StrictStr, Field

from gv_server.apis.image_api_base import BaseImageApi


class ImageApi(BaseImageApi):
    async def get_image(
        self,
        request: Request,
        connection: sqlite3.Connection,
        game_id: Annotated[StrictStr, Field(description="ID of the game to get the image for")],
    ) -> None:
        """Receive the requested image from the database"""
        # connection = sqlite3.connect('database.db')
        image_cursor = connection.execute(f'SELECT Data FROM Image WHERE ID = "{game_id}"')
        try:
            image_bytes = list(image_cursor)[0][0]
            return Response(content=image_bytes, status_code=200, media_type='image/jpeg')
        except KeyError:
            return Response('Image not found', 404)
