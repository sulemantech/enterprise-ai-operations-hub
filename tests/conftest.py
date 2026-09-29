"""Shared test fixtures.

Database tests need: docker compose up -d, alembic upgrade head, python seed.py
They are skipped when PostgreSQL is not running.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from api import app, get_connection
from db import get_engine


@pytest.fixture
def db_connection():
    """A connection inside a transaction that is rolled back after the test,
    so tests can change rows without affecting the seeded data."""
    try:
        connection = get_engine().connect()
        connection.execute(text("SELECT 1"))
    except (OperationalError, RuntimeError):
        pytest.skip("PostgreSQL is not running")
    connection.rollback()  # End the transaction SELECT 1 started automatically.

    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_connection):
    """An API client whose requests use the test's rolled-back connection."""
    app.dependency_overrides[get_connection] = lambda: db_connection
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
