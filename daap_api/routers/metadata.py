from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import select

from ..db import Session, session_dependency
from ..models.metadata import (
    DataProductCreate,
    DataProductRead,
    DataProductTable,
    SchemaCreate,
    SchemaRead,
    SchemaTable,
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


def parse_external_id(id) -> Tuple[str, str]:
    _, name, version = id.split(":")
    return name, version


def generate_external_id(data_product_name, version):
    return f"dp:{data_product_name}:{version}"


@router.post("/data-products/")
async def register_data_product(
    data_product: DataProductCreate,
    session: Session = session_dependency,
) -> DataProductRead:
    data_product_internal = DataProductTable.model_validate(data_product, strict=True)

    session.add(data_product_internal)

    try:
        session.commit()
        session.refresh(data_product_internal)
    except IntegrityError:
        session.rollback()
        data_product_internal = session.exec(
            select(DataProductTable).filter_by(name=data_product.name)
        ).one()

    # Check if the stored version is identical to the one passed in -
    # if so, we can just return it
    # TODO: implement idempotency of create requests as a cross-cutting concern
    # so we don't need the extra logic here
    if (
        DataProductCreate.model_validate(data_product_internal, strict=True)
        != data_product
    ):
        raise HTTPException(
            status_code=409, detail="A data product with this name already exists"
        )

    return DataProductRead.model_validate(data_product_internal)


@router.get("/data-products/{id}")
async def get_metadata(
    id: str, session: Session = session_dependency
) -> DataProductRead:
    try:
        data_product_name, version = parse_external_id(id)
    except ValueError:
        raise HTTPException(400, detail=f"Invalid id: {id}")
    logger.add_data_product(data_product_name)

    try:
        data_product_internal = session.exec(
            select(DataProductTable).filter_by(name=data_product_name, version=version)
        ).one()
    except NoResultFound:
        raise HTTPException(404, f"Data product does not exist with id {id}")

    attrs = data_product_internal.model_dump()

    attrs["schemas"] = [
        schema.tableDescription for schema in data_product_internal.schemas
    ]

    return DataProductRead.model_validate(attrs, strict=True)


@router.post("/schemas/")
async def create_schema(
    schema: SchemaCreate,
    session: Session = session_dependency,
) -> SchemaRead:
    schema_internal = SchemaTable.model_validate(schema, strict=True)

    session.add(schema)

    try:
        session.commit()
        session.refresh(schema_internal)
    except IntegrityError:
        session.rollback()
        schema_internal = session.exec(
            select(SchemaTable).join(DataProductTable).filter_by(name=schema.name)
        ).one()

    return SchemaRead.model_validate(schema_internal)


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
    formatted["name"] = table_name
    formatted["data_product_id"] = generate_external_id(
        data_product_name, schema.version
    )
    return SchemaRead.model_validate(formatted, strict=True)
