from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app import config


def make_engine(url: str):
    db_engine = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(db_engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return db_engine


engine = make_engine(config.DATABASE_URL)


def create_tables(db_engine=engine) -> None:
    from app import models  # noqa: F401  (registers the tables)

    SQLModel.metadata.create_all(db_engine)


def get_session():
    with Session(engine) as session:
        yield session
