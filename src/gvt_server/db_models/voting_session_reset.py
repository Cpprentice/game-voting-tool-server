from sqlmodel import SQLModel, Field, Relationship

from gvt_server.db_models.user_session import UserSession


class VotingSessionReset(SQLModel, table=True):
    __tablename__ = 'voting_session_reset'

    voting_session_id: str = Field(primary_key=True, foreign_key='voting_session.id')
    user_session_id: str = Field(primary_key=True, foreign_key='user_session.id')
    value: int = Field(nullable=False, ge=0, le=1)

    voting_session: "VotingSessionBackend" = Relationship(back_populates='session_reset_votes')
    user_session: UserSession = Relationship()
