from typing import Optional, Sequence

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased

from .metadata_orm_models import DataProductTable, SchemaTable


class DataProductRepository:
    IntegrityError = IntegrityError

    def __init__(self, session: Session):
        self.session = session

    def create(self, data_product: DataProductTable):
        """
        Attempt to save a data product to the database
        Raises IntegrityError if a unique constraint is violated.
        """
        self.session.add(data_product)
        self.session.commit()
        self.session.refresh(data_product)
        return data_product

    def fetch(self, name: str, version: str) -> Optional[DataProductTable]:
        """
        Load a data product by name and version
        """
        return self.session.execute(
            select(DataProductTable).filter_by(name=name, version=version)
        ).scalar()

    def fetch_latest(self, name: str) -> Optional[DataProductTable]:
        """
        Load the latest version of a data product by name
        """
        return self.session.execute(
            select(DataProductTable)
            .filter_by(name=name)
            .order_by(DataProductTable.version.desc())
            .limit(1)
        ).scalar()

    def list(self) -> Sequence[DataProductTable]:
        other = aliased(DataProductTable)
        subquery = (
            select(other.id)
            .where(other.name == DataProductTable.name)
            .where(other.version > DataProductTable.version)
        )
        return (
            self.session.execute(
                select(DataProductTable)
                .where(~exists(subquery))
                .order_by(DataProductTable.name)
            )
            .scalars()
            .fetchmany()
        )


class SchemaRepository:
    IntegrityError = IntegrityError

    def __init__(self, session: Session):
        self.session = session

    def create(self, schema: SchemaTable) -> SchemaTable:
        """
        Attempt to save a schema to the database
        Raises IntegrityError if a unique constraint is violated.
        """
        self.session.add(schema)
        self.session.commit()
        self.session.refresh(schema)
        return schema

    def fetch(
        self, data_product_name: str, version: str, table_name: str
    ) -> Optional[SchemaTable]:
        """
        Load a schema by data product name, version, and table name
        """
        return self.session.execute(
            select(SchemaTable)
            .join(DataProductTable)
            .where(SchemaTable.name == table_name)
            .where(DataProductTable.name == data_product_name)
            .where(DataProductTable.version == version)
        ).scalar()
