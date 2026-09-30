# Enterprise AI Operations Hub

Learn to build an AI application from end to end, one working step at a time.

## Business focus

**Contractor Evidence and Audit Preparation Assistant**, inspired by the FocusIMS supplier-management domain. The primary user is an operations manager at a trade or maintenance business. FocusBIS consultants preparing contractor evidence for review are a secondary potential audience.

The target question is: **“Why is JOB-102 blocked, which company procedure applies, and what should we request from the contractor?”**

FocusIMS already describes contractor-document management. Our proposed contribution connects conversational investigation, operational facts, procedure citations and approved follow-ups. This is an independent synthetic prototype, not an official product or integration. Client value and integration compatibility remain unvalidated. See the [public-product research](docs/FOCUSIMS_RESEARCH.md).

### Current capabilities

- Implemented: readiness rules, PostgreSQL records, API/browser results and a separate CLI AI workflow using validated tools and LangGraph.
- Manually demonstrated: JOB-102 explanation, missing job-ID clarification and unknown-job handling.
- Next: versioned company-procedure retrieval and citations.
- Planned: follow-up drafts, server-enforced approval, n8n test-inbox delivery and production controls.

The CLI graph is not yet connected to the browser. Document readiness is not an ISO compliance verdict or permission to commence work.

See [questions and workflow](docs/WORKFLOW.md) and [knowledge sources and RAG context](docs/knowledge/README.md).

## Our example

A manager checks fictional jobs and sees which contractors have missing documents. The planned complete journey adds procedure citations and approved follow-ups to a test inbox. Four fixed jobs provide predictable examples; generated records provide a larger dataset.

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

## How we will build it

Python rules -> FastAPI -> PostgreSQL -> React -> LLM -> LangGraph -> RAG -> n8n -> complete demo.

Each addition solves a problem you can already see. We will explain the code, run it, and change an example to understand its behavior before adding the next technology.

## Working together

Prioritise understanding and small working changes. Explain unfamiliar terms when they first appear. Teach only what the current step needs. Ask one short understanding question after a demonstration; avoid long homework lists. Discuss meaningful architecture changes, and keep documentation short.

The first end-to-end version runs locally with synthetic records and captured test email. Authentication, durable approvals, recovery, and deployment follow in a separate production preparation phase. Public deployment and real recipients require those controls first.

## Optional references

- [Workflow](docs/WORKFLOW.md)
- [Learning approach](docs/LEARNING_PATH.md)
- [Short decision summary](docs/decisions/README.md)
- [FocusIMS research](docs/FOCUSIMS_RESEARCH.md)
- [Preserved detailed plan](docs/archive/advanced-baseline/PROJECT_PLAN.md)
