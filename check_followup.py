from unittest.mock import MagicMock, patch
from copy import deepcopy

from followup_service import prepare_followup

connection = MagicMock()

assessment = {
    "status": "BLOCKED",
    "reason": "EXPIRES_BEFORE_JOB_END",
    "job": {
        "id": "JOB-MULTI",
        "contractor_ids": ["CON-001", "CON-002"],
    },
}

with patch(
    "followup_service.assess_job_by_id",
    return_value=assessment,
), patch("followup_service.contractors_by_id") as mock_contractors:
    try:
        prepare_followup(connection, "JOB-MULTI")
    except ValueError as error:
        assert "exactly one assigned contractor" in str(error)
    else:
        raise AssertionError("Expected multiple contractors to be rejected.")

    mock_contractors.assert_not_called()

print("Multiple-contractor guard passed.")

assessment_with_valid_insurance = {
    "status": "BLOCKED",
    "reason": "EXPIRES_BEFORE_JOB_END",
    "job": {
        "id": "JOB-TEST",
        "contractor_ids": ["CON-002"],
        "start_date": "2026-10-06",
        "end_date": "2026-10-09",
    },
    "policy": {"minimum_insurance_aud": 5_000_000},
    "documents": [
        {
            "id": "DOC-INSURANCE",
            "contractor_id": "CON-002",
            "type": "insurance",
            "valid_from": "2026-01-01",
            "valid_to": "2026-12-31",
            "coverage_amount": 10_000_000,
            "review_status": "verified",
        },
        {
            "id": "DOC-LICENCE",
            "contractor_id": "CON-002",
            "type": "trade_licence",
            "valid_from": "2026-01-01",
            "valid_to": "2026-10-07",
            "review_status": "verified",
        },
    ],
}

with patch(
    "followup_service.assess_job_by_id",
    return_value=assessment_with_valid_insurance,
), patch("followup_service.contractors_by_id") as mock_contractors:
    try:
        prepare_followup(connection, "JOB-TEST")
    except ValueError as error:
        assert "insurance document already meets" in str(error)
    else:
        raise AssertionError("Expected valid insurance to prevent the draft.")

    mock_contractors.assert_not_called()

print("Valid insurance prevents expiry follow-up.")

expired_assessment = deepcopy(assessment_with_valid_insurance)
expired_assessment["documents"][0]["valid_to"] = "2026-10-07"

with patch(
    "followup_service.assess_job_by_id",
    return_value=expired_assessment,
), patch(
    "followup_service.contractors_by_id",
    return_value={
        "CON-002": {
            "id": "CON-002",
            "name": "Demo Electrical Two",
            "email": "",
        }
    },
):
    try:
        prepare_followup(connection, "JOB-TEST")
    except ValueError as error:
        assert "has no email address" in str(error)
    else:
        raise AssertionError("Expected missing email to prevent the draft.")

print("Missing email prevents follow-up draft.")


draft_assessment = deepcopy(expired_assessment)
draft_assessment["job"].update({
    "organisation_id": "ORG-DEMO",
    "title": "Office lighting retrofit",
    "site": "North Sydney",
    "policy_id": "DEMO-CONTRACTOR-001",
    "policy_version": 1,
})

with patch(
    "followup_service.assess_job_by_id",
    return_value=draft_assessment,
), patch(
    "followup_service.contractors_by_id",
    return_value={
        "CON-002": {
            "id": "CON-002",
            "name": "Demo Electrical Two",
            "email": "two@example.invalid",
        }
    },
):
    draft = prepare_followup(connection, "JOB-TEST")

assert draft["status"] == "draft"
assert draft["job_id"] == "JOB-TEST"
assert draft["contractor_id"] == "CON-002"
assert draft["recipient"] == "two@example.invalid"
assert draft["assessment_status"] == "BLOCKED"
assert draft["reason"] == "EXPIRES_BEFORE_JOB_END"
assert draft["evidence_ids"] == ["DOC-INSURANCE"]
assert "2026-10-06" in draft["body"]
assert "2026-10-09" in draft["body"]

print("Eligible insurance-expiry draft created.")