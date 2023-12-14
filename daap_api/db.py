from typing import Generator

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

engine = create_engine(settings.database_uri, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for the ORM session
    """
    with Session(engine) as session:
        yield session


session_dependency = Depends(get_session)
