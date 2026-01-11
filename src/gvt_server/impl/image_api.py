from typing import Annotated

from fastapi import Request, Response
from pydantic import StrictStr, Field
from sqlmodel import Session, select

from gvt_server.apis.image_api_base import BaseImageApi
from gvt_server.db_models import Image


class ImageApi(BaseImageApi):
    async def get_image(
        self,
        request: Request,
        session: Session,
        game_id: Annotated[StrictStr, Field(description="ID of the game to get the image for")],
    ) -> None:
        """Receive the requested image from the database"""
        image = session.exec(select(Image).where(Image.id == game_id)).first()
        if image is None:
            return Response('Image not found', 404)
        return Response(content=image.data, status_code=200, media_type='image/jpeg')
