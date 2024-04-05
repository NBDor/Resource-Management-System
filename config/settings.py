import os
from pydantic_settings import BaseSettings


logging_dict = {
    "CRITICAL": 50,
    "FATAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}


class Settings(BaseSettings):
    VERIFYING_KEY: str = f"""{os.getenv("VERIFYING_KEY", "5ahp8kseKOVB_w")}"""
    SQL_USER: str = os.getenv("SQL_USER", "postgres")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD", "test4Life!")
    SQL_HOST: str = os.getenv("SQL_HOST", "localhost")
    SQL_DATABASE_NAME: str = os.getenv("SQL_DATABASE_NAME", "polaris-fast-lp")
    PIPELINE_MODE: str = os.getenv("PIPELINE_MODE", "disabled")
    SQL_PORT: str = os.getenv("SQL_PORT", "5401")
    PAGE_SIZE: int = os.getenv("PAGE_SIZE", 5)
    REDIS_SERVER: str = os.getenv("REDIS_SERVER", "redis://localhost:6379/1")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_DB_INDEX: int = os.getenv("REDIS_DB_INDEX", 1)
    MGMT_SERVICE_HOST: str = os.getenv("MGMT_SERVICE_HOST", "localhost")
    MGMT_SERVICE_PORT: int = os.getenv("MGMT_SERVICE_PORT", 8001)
    NX_INTEGRATION: str = os.getenv("NX_INTEGRATION", "disabled")
    WEBHOOK_MODULE: str = os.getenv("WEBHOOK_MODULE", "disabled")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME", "polaris-chat-files-staging")
    REGION: str = os.getenv("REGION", "eu-central-1")
    IMAGES_URL_PREFIX: str = os.getenv(
        "IMAGES_URL_PREFIX", f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com"
    )


app_settings = Settings()
