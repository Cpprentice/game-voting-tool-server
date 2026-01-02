import datetime

from alembic import op
import sqlalchemy as sa


def generate_table_backup(revision: str, table_name: str):
    bind = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=bind)
    backup_time = datetime.datetime.now()
    backup_time_string = backup_time.strftime('%Y-%m-%dT%H-%M-%S')

    table = metadata.tables.get(table_name)

    # If table exists and has data, dump it
    if table is not None:
        rows = bind.execute(sa.select(table)).fetchall()

        if rows:
            filename = f"backup_{table_name}_{revision}_{backup_time_string}.sql"
            with open(filename, "w") as f:
                for row in rows:
                    insert_sql = generate_insert_sql(table, row, bind)
                    f.write(insert_sql + ";\n")


def generate_insert_sql(table, row, bind):
    """Generate a literal INSERT statement for a single row."""
    row_data = row._asdict()
    for key, value in row_data.items():
        if isinstance(value, bytes):
            # row_data[key] = sa.func.UNHEX(value.hex())
            row_data[key] = sa.literal_column(f"x'{value.hex()}'")
    insert_stmt = table.insert().values(**row_data)
    compiled = insert_stmt.compile(
        bind=bind,
        compile_kwargs={"literal_binds": True}
    )
    return str(compiled)
