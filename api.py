"""HTTP layer: receives requests and returns what readiness.py decides.

No readiness rules live here, so the UI, the AI tool and n8n all get
the same answer from the same function.
"""

from collections.abc import Iterator
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Connection

import repository
from db import get_engine
from readiness import assess_job

MAX_WINDOW_DAYS = 31

app = FastAPI(title="Contractor readiness (demo)")


class Contractor(BaseModel):
    id: str
    name: str
    trade: str | None


class Assessment(BaseModel):
    job_id: str
    title: str | None
    site: str | None
    start_date: date
    end_date: date
    policy_id: str
    contractors: list[Contractor]
    status: str
    reason: str


def get_connection() -> Iterator[Connection]:
    """Give each request its own database connection, closed afterwards."""
    with get_engine().connect() as connection:
        yield connection


def assess_many(connection: Connection, jobs: list[dict]) -> list[Assessment]:
    """Assess jobs using three queries in total, however many jobs there are."""
    contractor_ids = sorted({cid for job in jobs for cid in job["contractor_ids"]})
    documents = repository.documents_for(connection, contractor_ids)
    contractors = repository.contractors_by_id(connection, contractor_ids)
    policies = repository.all_policies(connection)

    assessments = []
    for job in jobs:
        job_documents = [d for d in documents if d["contractor_id"] in job["contractor_ids"]]
        policy = policies[(job["policy_id"], job["policy_version"])]
        status, reason = assess_job(job, job_documents, policy)
        assessments.append(
            Assessment(
                job_id=job["id"],
                title=job["title"],
                site=job["site"],
                start_date=job["start_date"],
                end_date=job["end_date"],
                policy_id=job["policy_id"],
                contractors=[contractors[cid] for cid in job["contractor_ids"]],
                status=status,
                reason=reason,
            )
        )
    return assessments


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/assessments", response_model=list[Assessment])
def get_assessments(
    start: date = Query(description="First day of the window, e.g. 2026-10-05"),
    end: date = Query(description="Last day of the window, inclusive, e.g. 2026-10-11"),
    connection: Connection = Depends(get_connection),
):
    # FastAPI already rejects missing or badly formatted dates (422).
    # These checks cover dates that are valid on their own but not together.
    if end < start:
        raise HTTPException(status_code=422, detail="end must be on or after start")
    if (end - start).days + 1 > MAX_WINDOW_DAYS:
        raise HTTPException(
            status_code=422,
            detail=f"window must be at most {MAX_WINDOW_DAYS} days",
        )

    return assess_many(connection, repository.jobs_in_window(connection, start, end))


@app.get("/assessments/{job_id}", response_model=Assessment)
def get_assessment(job_id: str, connection: Connection = Depends(get_connection)):
    job = repository.get_job(connection, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return assess_many(connection, [job])[0]
