# Contractor readiness workflow

Status: selected project direction. Version 1. All entities and requirements below are fictional demonstration material.

## Objective and boundaries

Help an operations manager find missing contractor evidence for upcoming jobs and coordinate approved follow-up. Begin with insurance and trade-licence records only. Build an internal demonstration business API rather than reproduce FocusIMS. Client API availability and schemas remain unverified.

The initial input is reviewed structured metadata. PDF/OCR extraction is out of scope. The company policy is authored for this demo and is not an interpretation of Australian law or an ISO standard.

## Actors

- Manager: view assessments and evidence, edit drafts, approve/reject follow-up actions.
- Coordinator: view assessments, propose follow-ups, and record reviewed replacement evidence; cannot approve outbound actions.
- Workflow service: execute a specific approved action using scoped credentials; cannot grant approval.

Every role is scoped to its organisation. Identity and scope come from authentication, never model-generated arguments. The first deployment has one organisation; negative tests include out-of-scope IDs.

## Primary journey

1. Manager selects an inclusive date range or asks in natural language. Resolve relative dates using an explicit reference time and `Australia/Sydney`; display the exact range before assessing.
2. Read all authorised scheduled jobs in the range and their contractor assignments. Cancelled jobs are excluded; pagination must not silently omit jobs.
3. Load the job's versioned requirements and the contractor's reviewed document metadata.
4. Run deterministic checks and persist an assessment with source record versions and policy version.
5. Present job, contractor, status, reason codes, document references, and suggested follow-up. Retrieve policy passages for explanation.
6. Manager chooses findings for follow-up. Create editable drafts addressed to the contractor's registered contact, with affected jobs and missing evidence listed.
7. Show exact recipient, subject, body, task owner, and proposed due date. Store an immutable action version for approval. Editing any approved field invalidates approval.
8. An authorised manager approves or rejects. Approval expires after 24 hours in the demo. Recheck permissions and current evidence before execution; changed findings require a fresh draft and approval.
9. n8n creates a follow-up task through the business API and delivers the approved message to the local test inbox. Record separate task and notification outcomes.
10. Coordinator records reviewed replacement metadata. Rerun the affected assessment and show remaining findings. Task resolution requires an explicit coordinator action with an audit entry.

## Fictional policy DEMO-CONTRACTOR-001, version 1

- Each job specifies its required document types.
- A document must belong to the assigned contractor and have a `verified` review status.
- Validity must cover the whole job: `valid_from <= job.start_date` and `valid_to >= job.end_date`, using inclusive local calendar dates.
- Dates must be parseable and ordered. Missing or contradictory dates require review.
- An insurance document must state AUD coverage at least equal to the job's configured minimum. Unknown currency/amount requires review; a known insufficient amount blocks documentary readiness.
- If multiple records exist, one verified qualifying record can satisfy the requirement. Retained older expired records do not override a qualifying renewal. Ambiguous ownership/replacement relationships require review.
- A missing required document is a blocker. An unassigned job also has a blocker.
- Notification or approval cannot change evidence status. No action may waive a requirement in this release.

### Status and reason codes

| Status | Meaning | Example reason codes |
| --- | --- | --- |
| READY | All configured documentary checks pass | REQUIREMENTS_MET |
| BLOCKED | At least one definite required check fails | MISSING_DOCUMENT, EXPIRES_BEFORE_JOB_END, INSUFFICIENT_COVER, NO_CONTRACTOR |
| NEEDS_REVIEW | Evidence or requirements cannot be evaluated reliably | UNVERIFIED_DOCUMENT, INVALID_DATES, UNKNOWN_POLICY, AMBIGUOUS_RECORD |

Check all requirements and retain all findings. For a contractor assignment, BLOCKED takes precedence over NEEDS_REVIEW, then READY. A job takes the worst status across assignments. A job with no requirements configuration is NEEDS_REVIEW, never silently READY. READY refers only to these document checks, not overall site safety or permission to work.

## Fixed demonstration

Use reference date 2026-10-01 and window 2026-10-05 through 2026-10-11. Fixed dates keep the exercise repeatable after the current date changes.

| Job | Contractor | Seeded evidence | Expected |
| --- | --- | --- | --- |
| JOB-101 | CON-001 | Verified insurance and licence cover the job | READY |
| JOB-102 | CON-002 | Verified insurance expires 2026-10-07; job ends 2026-10-09 | BLOCKED: EXPIRES_BEFORE_JOB_END |
| JOB-103 | CON-003 | Insurance exists; required licence absent | BLOCKED: MISSING_DOCUMENT |
| JOB-104 | CON-004 | Insurance awaiting review; licence verified | NEEDS_REVIEW: UNVERIFIED_DOCUMENT |

Expected job totals: 1 ready, 2 blocked, 1 needs review. Declared coverage values are arbitrary demo parameters.

## Business entities and tool boundary

Start with organisations, users, contractors, jobs, assignments, requirement sets, and document metadata. Add assessments/findings, action drafts, approvals, follow-up tasks, deliveries, and audit events when their workflows are implemented.

Read tools: `list_jobs`, `get_contractor_evidence`, `assess_readiness`, `retrieve_policy`, `get_action_status`.

Proposal tools: `draft_follow_up`. Execution uses a server-validated approved action ID; the model cannot supply new recipients or payloads at execution time.

Examples of business endpoints to implement incrementally:

- `POST /assessments`: validate date range, check scope, persist deterministic results.
- `GET /assessments/{id}`: return evidence references and findings.
- `POST /follow-ups`: create a proposal for selected findings.
- `POST /follow-ups/{id}/approve` and `/reject`: role check and atomic state transition.
- Internal execution endpoint: validate service identity, action version, approval, expiry, and idempotency key.

## Failure and approval semantics

- Replaying an action ID must return the existing result; use a database uniqueness constraint.
- Task succeeds, email fails: preserve the task and retry delivery only.
- Timeout after a write: mark outcome unknown and reconcile by action ID before retrying.
- Process restarts while approval is pending: retain approval and graph state in PostgreSQL.
- Two approvals arrive: only one atomic transition may authorize execution.
- Duplicate webhook: no duplicate task or message. If the mail transport cannot guarantee deduplication after an ambiguous send, reconcile or request operator review rather than automatically resend.
- Approval is rejected, expired, changed, or out of scope: no execution.
- Workflow outcome is unknown: UI reports pending investigation, not sent.
- Policy or evidence changes after assessment: mark it stale and rerun before action approval/execution.
- Follow-up status is independent of readiness. Sending a request does not make a contractor ready.

## UI and acceptance demonstration

One assessment page with date range, job rows, status counts, evidence details, and an optional conversational input. Separate manager approval inbox and action timeline. Show findings and sources rather than hidden model reasoning.

Demonstrate the four seeded outcomes, a policy explanation, edited and rejected drafts, one approved test email/task, duplicate prevention, restart recovery, and a rerun after replacement evidence.

## Validate business value later

Ask the client to describe the current workflow without sharing private records: which screens are used, how often follow-ups occur, what remains manual, and what existing automation already covers. Measure manual versus assisted review time on the same synthetic cases, corrections made, and missed findings. Report measured demo results separately from any future client savings.
