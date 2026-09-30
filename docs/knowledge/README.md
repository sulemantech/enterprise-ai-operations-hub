# Knowledge base: contractor evidence

Status: source content and retrieval design only. Ingestion and RAG are not implemented yet.

## Purpose and data

Help a FocusIMS-context operations manager connect a readiness finding to the applicable company procedure. A FocusBIS consultant could later use these references for review preparation. The fictional organisation is Demo Field Services (`ORG-DEMO`).

| Source | Content | Use |
| --- | --- | --- |
| PostgreSQL operational records | Jobs, assignments, document dates, coverage, review status | Tools retrieve current facts and run rules |
| Versioned company procedures | Evidence requirements, validity, review and follow-up instructions | RAG retrieves passages for explanations |
| Structured policy configuration | Required types and minimum insurance amount | Authoritative inputs to Python rules |
| Future action records | Approved draft and delivery outcome | Tools report what actually happened |

`data/demo/readiness.json` supplies fixtures; `demo_data.py` adds generated operational data. These records are not the RAG corpus. Public FocusIMS/FocusBIS pages provide business context, not an approved customer procedure. Do not ingest source code, `.env` or credentials as knowledge.

## First source and questions

[Contractor Approval and Monitoring Procedure](contractor_approval_procedure.md), `DEMO-CONTRACTOR-001` version 1:

The procedure document is now `PROC-CONTRACTOR-001` version 2 (draft); the structured policy remains version 1. Keep both version fields in citations and chunk metadata. CP-01 to CP-06 describe existing checks; CP-07 to CP-12 describe proposed/manual processes. Store an `implementation_scope` label on chunks so process guidance cannot be mistaken for evidence that the application performed a check. Label all retrieved passages as synthetic draft content.

- Why must insurance cover the whole job? -> CP-03.
- What insurance amount does this policy require? -> CP-04.
- Why does unverified evidence need review? -> CP-05.
- Does READY establish ISO compliance? -> CP-06: no.
- What follow-up should happen? -> CP-07, a planned workflow.
- Who collects, reviews and accepts contractor evidence? -> CP-08.
- What should a reviewer check beyond expiry dates? -> CP-09.
- Does this job need a SWMS or induction? -> CP-10 explains the human review; current records cannot determine completion or task-specific applicability.
- What happens if job dates change? -> CP-11.
- What should be retained for a contractor review? -> CP-12, proposed records rather than implemented history.

The procedure now includes a manual evidence-review checklist. Later sources may include approved task-specific procedures and verified ISO mappings. Neither full ISO standards nor private client procedures are included. Never invent clause citations. Public references are contextual guidance, not automatically approved customer requirements.

## Implementation steps for Session 13

1. Review source text against the structured demo policy and implemented rules.
2. Split at CP section headings, retaining enough context for each passage to stand alone.
3. Store organisation ID, policy ID/version, document ID/version, section ID, title, source path, content hash, text and embedding model identifier per chunk.
4. Choose the embedding provider/model and dimension, then add a migration and repeatable ingestion process. Avoid duplicate chunks on re-indexing.
5. Derive scope and exact policy/version from the loaded job, not model-generated arguments. Filter before semantic ranking.
6. Search using the question and assessed reason. Give the model a small set of passages alongside authoritative operational facts.
7. Require section citations and verify cited IDs exist in the retrieved set. This alone does not establish semantic accuracy.

Retrieved text is untrusted input. It cannot grant permissions, execute actions or override code decisions.

## What goes into the model context?

- User question and explicit job ID.
- Relevant job, document and policy facts, including source versions.
- Python status/reason, separate from model prose.
- Matching procedure passages with source and section identifiers.
- Instructions to cite supporting passages and report missing sources.

For JOB-102, database records establish that DOC-003 ends on 2026-10-07 and the job ends on 2026-10-09. The assessment remains BLOCKED / EXPIRES_BEFORE_JOB_END. Retrieval supplies the full-period requirement; cite `DEMO-CONTRACTOR-001 v1, CP-03`.

## Acceptance cases

| Case | Expected behavior |
| --- | --- |
| JOB-102 with matching CP-03 | Correct dates, unchanged status and traceable citation |
| JOB-104 with CP-05 | Explain pending review without claiming authenticity |
| Job using a different generated policy | Do not substitute this policy's AUD 5 million threshold; report missing procedure until its source exists |
| Empty retrieval or failure | Return available structured assessment and disclose citation limitation |
| Procedure conflicts with configured rule | Preserve rule result and flag the inconsistency for review |
| ISO certification question | Explain limited document-check scope; no compliance verdict |

First milestone: a cited JOB-102 explanation. Full finding registers, audit exports and browser integration remain later work.
