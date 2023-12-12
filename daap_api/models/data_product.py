from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Status(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RETIREED = "retired"


class DataProductBase(SQLModel):
    """
    Base fields that are readable and writable
    """

    name: str = Field(
        regex=r"^[a-z0-9_]+$",
        description="The name of the Data Product. Must contain only lowercase letters, numbers, and the underscore character.",
        schema_extra={"example": "my_data_product"},
        index=True,
    )
    description: str = Field(
        description="Detailed description about what functional area this Data Product is representing, what purpose it has and business related information.",
        schema_extra={
            "example": "This data product holds lots of useful information I want to share with those who may have use for it."
        },
    )
    domain: str = Field(
        description="The identifier of the domain this Data Product belongs to. Should be one of HQ, HMPPS, OPG, LAA, HMCTS, CICA, or Platforms",
        schema_extra={"example": "HMPPS"},
    )
    dataProductOwner: str = Field(
        description="Data Product owner, the unique identifier of the actual user that owns, manages, and receives notifications about the Data Product. To make it technology independent it is usually the email address of the owner.",
        schema_extra={"example": "jane.doe@justice.gov.uk"},
    )
    dataProductOwnerDisplayName: str = Field(
        description="The human-readable version of dataProductOwner",
        schema_extra={"example": "Jane Doe"},
    )
    email: str = Field(
        description="point of contact between consumers and maintainers of the Data Product. It could be the owner or a distribution list, but must be reliable and responsive.",
        schema_extra={"example": "jane.doe@justice.gov.uk"},
    )
    status: Status = Field(
        description="this is an enum representing the status of this version of the Data Product. Allowed values are: [draft|published|retired]. This is a metadata that communicates the overall status of the Data Product but is not reflected to the actual deployment status."
    )
    retentionPeriod: int = Field(
        description="Retention period of the data in this data product in days.",
        schema_extra={"example": 3650},
    )
    dpiaRequired: bool = Field(
        description="Bool for if a data privacy impact assessment (dpia) is required to access this data product",
        schema_extra={"example": True},
    )


class DataProductCreate(DataProductBase):
    """
    A create request for a data product
    """

    dataProductMainainer: Optional[str] = Field(
        default=None,
        description="Secondary party who is able to approve DPIA access requests, but who may or may not be legally responsible for the data",
        schema_extra={"example": "information.asset.owner@justice.gov.uk"},
    )
    dataProductMaintainerDisplayName: Optional[str] = Field(
        default=None,
        description="The human-readable version of dataProductMaintainer",
        schema_extra={"example": "Jonny Data"},
    )
    tags: dict[str, str] = Field(
        default_factory=dict,
        description="Additional tags to add.",
        schema_extra={"example": {"sandbox": True}},
    )


class DataProductRead(DataProductBase):
    """
    A read request for a data product
    """

    schemas: list[str] = Field(
        default=None, description="List of schema names defined for this data product"
    )
    # version: str = Field(
    #     description="Data product version of the form [major].[minor]. Generated by data platform.",
    # )
    id: Optional[str] = Field(
        description="Data product unique id. Generated by data platform.",
        schema_extra={"example": "dp:civil-courts-data:v1.1"},
        default=None,
    )


class DataProductTable(DataProductBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    version: str = Field(
        description="Data product version of the form [major].[minor]. Generated by data platform.",
    )
    tags: dict[str, str] = Field(
        sa_column=Column(JSON),
        default_factory=dict,
        description="Additional tags to add.",
        schema_extra={"example": {"sandbox": True}},
    )
    dpiaLocation: Optional[str] = Field(
        description="Data Privacy Impact Assessment (DPIA) file s3 location for this data product. Generated by data platform.",
        default=None,
    )
    lastUpdated: Optional[datetime] = Field(
        default=None,
        description="Last data upload date to this data product. Generated by data platform.",
    )
    creationDate: Optional[datetime] = Field(
        default=None,
        description="Creation date of the data product. Generated by data platform.",
    )
    s3Location: Optional[str] = Field(
        default=None,
        description="S3 path to data in this data product. Generated by data platform.",
    )
    rowCount: Optional[int] = Field(
        default=None,
        description="Total row count of all tables in the data product, as a heuristic. Generated by data platform.",
    )
