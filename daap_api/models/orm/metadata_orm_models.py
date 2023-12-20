from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from daap_api.db import Base

from ..version import Version


class Status(Enum):
    draft = "draft"
    published = "published"
    retired = "retired"


class SchemaTable(Base):
    __tablename__ = "schemas"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    data_product_id: Mapped[int] = mapped_column(ForeignKey("data_products.id"))
    data_product: Mapped["DataProductTable"] = relationship(back_populates="schemas")

    name: Mapped[str] = mapped_column(
        index=True,
        unique=True,
    )

    tableDescription: Mapped[str]

    columns: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        default=list,
    )

    @property
    def external_id(self):
        return f"{self.data_product.external_id}:{self.name}"

    def to_attributes(self):
        """
        Helper method for serializing API resources
        """
        return {
            "id": self.external_id,
            "columns": self.columns,
            "name": self.name,
            "tableDescription": self.tableDescription,
        }

    def copy(self, **kwargs) -> SchemaTable:
        attributes = self.to_attributes()
        attributes.update(kwargs)
        return SchemaTable(**attributes)


class DataProductTable(Base):
    __tablename__ = "data_products"

    __table_args__ = (Index("name", "version", unique=True),)

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    schemas: Mapped[list["SchemaTable"]] = relationship(back_populates="data_product")

    name: Mapped[str] = mapped_column(
        index=True,
    )
    domain: Mapped[str]
    dataProductOwner: Mapped[str]
    dataProductOwnerDisplayName: Mapped[str]
    dataProductMaintainer: Mapped[Optional[str]]
    dataProductMaintainerDisplayName: Mapped[Optional[str]]
    status: Mapped[Status]
    email: Mapped[str]
    retentionPeriod: Mapped[int]
    dpiaRequired: Mapped[bool]
    dpiaLocation: Mapped[Optional[str]]
    lastUpdated: Mapped[Optional[datetime]]
    creationDate: Mapped[Optional[datetime]]
    s3Location: Mapped[Optional[str]]
    rowCount: Mapped[Optional[int]]

    version: Mapped[str] = mapped_column(default="v1.0")

    description: Mapped[str] = mapped_column(default="")
    tags: Mapped[dict[str, str]] = mapped_column(
        JSON,
        default=dict,
    )

    def next_major_version(self, **kwargs):
        version = str(Version.parse(self.version).increment_major())
        return self.copy(version=version, **kwargs)

    def next_minor_version(self, **kwargs):
        version = str(Version.parse(self.version).increment_minor())
        return self.copy(version=version, **kwargs)

    def copy(self, **kwargs) -> DataProductTable:
        columns = self.__table__.columns.keys()
        attributes = {k: getattr(self, k) for k in columns}
        del attributes["id"]
        attributes.update(kwargs)

        return DataProductTable(**attributes)

    @property
    def external_id(self):
        return f"dp:{self.name}:{self.version}"

    def to_attributes(self):
        """
        Helper method for serializing API resources
        """
        return {
            "id": self.external_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": self.status,
            "retentionPeriod": self.retentionPeriod,
            "dpiaRequired": self.dpiaRequired,
            "domain": self.domain,
            "dataProductOwner": self.dataProductOwner,
            "dataProductOwnerDisplayName": self.dataProductOwnerDisplayName,
            "email": self.email,
            "tags": self.tags,
            "dpiaLocation": self.dpiaLocation,
            "lastUpdated": self.lastUpdated,
            "s3Location": self.s3Location,
            "rowCount": self.rowCount,
        }
