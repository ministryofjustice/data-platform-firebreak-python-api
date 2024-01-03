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
    __table_args__ = (
        Index(
            "ix_schemas_name_data_product_id", "name", "data_product_id", unique=True
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    data_product_id: Mapped[int] = mapped_column(ForeignKey("data_product_versions.id"))
    data_product_version: Mapped["DataProductVersionTable"] = relationship(
        back_populates="schemas"
    )

    name: Mapped[str] = mapped_column(index=True)

    table_description: Mapped[str]

    columns: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        default=list,
    )

    @property
    def external_id(self):
        return f"{self.data_product_version.external_id}:{self.name}"

    def to_attributes(self):
        """
        Helper method for serializing API resources
        """
        return {
            "id": self.external_id,
            "columns": self.columns,
            "name": self.name,
            "tableDescription": self.table_description,
        }


class DataProductTable(Base):
    __tablename__ = "data_products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        index=True,
    )
    current_version_id: Mapped[int] = mapped_column(
        ForeignKey("data_product_versions.id")
    )
    current_version: Mapped["DataProductVersionTable"] = relationship(
        back_populates="data_product"
    )

    @property
    def external_id(self):
        return f"dp:{self.name}"


class DataProductVersionTable(Base):
    __tablename__ = "data_product_versions"

    __table_args__ = (
        Index("ix_data_prouduct_versions_name_version", "name", "version", unique=True),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    schemas: Mapped[list["SchemaTable"]] = relationship(
        back_populates="data_product_version"
    )
    data_product: Mapped["DataProductTable"] = relationship(
        back_populates="current_version"
    )

    name: Mapped[str] = mapped_column(
        index=True,
    )
    domain: Mapped[str]
    data_product_owner: Mapped[str]
    data_product_owner_display_name: Mapped[str]
    data_product_maintainer: Mapped[Optional[str]]
    data_product_maintainer_display_name: Mapped[Optional[str]]
    status: Mapped[Status]
    email: Mapped[str]
    retention_period: Mapped[int]
    dpia_required: Mapped[bool]
    dpia_location: Mapped[Optional[str]]
    last_updated: Mapped[Optional[datetime]]
    creation_date: Mapped[Optional[datetime]]
    s3_location: Mapped[Optional[str]]
    row_count: Mapped[Optional[int]]

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
            "retentionPeriod": self.retention_period,
            "dpiaRequired": self.dpia_required,
            "domain": self.domain,
            "dataProductOwner": self.data_product_owner,
            "dataProductOwnerDisplayName": self.data_product_owner_display_name,
            "email": self.email,
            "tags": self.tags,
            "dpiaLocation": self.dpia_location,
            "lastUpdated": self.last_updated,
            "s3Location": self.s3_location,
            "rowCount": self.row_count,
        }
