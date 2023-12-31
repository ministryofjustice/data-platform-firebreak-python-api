from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ..orm.metadata_orm_models import Status


class Column(BaseModel):
    name: str = Field(
        pattern=r"^[a-z0-9_]+$",
        description="The name of a column within your data.",
        json_schema_extra={"pattern": r"^[a-z0-9_]+$"},
    )
    type: str = Field(
        pattern=r"^(u?(tiny|small|big|)int)|float|double|decimal\(\d{1,2},\s?\d{1,2}\)|char\(\d{1,3}\)|varchar\(\d{0,5}\)|varchar|string|boolean|date|timestamp$",
        description="The data type of the Column. See https://docs.aws.amazon.com/athena/latest/ug/data-types.html",
    )
    description: str = Field(
        description="A description of the column that will feed the data catalogue."
    )


class SchemaBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    table_description: str = Field(
        description="A description of the data contained within the table",
        json_schema_extra={
            "example": "this table contains example data for an example data product."
        },
    )

    columns: list[Column] = Field(
        description="A list of objects which relate to columns in your data, each list item will contain, a name of the column, data type of the column and description of the column."
    )


class SchemaCreate(SchemaBase):
    model_config = ConfigDict(extra="forbid")


class SchemaRead(SchemaBase):
    id: str


class DataProductBase(BaseModel):
    """
    Base fields that are readable and writable
    """

    model_config = ConfigDict(alias_generator=to_camel)

    description: str = Field(
        description="Detailed description about what functional area this Data Product is representing, what purpose it has and business related information.",
        json_schema_extra={
            "example": "This data product holds lots of useful information I want to share with those who may have use for it."
        },
    )
    domain: str = Field(
        description="The identifier of the domain this Data Product belongs to. Should be one of HQ, HMPPS, OPG, LAA, HMCTS, CICA, or Platforms",
        json_schema_extra={"example": "HMPPS"},
    )
    data_product_owner: str = Field(
        description="Data Product owner, the unique identifier of the actual user that owns, manages, and receives notifications about the Data Product. To make it technology independent it is usually the email address of the owner.",
        json_schema_extra={"example": "jane.doe@justice.gov.uk"},
    )
    data_product_owner_display_name: str = Field(
        description="The human-readable version of dataProductOwner",
        json_schema_extra={"example": "Jane Doe"},
    )
    email: str = Field(
        description="point of contact between consumers and maintainers of the Data Product. It could be the owner or a distribution list, but must be reliable and responsive.",
        json_schema_extra={"example": "jane.doe@justice.gov.uk"},
    )
    status: Status = Field(
        description="this is an enum representing the status of this version of the Data Product. Allowed values are: [draft|published|retired]. This is a metadata that communicates the overall status of the Data Product but is not reflected to the actual deployment status."
    )
    retention_period: int = Field(
        description="Retention period of the data in this data product in days.",
        json_schema_extra={"example": 3650},
    )
    dpia_required: bool = Field(
        description="Bool for if a data privacy impact assessment (dpia) is required to access this data product",
        json_schema_extra={"example": True},
    )
    tags: dict[str, str] = Field(
        default_factory=dict,
        description="Additional tags to add.",
        json_schema_extra={"example": {"sandbox": True}},
    )


class DataProductCreate(DataProductBase):
    """
    A create request for a data product
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        pattern=r"^[a-z0-9_]+$",
        description="The name of the Data Product. Must contain only lowercase letters, numbers, and the underscore character.",
        json_schema_extra={"example": "my_data_product"},
    )

    data_product_maintainer: Optional[str] = Field(
        default=None,
        description="Secondary party who is able to approve DPIA access requests, but who may or may not be legally responsible for the data",
        json_schema_extra={"example": "information.asset.owner@justice.gov.uk"},
    )
    data_product_maintainer_display_name: Optional[str] = Field(
        default=None,
        description="The human-readable version of dataProductMaintainer",
        json_schema_extra={"example": "Jonny Data"},
    )


class DataProductUpdate(DataProductBase):
    """
    An update request for a data product
    """

    model_config = ConfigDict(extra="forbid")

    data_product_maintainer: Optional[str] = Field(
        default=None,
        description="Secondary party who is able to approve DPIA access requests, but who may or may not be legally responsible for the data",
        json_schema_extra={"example": "information.asset.owner@justice.gov.uk"},
    )
    data_product_maintainer_display_name: Optional[str] = Field(
        default=None,
        description="The human-readable version of dataProductMaintainer",
        json_schema_extra={"example": "Jonny Data"},
    )


class SchemaId(BaseModel):
    id: str


class DataProductRead(DataProductBase):
    """
    A read request for a data product
    """

    name: str = Field(
        pattern=r"^[a-z0-9_]+$",
        description="The name of the Data Product. Must contain only lowercase letters, numbers, and the underscore character.",
        json_schema_extra={"example": "my_data_product"},
    )

    schemas: list[SchemaId] = Field(
        default_factory=list,
        description="List of schemas defined for this data product",
    )

    version: str = Field(
        description="Data product version of the form [major].[minor]. Generated by data platform.",
    )

    id: str = Field(
        description="Data product unique id. Generated by data platform.",
        json_schema_extra={"example": "dp:civil-courts-data"},
    )

    @staticmethod
    def from_model(model):
        value = DataProductRead.model_validate(model.to_attributes())
        if model.data_product is not None:
            value.id = model.data_product.external_id
        value.schemas = [SchemaId(id=schema.external_id) for schema in model.schemas]

        return value


class SchemaReadWithDataProduct(SchemaRead):
    data_product: DataProductRead
