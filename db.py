"""One place that knows how to connect to PostgreSQL."""

import os
from functools import cache

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

load_dotenv()


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env.")
    return url


@cache  # One engine (and its connection pool) for the whole process.
def get_engine() -> Engine:
    return create_engine(database_url())
