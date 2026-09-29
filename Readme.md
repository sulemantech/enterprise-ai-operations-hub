# Enterprise AI Operations Hub

Learn to build an AI application from end to end, one working step at a time.

## Our example

A manager checks four fictional jobs, sees which contractors have missing documents, and approves a follow-up message to a test inbox.

We use invented data inspired by the FocusIMS business domain. This is an independent learning project; its value to that client is still unvalidated.

## Start here

1. [Today's small exercise](docs/DAY_01.md)
2. [Simple architecture](docs/architecture.md)
3. [Step-by-step plan](PROJECT_PLAN.md)

## Run it locally

Needs Python 3.11 and Docker Desktop. From the project folder, in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env          # then set your own local password in .env

docker compose up -d            # start PostgreSQL (port 5433)
alembic upgrade head            # create the tables
python seed.py                  # load the four demo jobs

python -m pytest                # run the checks
fastapi dev api.py              # API docs at http://127.0.0.1:8000/docs
```

In a second terminal, the browser page (needs Node.js 20.19+):

```powershell
cd web
npm install
npm run dev                     # open http://localhost:5173
```

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
