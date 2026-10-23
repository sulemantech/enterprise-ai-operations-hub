# Application Architecture

Status: readiness rules, PostgreSQL persistence, API/browser assessments, tenant-scoped LangGraph explanations, approval-gated n8n test delivery, and manual operator reconciliation are implemented. Security hardening, automated delivery lookup, and production operations remain open.

## Product Context

A manager investigates contractor evidence in a contractor-management workflow. The target journey connects operational facts, readiness findings, procedure citations, and approved follow-ups. All records are synthetic; no FocusIMS or FocusBIS integration exists.

## Request Flow and Retrieval Boundary

```text
Browser -> FastAPI -> repository + readiness rules -> PostgreSQL facts
Browser -> FastAPI -> LangGraph -> tenant-scoped tools -> PostgreSQL facts
                              -> policy retrieval -> model explanation
CLI question -> LangGraph (ORG-DEMO local workflow)
FastAPI -> approved follow-up delivery -> authenticated n8n webhook -> local test inbox
```

The operational database supplies assignments, dates, contractor evidence, and policy metadata. Versioned procedure sources are indexed in PostgreSQL/pgvector; retrieval filters by organisation, policy ID, and exact policy version before semantic ranking. Missing or incompatible text must be reported and cannot alter the deterministic readiness result.

The graph's prompts do not guarantee factual accuracy. The current assessment returns one overall reason, not a complete audit finding register. Broader automated evaluations remain necessary. The browser and CLI are separate entry points.

See [knowledge sources and context](knowledge/README.md), [question scope](WORKFLOW.md), [authentication configuration](authentication.md), and [test delivery setup](followup-delivery.md).

The deterministic readiness result remains authoritative; AI explains findings but cannot change a rule result or approve a follow-up. Approval is bound to the exact recipient, subject, and message text. Uncertain delivery is recorded and a manager must document the manually verified outcome before another send.
