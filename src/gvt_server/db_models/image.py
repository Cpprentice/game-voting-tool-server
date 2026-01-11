from sqlmodel import SQLModel, Field


class Image(SQLModel, table=True):
    id: str = Field(primary_key=True, foreign_key='game.id')
    data: bytes = Field(nullable=False)
