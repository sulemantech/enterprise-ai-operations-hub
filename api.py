"""HTTP layer: receives requests and returns what readiness.py decides.

No readiness rules live here, so the UI, the AI tool and n8n all get
the same answer from the same function.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from readiness import assess_job, load_demo

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
def get_assessments():
    demo = load_demo()
    return [assess(job, demo) for job in demo["jobs"]]


@app.get("/assessments/{job_id}", response_model=Assessment)
def get_assessment(job_id: str):
    demo = load_demo()
    job = next((job for job in demo["jobs"] if job["id"] == job_id), None)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return assess(job, demo)
