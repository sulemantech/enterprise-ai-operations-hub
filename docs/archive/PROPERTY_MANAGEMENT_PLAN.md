# Enterprise AI Operations Hub: delivery plan

## Starting point

Reviewed on 29 September 2026. The repository contains `Readme.md`, a detailed specification. There is no application code, dependency manifest, test suite, workflow export, or deployment configuration yet. `PROJECT_SPEC.md`, mentioned in the README, does not exist; use `Readme.md` as the specification.

The specification has a useful architectural boundary: LangGraph handles interpretation and routing, n8n handles deterministic integrations, and application code enforces permissions and business rules. The largest gap is operational detail: identity, durable approvals, duplicate prevention, partial failures, recovery, and release acceptance criteria.

This plan expands the README's original 10-day schedule. Ten days can establish a demo; production readiness must be earned through the gates below. This file is the proposed delivery schedule; the README remains the product brief.

## Fit to your goals and available time

The README describes your goal as a solo portfolio project for international clients, focused on AI solution and enterprise architecture. It also asks for a peer programming approach with architectural discussion. Your broader experience is not available in this conversation, so this plan does not assume a particular skill level.

- Baseline: 30 working days, 3–5 focused hours per day, approximately 90–150 hours over six working weeks.
- This is an initial estimate, not a production guarantee. Re-estimate after Days 5 and 10 using completed work.
- If Python, React, or Docker are new, reserve another 5–10 learning days and reassess. At two hours per day, budget approximately 45–75 sessions.
- Each milestone produces working behavior, evidence, and a short architecture explanation suitable for a client conversation.
- Discuss consequential architecture choices at the start of each milestone, as requested in the README. Implement one milestone at a time.
- Days are relative working sessions, not calendar deadlines. Carry unfinished acceptance criteria forward before opening the next milestone.

### Daily working rhythm

Use approximately 20 minutes for the architecture question, 100–180 minutes for implementation, 40–70 minutes for verification and fixes, and 20–30 minutes for notes and a demo. Read documentation to solve the day's concrete problem.

End each day with a small reviewable change, relevant checks, one observable result, and the next blocker recorded. Documentation-only work needs review rather than artificial tests.

## Release scope

### First release

- One fictional property-management company with seeded residents, properties, and charges.
- Authenticated resident and operator roles; residents can access only their own records.
- Web conversation, request status, operator approval inbox, and restricted execution timeline.
- Grounded FAQ answers, maintenance requests, appointments, human escalation, scheduled follow-up, and a simulated fee waiver requiring approval.
- PostgreSQL with pgvector, FastAPI, LangGraph, n8n, and one simple React frontend.
- CRM/work-order records owned by the application. One external calendar and one notification channel integrated through sandbox/test accounts before pilot readiness.
- Synthetic data throughout the portfolio demo. Clearly label simulated integrations and financial operations.

### Later

Voice, WhatsApp, multiple customer organizations, live financial changes, additional CRM vendors, Kubernetes, Kafka, microservices, and high availability. Expand only against a concrete customer requirement.

### What completion means

1. **Demo:** primary journeys work with seeded data and visible execution evidence.
2. **Pilot candidate:** access control, recovery, deployment, evaluation, and operational gates pass for a declared small workload.
3. **Customer production:** the real customer's identity provider, integrations, data handling requirements, support owner, traffic, budget, and recovery needs are validated. The calendar alone cannot establish this status.

## Architecture and decisions

Proposed minimum architecture:

```text
Browser -> FastAPI -> LangGraph -> retrieval / typed tool adapters
               |                          |
               |                          v
               |                         n8n -> calendar / notification adapters
               |                          |
               v                          v
          PostgreSQL <--- application business API
          business records, approvals, action ledger, audit, checkpoints, vectors
```

Use a modular monolith for application business logic. n8n calls authenticated business APIs; database mutations and authorization remain in application services. Separate n8n database credentials and graph checkpoint storage from business access. The LLM receives only allowlisted tools.

