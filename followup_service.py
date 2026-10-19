from sqlalchemy import Connection

from assessment_service import assess_job_by_id
from readiness import find_documents, check_document
from repository import contractors_by_id
from followup_repository import save_draft


def prepare_followup(connection: Connection, job_id: str, organisation_id: str) -> dict:
    assessment = assess_job_by_id(connection, job_id, organisation_id)
    if assessment["status"] == "READY":
        raise ValueError(
            f"Job {job_id} meets the configured requirements; "
            "no missing-evidence follow-up is needed."
        )
    if assessment["reason"] != "EXPIRES_BEFORE_JOB_END":
        raise ValueError(
            f"Follow-up drafting does not yet support reason: "
            f"{assessment['reason']}"
        )
    job = assessment["job"]
    contractor_ids = job["contractor_ids"]

    if len(contractor_ids) != 1:
        raise ValueError(
            "Follow-up drafting currently requires exactly one assigned contractor."
        )

    contractor_id = contractor_ids[0]
    insurance_documents = find_documents(
        assessment["documents"],
        contractor_id,
        "insurance",
    )

    if not insurance_documents:
        raise ValueError(
            "No insurance document found; an insurance-expiry draft "
            "cannot be prepared."
        )
    insurance_results = [
        check_document(document, job, assessment["policy"])
        for document in insurance_documents
    ]

    if None in insurance_results:
        raise ValueError(
            "An insurance document already meets the requirements; "
            "an insurance-expiry follow-up is not needed."
        )

    if not all(
        result == ("BLOCKED", "EXPIRES_BEFORE_JOB_END")
        for result in insurance_results
    ):
        raise ValueError(
            "Insurance has other issues that need review before "
            "using the expiry follow-up template."
        )
    contractors = contractors_by_id(connection, [contractor_id])

    contractor = contractors.get(contractor_id)

    if contractor is None:
        raise ValueError(f"Contractor {contractor_id} not found.")

    recipient = (contractor.get("email") or "").strip()

    if not recipient:
        raise ValueError(
            f"Contractor {contractor_id} has no email address."
        )
    subject = f"Insurance evidence required for {job['id']}"

    body = (
        f"Hello {contractor['name']},\n\n"
        f"Please provide updated insurance evidence for "
        f"{job['title']} ({job['id']}) at {job['site']}.\n\n"
        f"The insurance evidence currently recorded ends before "
        f"the job end date. Please provide evidence covering "
        f"the full assigned period, from {job['start_date']} "
        f"through {job['end_date']}, inclusive.\n\n"
        "The submitted evidence will need review before "
        "the job is reassessed.\n\n"
        "Thank you."
    )

    return {
        "status": "draft",
        "job_id": job["id"],
        "organisation_id": job["organisation_id"],
        "contractor_id": contractor_id,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "assessment_status": assessment["status"],
        "reason": assessment["reason"],
        "policy_id": job["policy_id"],
        "policy_version": job["policy_version"],
        "source_snapshot": {
            "assessment": assessment,
            "contractor": {
                "id": contractor["id"],
                "name": contractor["name"],
                "email": recipient,
            },
        },
        "evidence_ids": [
            document["id"] for document in insurance_documents
        ],
    }

def create_followup(connection: Connection, job_id: str, organisation_id: str) -> dict:
    """Prepare and store a draft; the caller owns the transaction."""
    draft = prepare_followup(connection, job_id, organisation_id)
    draft_id = save_draft(connection, draft)
    return {"id": draft_id, **draft}
