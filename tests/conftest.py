from __future__ import annotations

from collections.abc import Generator
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure `import app` works when running `pytest` from different working directories.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.base import Base
from app.db.session import get_db as get_db_dependency
from app.main import create_app

@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    # Use a temp SQLite file for isolation across tests.
    db_file = tmp_path / "test_address_book.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        future=True,
        pool_pre_ping=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, class_=Session, autocommit=False, autoflush=False, expire_on_commit=False)

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db_dependency] = override_get_db

    with TestClient(app) as c:
        yield c