| Decide | Proposed starting position | When to settle |
| --- | --- | --- |
| Frontend | Simple React app; use Next.js if it is already familiar or has a concrete benefit | Day 1 |
| Identity | Established authentication library/provider; server derives identity and role | Day 1, integrate Day 3 |
| Business scope | One company, resident-level record isolation | Day 1 |
| Approval policy | Routine maintenance allowed for own property; fee adjustments require an operator | Day 1 |
| LLM provider | One configured provider behind a small adapter; no multi-provider framework | Day 1, connect Day 7 |
| Integrations | Internal CRM/work orders; one calendar sandbox and notification channel | Day 1, provision by Day 16 |
| Hosting and costs | Single small deployment initially; choose budget, region, and provider explicitly | By Day 20 |
| Workload and recovery | Proposed targets below; revise against actual pilot needs | Day 1, confirm Day 20 |

Start credential/account setup on Day 1 to avoid blocking later integrations. Pin compatible stable dependencies during implementation after checking their current documentation.

## Risks to resolve in the implementation

| Risk or missing requirement | Planned control | Evidence |
| --- | --- | --- |
| User supplies another resident's ID | Derive identity from session and enforce ownership on every read/write, retrieval, and graph thread | Two residents cannot access each other's records |
| Repeated messages or workflow retries create duplicates | Durable action ID, unique constraint, and idempotent business endpoints | Replaying the same action yields one work order |
| n8n succeeds but the response is lost | Persist action state and reconcile by action ID before retrying | Timeout recovery shows the actual operation result |
| Restart loses an approval | Database approval plus persistent graph checkpoint | Restart while pending, then resume once |
| Approval is reused or parameters change | Bind approval to actor, immutable action version, scope, and expiry; revalidate before execution | Reused, expired, or altered approvals fail |
| Work order succeeds but notification fails | Track each step separately and retry notification independently | Existing work order survives notification failure |
| Two users select the same slot | Reservation/uniqueness control and provider conflict handling | One booking wins; the other gets an honest conflict |
| Retrieved instructions redirect the agent | Treat retrieved text as untrusted data; enforce permissions outside prompts | Injection cannot grant tool authority |
| Emergency request is handled as ordinary maintenance | Approved emergency guidance, immediate escalation path, and explicit delivery state | No false claim that emergency services were contacted |
| Debug timeline leaks sensitive content | Operator authorization, redaction, minimal retention | Resident cannot view operator-only traces |
| README mixes approval examples | One documented policy matrix governs all paths | Routine maintenance and fee-waiver demos agree with policy |

## Milestones

All milestones start **not started**. Gates describe required evidence, not completed checks.

| Milestone | Days | Outcome | Exit gate |
| --- | --- | --- | --- |
| M1: Foundation and identity | 1–5 | Reproducible app, database, authenticated records | Fresh setup works; resident isolation checks pass |
| M2: Useful AI workflow | 6–10 | FAQ and maintenance through LangGraph and n8n | Cited FAQ, clarification, real work-order ID, duplicate protection |
| M3: Durable governance | 11–15 | Approvals, recovery, operator visibility | Restart/replay/rejection/expiry checks pass with one execution |
| M4: Business integrations | 16–20 | Calendar, notifications, follow-up, combined journey | Sandbox integration and failure paths verified |
| M5: Quality and security | 21–25 | Measured behavior, bounded cost, reviewed controls | Evaluation and security gates pass |
| M6: Deployment and handoff | 26–30 | Operable release with evidence | Restore, rollback, alert, and final acceptance demonstrations pass |

## Daily tasks

### M1 — Foundation and identity

**Architecture question:** Where do identity, business authority, and data ownership live?

