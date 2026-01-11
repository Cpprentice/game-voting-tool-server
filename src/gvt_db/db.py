from pathlib import Path
from typing import Annotated

from alembic import command
from alembic.autogenerate import compare_metadata, produce_migrations, render_op_text
from alembic.autogenerate.api import AutogenContext
from alembic.autogenerate.render import render_op
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel

import gvt_server.db_models


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

alembic_config = Config()
script_location = (Path(__file__).parent / 'alembic').as_posix()
alembic_config.set_main_option("script_location", script_location)
alembic_config.set_main_option("sqlalchemy.url", sqlite_url)
alembic_config.attributes['engine'] = engine
# script_directory = ScriptDirectory.from_config(alembic_config)
# alembic_context = EnvironmentContext(alembic_config, script_directory)

def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]


def force_logout_dangling_user_sessions():
    session = next(get_session())
    dangling_sessions = gvt_server.db_models.UserSession.get_active_sessions(session)

    for dangling_session in dangling_sessions:
        dangling_session.logout_time = dangling_session.last_alive_time
        session.add(dangling_session)
    session.commit()


def database_startup():
    if not schema_is_up_to_date():
        msg = 'Schema does not match'
        print(msg)
        run_migrations()
        # raise RuntimeError(msg)


def run_migrations():
    # Run upgrade
    command.upgrade(alembic_config, "head")


def schema_is_up_to_date() -> bool:
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        diffs = compare_metadata(context, SQLModel.metadata)

        diff_ops = produce_migrations(context, SQLModel.metadata)
        gen_context = AutogenContext(context, SQLModel.metadata, {
            'alembic_module_prefix': '',
            'sqlalchemy_module_prefix': '',
            'user_module_prefix': ''
        })

        sql_statements = [render_op_text(gen_context, op) for op in diff_ops.upgrade_ops.ops]
        return len(diffs) == 0
