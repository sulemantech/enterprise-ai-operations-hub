"""Approval-gated, test-recipient-only delivery to the n8n webhook."""

from urllib.parse import urlparse

import httpx
from sqlalchemy import Connection

import followup_repository
from approval import ApprovalError, authorise_execution
from db import get_engine

TEST_RECIPIENT_SUFFIX = "@example.invalid"
REQUEST_TIMEOUT_SECONDS = 10.0


class DeliveryError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


def _webhook_configuration() -> tuple[str, str]:
    import os

    url = os.environ.get("N8N_FOLLOWUP_WEBHOOK_URL", "").strip()
    token = os.environ.get("N8N_FOLLOWUP_WEBHOOK_TOKEN", "").strip()
    if not url or not token:
        raise DeliveryError("n8n follow-up delivery is not configured", 503)

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DeliveryError("n8n webhook URL must be an absolute HTTP(S) URL", 503)
    if os.environ.get("APP_ENV", "development").lower() != "development":
        if parsed.scheme != "https":
            raise DeliveryError("n8n webhook must use HTTPS outside development", 503)
        if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
            raise DeliveryError("n8n webhook must not use loopback outside development", 503)
    return url, token


def _public_delivery_record(record: dict, already_processed: bool) -> dict:
    return {
        "delivery_id": record["id"],
        "draft_id": record["draft_id"],
        "approval_id": record["approval_id"],
        "status": record["status"],
        "already_processed": already_processed,
    }


def send_approved_followup(draft_id: int, organisation_id: str) -> dict:
    webhook_url, webhook_token = _webhook_configuration()

    with get_engine().begin() as connection:
        current_draft = followup_repository.get_draft(
            connection, draft_id, organisation_id
        )
        if current_draft is None:
            raise DeliveryError(f"Draft {draft_id} not found", 404)
        if current_draft["status"] in {
            "sending", "sent", "delivery_rejected", "delivery_unknown"
        }:
            approval = followup_repository.latest_approval(
                connection, draft_id, organisation_id
            )
            delivery = (
                followup_repository.get_delivery(
                    connection, approval["id"], organisation_id
                )
                if approval is not None
                else None
            )
            if delivery is not None:
                return _public_delivery_record(delivery, already_processed=True)
            raise DeliveryError("Delivery state requires reconciliation", 409)

        try:
            message = authorise_execution(connection, draft_id, organisation_id)
        except ApprovalError as error:
            raise DeliveryError(str(error), 409) from error

        if not message["recipient"].lower().endswith(TEST_RECIPIENT_SUFFIX):
            raise DeliveryError("Only @example.invalid test recipients are allowed", 422)

        idempotency_key = f"followup-approval-{message['approval_id']}"
        record, created = followup_repository.reserve_delivery(
            connection,
            message["approval_id"],
            draft_id,
            organisation_id,
            idempotency_key,
        )

    if not created:
        return _public_delivery_record(record, already_processed=True)

    payload = {
        "draft_id": draft_id,
        "approval_id": message["approval_id"],
        "recipient": message["recipient"],
        "subject": message["subject"],
        "body": message["body"],
    }

    try:
        response = httpx.post(
            webhook_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {webhook_token}",
                "Idempotency-Key": idempotency_key,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response_payload = response.json()
    except (httpx.RequestError, ValueError) as error:
        status = "unknown"
        http_status = None
        response_payload = None
        error_code = type(error).__name__
    else:
        http_status = response.status_code
        expected_response = (
            response.is_success
            and isinstance(response_payload, dict)
            and response_payload.get("status") == "sent"
            and response_payload.get("draft_id") == draft_id
            and response_payload.get("approval_id") == message["approval_id"]
        )
        rejected = (
            response.status_code == 422
            and isinstance(response_payload, dict)
            and response_payload.get("status") == "rejected"
        )
        if expected_response:
            status = "sent"
            error_code = None
        elif rejected:
            status = "rejected"
            error_code = "n8n_rejected"
        else:
            status = "unknown"
            error_code = "unexpected_n8n_response"
        response_payload = {
            key: response_payload.get(key)
            for key in ("status", "draft_id", "approval_id", "reason")
            if isinstance(response_payload, dict) and key in response_payload
        }

    with get_engine().begin() as connection:
        completed = followup_repository.complete_delivery(
            connection,
            record["id"],
            draft_id,
            status,
            http_status,
            response_payload,
            error_code,
        )

    return _public_delivery_record(completed, already_processed=False)