| Done | Day | Tasks | End-of-day evidence |
| --- | --- | --- | --- |
| [ ] | 1 | Confirm scope, roles, approval policy, budget assumptions, and providers. Draw trust boundaries. Scaffold FastAPI with a health endpoint. Start account/credential requests. | API starts; short architecture note and decision log explain the boundaries |
| [ ] | 2 | Add PostgreSQL/pgvector, local Compose, environment template, migrations, and synthetic seed data. Keep secrets out of source. | Fresh database migrates and seeds; readiness detects database failure |
| [ ] | 3 | Integrate authentication and resident/operator roles. Add ownership checks and session protection appropriate to the chosen auth method. | Unauthenticated access denied; resident A cannot read resident B's data |
| [ ] | 4 | Add typed work-order read/create endpoints, server-side validation, action IDs, uniqueness constraints, and basic audit events. | Valid create succeeds; invalid data and cross-resident writes fail; replay returns the same record |
| [ ] | 5 | Build minimal web login and request/status views. Add CI for backend checks, frontend build, and database integration checks. Fix foundation issues and re-estimate. | Browser-to-database flow works from a fresh setup; M1 review passes |

### M2 — Useful AI workflow

**Architecture question:** Which steps require model interpretation, and which must be deterministic?

| Done | Day | Tasks | End-of-day evidence |
| --- | --- | --- | --- |
| [ ] | 6 | Start n8n privately. Define authenticated webhook and callback contracts. Implement maintenance workflow calling the business API and export its sanitized definition. | Direct workflow request creates one work order; unauthenticated invocation fails |
| [ ] | 7 | Add explicit LangGraph state, provider adapter, structured intent output, typed tools, turn limits, and timeouts. Connect maintenance to n8n. | User message creates a work order through the complete path and returns its actual ID |
| [ ] | 8 | Add missing-field clarification, unknown intent, escalation, emergency guidance, and ownership-scoped status lookup. Begin a versioned evaluation dataset. | Ambiguous input creates no work order; escalation and emergency paths show verified status |
| [ ] | 9 | Write the nine fictional policy documents from the brief. Add versioned ingestion, embeddings, pgvector retrieval, source metadata, and repeatable indexing. | Known questions retrieve expected passages; repeated ingestion does not duplicate documents |
| [ ] | 10 | Connect grounded FAQ responses with citations and an insufficient-evidence response. Show action status and sources in the UI. Review demo and re-estimate. | FAQ, clarification, maintenance, and status journeys pass; no invented success on workflow failure |

### M3 — Durable governance

**Architecture question:** What survives a crash, and what authorizes a sensitive action?

Persistent checkpointers support graph continuity and interrupted workflows; in-memory state does not survive a restart. Use database persistence for the approval path. See [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).

| Done | Day | Tasks | End-of-day evidence |
| --- | --- | --- | --- |
| [ ] | 11 | Add persistent graph checkpoints and durable action states: proposed, awaiting approval, running, succeeded, failed, and unknown outcome. Scope thread access to identity. | Restart preserves conversation/action state; another resident cannot resume the thread |
| [ ] | 12 | Implement simulated fee-waiver proposal and server-enforced policy. Bind approval to exact amount, account, action version, and expiry. | Rephrasing the request cannot bypass approval; no financial mutation occurs while pending |
| [ ] | 13 | Build operator approve/reject inbox and authorized resume endpoint. Atomically consume approvals and revalidate permissions. | Approve executes once; reject never executes; unauthorized, expired, and duplicate approvals fail |
| [ ] | 14 | Add bounded retries, replay protection, outcome reconciliation, and recovery for failed workflow steps. | Kill/restart and lost-response exercises create no duplicate work orders or waivers |
| [ ] | 15 | Build restricted audit timeline with correlation/workflow IDs and redacted results. Review and repair all governance paths. | Demonstrate pending approval across restart, rejection, and one successful approved execution |

### M4 — Business integrations

**Architecture question:** How does the system report partial success across independent services?

