import logging
import os
import sys
from os import environ

import structlog
from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default values are for the data platform dev environment in the modernisation platform
    log_bucket_name: str = "logs-development20231011135449293200000002"
    metadata_bucket_name: str = "metadata-development20231011135450514100000004"
    data_bucket_name: str = "data-development20231011135451999500000005"
    landing_zone_bucket_name: str = "data-landing-development20231011135449285800000001"
    database_url: str = "postgresql+psycopg://postgres:postgres123@localhost:5432/daap_api_dev"  # pragma: allowlist secret
    database_url_test: str = "postgresql+psycopg://postgres:postgres123@localhost:5432/daap_api_test"  # pragma: allowlist secret
    enable_json_logs: bool = False

    auth_enabled: bool = True
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ["http://localhost:8000"]
    AZURE_OPENAPI_CLIENT_ID: str = ""
    AZURE_APP_CLIENT_ID: str = ""
    AZURE_TENANT_ID: str = ""
    SCOPE_DESCRIPTION: str = "user_impersonation"

    model_config = SettingsConfigDict(env_file=".env")

    @computed_field
    @property
    def SCOPE_NAME(self) -> str:
        return f"api://{self.AZURE_APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}"

    @computed_field
    @property
    def SCOPES(self) -> dict:
        return {
            self.SCOPE_NAME: self.SCOPE_DESCRIPTION,
        }


settings = Settings()


# Backwards compatability with old code
environ["LOG_BUCKET"] = settings.log_bucket_name
environ["METADATA_BUCKET"] = settings.metadata_bucket_name
environ["LANDING_ZONE_BUCKET"] = settings.landing_zone_bucket_name
environ["RAW_DATA_BUCKET"] = settings.data_bucket_name
environ["CURATED_DATA_BUCKET"] = settings.data_bucket_name


def setup_logging():
    """
    Configure structlog to format all messages
    logged through structlog or the standard library logging module
    https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    logs_render = (
        structlog.processors.JSONRenderer()
        if settings.enable_json_logs
        else structlog.dev.ConsoleRenderer(
            colors=True,
            event_key="message",
            timestamp_key="date_time",
        )
    )

    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.EventRenamer(to="message"),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", key="date_time"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            parameters={
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            },
        ),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler()

    # Use `ProcessorFormatter` to format all `logging` entries.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            logs_render,
        ],
    )

    handler.setFormatter(formatter)
    root_uvicorn_logger = logging.getLogger()
    root_uvicorn_logger.handlers.clear()
    root_uvicorn_logger.addHandler(handler)
    root_uvicorn_logger.setLevel(logging.INFO)

    # Avoid duplicate echo messages from SQLAlchemy
    logging.getLogger("sqlalchemy.engine.Engine").handlers.clear()
