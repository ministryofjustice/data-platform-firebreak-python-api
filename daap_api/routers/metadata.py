from fastapi import APIRouter, HTTPException, Request, status

from ..models.data_product import DataProduct
from ..models.schema import Schema
from ..services.data_platform_logging import DataPlatformLogger
from ..services.data_product_metadata import (
    DataProductMetadata,
    DataProductSchema,
    format_table_schema,
)
import time

router = APIRouter()

# TODO: treat this is an application dependency - or replace with something else
logger = DataPlatformLogger()


@router.get("/data-products/{data_product_name}")
async def get_metadata(data_product_name: str) -> DataProduct:
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

    return DataProduct.model_validate(metadata.latest_version_saved_data)


@router.get("/schemas/{data_product_name}/{table_name}")
async def get_schema(data_product_name: str, table_name: str) -> Schema:
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
    return Schema.model_validate(formatted)


@router.post("/data-products", status_code=status.HTTP_201_CREATED)
async def post_data_product(request: Request):
    """
    Registers given metadata for a new data product to the data platform
    """

    request_body_dict = await request.json()
    data_product_name = request_body_dict["metadata"]["name"]
    logger.add_data_product(data_product_name)
    logger.info(f"headers: {request.headers}")
    logger.info(f"body: {request_body_dict}")
    return {
        "data_product_name": request_body_dict["metadata"]["name"],
        "time": time.time(),
    }


@router.post(
    "/data-products/{data_product_name}/tables", status_code=status.HTTP_201_CREATED
)
async def post_schema(request: Request, data_product_name: str):
    """
    Registers a given schema for a new table within a data product to the data platform
    """
    request_body_dict = await request.json()
    table_name = request_body_dict["schema"]["tableName"]
    logger.add_data_product(data_product_name, table_name)
    print(f"headers: {request.headers}")
    print(f"body: {request_body_dict}")
    return {
        "data_product_name": data_product_name,
        "table_name": table_name,
        "time": time.time(),
    }
