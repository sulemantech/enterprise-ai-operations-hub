"""Checks that the seeded PostgreSQL data and constraints are as expected."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from readiness import load_demo


def test_fixture_jobs_are_seeded_unchanged(db_connection):
    demo = load_demo()
    rows = db_connection.execute(
        text("SELECT id, start_date, end_date FROM jobs WHERE id = ANY(:ids) ORDER BY id"),
        {"ids": [job["id"] for job in demo["jobs"]]},
    ).all()

    assert [(row.id, row.start_date.isoformat(), row.end_date.isoformat()) for row in rows] == [
        (job["id"], job["start_date"], job["end_date"]) for job in demo["jobs"]
    ]


def test_database_rejects_job_ending_before_it_starts(db_connection):
    with pytest.raises(IntegrityError, match="job_dates_ordered"):
        db_connection.execute(
            text("""
                INSERT INTO jobs (id, organisation_id, status, start_date, end_date,
                                  policy_id, policy_version)
                VALUES ('JOB-BAD', 'ORG-DEMO', 'scheduled', '2026-10-09', '2026-10-01',
                        'DEMO-CONTRACTOR-001', 1)
            """)
        )
