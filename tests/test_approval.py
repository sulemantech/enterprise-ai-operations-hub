"""Tests that approval records the exact message and that edits undo it."""

import pytest
from sqlalchemy import text

from approval import ApprovalError, approval_fingerprint, approve_draft, authorise_execution
from followup_repository import get_draft, latest_approval, update_draft_text
from followup_service import create_followup

ORG = "ORG-DEMO"


@pytest.fixture
def draft(db_connection):
    return create_followup(db_connection, "JOB-102", ORG)


def test_approval_copies_the_exact_message(db_connection, draft):
    approval = approve_draft(db_connection, draft["id"], ORG, "demo-manager")

    assert (approval["recipient"], approval["subject"], approval["body"]) == (
        draft["recipient"], draft["subject"], draft["body"]
    )
    assert approval["fingerprint"] == approval_fingerprint(
        draft["recipient"], draft["subject"], draft["body"]
    )
    assert approval["approved_by"] == "demo-manager"
    assert get_draft(db_connection, draft["id"], ORG)["status"] == "approved"


def test_approving_twice_is_refused(db_connection, draft):
    approve_draft(db_connection, draft["id"], ORG, "demo-manager")

    with pytest.raises(ApprovalError):
        approve_draft(db_connection, draft["id"], ORG, "demo-manager")


def test_editing_after_approval_returns_to_draft(db_connection, draft):
    approve_draft(db_connection, draft["id"], ORG, "demo-manager")

    edited = update_draft_text(db_connection, draft["id"], ORG, "New subject", "New body")

    assert edited["status"] == "draft"


def test_other_organisation_cannot_approve(db_connection, draft):
    assert approve_draft(db_connection, draft["id"], "ORG-OTHER", "someone") is None


def test_unapproved_draft_cannot_execute(db_connection, draft):
    with pytest.raises(ApprovalError, match="not approved"):
        authorise_execution(db_connection, draft["id"], ORG)


def test_approved_draft_can_execute_with_approved_text(db_connection, draft):
    approval = approve_draft(db_connection, draft["id"], ORG, "demo-manager")

    message = authorise_execution(db_connection, draft["id"], ORG)

    assert message["approval_id"] == approval["id"]
    assert (message["recipient"], message["body"]) == (draft["recipient"], draft["body"])


def test_draft_edited_after_approval_cannot_execute(db_connection, draft):
    approve_draft(db_connection, draft["id"], ORG, "demo-manager")
    update_draft_text(db_connection, draft["id"], ORG, "New subject", "New body")

    with pytest.raises(ApprovalError, match="not approved"):
        authorise_execution(db_connection, draft["id"], ORG)


def test_text_changed_outside_the_api_cannot_execute(db_connection, draft):
    approve_draft(db_connection, draft["id"], ORG, "demo-manager")
    db_connection.execute(
        text("UPDATE followup_drafts SET body = 'tampered' WHERE id = :id"), {"id": draft["id"]}
    )

    with pytest.raises(ApprovalError, match="changed after it was approved"):
        authorise_execution(db_connection, draft["id"], ORG)


def test_approve_endpoint(client, db_connection):
    draft = client.post("/assessments/JOB-102/followups").json()

    first = client.post(f"/followups/{draft['id']}/approve")
    second = client.post(f"/followups/{draft['id']}/approve")

    assert first.status_code == 200 and first.json()["status"] == "approved"
    assert second.status_code == 409
    assert client.post("/followups/999999/approve").status_code == 404
    approval = latest_approval(db_connection, draft["id"], ORG)
    assert approval["approved_by"] == "https://identity.example.test/|test-manager"


def test_send_endpoint_passes_session_organisation_to_delivery_service(client, monkeypatch):
    import followup_delivery

    calls = []

    def fake_send(draft_id, organisation_id):
        calls.append((draft_id, organisation_id))
        return {
            "delivery_id": 1,
            "draft_id": draft_id,
            "approval_id": 2,
            "status": "sent",
            "already_processed": False,
        }

    monkeypatch.setattr(followup_delivery, "send_approved_followup", fake_send)

    response = client.post("/followups/23/send")

    assert response.status_code == 200
    assert calls == [(23, ORG)]
