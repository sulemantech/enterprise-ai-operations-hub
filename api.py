"""HTTP layer: receives requests and returns what readiness.py decides.

No readiness rules live here, so the UI, the AI tool and n8n all get
the same answer from the same function.
"""

from datetime import date

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from readiness import assess_job, job_overlaps_window, load_demo

MAX_WINDOW_DAYS = 31

app = FastAPI(title="Contractor readiness (demo)")


class Assessment(BaseModel):
    job_id: str
    status: str
    reason: str


def assess(job: dict, demo: dict) -> Assessment:
    status, reason = assess_job(job, demo["documents"], demo["policy"])
    return Assessment(job_id=job["id"], status=status, reason=reason)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/assessments", response_model=list[Assessment])
def get_assessments(
    start: date = Query(description="First day of the window, e.g. 2026-10-05"),
    end: date = Query(description="Last day of the window, inclusive, e.g. 2026-10-11"),
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

    demo = load_demo()
    return [
        assess(job, demo)
        for job in demo["jobs"]
        if job_overlaps_window(job, start, end)
    ]


@app.get("/assessments/{job_id}", response_model=Assessment)
def get_assessment(job_id: str):
    demo = load_demo()
    job = next((job for job in demo["jobs"] if job["id"] == job_id), None)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return assess(job, demo)