| Done | Day | Tasks | End-of-day evidence |
| --- | --- | --- | --- |
| [ ] | 16 | Connect calendar sandbox; add available-slot lookup, explicit timezone handling, and booking contract. | Available slots match provider data; unavailable provider produces a controlled error |
| [ ] | 17 | Implement appointment workflow, booking conflicts, idempotency, CRM update, and reconciliation. Ask the user to confirm the exact slot. | Concurrent attempts cannot double-book; replay creates one appointment |
| [ ] | 18 | Connect notification sandbox/test recipient; persist delivery state and independent retry. | Failed notification does not recreate or undo a confirmed appointment |
| [ ] | 19 | Add scheduled follow-up and operator escalation queue with deduplication and attempt limits. | Repeated scheduler runs produce one notification per follow-up window |
| [ ] | 20 | Combine maintenance creation and appointment flow. Resolve failure UX. Confirm hosting, cost limits, target workload, and recovery objectives. | Full AC-repair scenario works; adapters are clearly labeled real/sandbox/simulated |

If credentials are blocked, mocks can keep development moving. Record the dependency; M4's integration gate remains open until the selected sandbox adapters are verified.

### M5 — Quality and security

**Architecture question:** What evidence supports the reliability claim, and what can still fail?

| Done | Day | Tasks | End-of-day evidence |
| --- | --- | --- | --- |
| [ ] | 21 | Complete at least 80 evaluation cases: normal, ambiguous, sensitive, adversarial, emergency, and dependency failure. Separate tuning examples from held-out cases. | Versioned cases contain expected intent, sources, actions, and forbidden behavior |
| [ ] | 22 | Run deterministic integration checks and live-model evaluations separately. Score per intent/category; manually inspect grounding. Record model, prompt, dataset version, latency, and cost. | Reproducible report identifies failures and fixes; thresholds below are assessed |
| [ ] | 23 | Review authentication, ownership, webhook replay, prompt injection, secrets, dependency risks, and public exposure. Disable unused n8n capabilities and protect its editor. | Negative tests and security review have no unresolved critical/high findings |
| [ ] | 24 | Add rate limits, payload limits, model/token budgets, bounded conversation history, retention/purge rules, and redacted logging. | Oversized/over-budget requests stop safely; purge handles messages and checkpoints consistently |
| [ ] | 25 | Run the agreed concurrency test and outage drills; fix the highest-impact defects and rerun affected checks. | Measured performance, truthful failure responses, and M5 gate report |

### M6 — Deployment and handoff

**Architecture question:** Can you deploy, diagnose, recover, and support the service yourself?

| Done | Day | Tasks | End-of-day evidence |
| --- | --- | --- | --- |
| [ ] | 26 | Build pinned deployable images and separate staging configuration. Deploy with HTTPS, protected internal services, and injected secrets. | Remote authenticated smoke test passes; database and n8n editor are not publicly exposed |
| [ ] | 27 | Automate encrypted off-host backups and restore into a clean environment. Include business DB, checkpoints, workflow configuration, and protected n8n encryption-key recovery. | Restore report proves records, pending approvals, and workflow credentials remain usable |
| [ ] | 28 | Implement controlled release/migration process and document rollback or forward repair. Rehearse with a compatible release. | Prior application release can be restored safely; migration recovery procedure is demonstrated |
| [ ] | 29 | Configure service/workflow failure alerts and budget alerts. Write incident/runbook instructions. Fix release blockers and prepare demo script and limitations. | Forced failure reaches the named operator; five-minute demo and runbook are usable |
| [ ] | 30 | Run final acceptance on the deployed version, review evidence, record architecture walkthrough, and tag the release only if gates pass. | Release decision states demo/pilot status, known limits, measured results, and next steps |

