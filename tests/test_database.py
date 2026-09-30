"""Checks that the seeded PostgreSQL data and constraints are as expected."""

import pytest
from datetime import date
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

import repository
from readiness import assess_job, load_demo


def test_unassigned_job_is_returned_and_blocked(db_connection):
    # This fixture rolls the deletion back after the test.
    db_connection.execute(
        text("DELETE FROM job_contractors WHERE job_id = :id"),
        {"id": "JOB-101"},
    )

    job = repository.get_job(db_connection, "JOB-101")
    assert job is not None
    assert job["contractor_ids"] == []

    jobs = repository.jobs_in_window(
        db_connection, date(2026, 10, 5), date(2026, 10, 11)
    )
    matching_jobs = [item for item in jobs if item["id"] == "JOB-101"]
    assert len(matching_jobs) == 1
    assert matching_jobs[0]["contractor_ids"] == []

    policy = repository.get_policy(db_connection, job["policy_id"], job["policy_version"])
    assert assess_job(job, [], policy) == ("BLOCKED", "NO_CONTRACTOR")


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
