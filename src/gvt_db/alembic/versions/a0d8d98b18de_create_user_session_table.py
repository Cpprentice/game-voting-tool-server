"""create user session table

Revision ID: a0d8d98b18de
Revises: e434698de3c2
Create Date: 2026-01-02 00:46:13.973301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes as sm

from gvt_db.alembic_util import generate_table_backup


# revision identifiers, used by Alembic.
revision: str = 'a0d8d98b18de'
down_revision: Union[str, Sequence[str], None] = '9d60762481a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_session',
        sa.Column('id', sm.AutoString(), primary_key=True),
        sa.Column('user_name', sm.AutoString(), nullable=False),
        sa.Column('login_time', sa.DateTime, nullable=False),
        sa.Column('last_alive_time', sa.DateTime, nullable=False),
        sa.Column('logout_time', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    generate_table_backup(revision, 'user_session')
    op.drop_table('user_session')
