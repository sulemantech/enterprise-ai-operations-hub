"""The generated demo data must be repeatable and show every kind of result."""

import demo_data
from readiness import assess_job
from seed import build_dataset


def test_generation_is_repeatable():
    assert demo_data.generate() == demo_data.generate()


def test_every_result_type_appears():
    data = build_dataset(include_generated=True)
    policies = {(p["id"], p["version"]): p for p in data["policies"]}

    reasons = {
        assess_job(job, data["documents"], policies[(job["policy_id"], job["policy_version"])])[1]
        for job in data["jobs"]
    }

    assert reasons == {
        "REQUIREMENTS_MET",
        "EXPIRES_BEFORE_JOB_END",
        "NOT_VALID_AT_JOB_START",
        "MISSING_DOCUMENT",
        "INSUFFICIENT_COVERAGE",
        "UNVERIFIED_DOCUMENT",
    }


def test_demo_emails_can_never_be_delivered():
    data = build_dataset(include_generated=True)

    assert all(c["email"].endswith("@example.invalid") for c in data["contractors"])
