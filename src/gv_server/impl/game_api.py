import json
import sqlite3
import urllib.request
from typing import Optional, List

import fake_useragent
from bs4 import BeautifulSoup
from fastapi import Request, Response
from pydantic import StrictStr

from gv_server.apis.game_api_base import BaseGameApi
from gv_server.models.game import Game
from gv_server.db import gv_select, gv_insert


class GameApi(BaseGameApi):
    async def create_game(
        self,
        request: Request,
        connection: sqlite3.Connection,
        game: Optional[Game],
    ) -> Game:
        """Add a new game from a data record"""
        connection = sqlite3.connect('database.db')
        inserted_game = gv_insert(game, connection)

        image_url = game.cover
        image_bytes = urllib.request.urlopen(image_url).read()

        with connection:
            connection.execute('INSERT INTO Image (ID, Data) VALUES (?, ?);', (game.id, image_bytes))
        connection.close()
        return inserted_game


    async def create_game_from_steam(
        self,
        request: Request,
        connection: sqlite3.Connection,
        body: Optional[StrictStr],
    ) -> Game:
        """Scrapes the steam store for data"""

        api_response = urllib.request.urlopen(f'http://store.steampowered.com/api/appdetails?appids={body}')
        steam_data = json.loads(api_response.read())
        if body not in steam_data:
            return Response('Steam App ID not found', 400)
        steam_data = steam_data[body]['data']
        new_game = Game(
            ID=body,
            name=steam_data['name'],
            cover='',
            genre=[x['description'] for x in steam_data['genres']],
            mp="yes",
            type="Base",
            toplevel="yes",
            meta=[],
            parent=None,
            children=[],
            steam_appid=body,
            detailed_description=steam_data['about_the_game'],
            description=steam_data['short_description'],
            categories=[x['description'] for x in steam_data['categories']],
            release_date=None,  # steam_data['release_date']['date'],
            readme=steam_data['about_the_game']
        )
        connection = sqlite3.connect('database.db')
        inserted_game = gv_insert(new_game, connection)

        # # scrape image
        # ua = fake_useragent.UserAgent()
        # request = urllib.request.Request(f'https://steamdb.info/app/{body}/info/')
        # request.add_header('User-Agent', ua.chrome)
        # steamdb_response = urllib.request.urlopen(request)
        # soup = BeautifulSoup(steamdb_response.read(), 'html.parser')
        # image_links = soup.find_all('a', class_='image-hover')
        # _ = 42
        image_url = f'https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{body}/library_600x900.jpg'
        image_bytes = urllib.request.urlopen(image_url).read()

        with connection:
            connection.execute('INSERT INTO Image (ID, Data) VALUES (?, ?);', (body, image_bytes))
        connection.close()
        return inserted_game




    async def get_games(
        self,
        request: Request,
        connection: sqlite3.Connection,
    ) -> List[Game]:
        """Receive game list"""
        connection = sqlite3.connect('database.db')
        games = gv_select(Game, connection)

        for game in games:
            image_url = str(request.url_for("get_image", game_id=game.id))  # This gives you the full URL
            game.cover = image_url

        _ = 42
        connection.close()
        return games
