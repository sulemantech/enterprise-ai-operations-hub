import hashlib
import json

from sqlalchemy import Connection

import followup_repository


class ApprovalError(Exception):
    """The draft cannot be approved in its current state."""


def approval_fingerprint(recipient: str, subject: str, body: str) -> str:
    payload = json.dumps([recipient, subject, body])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def approve_draft(
    connection: Connection,
    draft_id: int,
    organisation_id: str,
    approved_by: str,
) -> dict | None:
    """Record approval of the draft's current text; the caller owns the transaction.

    Returns None when the draft does not exist for this organisation.
    """
    draft = followup_repository.lock_draft(connection, draft_id, organisation_id)
    if draft is None:
        return None
    if draft["status"] != "draft":
        raise ApprovalError(f"Draft {draft_id} is {draft['status']}, not awaiting approval")

    approval = followup_repository.insert_approval(connection, {
        "draft_id": draft_id,
        "organisation_id": organisation_id,
        "approved_by": approved_by,
        "recipient": draft["recipient"],
        "subject": draft["subject"],
        "body": draft["body"],
        "fingerprint": approval_fingerprint(
            draft["recipient"], draft["subject"], draft["body"]
        ),
    })
    followup_repository.set_draft_status(connection, draft_id, "approved")
    return approval


def authorise_execution(connection: Connection, draft_id: int, organisation_id: str) -> dict:
    """Return the approved message if it may be sent now, otherwise raise ApprovalError.

    The status alone is not trusted: the fingerprint of the current draft must
    still match the approval, so text changed by any path other than the edit
    endpoint is refused too. The returned text comes from the approval row,
    because that is what the manager actually approved.
    """
    draft = followup_repository.get_draft(connection, draft_id, organisation_id)
    if draft is None:
        raise ApprovalError(f"Draft {draft_id} not found")
    if draft["status"] != "approved":
        raise ApprovalError(f"Draft {draft_id} is {draft['status']}, not approved")

    approval = followup_repository.latest_approval(connection, draft_id, organisation_id)
    if approval is None:
        raise ApprovalError(f"Draft {draft_id} has no approval record")

    current = approval_fingerprint(draft["recipient"], draft["subject"], draft["body"])
    if current != approval["fingerprint"]:
        raise ApprovalError(f"Draft {draft_id} changed after it was approved")

    return {
        "draft_id": draft_id,
        "approval_id": approval["id"],
        "recipient": approval["recipient"],
        "subject": approval["subject"],
        "body": approval["body"],
    }
