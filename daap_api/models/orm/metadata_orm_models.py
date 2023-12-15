from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from daap_api.db import Base


class Status(Enum):
    draft = "draft"
    published = "published"
    retired = "retired"


class SchemaTable(Base):
    __tablename__ = "schemas"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str]

    tableDescription: Mapped[str]

    columns: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        default=list,
    )

    def to_attributes(self):
        """
        Helper method for serializing API resources
        """
        return {
            "columns": self.columns,
            "name": self.name,
            "tableDescription": self.tableDescription,
        }


class DataProductTable(Base):
    __tablename__ = "dataproducts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        index=True,
        unique=True,
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

    def to_attributes(self):
        """
        Helper method for serializing API resources
        """
        return {
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
