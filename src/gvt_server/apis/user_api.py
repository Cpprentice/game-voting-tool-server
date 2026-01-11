# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from gvt_server.apis.user_api_base import BaseUserApi
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

from gvt_db.db import SessionDependency

router = APIRouter()

ns_pkg = gvt_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/user/login",
    responses={
        200: {"model": str, "description": "successful operation"},
        400: {"description": "Userame already in use"},
    },
    tags=["user"],
    summary="Logs user into the system",
    response_model_by_alias=True,
)
async def login_user(
    request: Request,
    session: SessionDependency,
    body: Annotated[StrictStr, Field(description="Desired user name")] = Body(None, description="Desired user name"),
) -> str:
    """"""
    if not BaseUserApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserApi.subclasses[0]().login_user(request, session, body)
