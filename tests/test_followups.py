"""Tests that follow-up drafts are stored, visible and editable, and never sent."""

from sqlalchemy import text


def create_draft(client, job_id="JOB-102"):
    return client.post(f"/assessments/{job_id}/followups")


def test_blocked_insurance_job_gets_a_draft(client):
    response = create_draft(client)

    assert response.status_code == 201
    draft = response.json()
    assert draft["status"] == "draft"
    assert draft["job_id"] == "JOB-102"
    assert draft["recipient"] == "two@example.invalid"
    assert draft["reason"] == "EXPIRES_BEFORE_JOB_END"
    assert draft["evidence_ids"] == ["DOC-003"]
    assert "2026-10-06" in draft["body"] and "2026-10-09" in draft["body"]


def test_draft_can_be_read_back(client):
    draft = create_draft(client).json()

    response = client.get(f"/followups/{draft['id']}")

    assert response.status_code == 200
    assert response.json() == draft


def test_ready_job_gets_no_draft(client):
    response = create_draft(client, "JOB-101")

    assert response.status_code == 409
    assert "no missing-evidence follow-up is needed" in response.json()["detail"]


def test_unsupported_reason_gets_no_draft(client):
    response = create_draft(client, "JOB-103")

    assert response.status_code == 409
    assert "does not yet support reason" in response.json()["detail"]


def test_unknown_job_and_draft_return_404(client):
    assert create_draft(client, "JOB-999").status_code == 404
    assert client.get("/followups/999999").status_code == 404


def test_editing_changes_wording_but_not_recipient(client):
    draft = create_draft(client).json()

    response = client.patch(
        f"/followups/{draft['id']}",
        json={"subject": "Updated subject", "body": "Updated body"},
    )

    assert response.status_code == 200
    edited = response.json()
    assert (edited["subject"], edited["body"]) == ("Updated subject", "Updated body")
    assert edited["recipient"] == draft["recipient"]
    assert edited["status"] == "draft"


def test_empty_edit_is_rejected(client):
    draft = create_draft(client).json()

    response = client.patch(f"/followups/{draft['id']}", json={"subject": "", "body": "x"})

    assert response.status_code == 422


def test_sent_messages_cannot_be_edited(client, db_connection):
    draft = create_draft(client).json()
    db_connection.execute(
        text("UPDATE followup_drafts SET status = 'sent' WHERE id = :id"), {"id": draft["id"]}
    )

    response = client.patch(f"/followups/{draft['id']}", json={"subject": "s", "body": "b"})

    assert response.status_code == 409
