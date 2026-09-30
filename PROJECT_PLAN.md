# Learning-first project plan

## Goal

Understand and build one complete local workflow: check fictional jobs, explain missing contractor evidence, approve a follow-up, and see it in a test inbox.

Business focus: contractor evidence and audit preparation inspired by FocusIMS supplier management; FocusBIS consulting is a secondary potential use. Use synthetic Demo Field Services records and company procedures. No client integration or verified ISO clause mapping is included. See [questions](docs/WORKFLOW.md) and [knowledge-base design](docs/knowledge/README.md).

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
| 13 | RAG | Index the synthetic contractor procedure with organisation, policy version and section metadata | JOB-102 cites CP-03 from DEMO-CONTRACTOR-001 v1; incompatible policy passages are excluded |
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
- [x] Session 11: CLI tool selection, validation, assessment and explanation; missing-ID and unknown-job handling manually demonstrated.
- [x] Session 12: LangGraph nodes and conditional routing implemented; user demonstrated JOB-102, missing-ID and unknown-job paths. These are manual checks, not comprehensive AI evaluation.
- [ ] Session 13: source procedure prepared in `docs/knowledge/`; chunking, embeddings, pgvector retrieval and citations still to implement.

Focus from here: versioned procedure retrieval, explanation evaluation and approved follow-ups. LLM provider: Claude (Anthropic API). Choose an embedding provider separately before indexing.

Next: read the [knowledge-base plan](docs/knowledge/README.md) and its synthetic procedure. Day 1 remains an onboarding reference.

## Next session: tomorrow — Session 13A, prepare retrieval passages

Completed today:

- [x] Demonstrated the three LangGraph paths: assessed job, missing job ID and unknown job.
- [x] Selected FocusIMS contractor evidence review as the primary business context.
- [x] Defined supported versus planned questions and the boundary between operational data and RAG sources.
- [x] Prepared procedure document v2 (draft), including manual review responsibilities and site coordination; automated policy remains v1.

Tomorrow's first task is to write a small section loader, with the learner writing code and the assistant reviewing it.

1. Create `knowledge_ingest.py` with a function that reads the procedure as UTF-8.
2. Split only at numbered CP headings, producing 12 nonempty passages, CP-01 through CP-12. Keep the heading and section text; exclude introductory and reference-history text from section bodies.
3. Attach organisation, policy ID/version, document ID/version, source path and section ID to each passage. Preserve the draft/synthetic label and distinguish implemented checks (CP-01–06) from proposed/manual processes (CP-07–12).
4. Print the IDs, titles and lengths for inspection. Confirm CP-03 preserves the full-job validity requirement and CP-10 does not imply site checks have been completed.
5. Check missing-file handling, duplicate section IDs and empty sections locally, without paid model calls.

Done when: the source becomes 12 traceable passages and you can explain the difference between policy version 1 and procedure document version 2.

After that: select an embedding model and cost limit, create pgvector storage and ingestion, then retrieve by matching organisation/policy version and add citations. Do not call Session 13 complete until JOB-102 cites the right passage and missing/incompatible sources are handled.

Deferred: PDF uploads/OCR, private client data, ISO clause mappings and automatic checks for induction, SWMS or permits. These do not block the first RAG demonstration.
