from contextlib import nullcontext

import httpx
import pytest

import followup_delivery
from approval import ApprovalError
from followup_delivery import DeliveryError, send_approved_followup


APPROVED_MESSAGE = {
    "draft_id": 19,
    "approval_id": 31,
    "recipient": "contractor@example.invalid",
    "subject": "Updated insurance evidence",
    "body": "Please provide updated evidence.",
}


class FakeEngine:
    def begin(self):
        return nullcontext(object())


def configure_test_webhook(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(
        "N8N_FOLLOWUP_WEBHOOK_URL",
        "http://localhost:5678/webhook/followup-send",
    )
    monkeypatch.setenv("N8N_FOLLOWUP_WEBHOOK_TOKEN", "test-token")
    monkeypatch.setattr(followup_delivery, "get_engine", FakeEngine)
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "get_draft",
        lambda *_args: {"status": "approved"},
    )
    monkeypatch.setattr(
        followup_delivery,
        "authorise_execution",
        lambda *_args: dict(APPROVED_MESSAGE),
    )


def test_missing_n8n_settings_fail_before_claiming_delivery(monkeypatch):
    monkeypatch.delenv("N8N_FOLLOWUP_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("N8N_FOLLOWUP_WEBHOOK_TOKEN", raising=False)

    with pytest.raises(DeliveryError) as error:
        send_approved_followup(19, "ORG-DEMO")

    assert error.value.status_code == 503


def test_only_approved_test_recipient_can_reach_n8n(monkeypatch):
    configure_test_webhook(monkeypatch)
    message = {**APPROVED_MESSAGE, "recipient": "real@example.com"}
    monkeypatch.setattr(followup_delivery, "authorise_execution", lambda *_args: message)
    reserve_calls = []
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "reserve_delivery",
        lambda *args: reserve_calls.append(args),
    )

    with pytest.raises(DeliveryError) as error:
        send_approved_followup(19, "ORG-DEMO")

    assert error.value.status_code == 422
    assert reserve_calls == []


def test_unapproved_draft_is_never_sent(monkeypatch):
    configure_test_webhook(monkeypatch)
    monkeypatch.setattr(
        followup_delivery,
        "authorise_execution",
        lambda *_args: (_ for _ in ()).throw(ApprovalError("not approved")),
    )

    with pytest.raises(DeliveryError) as error:
        send_approved_followup(19, "ORG-DEMO")

    assert error.value.status_code == 409


def test_successful_test_delivery_uses_approved_payload_and_records_result(monkeypatch):
    configure_test_webhook(monkeypatch)
    record = {
        "id": 4,
        "draft_id": 19,
        "approval_id": 31,
        "status": "sending",
    }
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "reserve_delivery",
        lambda *_args: (record, True),
    )
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append((url, json, headers, timeout))
        return httpx.Response(
            200,
            json={"status": "sent", "draft_id": 19, "approval_id": 31},
        )

    monkeypatch.setattr(followup_delivery.httpx, "post", fake_post)
    completions = []

    def complete(_connection, delivery_id, draft_id, status, http_status,
                 response_payload, error_code):
        result = {
            **record,
            "status": status,
            "http_status": http_status,
            "response_payload": response_payload,
            "error_code": error_code,
        }
        completions.append((delivery_id, draft_id, result))
        return result

    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "complete_delivery",
        complete,
    )

    result = send_approved_followup(19, "ORG-DEMO")

    assert calls[0][1] == APPROVED_MESSAGE
    assert calls[0][2]["Authorization"] == "Bearer test-token"
    assert calls[0][2]["Idempotency-Key"] == "followup-approval-31"
    assert result["status"] == "sent"
    assert completions[0][2]["status"] == "sent"


def test_repeated_approval_delivery_does_not_call_n8n_twice(monkeypatch):
    configure_test_webhook(monkeypatch)
    existing = {
        "id": 4,
        "draft_id": 19,
        "approval_id": 31,
        "status": "sent",
    }
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "reserve_delivery",
        lambda *_args: (existing, False),
    )
    monkeypatch.setattr(
        followup_delivery.httpx,
        "post",
        lambda *_args, **_kwargs: pytest.fail("duplicate delivery attempted"),
    )

    result = send_approved_followup(19, "ORG-DEMO")

    assert result["status"] == "sent"
    assert result["already_processed"] is True


def test_completed_draft_returns_saved_delivery_without_reauthorising(monkeypatch):
    configure_test_webhook(monkeypatch)
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "get_draft",
        lambda *_args: {"status": "sent"},
    )
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "latest_approval",
        lambda *_args: {"id": 31},
    )
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "get_delivery",
        lambda *_args: {
            "id": 4,
            "draft_id": 19,
            "approval_id": 31,
            "status": "sent",
        },
    )
    monkeypatch.setattr(
        followup_delivery,
        "authorise_execution",
        lambda *_args: pytest.fail("already-sent draft must not be re-authorised"),
    )
    monkeypatch.setattr(
        followup_delivery.httpx,
        "post",
        lambda *_args, **_kwargs: pytest.fail("already-sent draft must not be resent"),
    )

    result = send_approved_followup(19, "ORG-DEMO")

    assert result["status"] == "sent"
    assert result["already_processed"] is True


def test_delivery_endpoint_uses_authenticated_organisation(client, monkeypatch):
    import followup_delivery

    calls = []

    def fake_send(draft_id, organisation_id):
        calls.append((draft_id, organisation_id))
        return {
            "delivery_id": 4,
            "draft_id": draft_id,
            "approval_id": 31,
            "status": "sent",
            "already_processed": False,
        }

    monkeypatch.setattr(followup_delivery, "send_approved_followup", fake_send)
    response = client.post("/followups/19/send")

    assert response.status_code == 200
    assert calls == [(19, "ORG-DEMO")]


def test_timeout_is_recorded_unknown_and_not_reported_as_success(monkeypatch):
    configure_test_webhook(monkeypatch)
    record = {
        "id": 4,
        "draft_id": 19,
        "approval_id": 31,
        "status": "sending",
    }
    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "reserve_delivery",
        lambda *_args: (record, True),
    )
    monkeypatch.setattr(
        followup_delivery.httpx,
        "post",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(httpx.TimeoutException("timeout")),
    )
    completions = []

    def complete(_connection, _delivery_id, _draft_id, status, http_status,
                 response_payload, error_code):
        completions.append((status, http_status, response_payload, error_code))
        return {**record, "status": status}

    monkeypatch.setattr(
        followup_delivery.followup_repository,
        "complete_delivery",
        complete,
    )

    result = send_approved_followup(19, "ORG-DEMO")

    assert result["status"] == "unknown"
    assert completions[0][0] == "unknown"
    assert completions[0][3] == "TimeoutException"
