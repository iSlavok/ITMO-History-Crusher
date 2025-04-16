import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SqlaSession

from bot.database import Base

engine = create_engine(os.getenv("DATABASE_URL"))

Session = sessionmaker(bind=engine)


def get_session() -> Generator[SqlaSession, None, None]:
    session: SqlaSession = Session()
    try:
        yield session
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(bind=engine)
