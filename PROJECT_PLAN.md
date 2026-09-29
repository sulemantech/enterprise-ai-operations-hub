# Learning-first project plan

## Goal

Understand and build one complete local workflow: check fictional jobs, explain missing contractor evidence, approve a follow-up, and see it in a test inbox.

Use 2–4 focused hours per session as a starting estimate. Repeat or split a session when needed. Progress is based on understanding and working behavior. Your actual experience and daily availability can adjust the pace.

## Phase 1: build and understand the local demo

| Session | Add or learn | Small task | Done when |
| --- | --- | --- | --- |
| 1 | Business example and Python setup | Read JOB-102 and check Python in your terminal | You can explain its status and Python runs |
| 2 | Python function | Load fixture data and check full-job date coverage | JOB-102 returns the expected reason |
| 3 | Remaining rules | Check missing, unverified, and insufficient evidence; add a few meaningful tests | All four jobs match expected outcomes; end-date boundary passes |
| 4 | FastAPI | Expose the same assessment through one endpoint | API documentation can request and display results |
| 5 | API inputs and errors | Add explicit date inputs and handle invalid requests | Valid request works; invalid input gives a clear error |
| 6 | Docker and PostgreSQL | Start a local database; create first schema migration and seed data | Four jobs can be read from PostgreSQL |
| 7 | Database integration | Replace JSON loading with database reads | Changing a stored example changes the assessment correctly |
| 8 | React basics | Build one page with a Check jobs button | Clicking it calls the API |
| 9 | UI results | Show job, status, reason, loading, and error states | The ordinary application works without AI |
| 10 | One LLM call | Explain an existing assessment using a configured model | Explanation agrees with the actual findings |
| 11 | A controlled AI tool | Let a question trigger the assessment tool; validate arguments in code | AI obtains facts through the same service as the UI |
| 12 | LangGraph | Make explicit steps for question, assessment, and explanation | You can trace the inputs and output of each step |
| 13 | RAG | Write a short fictional policy; embed, store in pgvector, and retrieve passages | An answer cites the relevant policy passage |
| 14 | AI uncertainty | Handle no matching policy, unsupported questions, and model failures | No invented requirement or successful action is reported |
| 15 | Follow-up proposal | Produce an editable draft for a selected finding | Exact recipient and message are visible; nothing is sent |
| 16 | Local approval | Store the approved draft version and enforce approval on the server | Unapproved or edited drafts cannot execute |
| 17 | n8n and test inbox | Run one approved follow-up via authenticated local service calls | One message appears in the capture inbox |
| 18 | Workflow results | Persist and display success/failure separately from readiness | A failed send is visible and does not change job readiness |
| 19 | Complete journey | Run question -> evidence -> draft -> approval -> test email | Demonstrate the whole local flow and trace each component |
| 20 | Review and consolidate | Fix confusing behavior, run checks, and record a short walkthrough | You can explain the flow, change a rule, and diagnose one failure |

Introduce a new technology only after the preceding behavior works. Use the model's documented SDK when Session 10 arrives; provider choice and spending limits are decided then.

### Milestones

- **M1, Sessions 1–5:** correct Python checks exposed through an API.
- **M2, Sessions 6–9:** database-backed browser application.
- **M3, Sessions 10–14:** AI questions and grounded explanations.
- **M4, Sessions 15–20:** approved workflow and complete local demonstration.

Each milestone ends with one working demonstration and one short explanation from you. Add tests that protect real behavior; avoid tests that merely repeat the implementation.

## Phase 2: prepare for production

After the local flow is understood, use these as the next learning sessions. Re-estimate their duration at that point; each topic may need several sessions.

| Order | Topic | Evidence required |
| --- | --- | --- |
| 1 | Real authentication and role/record permissions | Anonymous and out-of-scope actions fail |
| 2 | Durable approvals and graph state | Restart preserves pending approval; expiry and stale evidence are handled |
| 3 | Duplicate prevention and partial failures | Retry creates no duplicate task; uncertain email outcome is reconciled before resend |
| 4 | Audit, limits, and secret handling | Trace an action; enforce request/cost limits; no credentials leak |
| 5 | Broader tests and AI evaluation | Measured correctness and groundedness; critical controls pass |
| 6 | Deployment and recovery | HTTPS, protected services, backup restore, alerts, and release recovery work |

The [preserved production plan](docs/archive/advanced-baseline/PROJECT_PLAN.md) provides detailed acceptance criteria for this phase. Its old day numbers no longer control the schedule.

The local learning demo uses only synthetic records and a capture inbox. Do not expose it publicly or enable real recipients until appropriate controls are implemented. Customer production also requires validated business need and authorised integration access.

## How we work each session

1. Explain one concept in plain language.
2. Make one small change together.
3. Run it and inspect the actual result.
4. Change or break one input to understand the behavior.
5. Record a short note: what worked, what you learned, what comes next.

## Current status

- [x] Example workflow and synthetic data prepared.
- [x] Simple architecture and learning sequence prepared.
- [x] Python 3.11.9 and project virtual environment verified.
- [x] First insurance date function implemented in `readiness.py`; JOB-102 and three date boundary cases checked.
- [x] Session 2: `assess_job` returns the expected reason for JOB-102.
- [x] Session 3: missing, unverified, insufficient-coverage and date checks; all four jobs match; 12 pytest tests pass (`python -m pytest`).
- [x] Session 4: `GET /assessments` and `GET /assessments/{job_id}` in `api.py`; run with `fastapi dev api.py`, docs at `/docs`.
- [x] Session 5: `GET /assessments?start=&end=` selects jobs that overlap the window; missing, malformed, reversed, or over-31-day windows return 422. **M1 complete.**
- [x] Session 6: PostgreSQL (pgvector image) in Docker on port 5433; Alembic migration `0001` creates the tables; `seed.py` loads the four jobs.
- [x] Session 7: API reads jobs, documents and policies from PostgreSQL via `repository.py`; rules unchanged. Tests run in rolled-back transactions.
- [x] Sessions 8–9: React page in `web/` (Vite + TypeScript) with date inputs, Check jobs, results table, loading, empty and error states. Built for the learner (fast-tracked). **M2 complete.**
- [x] Session 10: `explain.py` asks Claude (`claude-opus-5`, structured output) to explain a rules result; `check_grounding` rejects changed status/reason or unknown IDs. About 1 cent per explanation.
- [x] Richer demo data: `demo_data.py` generates 140 extra jobs, 30 contractors and a high-risk policy (fixed seed); `seed.py` resets the database to fixture + generated data (`--small` for the four fixture jobs only). Migration `0002` adds job title/site and contractor trade; the UI has summary filters and search.
- [ ] Session 11: a question triggers the assessment as a validated Claude tool.

Focus from here: AI integration, LangGraph, and the approval workflow. LLM provider: Claude (Anthropic API).

Start with [Day 1](docs/DAY_01.md). Everything else is reference material until we reach it.
