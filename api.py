"""HTTP layer: receives requests and returns what readiness.py decides.

No readiness rules live here, so the UI, the AI tool and n8n all get
the same answer from the same function.
"""

import logging
import os
from datetime import date, datetime
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy import Connection

import followup_repository
import repository
from approval import ApprovalError, approve_draft
from auth import (
    LOCAL_DEVELOPMENT_ISSUER,
    LOCAL_DEVELOPMENT_SUBJECT,
    Principal,
    begin_hello_login,
    complete_hello_login,
    get_current_principal,
    get_session_identity,
    require_manager,
)
from db import get_connection, get_transaction
from followup_service import create_followup
from readiness import assess_job

MAX_WINDOW_DAYS = 31
logger = logging.getLogger(__name__)

app = FastAPI(title="Contractor readiness")
session_secret = os.environ.get("SESSION_SECRET")
app_environment = os.environ.get("APP_ENV", "development").lower()
if app_environment != "development" and not session_secret:
    raise RuntimeError("SESSION_SECRET must be configured outside development")
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret or "local-development-only-change-before-deployment",
    session_cookie="contractor_readiness_session",
    max_age=8 * 60 * 60,
    same_site="lax",
    https_only=app_environment != "development",
)


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
    followup_status: str | None


class ReadinessExplanation(BaseModel):
    job_id: str
    answer: str


class FollowupDelivery(BaseModel):
    delivery_id: int
    draft_id: int
    approval_id: int
    status: str
    already_processed: bool


class FollowupDraft(BaseModel):
    id: int
    status: str
    job_id: str
    contractor_id: str
    recipient: str
    subject: str
    body: str
    reason: str
    evidence_ids: list[str]
    created_at: datetime


class FollowupEdit(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)


class FollowupReconciliation(BaseModel):
    outcome: Literal["sent", "not_sent"]
    note: str = Field(min_length=8, max_length=500)


def assess_many(
    connection: Connection, jobs: list[dict], organisation_id: str
) -> list[Assessment]:
    """Assess jobs using three queries in total, however many jobs there are."""
    contractor_ids = sorted({cid for job in jobs for cid in job["contractor_ids"]})
    documents = repository.documents_for(connection, contractor_ids)
    contractors = repository.contractors_by_id(connection, contractor_ids)
    policies = repository.all_policies(connection)
    followup_statuses = followup_repository.latest_status_by_job(
        connection, [job["id"] for job in jobs], organisation_id
    )

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
                followup_status=followup_statuses.get(job["id"]),
            )
        )
    return assessments


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/auth/login")
async def login_with_hello(request: Request):
    return await begin_hello_login(request)


@app.post("/auth/dev-login")
def login_to_local_demo(request: Request):
    if app_environment != "development":
        raise HTTPException(status_code=404, detail="Not found")
    request.session.clear()
    request.session["oidc_issuer"] = LOCAL_DEVELOPMENT_ISSUER
    request.session["oidc_subject"] = LOCAL_DEVELOPMENT_SUBJECT
    return {"status": "signed_in", "mode": "local_demo"}


@app.get("/auth/callback")
async def hello_callback(request: Request):
    await complete_hello_login(request)
    frontend_url = os.environ.get("HELLO_FRONTEND_URL", "http://localhost:5173/")
    return RedirectResponse(frontend_url)


@app.get("/auth/identity")
def get_authenticated_identity(identity: dict = Depends(get_session_identity)):
    return identity


@app.get("/auth/me")
def get_current_user(principal: Principal = Depends(get_current_principal)):
    return {
        "issuer": principal.issuer,
        "subject": principal.subject,
        "organisation_id": principal.organisation_id,
        "role": principal.role,
    }


@app.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"status": "logged_out"}


