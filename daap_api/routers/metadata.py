from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.routing import serialize_response
from fastapi.utils import create_response_field

from ..db import Session, session_dependency
from ..models.metadata import (
    DataProductCreate,
    DataProductRead,
    DataProductTable,
    SchemaRead,
    Status,
)
from ..services.data_platform_logging import DataPlatformLogger
from ..services.metadata_services import (
    DataProductMetadata,
    DataProductSchema,
    format_table_schema,
)

router = APIRouter()

# TODO: treat this is an application dependency - or replace with something else
logger = DataPlatformLogger()


@router.post("/data-products/")
async def register_data_product(
    data_product: DataProductCreate,
    session: Session = session_dependency,
) -> DataProductRead:
    data_product_internal = DataProductTable.model_validate(
        data_product.model_dump() | {"version": "v1.0"}, strict=True
    )

    session.add(data_product_internal)
    session.commit()
    session.refresh(data_product_internal)

    # TODO: make this transformation less hacky.
    attrs = data_product_internal.model_dump()
    del attrs["id"]
    attrs["version"] = "v1.0"
    return DataProductRead.model_validate(attrs)


@router.get("/data-products/{data_product_name}")
async def get_metadata(data_product_name: str) -> DataProductRead:
    logger.add_data_product(data_product_name)

    metadata = DataProductMetadata(
        data_product_name=data_product_name,
        logger=logger,
        input_data=None,
    ).load()

    if not metadata.exists:
        message = f"no existing metadata found in S3 for {data_product_name=}"
        logger.error(message)
        raise HTTPException(status_code=404, detail=message)

    model_attrs = metadata.latest_version_saved_data | {"version": metadata.version}
    model_attrs["status"] = Status[model_attrs["status"].upper()]
    return DataProductRead.model_validate(model_attrs, strict=True)


@router.get("/schemas/{data_product_name}/{table_name}")
async def get_schema(data_product_name: str, table_name: str) -> SchemaRead:
    logger.add_data_product(data_product_name, table_name)

    schema = DataProductSchema(
        data_product_name=data_product_name,
        table_name=table_name,
        logger=logger,
        input_data=None,
    ).load()

    if not schema.exists:
        message = (
            f"no existing schema found in S3 for {data_product_name=}, {table_name=}"
        )
        logger.error(message)
        raise HTTPException(status_code=404, detail=message)

    formatted = format_table_schema(schema.latest_version_saved_data)
    return SchemaRead.model_validate(formatted, strict=True)
