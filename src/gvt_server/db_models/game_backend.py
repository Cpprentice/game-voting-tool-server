from typing import ClassVar

from sqlmodel import Field

from gvt_logic.util import UrlFactory
from gvt_server.models.game import Game


class GameBackend(Game, table=True):
    __tablename__ = 'game'

    id: str = Field(primary_key=True)
    cover_url: ClassVar[str | None]

    def get_game(self, url_factory: UrlFactory) -> Game:
        cover_url = str(url_factory.url_for("get_image", game_id=self.id))  # This gives you the full URI
        return Game(cover_url=cover_url, **self.model_dump())
