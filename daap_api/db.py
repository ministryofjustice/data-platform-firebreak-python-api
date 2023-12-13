from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

connect_args = {"check_same_thread": False}
engine = create_engine(settings.database_uri, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    FastAPI dependency for the ORM session
    """
    with Session(engine) as session:
        yield session


session_dependency = Depends(get_session)
