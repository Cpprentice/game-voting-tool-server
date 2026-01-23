from datetime import datetime
from typing import Self

from sqlmodel import SQLModel, Field, Session, select


class UserSession(SQLModel, table=True):
    __tablename__ = 'user_session'

    id: str = Field(primary_key=True)
    user_name: str = Field(nullable=False)
    login_time: datetime = Field(nullable=False)
    last_alive_time: datetime = Field(nullable=False)
    logout_time: datetime = Field(nullable=True)

    @classmethod
    def get_active_sessions(cls, db_session: Session) -> list[Self]:
        return db_session.exec(select(cls).where(cls.logout_time.is_(None))).all()

    @classmethod
    def get_active_session(cls, db_session: Session, user_id: str) -> Self | None:
        return db_session.exec(select(cls).where(cls.logout_time.is_(None)).where(cls.id == user_id)).first()

    @classmethod
    def get_active_session_count(cls, db_session: Session) -> int:
        # db_session.exec(text('SELECT count(*) FROM user_session WHERE logout_time IS NULL')).scalar_one()
        # db_session.exec(select(cls).where(cls.logout_time.is_(None)).count()).scalar_one()
        return len(cls.get_active_sessions(db_session))

    @classmethod
    def get_active_session_ids(cls, db_session: Session) -> set[str]:
        return {
            user.id
            for user in cls.get_active_sessions(db_session)
        }