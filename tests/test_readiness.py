"""Tests that protect the readiness rules, not the implementation details."""

import copy
from datetime import date

import pytest

from readiness import assess_job, dates_cover_job, load_demo

DEMO = load_demo()


def job_by_id(demo: dict, job_id: str) -> dict:
    return next(job for job in demo["jobs"] if job["id"] == job_id)


def document_by_id(demo: dict, document_id: str) -> dict:
    return next(document for document in demo["documents"] if document["id"] == document_id)


@pytest.mark.parametrize("expected", DEMO["expected_results"], ids=lambda e: e["job_id"])
def test_demo_jobs_match_expected_results(expected):
    job = job_by_id(DEMO, expected["job_id"])
    assert assess_job(job, DEMO["documents"], DEMO["policy"]) == (
        expected["status"],
        expected["reason"],
    )


# End-date boundary: a job running 2026-10-06 to 2026-10-09.
@pytest.mark.parametrize(
    ("valid_to", "covered"),
    [
        (date(2026, 10, 10), True),   # ends the day after the job
        (date(2026, 10, 9), True),    # ends on the job's last day: still covered
        (date(2026, 10, 8), False),   # ends one day early
    ],
)
def test_end_date_boundary(valid_to, covered):
    assert dates_cover_job(date(2026, 10, 6), date(2026, 10, 9), date(2026, 1, 1), valid_to) is covered


def test_document_starting_after_job_start_blocks():
    demo = copy.deepcopy(DEMO)
    document_by_id(demo, "DOC-001")["valid_from"] = "2026-10-06"  # JOB-101 starts 2026-10-05

    assert assess_job(job_by_id(demo, "JOB-101"), demo["documents"], demo["policy"]) == (
        "BLOCKED",
        "NOT_VALID_AT_JOB_START",
    )


def test_insurance_below_minimum_blocks():
    demo = copy.deepcopy(DEMO)
    document_by_id(demo, "DOC-001")["coverage_amount"] = 4_999_999

    assert assess_job(job_by_id(demo, "JOB-101"), demo["documents"], demo["policy"]) == (
        "BLOCKED",
        "INSUFFICIENT_COVERAGE",
    )


def test_insurance_exactly_at_minimum_is_ready():
    demo = copy.deepcopy(DEMO)
    document_by_id(demo, "DOC-001")["coverage_amount"] = 5_000_000

    assert assess_job(job_by_id(demo, "JOB-101"), demo["documents"], demo["policy"]) == (
        "READY",
        "REQUIREMENTS_MET",
    )


def test_blocking_problem_outranks_review_problem():
    # JOB-104 has pending insurance; also remove its licence.
    demo = copy.deepcopy(DEMO)
    demo["documents"] = [d for d in demo["documents"] if d["id"] != "DOC-007"]

    assert assess_job(job_by_id(demo, "JOB-104"), demo["documents"], demo["policy"]) == (
        "BLOCKED",
        "MISSING_DOCUMENT",
    )


def test_one_good_document_is_enough():
    # CON-002's insurance expires too early, but a second, valid policy is added.
    demo = copy.deepcopy(DEMO)
    replacement = dict(document_by_id(demo, "DOC-003"), id="DOC-099", valid_to="2026-12-31")
    demo["documents"].append(replacement)

    assert assess_job(job_by_id(demo, "JOB-102"), demo["documents"], demo["policy"]) == (
        "READY",
        "REQUIREMENTS_MET",
    )

def test_job_without_contractors_is_blocked():
    demo = copy.deepcopy(DEMO)
    job = job_by_id(demo, "JOB-101")
    job["contractor_ids"] = []

    assert assess_job(job, demo["documents"], demo["policy"]) == (
        "BLOCKED", "NO_CONTRACTOR"
    )


def test_unknown_insurance_amount_needs_review():
    demo = copy.deepcopy(DEMO)
    document_by_id(demo, "DOC-001")["coverage_amount"] = None

    assert assess_job(
        job_by_id(demo, "JOB-101"), demo["documents"], demo["policy"]
    ) == ("NEEDS_REVIEW", "UNKNOWN_COVERAGE")


def test_zero_insurance_amount_is_blocked():
    demo = copy.deepcopy(DEMO)
    document_by_id(demo, "DOC-001")["coverage_amount"] = 0

    assert assess_job(
        job_by_id(demo, "JOB-101"), demo["documents"], demo["policy"]
    ) == ("BLOCKED", "INSUFFICIENT_COVERAGE")