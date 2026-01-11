import csv
import ctypes
import sys

from sqlmodel import Session, select

from gvt_db.db import get_session
from gvt_server.db_models import GameBackend, Image

MAX_SIGNED_LONG = (1 << (8 * ctypes.sizeof(ctypes.c_long) - 1)) - 1


def print_usage():
    print('Usage: extract-game-collection.exe <path-to-target-csv-file>')


def main():
    try:
        csv_file_path = sys.argv[1]
    except IndexError:
        print_usage()
        sys.exit(-1)

    session: Session = next(get_session())
    query_result = session.exec(select(GameBackend, Image).join(Image, GameBackend.id == Image.id)).all()

    csv_data = [
        dict(
            id=game.id,
            name=game.name,
            steam_appid=game.steam_appid,
            data=image.data.hex()
        )
        for game, image in query_result
    ]

    csv.field_size_limit(MAX_SIGNED_LONG)
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['id', 'name', 'steam_appid', 'data'])
        writer.writeheader()
        writer.writerows(csv_data)


if __name__ == '__main__':
    main()
