"""Tests that the API returns the same results as the readiness rules."""

import pytest
from sqlalchemy import text

DEMO_WINDOW = {"start": "2026-10-05", "end": "2026-10-11"}


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def status_by_job(response) -> dict[str, tuple[str, str]]:
    return {a["job_id"]: (a["status"], a["reason"]) for a in response.json()}


def test_demo_window_includes_the_four_fixture_jobs(client):
    response = client.get("/assessments", params=DEMO_WINDOW)

    assert response.status_code == 200
    results = status_by_job(response)
    assert results["JOB-101"] == ("READY", "REQUIREMENTS_MET")
    assert results["JOB-102"] == ("BLOCKED", "EXPIRES_BEFORE_JOB_END")
    assert results["JOB-103"] == ("BLOCKED", "MISSING_DOCUMENT")
    assert results["JOB-104"] == ("NEEDS_REVIEW", "UNVERIFIED_DOCUMENT")


def test_assessment_describes_the_job(client):
    response = client.get("/assessments/JOB-102")

    assert response.json() == {
        "job_id": "JOB-102",
        "title": "Office lighting retrofit",
        "site": "North Sydney",
        "start_date": "2026-10-06",
        "end_date": "2026-10-09",
        "policy_id": "DEMO-CONTRACTOR-001",
        "contractors": [{"id": "CON-002", "name": "Demo Electrical Two", "trade": "Electrical"}],
        "status": "BLOCKED",
        "reason": "EXPIRES_BEFORE_JOB_END",
    }


def test_window_includes_jobs_that_overlap_it(client):
    response = client.get("/assessments", params={"start": "2026-10-07", "end": "2026-10-07"})

    # JOB-102 runs 10-06 to 10-09, so it is still running on 10-07.
    assert {"JOB-102", "JOB-103"} <= status_by_job(response).keys()
    for assessment in response.json():
        assert assessment["start_date"] <= "2026-10-07" <= assessment["end_date"]


def test_window_with_no_jobs_returns_empty_list(client):
    response = client.get("/assessments", params={"start": "2027-06-01", "end": "2027-06-07"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params",
    [
        {},                                               # both dates missing
        {"start": "2026-10-05"},                          # end missing
        {"start": "05/10/2026", "end": "2026-10-11"},     # wrong format
        {"start": "2026-02-30", "end": "2026-03-01"},     # not a real date
        {"start": "2026-10-11", "end": "2026-10-05"},     # end before start
        {"start": "2026-01-01", "end": "2026-12-31"},     # window too long
    ],
)
def test_invalid_window_is_rejected(client, params):
    response = client.get("/assessments", params=params)

    assert response.status_code == 422


def test_invalid_window_explains_the_problem(client):
    response = client.get("/assessments", params={"start": "2026-10-11", "end": "2026-10-05"})

    assert response.json() == {"detail": "end must be on or after start"}


def test_unknown_job_returns_404(client):
    response = client.get("/assessments/JOB-999")

    assert response.status_code == 404


def test_changing_a_stored_document_changes_the_assessment(client, db_connection):
    # JOB-104 needs review only because DOC-006 is pending. Verify it in the database.
    db_connection.execute(text("UPDATE documents SET review_status = 'verified' WHERE id = 'DOC-006'"))

    response = client.get("/assessments/JOB-104")

    assert (response.json()["status"], response.json()["reason"]) == ("READY", "REQUIREMENTS_MET")
