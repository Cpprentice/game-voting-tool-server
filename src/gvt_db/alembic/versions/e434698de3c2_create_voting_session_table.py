"""create voting session table

Revision ID: e434698de3c2
Revises: 9d60762481a3
Create Date: 2026-01-01 20:10:17.651088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel as sm

from gvt_db.alembic_util import generate_table_backup


# revision identifiers, used by Alembic.
revision: str = 'e434698de3c2'
down_revision: Union[str, Sequence[str], None] = 'a0d8d98b18de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'voting_session',
        sa.Column('id', sm.AutoString(), primary_key=True),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('game_id_1', sm.AutoString(), nullable=True),
        sa.Column('game_id_2', sm.AutoString(), nullable=True),
        sa.Column('game_id_3', sm.AutoString(), nullable=True),
        sa.Column('game_id_4', sm.AutoString(), nullable=True),
        sa.Column('game_id_5', sm.AutoString(), nullable=True),
        sa.Column('game_id_6', sm.AutoString(), nullable=True),
    )

    op.create_table(
        'vote',
        sa.Column('voting_session_id', sm.AutoString(), primary_key=True),
        sa.Column('user_session_id', sm.AutoString(), primary_key=True),
        sa.Column('game_id', sm.AutoString(), primary_key=True),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['voting_session_id'], ['voting_session.id']),
        sa.ForeignKeyConstraint(['user_session_id'], ['user_session.id']),
        sa.ForeignKeyConstraint(['game_id'], ['game.id']),
    )


def downgrade() -> None:
    """Downgrade schema."""
    generate_table_backup(revision, 'vote')
    op.drop_table('vote')

    generate_table_backup(revision, 'voting_session')
    op.drop_table('voting_session')
