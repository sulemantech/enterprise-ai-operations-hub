"""Decide whether each fictional job is ready, based on contractor documents."""

import json
from datetime import date
from pathlib import Path

READY = "READY"
BLOCKED = "BLOCKED"
NEEDS_REVIEW = "NEEDS_REVIEW"

# Higher number = more serious. Used to pick one result when there are several.
SEVERITY = {NEEDS_REVIEW: 1, BLOCKED: 2}


def dates_cover_job(
    job_start: date,
    job_end: date,
    valid_from: date,
    valid_to: date,
) -> bool:
    """Return whether a document is valid for every day of the job, inclusively."""
    return valid_from <= job_start and valid_to >= job_end


def find_documents(
    documents: list[dict],
    contractor_id: str,
    document_type: str,
) -> list[dict]:
    """Return the contractor's documents of one type, e.g. "insurance"."""
    return [
        document
        for document in documents
        if document["contractor_id"] == contractor_id
        and document["type"].lower() == document_type
    ]


def check_document(document: dict, job: dict, policy: dict) -> tuple[str, str] | None:
    """Return (status, reason) for the first problem with one document, or None if it is fine."""
    job_start = date.fromisoformat(job["start_date"])
    job_end = date.fromisoformat(job["end_date"])
    valid_from = date.fromisoformat(document["valid_from"])
    valid_to = date.fromisoformat(document["valid_to"])

    if not dates_cover_job(job_start, job_end, valid_from, valid_to):
        if valid_to < job_end:
            return BLOCKED, "EXPIRES_BEFORE_JOB_END"
        return BLOCKED, "NOT_VALID_AT_JOB_START"

    if document["type"] == "insurance":
        amount = document.get("coverage_amount")

        if amount is None:
            return NEEDS_REVIEW, "UNKNOWN_COVERAGE"

        if amount < policy["minimum_insurance_aud"]:
            return BLOCKED, "INSUFFICIENT_COVERAGE"

    # Checked last: a person can fix this by reviewing the document,
    # whereas the problems above need a new document.
    if document["review_status"] != "verified":
        return NEEDS_REVIEW, "UNVERIFIED_DOCUMENT"

    return None


def assess_job(job: dict, documents: list[dict], policy: dict) -> tuple[str, str]:
    """Return (status, reason) for a job, e.g. ("BLOCKED", "MISSING_DOCUMENT")."""
    problems = []

    if not job["contractor_ids"]:
        return BLOCKED, "NO_CONTRACTOR"
    
    for contractor_id in job["contractor_ids"]:
        for required_type in policy["required_types"]:
            candidates = find_documents(documents, contractor_id, required_type)

            if not candidates:
                problems.append((BLOCKED, "MISSING_DOCUMENT"))
                continue

            results = [check_document(document, job, policy) for document in candidates]
            if None in results:
                continue  # At least one document of this type is fine.

            # Every candidate has a problem; report the one closest to being fixed.
            problems.append(min(results, key=lambda result: SEVERITY[result[0]]))

    if not problems:
        return READY, "REQUIREMENTS_MET"

    # The job's status is its most serious problem.
    return max(problems, key=lambda problem: SEVERITY[problem[0]])


def load_demo() -> dict:
    """Load the synthetic demo data."""
    data_path = Path(__file__).parent / "data" / "demo" / "readiness.json"
    with data_path.open(encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    demo = load_demo()
    expected = {result["job_id"]: result for result in demo["expected_results"]}

    for job in demo["jobs"]:
        status, reason = assess_job(job, demo["documents"], demo["policy"])
        want = expected[job["id"]]
        mark = "ok" if (status, reason) == (want["status"], want["reason"]) else "MISMATCH"
        print(f"{job['id']}  {status:<13} {reason:<24} {mark}")
    
    unassigned_job = demo["jobs"][0].copy()
    unassigned_job["contractor_ids"] = []

    result = assess_job(unassigned_job, demo["documents"], demo["policy"])
    assert result == (BLOCKED, "NO_CONTRACTOR")
    print("No-contractor check passed.")

    insurance = demo["documents"][0].copy()
    insurance["coverage_amount"] = None

    result = check_document(insurance, demo["jobs"][0], demo["policy"])
    assert result == (NEEDS_REVIEW, "UNKNOWN_COVERAGE")
    print("Unknown-coverage check passed.")

    insurance["coverage_amount"] = 0

    result = check_document(insurance, demo["jobs"][0], demo["policy"])
    assert result == (BLOCKED, "INSUFFICIENT_COVERAGE")
    print("Zero-coverage check passed.")
