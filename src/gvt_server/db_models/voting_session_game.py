from sqlmodel import SQLModel, Field, Relationship

from gvt_server.db_models.game_backend import GameBackend
from gvt_server.db_models.user_session import UserSession


class VotingSessionGame(SQLModel, table=True):
    __tablename__ = 'voting_session_game'

    voting_session_id: str = Field(primary_key=True, foreign_key='voting_session.id')
    user_session_id: str = Field(primary_key=True, foreign_key='user_session.id')
    game_id: str = Field(primary_key=True, foreign_key='game.id')

    voting_session: "VotingSessionBackend" = Relationship(back_populates='session_games')
    game: GameBackend = Relationship()
    user_session: UserSession = Relationship()
