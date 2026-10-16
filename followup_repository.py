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
