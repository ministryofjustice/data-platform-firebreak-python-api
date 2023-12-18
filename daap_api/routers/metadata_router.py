from typing import Tuple

import structlog
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import select

from ..db import Session, session_dependency
from ..models.api.metadata_api_models import (
    DataProductCreate,
    DataProductRead,
    SchemaCreate,
    SchemaRead,
)
from ..models.orm.metadata_orm_models import DataProductTable, SchemaTable
from ..services.metadata_services import DataProductSchema, format_table_schema

router = APIRouter()

logger = structlog.get_logger(__name__)


def parse_data_product_id(id) -> Tuple[str, str]:
    _, name, version = id.split(":")
    return name, version


def parse_schema_id(id) -> Tuple[str, str, str]:
    _, name, version, table_name = id.split(":")
    return name, version, table_name


@router.post("/data-products/")
async def register_data_product(
    data_product: DataProductCreate,
    session: Session = session_dependency,
) -> DataProductRead:
    data_product_internal = DataProductTable(**data_product.model_dump())

    session.add(data_product_internal)

    try:
        session.commit()
        session.refresh(data_product_internal)
    except IntegrityError:
        session.rollback()
        data_product_internal = session.query(
            select(DataProductTable).filter_by(name=data_product.name)
        ).one()

    # Check if the stored version is identical to the one passed in -
    # if so, we can just return it
    # TODO: implement idempotency of create requests as a cross-cutting concern
    # so we don't need the extra logic here
    if (
        DataProductCreate.model_validate(
            data_product_internal.to_attributes(), strict=True
        )
        != data_product
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A data product with this name already exists",
        )

    return DataProductRead.model_validate(data_product_internal.to_attributes())


@router.get("/data-products/{id}")
async def get_metadata(
    id: str, session: Session = session_dependency
) -> DataProductRead:
    try:
        data_product_name, version = parse_data_product_id(id)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}")

    data_product_internal = session.execute(
        select(DataProductTable).filter_by(name=data_product_name, version=version)
    ).scalar()
    if data_product_internal is None:
        logger.info("Data product does not exist")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Data product does not exist with id {id}"
        )

    return DataProductRead.model_validate(
        data_product_internal.to_attributes(), strict=True
    )


@router.post("/schemas/{id}")
async def create_schema(
    id: str, schema: SchemaCreate, session: Session = session_dependency
) -> SchemaRead:
    data_product_name, version, table_name = parse_schema_id(id)

    data_product_internal = session.execute(
        select(DataProductTable).filter_by(name=data_product_name, version=version)
    ).scalar()

    if data_product_internal is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a data product that does not exist",
        )

    schema_internal = SchemaTable(
        data_product=data_product_internal, name=table_name, **schema.model_dump()
    )
    session.add(schema_internal)

    try:
        session.commit()
        session.refresh(data_product_internal)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"A schema with this name already exists"
        )

    return SchemaRead.model_validate(schema_internal.to_attributes())


@router.get("/schemas/{id}")
async def get_schema(id: str, session: Session = session_dependency) -> SchemaRead:
    data_product_name, version, table_name = parse_schema_id(id)
    schema_internal = session.execute(
        select(SchemaTable)
        .join(DataProductTable)
        .where(SchemaTable.name == table_name)
        .where(DataProductTable.name == data_product_name)
        .where(DataProductTable.version == version)
    ).scalar()

    if schema_internal is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a schema version that does not exist",
        )

    return SchemaRead.model_validate(schema_internal.to_attributes(), strict=True)
