"""One place that knows how to connect to PostgreSQL."""

import os
from collections.abc import Iterator
from functools import cache

from dotenv import load_dotenv
from sqlalchemy import Connection, Engine, create_engine

load_dotenv()


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env.")
    return url


@cache  # One engine (and its connection pool) for the whole process.
def get_engine() -> Engine:
    return create_engine(database_url())


def get_connection() -> Iterator[Connection]:
    with get_engine().connect() as connection:
        yield connection


def get_transaction() -> Iterator[Connection]:
    with get_engine().begin() as connection:
        yield connection
