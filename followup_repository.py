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
    """Edit the wording of a draft that has not left the draft status."""
    row = connection.execute(
        text("""
            UPDATE followup_drafts
            SET subject = :subject, body = :body
            WHERE id = :draft_id
              AND organisation_id = :organisation_id
              AND status = 'draft'
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
