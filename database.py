from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config.settings import app_settings


def get_url() -> str:
    user = app_settings.SQL_USER
    password = app_settings.SQL_PASSWORD
    server = app_settings.SQL_HOST
    db = app_settings.SQL_DATABASE_NAME
    port = app_settings.SQL_PORT
    return f"postgresql://{user}:{password}@{server}:{port}/{db}"


def get_celery_url() -> str:
    return f"db+{get_url()}"


SQLALCHEMY_DATABASE_URL = get_url()

# Increase the connection pool size and set the maximum overflow
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=10, poolclass=QueuePool, pool_pre_ping=True
)

# Enable connection recycling after a specified duration (e.g., 5 min)
engine.pool_recycle = 300

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = DeclarativeBase


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
