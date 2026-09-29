"""Tests that the API returns the same results as the readiness rules."""

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_assessments_returns_all_four_jobs():
    response = client.get("/assessments")

    assert response.status_code == 200
    assert response.json() == [
        {"job_id": "JOB-101", "status": "READY", "reason": "REQUIREMENTS_MET"},
        {"job_id": "JOB-102", "status": "BLOCKED", "reason": "EXPIRES_BEFORE_JOB_END"},
        {"job_id": "JOB-103", "status": "BLOCKED", "reason": "MISSING_DOCUMENT"},
        {"job_id": "JOB-104", "status": "NEEDS_REVIEW", "reason": "UNVERIFIED_DOCUMENT"},
    ]


def test_single_assessment():
    response = client.get("/assessments/JOB-102")

    assert response.status_code == 200
    assert response.json()["reason"] == "EXPIRES_BEFORE_JOB_END"


def test_unknown_job_returns_404():
    response = client.get("/assessments/JOB-999")

    assert response.status_code == 404
