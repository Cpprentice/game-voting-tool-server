# This contains modified classes for backend usage
from datetime import datetime
from typing import ClassVar, Callable

from fastapi import Request
from pydantic import model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlmodel import Field, SQLModel, Session, select

from gvt_server.models.game import Game
from gvt_server.models.voting_session import VotingSession


def get_cover_url(self: Game, request: Request) -> str:
    return str(request.url_for('get_image', game_id=self.id))


class GameBackend(Game, table=True):
    __tablename__ = 'game'
    id: str = Field(primary_key=True)
    cover_url: ClassVar[str | None]
    # cover_url: ClassVar[str | None] = hybrid_property(lambda self: f'http://myserver:8000/images/{self.game_id}')
    # cover_url: ClassVar[Callable] = hybrid_method(get_cover_url)

    # @model_serializer(mode='wrap')
    # def serialize_model(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
    #     _ = handler.context
    #     serialized = handler(self)
    #     serialized['cover_url'] = self.cover_url
    #     return serialized

    def get_game(self, request: Request) -> Game:
        cover_url = str(request.url_for("get_image", game_id=self.id))  # This gives you the full URI
        return Game(cover_url=cover_url, **self.model_dump())


class Image(SQLModel, table=True):
    id: str = Field(primary_key=True, foreign_key='game.id')
    data: bytes = Field(nullable=False)


class UserSession(SQLModel, table=True):
    __tablename__ = 'user_session'
    id: str = Field(primary_key=True)
    user_name: str = Field(nullable=False)
    login_time: datetime = Field(nullable=False)
    logout_time: datetime = Field(nullable=True)


class Vote(SQLModel, table=True):
    voting_session_id: str = Field(primary_key=True, foreign_key='voting_session.id')
    user_session_id: str = Field(primary_key=True, foreign_key='user_session.id')
    game_id: str = Field(primary_key=True, foreign_key='game.id')
    value: int = Field(nullable=False, ge=-1, le=1)


class VotingSessionBackend(VotingSession, table=True):
    __tablename__ = 'voting_session'
    id: str = Field(primary_key=True)
    games: ClassVar[list[Game]]
    game_id_1: str | None = Field(nullable=True)
    game_id_2: str | None = Field(nullable=True)
    game_id_3: str | None = Field(nullable=True)
    game_id_4: str | None = Field(nullable=True)
    game_id_5: str | None = Field(nullable=True)
    game_id_6: str | None = Field(nullable=True)

    @property
    def game_ids(self) -> list[str]:
        return [
            game_id
            for game_id in [
                self.game_id_1,
                self.game_id_2,
                self.game_id_3,
                self.game_id_4,
                self.game_id_5,
                self.game_id_6,
            ]
            if game_id is not None and not game_id == ''
        ]

    def get_voting_session(self, request: Request, session: Session) -> VotingSession:
        games = [
            game
            for game in session.exec(
                select(GameBackend).where(GameBackend.id in self.game_ids)
            ).all()
        ]
        return VotingSession(games=games, **self.model_dump())

    def try_to_add_game(self, game_id: str) -> bool:
        def is_value_set(game: str | None) -> bool:
            return game is not None and not game == ''

        status = True
        if not is_value_set(self.game_id_1):
            self.game_id_1 = game_id
        elif not is_value_set(self.game_id_2):
            self.game_id_2 = game_id
        elif not is_value_set(self.game_id_3):
            self.game_id_3 = game_id
        elif not is_value_set(self.game_id_4):
            self.game_id_4 = game_id
        elif not is_value_set(self.game_id_5):
            self.game_id_5 = game_id
        elif not is_value_set(self.game_id_6):
            self.game_id_6 = game_id
        else:
            status = False
        return status

