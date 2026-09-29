"""Checks against the local PostgreSQL. Skipped when the database is not running.

Setup: docker compose up -d, alembic upgrade head, python seed.py
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from db import get_engine
from readiness import load_demo

try:
    engine = get_engine()
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
except (OperationalError, RuntimeError):
    pytest.skip("PostgreSQL is not running", allow_module_level=True)


def test_seeded_jobs_match_the_demo_file():
    demo = load_demo()
    with engine.connect() as connection:
        rows = connection.execute(
            text("SELECT id, start_date, end_date FROM jobs ORDER BY id")
        ).all()

    assert [(row.id, row.start_date.isoformat(), row.end_date.isoformat()) for row in rows] == [
        (job["id"], job["start_date"], job["end_date"]) for job in demo["jobs"]
    ]


def test_database_rejects_job_ending_before_it_starts():
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(IntegrityError, match="job_dates_ordered"):
                connection.execute(
                    text("""
                        INSERT INTO jobs (id, organisation_id, status, start_date, end_date,
                                          policy_id, policy_version)
                        VALUES ('JOB-BAD', 'ORG-DEMO', 'scheduled', '2026-10-09', '2026-10-01',
                                'DEMO-CONTRACTOR-001', 1)
                    """)
                )
        finally:
            transaction.rollback()
