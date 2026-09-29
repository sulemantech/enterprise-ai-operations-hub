# Enterprise AI Operations Hub

An operations readiness assistant for a fictional field-service business: identify missing contractor requirements for upcoming jobs, explain the evidence, and execute approved follow-ups.

## Start here

- [FocusIMS research and opportunity limits](docs/FOCUSIMS_RESEARCH.md)
- [Settled workflow and business rules](docs/WORKFLOW.md)
- [Architecture and runtime flows](docs/architecture.md)
- [Architecture decision records](docs/decisions/README.md)
- [Architecture learning path](docs/LEARNING_PATH.md)
- [Daily tasks and milestone gates](PROJECT_PLAN.md)
- [Day 1 guided exercise](docs/DAY_01.md)
- [Synthetic starting dataset](data/demo/readiness.json)

## Current status

Workflow and delivery plan defined. Synthetic examples prepared. Application implementation has not started. The initial property-management specification and plan are preserved under `docs/archive/` as historical context; they are superseded by the documents above.

## Business context

FocusIMS publicly describes supplier, project, personnel, asset, and document management. FocusBIS describes custom solutions based on FocusIMS modules. These public descriptions inform the demonstration domain:

- [FocusIMS supplier management](https://focusims.com.au/hseqsoftware/supplier-management/)
- [FocusBIS custom solutions](https://www.focusbis.com.au/services/customims/)

Our hypothesis is that staff may still spend time investigating missing contractor evidence and coordinating follow-up across records. This is an unvalidated opportunity, not a confirmed deficiency in either product. The demo is independent, uses invented data and policies, and does not connect to client systems.

## First release

A manager asks: “Check contractor document readiness for jobs from 5 to 11 October 2026.”

The system loads authorised records, applies deterministic rules, explains findings with evidence, drafts follow-ups, obtains approval, and creates tasks and test emails. After a coordinator records reviewed replacement evidence, it reruns the assessment.

Scope: one fictional company, scheduled jobs, assigned contractors, reviewed insurance/licence metadata, one fictional requirements policy, and manager/coordinator roles. The result describes documentary readiness under that policy. It does not authorise work or certify compliance.

Later: document extraction, staff training, asset servicing, real provider adapters, multiple organisations, voice, and WhatsApp.

## Architecture

```text
Web -> FastAPI -> LangGraph -> allowlisted read tools / policy retrieval
          |                      |
          |                 proposed follow-up
          |                      v
          |                durable human approval
          |                      |
          |                      v
          |                     n8n -> business API -> tasks
          |                      |                 -> test inbox
          v                      v
PostgreSQL: jobs, contractors, evidence, assessments, approvals, actions, audit
```

- FastAPI/application services own authorization, rules, state changes, and verified results.
- LangGraph interprets requests and coordinates retrieval, clarification, and approval.
- RAG explains fictional policy with versioned citations. Missing retrieval cannot invent requirements.
- n8n runs deterministic approved workflows through authenticated APIs.
- PostgreSQL stores operational records; pgvector supports policy retrieval.
- React provides assessment, evidence, approval, and workflow views.
- A local SMTP capture inbox provides demonstrable delivery without external recipients.

The first business slice is a deterministic readiness assessment. AI is added after its expected outcomes are established.

## Working together

Act as a peer programmer and architecture partner. At each milestone explain what we are building, why, the boundaries, consequential choices, and the smallest useful implementation. Discuss meaningful architecture changes before implementing them. The workflow selected here is approved as the direction; routine implementation does not need repeated permission.

Work incrementally, explain important code, test meaningful behavior, inspect failures, and fix issues before advancing. Challenge unnecessary complexity. Keep a modular monolith and avoid speculative frameworks or infrastructure.

## Definition of success

Demonstrate a traceable path from a manager's request to evidence-backed findings, approved actions, verified outcomes, and recovery from failure. Measure quality and review time on synthetic cases. Real client value and production suitability require subsequent validation with the client.
