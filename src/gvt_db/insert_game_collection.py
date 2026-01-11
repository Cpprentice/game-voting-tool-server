import csv
import ctypes
import sys

from sqlmodel import Session, select

from gvt_db.db import get_session
from gvt_server.db_models import GameBackend, Image

MAX_SIGNED_LONG = (1 << (8 * ctypes.sizeof(ctypes.c_long) - 1)) - 1


def print_usage():
    print('Usage: insert-game-collection.exe <path-to-csv-file-with-data>')
    print('The CSV file must have an "id" and "name" column')


def main():
    try:
        csv_file_path = sys.argv[1]
    except IndexError:
        print_usage()
        sys.exit(-1)

    csv.field_size_limit(MAX_SIGNED_LONG)
    with open(csv_file_path, 'r', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        data = list(reader)
    session: Session = next(get_session())
    for game in data:
        game_object = session.exec(select(GameBackend).where(GameBackend.id == game['id'])).first()
        if game_object is None:
            game_object = GameBackend(**game)
            session.add(game_object)
        if 'data' in game:
            image_object = session.exec(select(Image).where(Image.id == game['id'])).first()
            if image_object is None:
                image = bytes.fromhex(game['data'])
                image_object = Image(id=game_object.id, data=image)
                session.add(image_object)
    session.commit()


if __name__ == '__main__':
    main()
