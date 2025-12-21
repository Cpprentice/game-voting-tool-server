# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from gvt_server.apis.image_api_base import BaseImageApi
import gvt_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
    Request
)

from gvt_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated

from gvt_db.db import get_connection

router = APIRouter()

ns_pkg = gvt_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/images/{game_id}",
    responses={
        200: {"description": "successful operation"},
        404: {"description": "not found"},
    },
    tags=["image"],
    summary="Get a certain image",
    response_model_by_alias=True,
)
async def get_image(
    request: Request,
    connection = Depends(get_connection),
    game_id: Annotated[StrictStr, Field(description="ID of the game to get the image for")] = Path(..., description="ID of the game to get the image for"),
) -> None:
    """Receive the requested image from the database"""
    if not BaseImageApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseImageApi.subclasses[0]().get_image(request, connection, game_id)
