"""add reroll table

Revision ID: 03aa487d7edc
Revises: e434698de3c2
Create Date: 2026-01-20 00:41:21.297982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes as sm

from gvt_db.alembic_util import generate_table_backup


# revision identifiers, used by Alembic.
revision: str = '03aa487d7edc'
down_revision: Union[str, Sequence[str], None] = 'e434698de3c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'voting_session_reset',
        sa.Column('voting_session_id', sm.AutoString(), nullable=False),
        sa.Column('user_session_id', sm.AutoString(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_session_id'], ['user_session.id'], ),
        sa.ForeignKeyConstraint(['voting_session_id'], ['voting_session.id'], ),
        sa.PrimaryKeyConstraint('voting_session_id', 'user_session_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    generate_table_backup(revision, 'voting_session_reset')
    op.drop_table('voting_session_reset')
