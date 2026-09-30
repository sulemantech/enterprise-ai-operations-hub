"""Read readiness records from PostgreSQL.

Records are returned in the same shape as data/demo/readiness.json
(dates as ISO strings, jobs with a contractor_ids list), so the rules in
readiness.py work unchanged whichever source the data comes from.
"""

from datetime import date

from sqlalchemy import Connection, text


def _job_record(row) -> dict:
    return {
        "id": row.id,
        "organisation_id": row.organisation_id,
        "status": row.status,
        "title": row.title,
        "site": row.site,
        "contractor_ids": list(row.contractor_ids),
        "start_date": row.start_date.isoformat(),
        "end_date": row.end_date.isoformat(),
        "policy_id": row.policy_id,
        "policy_version": row.policy_version,
    }


# One row per job, with its contractors gathered into an array.
_JOBS_SQL = """
    SELECT j.id, j.organisation_id, j.status, j.title, j.site, j.start_date, j.end_date,
           j.policy_id, j.policy_version,
           COALESCE(
               array_agg(jc.contractor_id ORDER BY jc.contractor_id)
                   FILTER (WHERE jc.contractor_id IS NOT NULL),
               '{}'
           ) AS contractor_ids
    FROM jobs j
    LEFT JOIN job_contractors jc ON jc.job_id = j.id
"""


def jobs_in_window(connection: Connection, start: date, end: date) -> list[dict]:
    """Return jobs with at least one day inside the window, inclusively."""
    rows = connection.execute(
        text(_JOBS_SQL + """
            WHERE j.start_date <= :end AND j.end_date >= :start
            GROUP BY j.id
            ORDER BY j.start_date, j.id
        """),
        {"start": start, "end": end},
    )
    return [_job_record(row) for row in rows]


def get_job(connection: Connection, job_id: str) -> dict | None:
    row = connection.execute(
        text(_JOBS_SQL + " WHERE j.id = :job_id GROUP BY j.id"),
        {"job_id": job_id},
    ).first()
    return _job_record(row) if row else None


def documents_for(connection: Connection, contractor_ids: list[str]) -> list[dict]:
    rows = connection.execute(
        text("""
            SELECT id, contractor_id, type, review_status, valid_from, valid_to,
                   coverage_amount, currency
            FROM documents
            WHERE contractor_id = ANY(:contractor_ids)
            ORDER BY id
        """),
        {"contractor_ids": contractor_ids},
    )
    return [
        {
            **row._asdict(),
            "valid_from": row.valid_from.isoformat(),
            "valid_to": row.valid_to.isoformat(),
        }
        for row in rows
    ]


def get_policy(connection: Connection, policy_id: str, version: int) -> dict:
    row = connection.execute(
        text("""
            SELECT id, version, required_types, minimum_insurance_aud
            FROM policies
            WHERE id = :id AND version = :version
        """),
        {"id": policy_id, "version": version},
    ).one()
    return {**row._asdict(), "required_types": list(row.required_types)}


def contractors_by_id(connection: Connection, contractor_ids: list[str]) -> dict[str, dict]:
    rows = connection.execute(
        text("SELECT id, name, email, trade FROM contractors WHERE id = ANY(:ids)"),
        {"ids": contractor_ids},
    )
    return {row.id: row._asdict() for row in rows}


def all_policies(connection: Connection) -> dict[tuple[str, int], dict]:
    """All policies keyed by (id, version). There are few, so load them once."""
    rows = connection.execute(
        text("SELECT id, version, required_types, minimum_insurance_aud FROM policies")
    )
    return {
        (row.id, row.version): {**row._asdict(), "required_types": list(row.required_types)}
        for row in rows
    }
