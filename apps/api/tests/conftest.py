from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://swafy:swafy-dev-password@localhost:5432/swafy_test",
)
os.environ.setdefault(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://swafy:swafy-dev-password@localhost:5432/swafy_test",
)
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-characters-long")
os.environ.setdefault("WORKER_SERVICE_TOKEN", "test-worker-token-at-least-32-chars")
os.environ.setdefault("ENVIRONMENT", "test")

from swafy_api import models  # noqa: F401,E402
from swafy_api.config import normalize_database_url  # noqa: E402
from swafy_api.db import Base, get_db  # noqa: E402
from swafy_api.main import app  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    raw_test_url = os.environ["TEST_DATABASE_URL"]
    database_name = make_url(raw_test_url).database or ""
    if "test" not in database_name.lower():
        raise RuntimeError(
            "TEST_DATABASE_URL must target a dedicated database whose name contains 'test'; "
            "the test fixture drops and recreates application tables."
        )
    database_url = normalize_database_url(raw_test_url)
    engine = create_engine(database_url, pool_pre_ping=True)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
