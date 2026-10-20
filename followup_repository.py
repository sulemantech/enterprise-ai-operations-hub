from sqlalchemy import Connection, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB


def save_draft(connection: Connection, draft: dict) -> int:
    """Insert a new draft; the caller owns the transaction."""
    statement = text("""
        INSERT INTO followup_drafts (
            organisation_id, job_id, contractor_id,
            recipient, subject, body,
            assessment_status, reason,
            policy_id, policy_version,
            evidence_ids, source_snapshot
        ) VALUES (
            :organisation_id, :job_id, :contractor_id,
            :recipient, :subject, :body,
            :assessment_status, :reason,
            :policy_id, :policy_version,
            :evidence_ids, :source_snapshot
        )
        RETURNING id
    """).bindparams(
        bindparam("evidence_ids", type_=JSONB),
        bindparam("source_snapshot", type_=JSONB),
    )

    result = connection.execute(statement, draft)
    return result.scalar_one()


def get_draft(
    connection: Connection,
    draft_id: int,
    organisation_id: str,
) -> dict | None:
    row = connection.execute(
        text("""
            SELECT *
            FROM followup_drafts
            WHERE id = :draft_id
              AND organisation_id = :organisation_id
        """),
        {
            "draft_id": draft_id,
            "organisation_id": organisation_id,
        },
    ).mappings().first()

    return dict(row) if row is not None else None


def latest_status_by_job(
    connection: Connection,
    job_ids: list[str],
    organisation_id: str,
) -> dict[str, str]:
    if not job_ids:
        return {}

    rows = connection.execute(
        text("""
            SELECT DISTINCT ON (job_id) job_id, status
            FROM followup_drafts
            WHERE organisation_id = :organisation_id
              AND job_id IN :job_ids
            ORDER BY job_id, created_at DESC, id DESC
        """).bindparams(bindparam("job_ids", expanding=True)),
        {"organisation_id": organisation_id, "job_ids": job_ids},
    ).mappings().all()
    return {row["job_id"]: row["status"] for row in rows}

def update_draft_text(
    connection: Connection,
    draft_id: int,
    organisation_id: str,
    subject: str,
    body: str,
) -> dict | None:
    """Edit the wording of a draft or approved message.

    Editing an approved message returns it to 'draft': the approval was for
    the old text, so it must be approved again before it can be sent.
    """
    row = connection.execute(
        text("""
            UPDATE followup_drafts
            SET subject = :subject, body = :body, status = 'draft'
            WHERE id = :draft_id
              AND organisation_id = :organisation_id
              AND status IN ('draft', 'approved')
            RETURNING *
        """),
        {
            "draft_id": draft_id,
            "organisation_id": organisation_id,
            "subject": subject,
            "body": body,
        },
    ).mappings().first()

    return dict(row) if row is not None else None


def lock_draft(
    connection: Connection,
    draft_id: int,
    organisation_id: str,
) -> dict | None:
    """Read a draft and lock its row until the caller's transaction ends,
    so a concurrent edit cannot slip in between reading and approving."""
    row = connection.execute(
        text("""
            SELECT *
            FROM followup_drafts
            WHERE id = :draft_id
              AND organisation_id = :organisation_id
            FOR UPDATE
        """),
        {"draft_id": draft_id, "organisation_id": organisation_id},
    ).mappings().first()

    return dict(row) if row is not None else None


def insert_approval(connection: Connection, approval: dict) -> dict:
    row = connection.execute(
        text("""
            INSERT INTO followup_approvals (
                draft_id, organisation_id, approved_by,
                recipient, subject, body, fingerprint
            ) VALUES (
                :draft_id, :organisation_id, :approved_by,
                :recipient, :subject, :body, :fingerprint
            )
            RETURNING *
        """),
        approval,
    ).mappings().one()

    return dict(row)


def set_draft_status(connection: Connection, draft_id: int, status: str) -> None:
    connection.execute(
        text("UPDATE followup_drafts SET status = :status WHERE id = :draft_id"),
        {"draft_id": draft_id, "status": status},
    )


def latest_approval(
    connection: Connection,
    draft_id: int,
    organisation_id: str,
) -> dict | None:
    row = connection.execute(
        text("""
            SELECT *
            FROM followup_approvals
            WHERE draft_id = :draft_id
              AND organisation_id = :organisation_id
            ORDER BY approved_at DESC, id DESC
            LIMIT 1
        """),
        {"draft_id": draft_id, "organisation_id": organisation_id},
    ).mappings().first()

    return dict(row) if row is not None else None


def reserve_delivery(connection: Connection, approval_id: int, draft_id: int,
                     organisation_id: str, idempotency_key: str) -> tuple[dict, bool]:
    row = connection.execute(
        text("""
            INSERT INTO followup_deliveries (
                draft_id, approval_id, organisation_id, idempotency_key, status
            ) VALUES (
                :draft_id, :approval_id, :organisation_id, :idempotency_key, 'sending'
            )
            ON CONFLICT (approval_id) DO NOTHING
            RETURNING *
        """),
        {
            "draft_id": draft_id,
            "approval_id": approval_id,
            "organisation_id": organisation_id,
            "idempotency_key": idempotency_key,
        },
    ).mappings().first()
    if row is not None:
        connection.execute(
            text("UPDATE followup_drafts SET status = 'sending' WHERE id = :draft_id"),
            {"draft_id": draft_id},
        )
        return dict(row), True

    existing = connection.execute(
        text("""
            SELECT * FROM followup_deliveries
            WHERE approval_id = :approval_id
              AND organisation_id = :organisation_id
        """),
        {"approval_id": approval_id, "organisation_id": organisation_id},
    ).mappings().one()
    return dict(existing), False


def get_delivery(connection: Connection, approval_id: int,
                 organisation_id: str) -> dict | None:
    row = connection.execute(
        text("""
            SELECT * FROM followup_deliveries
            WHERE approval_id = :approval_id
              AND organisation_id = :organisation_id
        """),
        {"approval_id": approval_id, "organisation_id": organisation_id},
    ).mappings().first()
    return dict(row) if row is not None else None


def complete_delivery(connection: Connection, delivery_id: int, draft_id: int,
                      status: str, http_status: int | None,
                      response_payload: dict | None, error_code: str | None) -> dict:
    result = connection.execute(
        text("""
            UPDATE followup_deliveries
            SET status = :status,
                http_status = :http_status,
                response_payload = :response_payload,
                error_code = :error_code,
                updated_at = now()
            WHERE id = :delivery_id
            RETURNING *
        """).bindparams(bindparam("response_payload", type_=JSONB)),
        {
            "delivery_id": delivery_id,
            "status": status,
            "http_status": http_status,
            "response_payload": response_payload,
            "error_code": error_code,
        },
    ).mappings().one()
    draft_status = {
        "sent": "sent",
        "rejected": "delivery_rejected",
        "unknown": "delivery_unknown",
    }[status]
    connection.execute(
        text("""
            UPDATE followup_drafts SET status = :status
            WHERE id = :draft_id AND status = 'sending'
        """),
        {"draft_id": draft_id, "status": draft_status},
    )
    return dict(result)
