# Delivery plan: contractor operations readiness

## Scope and working agreement

Build the workflow in [docs/WORKFLOW.md](docs/WORKFLOW.md): upcoming jobs -> deterministic contractor evidence checks -> sourced explanation -> proposed follow-up -> manager approval -> task and test email -> verified outcome -> reassessment after evidence changes.

This replaces the property-management plan preserved in `docs/archive/`. No real client data or account access is required. This is an independent demo inspired by the public business domain; the client pain hypothesis remains unvalidated.

Baseline: 30 working days at 3–5 focused hours per day (90–150 hours), with re-estimation at Days 5, 10, and 20. Your wider experience and actual daily availability remain to be confirmed. Extend the estimate if the stack is new. Dates below are relative sessions, not fixed deadlines. A failed milestone gate carries forward; completing a calendar day does not prove readiness.

Daily rhythm: 20 minutes on architecture, 100–180 minutes implementing a small behavior, 40–70 minutes verifying/fixing, and 20–30 minutes documenting and demonstrating. Learn the concepts needed for the current slice. Explain consequential decisions before implementation; review milestone evidence before advancing.

## Current progress

- [x] Select business workflow and its initial scope.
- [x] Define fictional policy, roles, status rules, approval boundaries, and failure behavior.
- [x] Prepare four synthetic jobs and expected outcomes.
- [x] Rewrite roadmap and prepare Day 1 exercise.
- [x] Document the architecture baseline and four initial ADRs; implementation verification remains pending.
- [ ] Verify Python and Docker from the user's terminal.
- [ ] Complete manual Day 1 walkthrough.
- [ ] Implement application code.

Only planning and fixtures are complete. No runtime, test suite, model integration, or deployment has been built.

## Scope controls

Release includes one fictional company; manager and coordinator roles; jobs, contractors, reviewed document metadata; readiness assessment; fictional policy RAG; approved task/email workflow; audit and recovery; authenticated hosted demo.

Defer PDF extraction, OCR, staff training, equipment maintenance, scheduling, billing, real CRM/calendar integrations, live contractor emails, multi-company onboarding, voice, and WhatsApp. A local business API and SMTP capture inbox supply the integration boundaries. No external CRM subscription is needed.

Use a modular FastAPI application, PostgreSQL/pgvector, LangGraph, n8n, and a simple React frontend. Discuss auth implementation before Day 6 and LLM provider/cost cap before Day 11. Choose hosting and budget by Day 20. Pin compatible stable tool versions during setup. Avoid Kubernetes, microservices, or additional infrastructure without a demonstrated need.

## Milestones and acceptance gates

| Milestone | Days | Demonstrable result | Required gate |
| --- | --- | --- | --- |
| M1: Business model and rules | 1–5 | Deterministic assessment of fictional jobs | Four seeded outcomes plus boundary checks pass without an LLM |
| M2: Authenticated application | 6–10 | Browser assessment with evidence | Ownership/role tests pass and fresh setup is repeatable |
| M3: AI explanation and proposals | 11–15 | Natural-language question produces grounded findings and draft follow-up | No unsupported claims, invented records, or unapproved execution |
| M4: Approval and workflow | 16–20 | Approved task/test-email workflow with recovery | Reject, replay, restart, stale-data, and partial-failure cases pass |
| M5: Quality and operations | 21–25 | Measured accuracy, cost, security, and recovery behavior | Critical safety tests and agreed workload targets pass |
| M6: Deployment and handoff | 26–30 | Hosted demo with operational evidence | Restore, rollback, alert, and final acceptance drills pass |

All milestone gates remain open.

## Daily tasks

Follow the [learning path](docs/LEARNING_PATH.md) alongside these tasks. At each milestone explain a trade-off, predict a failure, demonstrate it with a meaningful check, and teach the design back. Use [architecture.md](docs/architecture.md) and the [ADRs](docs/decisions/README.md) as living references. Reserve today's learning time for the first architecture exercise rather than adding extra hours to the schedule.

### M1 — Business model and rules

Architecture question: which facts and rules determine a result independently of AI?

| Done | Day | Tasks | Evidence to finish |
| --- | --- | --- | --- |
| [ ] | 1 | Read workflow, manually assess four seeded jobs, and verify local tools. Record open questions. | Explain why JOB-102 is blocked and JOB-104 needs review; capture environment results |
| [ ] | 2 | Scaffold Python project and FastAPI with config, health endpoint, dependency lock, and minimal setup instructions. | API runs; health check passes; secrets are excluded from Git |
| [ ] | 3 | Define typed job, assignment, requirement, document, and result models. Load seed JSON; reject malformed records. | Valid fixture loads; invalid dates/IDs/types fail clearly |
| [ ] | 4 | Implement pure readiness rules: full-job validity, reviewed status, missing evidence, coverage threshold, and status aggregation. | Four expected outcomes and start/end boundary tests pass |
| [ ] | 5 | Add tests for multiple documents, unknown policy, no assignment, mixed findings, and unknown amounts. Expose assessment endpoint using fixtures. Review and re-estimate. | M1 gate: deterministic endpoint returns findings with record references |

