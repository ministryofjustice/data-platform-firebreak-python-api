from typing import Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


from .config import settings

engine = create_engine(settings.database_uri, echo=True)


def create_db_and_tables():
    Base.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for the ORM session
    """
    with Session(engine) as session:
        yield session


session_dependency = Depends(get_session)
