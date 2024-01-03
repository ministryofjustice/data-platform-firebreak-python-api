from typing import Tuple

import structlog
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..db import Session, session_dependency
from ..models.api.metadata_api_models import (
    DataProductCreate,
    DataProductRead,
    DataProductUpdate,
    SchemaCreate,
    SchemaRead,
    SchemaReadWithDataProduct,
)
from ..models.orm.metadata_orm_models import (
    DataProductTable,
    DataProductVersionTable,
    SchemaTable,
)
from ..models.orm.metadata_repositories import DataProductRepository, SchemaRepository
from ..services.versioning_service import VersioningService

v1_router = APIRouter()

logger = structlog.get_logger(__name__)


def parse_data_product_id(id) -> str:
    try:
        _, name = id.split(":")
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}")
    return name


def parse_schema_id(id) -> Tuple[str, str]:
    try:
        _, name, table_name = id.split(":")
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}")
    return name, table_name


@v1_router.get("/data-products/")
async def list_data_products(
    session: Session = session_dependency,
) -> list[DataProductRead]:
    """
    List all data products on the platform
    """
    repo = DataProductRepository(session)
    return [DataProductRead.from_model(dp) for dp in repo.list()]


@v1_router.post("/data-products/")
async def register_data_product(
    data_product: DataProductCreate,
    session: Session = session_dependency,
) -> DataProductRead:
    """
    Register a data product with the Data Platform. This makes information about
    your data product visible in the data catalgoue.

    A unique ID will be generated for the initial version of the data product.
    """
    data_product_internal = DataProductVersionTable(**data_product.model_dump())
    repo = DataProductRepository(session)

    try:
        repo.create(data_product_internal)
    except repo.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A data product with this name already exists",
        )

    return DataProductRead.from_model(data_product_internal)


@v1_router.put("/data-products/{id}")
async def update_data_product(
    id: str,
    data_product: DataProductUpdate,
    session: Session = session_dependency,
) -> DataProductRead:
    """
    Update metadata directly associated with a data product.
    This will create a new minor version and return a new ID.
    """
    repo = DataProductRepository(session)
    data_product_name = parse_data_product_id(id)

    current_metadata = repo.fetch_latest(name=data_product_name)

    if current_metadata is None:
        logger.info("Data product does not exist")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Data product does not exist with id {id}"
        )

    versioning_service = VersioningService(current_metadata)
    new_version = versioning_service.update_metadata(**data_product.model_dump())
    repo.update(current_metadata.data_product, new_version)
    return DataProductRead.from_model(new_version)


@v1_router.get("/data-products/{id}")
async def get_metadata(
    id: str, session: Session = session_dependency
) -> DataProductRead:
    """
    Fetch metadata about a data product by ID.
    """
    data_product_name = parse_data_product_id(id)

    repo = DataProductRepository(session)

    data_product_internal = repo.fetch_latest(name=data_product_name)
    if data_product_internal is None:
        logger.info("Data product does not exist")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Data product does not exist with id {id}"
        )

    return DataProductRead.from_model(data_product_internal)


@v1_router.post("/schemas/{id}")
async def create_schema(
    id: str, schema: SchemaCreate, session: Session = session_dependency
) -> SchemaRead:
    """
    Register a schema (blueprint of your table) for a new table in your Data Product.
    """
    data_product_name, table_name = parse_schema_id(id)

    data_product_version = DataProductRepository(session).fetch_latest(
        name=data_product_name
    )
    if data_product_version is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a data product that does not exist",
        )

    # TODO: this should create a new version in some cases
    schema_internal = SchemaTable(
        data_product_version=data_product_version,
        name=table_name,
        **schema.model_dump(),
    )
    repo = SchemaRepository(session)
    try:
        repo.create(schema_internal)
    except IntegrityError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"A schema with this name already exists"
        )

    return SchemaRead.model_validate(schema_internal.to_attributes())


@v1_router.get("/schemas/{id}")
async def get_schema(id: str, session: Session = session_dependency) -> SchemaRead:
    """
    Get a schema that has been registered to a data product by ID.
    """
    data_product_name, table_name = parse_schema_id(id)
    schema = SchemaRepository(session).fetch_latest(
        data_product_name=data_product_name, table_name=table_name
    )
    if schema is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a schema version that does not exist",
        )

    return SchemaRead.model_validate(schema.to_attributes(), strict=True)


@v1_router.put("/schemas/{id}")
async def update_schema(
    id: str, schema: SchemaCreate, session: Session = session_dependency
) -> SchemaReadWithDataProduct:
    data_product_name, table_name = parse_schema_id(id)
    repo = SchemaRepository(session)
    fetched_schema = repo.fetch_latest(
        data_product_name=data_product_name, table_name=table_name
    )
    if fetched_schema is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"id {id} references a data product version that does not exist",
        )
    versioning_service = VersioningService(fetched_schema.data_product_version)

    new_version = versioning_service.update_schema(
        table_name,
        columns=[column.model_dump() for column in schema.columns],
        tableDescription=schema.tableDescription,
    )

    DataProductRepository(session).update(
        fetched_schema.data_product_version.data_product, new_version
    )

    new_schema = [
        schema for schema in new_version.schemas if schema.name == table_name
    ][0]
    attributes = new_schema.to_attributes()
    attributes["data_product"] = new_version.to_attributes()
    attributes["data_product"]["id"] = new_version.data_product.external_id
    return SchemaReadWithDataProduct.model_validate(attributes)
