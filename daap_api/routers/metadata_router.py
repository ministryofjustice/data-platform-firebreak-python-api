from typing import Tuple

import structlog
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..db import Session, session_dependency
from ..models.api.metadata_api_models import (
    DataProductCreate,
    DataProductRead,
    SchemaCreate,
    SchemaRead,
)
from ..models.orm.metadata_orm_models import DataProductTable, SchemaTable
from ..models.orm.metadata_repositories import DataProductRepository, SchemaRepository
from ..services.metadata_services import DataProductSchema, format_table_schema

router = APIRouter()

logger = structlog.get_logger(__name__)


def parse_data_product_id(id) -> Tuple[str, str]:
    _, name, version = id.split(":")
    return name, version


def parse_schema_id(id) -> Tuple[str, str, str]:
    _, name, version, table_name = id.split(":")
    return name, version, table_name


@router.get("/data-products/")
async def list_data_products(
    session: Session = session_dependency,
) -> list[DataProductRead]:
    """
    List all data products on the platform
    """
    repo = DataProductRepository(session)
    return [DataProductRead.model_validate(dp.to_attributes()) for dp in repo.list()]


@router.post("/data-products/")
async def register_data_product(
    data_product: DataProductCreate,
    session: Session = session_dependency,
) -> DataProductRead:
    """
    Register a data product with the Data Platform. This makes information about
    your data product visible in the data catalgoue.

    A unique ID will be generated for the initial version of the data product.
    """
    data_product_internal = DataProductTable(**data_product.model_dump())
    repo = DataProductRepository(session)

    try:
        repo.create(data_product_internal)
    except repo.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A data product with this name already exists",
        )

    return DataProductRead.model_validate(data_product_internal.to_attributes())


@router.get("/data-products/{id}")
async def get_metadata(
    id: str, session: Session = session_dependency
) -> DataProductRead:
    """
    Fetch metadata about a data product by ID.
    """
    try:
        data_product_name, version = parse_data_product_id(id)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}")

    repo = DataProductRepository(session)

    data_product_internal = repo.fetch(name=data_product_name, version=version)
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
    """
    Register a schema (blueprint of your table) for a new table in your Data Product.
    """
    data_product_name, version, table_name = parse_schema_id(id)

    data_product = DataProductRepository(session).fetch(
        name=data_product_name, version=version
    )
    if data_product is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a data product that does not exist",
        )

    schema_internal = SchemaTable(
        data_product=data_product, name=table_name, **schema.model_dump()
    )
    repo = SchemaRepository(session)
    try:
        repo.create(schema_internal)
    except IntegrityError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"A schema with this name already exists"
        )

    return SchemaRead.model_validate(schema_internal.to_attributes())


@router.get("/schemas/{id}")
async def get_schema(id: str, session: Session = session_dependency) -> SchemaRead:
    """
    Get a schema that has been registered to a data product by ID.
    """
    data_product_name, version, table_name = parse_schema_id(id)
    schema = SchemaRepository(session).fetch(
        data_product_name=data_product_name, version=version, table_name=table_name
    )
    if schema is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a schema version that does not exist",
        )

    return SchemaRead.model_validate(schema.to_attributes(), strict=True)
