from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _create_engine(db_url: str) -> Engine:
    connect_args: dict[str, object] = {}
    if db_url.startswith("sqlite"):
        # SQLite default driver disallows cross-thread usage. FastAPI commonly uses multiple threads.
        connect_args = {"check_same_thread": False}

    return create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        future=True,
    )


engine = _create_engine(settings.db_url)
SessionLocal = sessionmaker(bind=engine, class_=Session, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a SQLAlchemy session per request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

