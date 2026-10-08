import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import resolve_database_url, settings

DATABASE_URL = resolve_database_url(
    settings.DATABASE_URL,
    settings.SQLITE_DB_PATH,
    on_railway=bool(os.environ.get("RAILWAY_ENVIRONMENT_NAME")),
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()