@app.get("/assessments", response_model=list[Assessment])
def get_assessments(
    start: date = Query(description="First day of the window, e.g. 2026-10-05"),
    end: date = Query(description="Last day of the window, inclusive, e.g. 2026-10-11"),
    principal: Principal = Depends(get_current_principal),
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

    return assess_many(
        connection,
        repository.jobs_in_window(connection, start, end, principal.organisation_id),
        principal.organisation_id,
    )


@app.get("/assessments/{job_id}", response_model=Assessment)
def get_assessment(
    job_id: str,
    principal: Principal = Depends(get_current_principal),
    connection: Connection = Depends(get_connection),
):
    job = repository.get_job(connection, job_id, principal.organisation_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return assess_many(connection, [job], principal.organisation_id)[0]


@app.get("/assessments/{job_id}/explanation", response_model=ReadinessExplanation)
def get_readiness_explanation(
    job_id: str,
    principal: Principal = Depends(get_current_principal),
    connection: Connection = Depends(get_connection),
):
    if repository.get_job(connection, job_id, principal.organisation_id) is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    try:
        from readiness_graph import explain_readiness_for_job

        answer = explain_readiness_for_job(job_id, principal.organisation_id)
    except Exception as error:
        logger.error(
            "LangGraph explanation failed for job %s (%s)",
            job_id,
            type(error).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail="AI explanation is unavailable; check model provider configuration.",
        ) from error

    return ReadinessExplanation(job_id=job_id, answer=answer)


@app.post("/assessments/{job_id}/followups", response_model=FollowupDraft, status_code=201)
def create_followup_draft(
    job_id: str,
    principal: Principal = Depends(require_manager),
    connection: Connection = Depends(get_transaction),
):
    """Store a draft message for a blocked job. Nothing is sent."""
    if repository.get_job(connection, job_id, principal.organisation_id) is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    try:
        draft = create_followup(connection, job_id, principal.organisation_id)
    except ValueError as error:
        # The job exists, but this finding has no supported follow-up.
        raise HTTPException(status_code=409, detail=str(error))
    return followup_repository.get_draft(connection, draft["id"], principal.organisation_id)


@app.get("/followups/{draft_id}", response_model=FollowupDraft)
def get_followup_draft(
    draft_id: int,
    principal: Principal = Depends(get_current_principal),
    connection: Connection = Depends(get_connection),
):
    draft = followup_repository.get_draft(connection, draft_id, principal.organisation_id)
    if draft is None:
        raise HTTPException(status_code=404, detail=f"Draft {draft_id} not found")
    return draft


@app.patch("/followups/{draft_id}", response_model=FollowupDraft)
def edit_followup_draft(
    draft_id: int,
    edit: FollowupEdit,
    principal: Principal = Depends(require_manager),
    connection: Connection = Depends(get_transaction),
):
    """Change the wording only; recipient and evidence stay as generated."""
    draft = followup_repository.update_draft_text(
        connection, draft_id, principal.organisation_id, edit.subject, edit.body
    )
    if draft is None:
        if followup_repository.get_draft(connection, draft_id, principal.organisation_id) is None:
            raise HTTPException(status_code=404, detail=f"Draft {draft_id} not found")
        raise HTTPException(status_code=409, detail="Only drafts can be edited")
    return draft


@app.post("/followups/{draft_id}/approve", response_model=FollowupDraft)
def approve_followup_draft(
    draft_id: int,
    principal: Principal = Depends(require_manager),
    connection: Connection = Depends(get_transaction),
):
    """Approve the draft's current text. Editing it afterwards needs a new approval."""
    try:
        approval = approve_draft(
            connection,
            draft_id,
            principal.organisation_id,
            f"{principal.issuer}|{principal.subject}",
        )
    except ApprovalError as error:
        raise HTTPException(status_code=409, detail=str(error))
    if approval is None:
        raise HTTPException(status_code=404, detail=f"Draft {draft_id} not found")
    return followup_repository.get_draft(connection, draft_id, principal.organisation_id)


@app.post("/followups/{draft_id}/send", response_model=FollowupDelivery)
def send_approved_followup(
    draft_id: int,
    principal: Principal = Depends(require_manager),
):
    from followup_delivery import DeliveryError, send_approved_followup as send

    try:
        return send(draft_id, principal.organisation_id)
    except DeliveryError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error


@app.post("/followups/{draft_id}/reconcile", response_model=FollowupDelivery)
def reconcile_followup_delivery(
    draft_id: int,
    reconciliation: FollowupReconciliation,
    principal: Principal = Depends(require_manager),
    connection: Connection = Depends(get_transaction),
):
    """Record a manager's manual verification of an unknown n8n outcome."""
    note = reconciliation.note.strip()
    if len(note) < 8:
        raise HTTPException(
            status_code=422,
            detail="Reconciliation note must contain at least 8 non-whitespace characters",
        )
    delivery = followup_repository.reconcile_delivery(
        connection,
        draft_id,
        principal.organisation_id,
        reconciliation.outcome,
        f"{principal.issuer}|{principal.subject}",
        note,
    )
    if delivery is None:
        draft = followup_repository.get_draft(
            connection, draft_id, principal.organisation_id
        )
        if draft is None:
            raise HTTPException(status_code=404, detail=f"Draft {draft_id} not found")
        raise HTTPException(
            status_code=409,
            detail="Only an unknown delivery can be reconciled",
        )
    return {
        "delivery_id": delivery["id"],
        "draft_id": delivery["draft_id"],
        "approval_id": delivery["approval_id"],
        "status": delivery["status"],
        "already_processed": False,
    }
