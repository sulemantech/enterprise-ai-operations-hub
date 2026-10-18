# Enterprise AI Operations Hub

Learn to build an AI application from end to end, one working step at a time.

## Business focus

**Contractor Evidence and Audit Preparation Assistant**, inspired by the FocusIMS supplier-management domain. The primary user is an operations manager at a trade or maintenance business. FocusBIS consultants preparing contractor evidence for review are a secondary potential audience.

The target question is: **“Why is JOB-102 blocked, which company procedure applies, and what should we request from the contractor?”**

FocusIMS already describes contractor-document management. Our proposed contribution connects conversational investigation, operational facts, procedure citations and approved follow-ups. This is an independent synthetic prototype, not an official product or integration. Client value and integration compatibility remain unvalidated. See the [public-product research](docs/FOCUSIMS_RESEARCH.md).

### Current capabilities

- Implemented: readiness rules, PostgreSQL records, API/browser assessments, a separate LangGraph CLI with policy retrieval and citation checks, and saved follow-up drafts with exact-text approval records.
- Manually demonstrated: JOB-102 explanation, missing job-ID clarification and unknown-job handling.
- Still to connect: browser/API to LangGraph, and the post-approval server gate to the n8n webhook and delivery-status handling.
- Before production: real authentication, tenant authorization, idempotent execution, reliable delivery reconciliation, audit and recovery controls.

The CLI graph is not yet connected to the browser. Document readiness is not an ISO compliance verdict or permission to commence work.

See [questions and workflow](docs/WORKFLOW.md) and [knowledge sources and RAG context](docs/knowledge/README.md).

## System architecture

![End-to-end connected architecture: solid lines show working capability; dashed lines show integration work remaining](docs/end-to-end-connected-architecture.png)

The diagram shows the complete target journey. The React app, FastAPI, Python checks, PostgreSQL, LangGraph CLI, draft approval records, and n8n test workflow exist, but the API-to-LangGraph and approval-gated API-to-n8n connections still need wiring. This is a project in progress, not a deployed production service or a real customer integration. [Open the SVG](docs/end-to-end-connected-architecture.svg).

### Component flows

The [LangGraph + AI diagram](docs/langgraph-ai-flow.svg) details tool routing, deterministic checks, policy retrieval and citation validation. The [n8n diagram](docs/n8n-followup-workflow.svg) shows its authenticated webhook, test-recipient guard, SMTP step and response branches. Both distinguish existing workflow logic from connections still to build.

![LangGraph and AI reasoning flow](docs/langgraph-ai-flow.png)

![n8n guarded follow-up workflow](docs/n8n-followup-workflow.png)

See the [animated workflow GIF](docs/contractor-readiness-workflow.gif) and [LinkedIn architecture image](docs/contractor-readiness-production-linkedin.png) for additional visuals.

## Our example

A manager checks fictional jobs and sees which contractors have missing documents. A separate CLI can explain a result with matching procedure passages; saved follow-up drafts can be reviewed and approved. The API-to-LangGraph and approval-gated n8n delivery connections remain to be built. Four fixed jobs provide predictable examples; generated records provide a larger dataset.

We use invented data inspired by the FocusIMS business domain. This is an independent learning project; its value to that client is still unvalidated.

## Start here

1. [Today's small exercise](docs/DAY_01.md)
2. [Simple architecture](docs/architecture.md)
3. [Step-by-step plan](PROJECT_PLAN.md)

## Run it locally

Needs Python 3.11 and Docker Desktop. From the project folder, in CMD:

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env

docker compose up -d
alembic upgrade head
python seed.py

python -m pytest
fastapi dev api.py
```

Set database credentials and the model API key in `.env`. PostgreSQL uses port 5433; API docs are at http://127.0.0.1:8000/docs. Seeding resets demo records: the default loads fixtures plus generated data; `python seed.py --small` loads only the four fixture jobs.

Run the separate graph with `python readiness_graph.py "Why is JOB-102 blocked?"`. This makes paid model requests.

In a second terminal, the browser page (needs Node.js 20.19+):

```cmd
cd web
npm install
npm run dev
```

Open http://localhost:5173.

## Integration roadmap

Current: React -> FastAPI -> Python rules + PostgreSQL; separate CLI -> LangGraph -> tools + policy retrieval.

Next: FastAPI -> LangGraph; after human approval, FastAPI -> n8n -> test inbox -> recorded delivery outcome.

Each addition solves a problem you can already see. We will explain the code, run it, and change an example to understand its behavior before adding the next technology.

## Working together

Prioritise understanding and small working changes. Explain unfamiliar terms when they first appear. Teach only what the current step needs. Ask one short understanding question after a demonstration; avoid long homework lists. Discuss meaningful architecture changes, and keep documentation short.

The app uses synthetic records, and the n8n workflow is restricted to test recipients. The browser-to-LangGraph and server-to-n8n paths are not connected end-to-end yet. Public deployment and real recipients require authentication, approval-gated execution, durable audit and recovery controls first.

## Optional references

- [Workflow](docs/WORKFLOW.md)
- [Learning approach](docs/LEARNING_PATH.md)
- [Short decision summary](docs/decisions/README.md)
- [FocusIMS research](docs/FOCUSIMS_RESEARCH.md)
- [Preserved detailed plan](docs/archive/advanced-baseline/PROJECT_PLAN.md)
