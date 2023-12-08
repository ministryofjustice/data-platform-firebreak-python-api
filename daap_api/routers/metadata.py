from fastapi import APIRouter, HTTPException

from ..config import Settings
from ..services.data_platform_logging import DataPlatformLogger
from ..services.data_product_metadata import DataProductMetadata

router = APIRouter()

# TODO: treat this is an application dependency - or replace with something else
logger = DataPlatformLogger()


@router.get("/data-products/{data_product_name}")
async def get_metadata(data_product_name: str):
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

    return metadata.latest_version_saved_data
