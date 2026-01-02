"""create game and image table

Revision ID: 9d60762481a3
Revises: 
Create Date: 2025-12-23 15:48:27.512298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes as sm

from gvt_db.alembic_util import generate_table_backup

# revision identifiers, used by Alembic.
revision: str = '9d60762481a3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = 'main'
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'game',
        sa.Column('id', sm.AutoString(), primary_key=True),
        sa.Column('name', sm.AutoString(), nullable=False),
        sa.Column('steam_appid', sm.AutoString()),
    )
    op.create_table(
        'image',
        sa.Column('id', sm.AutoString(), primary_key=True),
        sa.Column('data', sa.BLOB, nullable=False),
        sa.ForeignKeyConstraint(['id'], ['game.id']),
    )


def downgrade():
    generate_table_backup(revision, 'image')
    op.drop_table('image')

    generate_table_backup(revision, 'game')
    op.drop_table("game")