Database backup methods have different recovery properties; choose against the agreed recovery targets and verify restoration. See [PostgreSQL backup and restore](https://www.postgresql.org/docs/current/backup.html).

## Proposed release gates

These are starting targets to agree on, not measured results or promises of universal reliability.

### Functional and AI quality

- [ ] Both primary demo scenarios pass: maintenance plus appointment, and fee waiver with approval.
- [ ] Status, FAQ, clarification, rejection, escalation, emergency, and notification-failure paths pass.
- [ ] At least 80 versioned cases; report tuning and held-out results separately.
- [ ] Intent accuracy at least 90% overall with per-category counts reported.
- [ ] Expected source appears in top five retrieval results for at least 90% of answerable knowledge cases.
- [ ] At least 95% of reviewed factual policy claims are supported by cited sources; all insufficient-evidence cases avoid invented policy.
- [ ] All critical authorization, approval-bypass, duplicate-execution, and false-success cases pass. An average quality score cannot compensate for these failures.
- [ ] Three live-model runs of the critical AI cases show no unsafe action; retain observed failures even after fixes.

### Security and reliability

- [ ] Ownership checks cover API records, graph threads, approval decisions, document scope, and operator traces.
- [ ] Validated, authenticated workflow boundaries; least-privilege service credentials; no secrets in repository or exports.
- [ ] Pending approval survives restart. Reject/expire/replay/changed-parameters tests pass.
- [ ] Timeout after successful side effect is reconciled before retry; no duplicate action occurs.
- [ ] User-visible success comes from verified business state. Unknown outcomes remain pending until reconciled.
- [ ] Security review and dependency scan have no unresolved critical/high findings.
- [ ] Retention, deletion, redaction, and access rules are documented and exercised with synthetic records.

### Performance and operations

- [ ] Proposed workload: 10 concurrent conversations for 15 minutes with a documented mix of FAQ, maintenance, and status requests.
- [ ] Proposed targets under healthy dependencies: p95 non-AI API latency below 500 ms; p95 completed AI turn below 15 seconds, excluding human wait; unexpected request errors below 1%.
- [ ] Document machine, model, dataset, test duration, token usage, and cost. Adjust workload or architecture when measurements miss targets.
- [ ] Select numeric per-request and daily spending limits before pilot; rate/budget controls and alerts work.
- [ ] Proposed initial recovery targets: at most 24 hours of data loss and service recovery within four hours. Customer requirements may need stronger backup/hosting choices.
- [ ] Restore, rollback, and alert drills pass with timestamps and results recorded.
- [ ] A named owner has the runbook, account access, escalation procedure, and maintenance responsibility.

### Before real customer production

- [ ] Validate actual provider credentials, contracts, rate limits, and integration failure behavior.
- [ ] Agree data location, permitted data use, retention, access, and applicable customer requirements.
- [ ] Replace simulated financial operations only after customer business rules and approval authority are agreed.
- [ ] Approve actual workload, availability and recovery targets, support hours, and monthly operating budget.
- [ ] Perform user acceptance with the customer's staff and record the release decision.

## Evidence and progress tracking

Create supporting files as work needs them: `docs/architecture.md`, focused ADRs, `docs/security.md`, `docs/runbook.md`, `docs/demo.md`, sanitized n8n exports, and versioned evaluation reports. Link each milestone to its relevant test output, demo, and unresolved issues.

| Milestone | Status | Evidence link / revision | Blocker / next action |
| --- | --- | --- | --- |
| M1 | Not started | — | Begin Day 1 |
| M2 | Not started | — | Requires M1 |
| M3 | Not started | — | Requires M2 |
| M4 | Not started | — | Provision sandbox credentials early |
| M5 | Not started | — | Add cases throughout development |
| M6 | Not started | — | Confirm hosting and budget by Day 20 |

Keep an end-of-day entry using this template:

```text
Day / date:
Completed behavior:
Evidence / checks:
Architecture decision and reason:
Remaining issue:
Next smallest task:
Actual focused hours:
```

## Your first session

1. Confirm the release scope and the Day 1 decisions above.
2. Explain the request path and trust boundaries in your own words.
3. Scaffold the API health endpoint and verify it locally.
4. Record the first architecture decision: application permissions and business rules remain authoritative across LangGraph and n8n.
5. Review the small change together before advancing.

The strongest portfolio result will be a system whose successful actions, rejected actions, and recovery behavior you can explain and demonstrate.
