from typing import Generator, Self

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    def changed_fields(self, other: Self):
        result = set()

        for column in self.__table__.columns:
            if column.primary_key or column.foreign_keys:
                continue
            a_value = getattr(self, column.name)
            b_value = getattr(other, column.name)
            if a_value is None and b_value is None:
                continue
            if a_value != b_value:
                result.add(column.name)

        return result


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
