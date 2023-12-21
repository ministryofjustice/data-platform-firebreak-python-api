from typing import Optional, Sequence

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased

from .metadata_orm_models import DataProductTable, DataProductVersionTable, SchemaTable


class DataProductRepository:
    IntegrityError = IntegrityError

    def __init__(self, session: Session):
        self.session = session

    def create(self, data_product_version: DataProductVersionTable):
        """
        Attempt to create an initial version of a data product.
        Raises IntegrityError if a unique constraint is violated.
        """
        self.session.add(data_product_version)
        data_product = DataProductTable(
            current_version=data_product_version, name=data_product_version.name
        )
        self.session.add(data_product)
        self.session.commit()
        self.session.refresh(data_product_version)
        return data_product_version

    def update(
        self, data_product: DataProductTable, new_version: DataProductVersionTable
    ):
        """
        Update a data product to a new version
        """
        data_product.current_version = new_version
        self.session.add(new_version)
        self.session.add(
            data_product,
        )

        self.session.commit()
        self.session.refresh(new_version)
        return new_version

    def fetch(self, name: str, version: str) -> Optional[DataProductVersionTable]:
        """
        Load a data product by name and version
        """
        return self.session.execute(
            select(DataProductVersionTable).filter_by(name=name, version=version)
        ).scalar()

    def fetch_latest(self, name: str) -> Optional[DataProductVersionTable]:
        """
        Load the latest version of a data product by name
        """
        return self.session.execute(
            select(DataProductVersionTable, DataProductVersionTable.data_product)
            .select_from(DataProductTable)
            .join(DataProductVersionTable, DataProductTable.current_version)
            .filter_by(name=name)
        ).scalar()

    def list(self) -> Sequence[DataProductVersionTable]:
        return (
            self.session.execute(
                select(DataProductVersionTable)
                .select_from(DataProductTable)
                .join(DataProductVersionTable, DataProductTable.current_version)
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
            .join(DataProductVersionTable, SchemaTable.data_product_version)
            .where(SchemaTable.name == table_name)
            .where(DataProductVersionTable.name == data_product_name)
            .where(DataProductVersionTable.version == version)
        ).scalar()
