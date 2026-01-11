import json
import urllib.request
from typing import Optional

from fastapi import Request, Response
from pydantic import StrictStr
import sqlmodel
from sqlmodel import select, col

from gvt_server.apis.game_api_base import BaseGameApi
from gvt_server.db_models import GameBackend, Image
from gvt_server.models.game import Game


class GameApi(BaseGameApi):
    async def create_game(
        self,
        request: Request,
        session: sqlmodel.Session,
        game: Optional[Game],
    ) -> Game:
        """Add a new game from a data record"""

        game_backend = GameBackend(**game.model_dump())

        image_url = game.cover_url
        image_bytes = urllib.request.urlopen(image_url).read()
        image = Image(id=game.id, data=image_bytes)

        session.add(game_backend)
        session.add(image)

        return game_backend.get_game(request)

    async def create_game_from_steam(
        self,
        request: Request,
        session: sqlmodel.Session,
        body: Optional[StrictStr],
    ) -> Game | Response:
        """Scrapes the steam store for data"""

        api_response = urllib.request.urlopen(f'http://store.steampowered.com/api/appdetails?appids={body}')
        steam_data = json.loads(api_response.read())
        if body not in steam_data:
            return Response('Steam App ID not found', 400)
        steam_data = steam_data[body]['data']

        game = GameBackend(id=body, name=steam_data['name'], steam_appid=body)

        image_url = f'https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{body}/library_600x900.jpg'
        image_bytes = urllib.request.urlopen(image_url).read()
        image = Image(id=body, data=image_bytes)

        session.add(game)
        session.add(image)

        session.commit()
        return game.get_game(request)

    async def get_games(
        self,
        request: Request,
        session: sqlmodel.Session,
    ) -> list[Game]:
        """Receive game list"""
        backend_games: list[GameBackend] = session.exec(select(GameBackend).order_by(col(GameBackend.name))).all()
        games = [
            backend_game.get_game(request)
            for backend_game in backend_games
        ]
        return games
