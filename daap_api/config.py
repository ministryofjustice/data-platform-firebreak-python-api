from os import environ

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Default values are for the data platform dev environment in the modernisation platform
    log_bucket_name: str = "logs-development20231011135449293200000002"
    metadata_bucket_name: str = "metadata-development20231011135450514100000004"
    data_bucket_name: str = "data-development20231011135451999500000005"
    landing_zone_bucket_name: str = "data-landing-development20231011135449285800000001"
    database_uri: str = "postgresql+psycopg://postgres:postgres123@localhost:5432/daap_api_dev"  # pragma: allowlist secret
    database_uri_test: str = "postgresql+psycopg://postgres:postgres123@localhost:5432/daap_api_test"  # pragma: allowlist secret


settings = Settings()

# Backwards compatability with old code
environ["LOG_BUCKET"] = settings.log_bucket_name
environ["METADATA_BUCKET"] = settings.metadata_bucket_name
environ["LANDING_ZONE_BUCKET"] = settings.landing_zone_bucket_name
environ["RAW_DATA_BUCKET"] = settings.data_bucket_name
environ["CURATED_DATA_BUCKET"] = settings.data_bucket_name
