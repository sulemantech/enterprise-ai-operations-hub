from sqlalchemy import Connection

import repository
from db import get_engine
from readiness import assess_job


def get_job_assessment(job_id: str, organisation_id: str) -> dict:
    with get_engine().connect() as conn:
        return assess_job_by_id(conn, job_id, organisation_id)


def assess_job_by_id(conn: Connection, job_id: str, organisation_id: str) -> dict:
    """Assess one job using the caller's connection (and transaction)."""
    job = repository.get_job(conn, job_id, organisation_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")

    documents = repository.documents_for(
        connection=conn,
        contractor_ids=job["contractor_ids"],
    )
    policy = repository.get_policy(conn, job["policy_id"], job["policy_version"])

    status, reason = assess_job(job, documents, policy)

    return {
        "job": job,
        "documents": documents,
        "policy": policy,
        "status": status,
        "reason": reason,
    }
