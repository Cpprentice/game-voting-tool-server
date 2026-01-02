from alembic import context
from sqlalchemy import engine_from_config, pool
import sqlmodel

import gvt_server.models.backend
from gvt_db.db import alembic_config

# config = context.config
config = alembic_config
target_metadata = sqlmodel.SQLModel.metadata  # your SQLAlchemy metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    engine = config.attributes['engine']

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