### M2 — Authenticated application

Architecture question: who can see evidence and change business state?

| Done | Day | Tasks | Evidence to finish |
| --- | --- | --- | --- |
| [ ] | 6 | Choose established auth approach, define manager/coordinator permissions, and add PostgreSQL Compose service with migrations. | Database starts and migrations run; auth decision recorded |
| [ ] | 7 | Persist organisation, users, jobs, assignments, requirements, and reviewed metadata. Make synthetic seeding repeatable. | Reseeding does not duplicate records; relationships and constraints are verified |
| [ ] | 8 | Integrate authentication and enforce organisation ownership and role checks in business services. | Anonymous/out-of-scope requests fail; coordinator cannot approve actions |
| [ ] | 9 | Build React assessment view: explicit date window, job status, reason codes, and evidence details. Persist assessment snapshots and source versions. | Browser displays the four seeded outcomes and links each to evidence |
| [ ] | 10 | Add CI for rule/API/database tests and frontend build. Document fresh setup. Fix integration defects and re-estimate. | M2 gate: a clean database and fresh setup reproduce the assessment |

### M3 — AI explanation and proposals

Architecture question: what can the model interpret, and what must it never decide?

| Done | Day | Tasks | Evidence to finish |
| --- | --- | --- | --- |
| [ ] | 11 | Select model/provider and request budget. Add small provider adapter, typed graph state, read-tool allowlist, turn/time/token limits. | Graph reads existing assessments; it cannot change readiness or business records |
| [ ] | 12 | Interpret requests and exact date ranges. Add clarification, unknown intent, fixed-clock tests, and Australia/Sydney handling. | Ambiguous dates trigger clarification; exact interpreted range is visible |
| [ ] | 13 | Author fictional policy and follow-up procedure. Add versioned pgvector ingestion and source-aware retrieval. | Re-ingestion avoids duplicates; known questions retrieve the correct policy version |
| [ ] | 14 | Generate explanations grounded in rule findings and policy passages. Handle empty results, missing policy, and tool failures. | No invented contractor, requirement, or success claim; structured findings remain authoritative |
| [ ] | 15 | Draft editable follow-ups with registered recipients and exact proposed task/email contents. Record versions. Review the AI slice. | M3 gate: manager reviews a proposal; generating a draft sends nothing |

### M4 — Approval and workflow

Architecture question: what specifically was approved, and how do we prevent repeated side effects?

| Done | Day | Tasks | Evidence to finish |
| --- | --- | --- | --- |
| [ ] | 16 | Implement immutable approved action versions, manager approval/rejection, 24-hour expiry, and durable graph checkpoints. | Rejected/expired/edited actions cannot execute; pending approval survives restart |
| [ ] | 17 | Add private n8n and local SMTP capture inbox. Authenticate workflow calls. Execute approved task creation and email delivery; export sanitized workflow. | One approved action creates one task and one captured email |
| [ ] | 18 | Add durable action ledger, uniqueness constraints, bounded retries, delivery states, and unknown-outcome reconciliation. | Duplicate callback and lost-response tests do not duplicate tasks; ambiguous email send is held for reconciliation |
| [ ] | 19 | Revalidate source versions before execution. Allow coordinator to record reviewed replacement evidence; rerun assessment and explicitly resolve task. | Changed evidence invalidates stale proposals; sending a reminder never changes readiness |
| [ ] | 20 | Add audit timeline and full end-to-end exercises. Fix workflow defects; select hosting/budget and confirm workload/recovery targets. | M4 gate: approved, rejected, stale, replayed, restarted, and partially failed workflows behave correctly |

### M5 — Quality and operations

Architecture question: what measured evidence supports this system's reliability?

| Done | Day | Tasks | Evidence to finish |
| --- | --- | --- | --- |
| [ ] | 21 | Expand to at least 60 versioned cases across deterministic boundaries, requests, grounding, approval, and failures. Keep tuning and held-out cases separate. | Cases specify exact expected/forbidden behavior; include multi-contractor jobs and date boundaries |
| [ ] | 22 | Run deterministic integration tests and live-model evaluation separately. Measure extraction of date intent, citation support, tool use, latency, and cost; fix failures. | Reproducible report includes counts, model/prompt/data versions, and limitations |
| [ ] | 23 | Review auth, session protection, organisation scope, injection, webhooks, secrets, dependencies, and n8n exposure. | No unresolved critical/high security findings; negative tests cover every privileged boundary |
| [ ] | 24 | Add rate/payload limits, cost caps, redacted logs, retention/purge behavior, and dependency error handling. | Limits stop excessive use safely; purge and redaction checks pass |
| [ ] | 25 | Run agreed concurrency workload and outage/restart exercises. Benchmark manual versus assisted review using the same synthetic cases. Fix and reassess. | M5 gate: quality thresholds and measured workload targets pass; demo savings are labelled synthetic |

