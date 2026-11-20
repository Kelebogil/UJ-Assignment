
import sqlite3
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "storage" / "fleet.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enforce relational database foreign keys
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


@contextmanager
def connection_scope():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialise_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with connection_scope() as connection:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)

    print("Database initialised successfully.")


if __name__ == "__main__":
    initialise_database()
