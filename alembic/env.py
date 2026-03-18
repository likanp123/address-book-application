from __future__ import annotations

import logging

from alembic import context
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.base import Base

# Import models so SQLAlchemy metadata is populated.
from app.models.address import Address  # noqa: F401


logger = logging.getLogger("alembic.env")

# Alembic Config object
config = context.config

# Target metadata for 'autogenerate' support.
target_metadata = Base.metadata


def _create_alembic_engine():
    connect_args: dict[str, object] = {}
    if settings.db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    return create_engine(
        settings.db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    context.configure(
        url=settings.db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = _create_alembic_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

