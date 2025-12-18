import _thread
import datetime
import functools
import json
import sqlite3

from pydantic import BaseModel
# from sqlalchemy import Engine, text

# from gv_server.models.game import Game

# from sqlmodel import SQLModel, create_engine, Session
# from sqlalchemy import select

class DBConnection:
    def __init__(self):
        self.raw_connection

def get_connection() -> sqlite3.Connection:
    thread_id = _thread.get_ident()
    if thread_id in get_connection.storage:
        return get_connection.storage[thread_id]
    if len(get_connection.storage) == 0:
        get_connection.storage[thread_id] = create_database()
    else:
        get_connection.storage[thread_id] = sqlite3.connect('database.db')
    return get_connection.storage[thread_id]


get_connection.storage = {}


def create_database() -> sqlite3.Connection:
    # engine = sqlite3.connect("sqlite:///database.db")
    engine = sqlite3.connect("database.db")

    with engine:
        engine.execute('CREATE TABLE IF NOT EXISTS migrations (source_date TEXT PRIMARY KEY, applied_date TEXT NOT NULL);')

    def migrate(source_date: str):
        _ = 42
        def decorator(func):
            _ = 42
            def wrapper():
                _ = 42
                try:
                    cursor = engine.execute(f'SELECT * FROM migrations WHERE source_date = "{source_date}"')
                    if len(list(cursor)) != 0:
                        return
                    with engine:
                        engine.execute('BEGIN')
                        func(engine)
                        engine.execute('COMMIT')
                    with engine:
                        engine.execute(f'INSERT INTO migrations (source_date, applied_date) '
                                       f'VALUES ("{source_date}", "{datetime.datetime.now().isoformat()}")')
                except Exception as e:
                    raise e

            wrapper()
            # return wrapper
        return decorator

    @migrate('2025-01-03 06:31:00')
    def create_game_and_image_table(db: sqlite3.Connection):
        db.execute('CREATE TABLE Game ('
                   'ID TEXT PRIMARY KEY, '
                   'Name TEXT NOT NULL, '
                   'Cover TEXT NOT NULL, '
                   'SteamAppid TEXT, '
                   'detailed_description TEXT, '
                   'description TEXT, '
                   'release_date TEXT, '
                   'Genre JSONB NOT NULL, '
                   'MP TEXT NOT NULL, '
                   'Type TEXT NOT NULL, '
                   'Toplevel TEXT NOT NULL, '
                   'Meta JSONB NOT NULL, '
                   'Parent TEXT, '
                   'Children JSONB NOT NULL, '
                   'Readme TEXT, '
                   'categories JSONB, '
                   'genres JSONB'
                   ')')

        db.execute('CREATE TABLE Image ('
                   'ID TEXT PRIMARY KEY, '
                   'Data BLOB NOT NULL'
                   ')')

    # @migrate('2025-01-02 00:58:00')
    # def insert_some_test_games(db: sqlite3.Connection):
    #     db.execute('INSERT INTO Game (id, name, image) VALUES '
    #                '("eat", "eat", "url://"), '
    #                '("sleep", "sleep", "url://"), '
    #                '("game", "game", "url://"), '
    #                '("repeat", "repeat", "url://")'
    #                ';')
    # SQLModel.metadata.create_all(engine)

    # with Session(engine) as session:
    #     statement = select(Game)  # .where(Game.name == "Spider-Boy")
    #     test = session.exec(statement).first()
    #     print(test)

    @migrate('2025-09-07 21:10:00')
    def create_active_user_session_table(db: sqlite3.Connection):
        db.execute(
            'CREATE TABLE user_session ('
            'user_name TEXT PRIMARY KEY NOT NULL, '
            'login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ')'
        )

    @migrate('2025-09-07 21:20:00')
    def create_lan_party_table(db: sqlite3.Connection):
        db.execute(
            'CREATE TABLE lan_party ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'starting_date DATE NOT NULL'
            ')'
        )

    @migrate('2025-09-07 21:30:00')
    def create_active_voting_session_table(db: sqlite3.Connection):

        db.execute(
            'CREATE TABLE voting_session_games ('
            'game_id TEXT PRIMARY KEY, '
            'FOREIGN KEY (game_id) REFERENCES Game(ID) ON DELETE CASCADE'
            ')'
        )

        db.execute(
            'CREATE TABLE voting_session_user_votes ('
            'game_id TEXT NOT NULL, '
            'user_name TEXT NOT NULL, '
            'vote INTEGER, '
            'PRIMARY KEY (game_id, user_name), '
            'FOREIGN KEY (game_id) REFERENCES voting_session_games(game_id) ON DELETE CASCADE, '
            'FOREIGN KEY (user_name) REFERENCES user_session(user_name) ON DELETE CASCADE'
            ')'
        )

        db.execute(
            'CREATE VIEW voting_session_status ('
            'game_id, up_votes, down_votes, user_count'
            ') AS SELECT '
            'g.game_id, '
            'SUM(CASE WHEN uv.vote = 1 THEN 1 ELSE 0 END), '
            'SUM(CASE WHEN uv.vote = -1 THEN 1 ELSE 0 END), '
            '(SELECT COUNT(*) FROM user_session) '
            'FROM voting_session_games g '
            'LEFT JOIN voting_session_user_votes uv '
            'ON uv.game_id = g.game_id '
            'GROUP BY g.game_id;'
        )

    # @migrate('2025-09-07 21:40:00')
    # def create_voting_history

    return engine


def gv_reset_voting_state(engine: sqlite3.Connection):
    engine.execute('DELETE FROM voting_session_games;')

def reset_user_sessions(engine: sqlite3.Connection):
    engine.execute('DELETE FROM user_session;')


def gv_insert(obj: BaseModel, engine: sqlite3.Connection) -> BaseModel:

    def convert_value(x):
        try:
            if isinstance(x, (str, int, float)) or x is None:
                return json.dumps(x).replace('\\"', '""')
            elif isinstance(x, (list, dict)):
                return json.dumps(json.dumps(x)).replace('\\"', '""')
            else:
                raise NotImplemented('non supported serialization')
        except Exception as e:
            return x
    try:
        data = obj.model_dump(by_alias=True)
        with engine:
            keys = data.keys()
            fields_string = ', '.join(keys)
            converted_values = [convert_value(x) for x in data.values()]
            values_string = ', '.join(converted_values)
            sql_string = f'INSERT INTO {obj.__class__.__name__} ({fields_string}) VALUES ({values_string})'
            insert_response = engine.execute(sql_string)
    except Exception as e:
        raise e
    return obj


def gv_select(_class: type, engine: sqlite3.Connection) -> list[BaseModel]:
    # with Session(engine) as session:
    cursor = engine.execute(f'SELECT * FROM {_class.__name__}')
    # response = session.exec(text(f'SELECT * FROM {_class.__name__}'))

    def convert_value(x):
        try:
            y = json.loads(x)
            if isinstance(y, int) and isinstance(x, str):
                return x
            return y
        except:
            return x

    return [
        _class(**dict(zip([x[0] for x in cursor.description], [convert_value(y) for y in row])))
        for row in cursor
    ]
    _ = 42