### M6 — Deployment and handoff

Architecture question: can you operate and recover the system yourself?

| Done | Day | Tasks | Evidence to finish |
| --- | --- | --- | --- |
| [ ] | 26 | Build pinned images and deploy staging with HTTPS, separate secrets/config, restricted n8n, and private database/test inbox. Keep external mail delivery disabled. | Authenticated remote smoke test passes; internal services are not publicly exposed |
| [ ] | 27 | Automate encrypted off-host backups and restore into a clean environment. Include business data, checkpoints, workflow config, and protected n8n key recovery. | Restored pending approvals and workflow credentials remain usable |
| [ ] | 28 | Rehearse release, migration, rollback/forward-repair, and configuration recovery. | Documented recovery succeeds with a compatible application/database version |
| [ ] | 29 | Set error/workflow/cost alerts, name operator, write runbook, prepare five-minute walkthrough, and fix release blockers. | Forced failure reaches operator; setup and incident instructions are usable |
| [ ] | 30 | Run deployed acceptance suite, review all gates, publish measured limitations, and record architecture demo. Tag release only if gates pass. | M6 gate: explicit demo/pilot-candidate release decision with evidence |

## Release gates

### Functional correctness

- [ ] Four fixed scenarios produce 1 READY, 2 BLOCKED, and 1 NEEDS_REVIEW.
- [ ] Full-job coverage, inclusive dates, multiple documents, unknown policy, missing assignment, and mixed-status rules pass deterministic tests.
- [ ] Zero critical failures in authorisation, approval bypass, stale action execution, duplicate tasks, or false success claims.
- [ ] A reminder never marks evidence verified or a contractor ready.
- [ ] Reviewer can inspect original record references and policy version for every finding.

### AI quality

- [ ] At least 60 cases, with category counts and held-out results reported separately.
- [ ] At least 90% correct request/date interpretation on unambiguous held-out cases; all designated ambiguous cases clarify.
- [ ] Expected policy passage appears in top five results for at least 90% of answerable retrieval cases.
- [ ] At least 95% of reviewed factual explanation claims have valid supporting evidence; missing evidence is acknowledged.
- [ ] Three runs of critical AI cases produce no unapproved execution or invented successful outcome.
- [ ] Report errors and reviewer corrections; overall averages cannot excuse a critical control failure.

### Reliability and operation

- [ ] Approval survives restart; rejection, expiry, changed payload, changed evidence, and repeated approval behave correctly.
- [ ] Task success plus email failure preserves task and isolates delivery recovery.
- [ ] Unknown email outcome never triggers a blind resend.
- [ ] Proposed workload: 10 concurrent users for 15 minutes with a declared mix of assessment, explanation, and status requests.
- [ ] Proposed targets under healthy dependencies: p95 non-AI API below 500 ms; p95 AI response below 15 seconds excluding human wait; unexpected errors below 1%.
- [ ] Record environment, case mix, model, cost, and observed throughput. Revise targets by Day 20 against hosting budget.
- [ ] Set numeric request/daily spending caps before hosted use; enforce and demonstrate alerts.
- [ ] Proposed recovery objectives: at most 24 hours of data loss and recovery within four hours; verify with a restore drill.
- [ ] HTTPS, least privilege, secret handling, retention, protected workflow editor, and dependency review complete.
- [ ] Runbook, named operator, restore, release recovery, and alert drill complete.

### Status of the final deliverable

A deployed synthetic demonstration can meet these engineering gates. Actual customer production also requires validation of the pain point, approved access and integration contracts, real policy rules, data handling requirements, workload, budget, support ownership, and customer acceptance. No client data or production integration is assumed by this plan.

## Risks and contingency

| Risk | Response |
| --- | --- |
| Client already has an equivalent workflow | Validate before pitching savings; retain project as independent architectural demonstration |
| Approval or workflow work takes longer | Extend M4; defer UI polish and broader data generation rather than weaken controls |
| Model guesses requirements | Business rules own findings; retrieved policies explain only |
| External credentials unavailable | Use synthetic records and local inbox; all initial milestones remain achievable |
| Runtime access blocked in agent session | Compare with user's terminal before changing installations |
| New policy/evidence changes conclusions | Persist source versions, mark stale, reassess before execution |
| Deployment budget unavailable | Finish local acceptance; keep deployment gate open and document the dependency |

## Daily progress record

```text
Day/date:
Behavior completed:
Checks and evidence:
Architecture decision and reason:
Remaining issue:
Next smallest task:
Focused hours:
```

Begin with [Day 1](docs/DAY_01.md). Do not implement later milestones in one batch.
