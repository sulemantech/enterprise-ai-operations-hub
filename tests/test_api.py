"""Tests that the API returns the same results as the readiness rules."""

import pytest
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

DEMO_WINDOW = {"start": "2026-10-05", "end": "2026-10-11"}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_window_returns_all_four_jobs():
    response = client.get("/assessments", params=DEMO_WINDOW)

    assert response.status_code == 200
    assert response.json() == [
        {"job_id": "JOB-101", "status": "READY", "reason": "REQUIREMENTS_MET"},
        {"job_id": "JOB-102", "status": "BLOCKED", "reason": "EXPIRES_BEFORE_JOB_END"},
        {"job_id": "JOB-103", "status": "BLOCKED", "reason": "MISSING_DOCUMENT"},
        {"job_id": "JOB-104", "status": "NEEDS_REVIEW", "reason": "UNVERIFIED_DOCUMENT"},
    ]


def test_window_includes_jobs_that_overlap_it():
    # JOB-102 runs 10-06 to 10-09, so it is still running on 10-07.
    response = client.get("/assessments", params={"start": "2026-10-07", "end": "2026-10-07"})

    assert [a["job_id"] for a in response.json()] == ["JOB-102", "JOB-103"]


def test_window_with_no_jobs_returns_empty_list():
    response = client.get("/assessments", params={"start": "2026-11-01", "end": "2026-11-07"})

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
def test_invalid_window_is_rejected(params):
    response = client.get("/assessments", params=params)

    assert response.status_code == 422


def test_invalid_window_explains_the_problem():
    response = client.get("/assessments", params={"start": "2026-10-11", "end": "2026-10-05"})

    assert response.json() == {"detail": "end must be on or after start"}


def test_single_assessment():
    response = client.get("/assessments/JOB-102")

    assert response.status_code == 200
    assert response.json()["reason"] == "EXPIRES_BEFORE_JOB_END"


def test_unknown_job_returns_404():
    response = client.get("/assessments/JOB-999")

    assert response.status_code == 404
