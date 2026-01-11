from sqlmodel import SQLModel, Field, Relationship

from gvt_server.db_models.game_backend import GameBackend
from gvt_server.db_models.user_session import UserSession


class VotingSessionUserVote(SQLModel, table=True):
    __tablename__ = 'voting_session_user_vote'
    voting_session_id: str = Field(primary_key=True, foreign_key='voting_session.id')
    user_session_id: str = Field(primary_key=True, foreign_key='user_session.id')
    game_id: str = Field(primary_key=True, foreign_key='game.id')
    value: int = Field(nullable=False, ge=-1, le=1)

    voting_session: "VotingSessionBackend" = Relationship(back_populates='session_user_votes')
    user_session: UserSession = Relationship()
    game: GameBackend = Relationship()
