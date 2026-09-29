# Enterprise AI Operations Hub

Learn to build an AI application from end to end, one working step at a time.

## Our example

A manager checks four fictional jobs, sees which contractors have missing documents, and approves a follow-up message to a test inbox.

We use invented data inspired by the FocusIMS business domain. This is an independent learning project; its value to that client is still unvalidated.

## Start here

1. [Today's small exercise](docs/DAY_01.md)
2. [Simple architecture](docs/architecture.md)
3. [Step-by-step plan](PROJECT_PLAN.md)

No application code has been written yet. The sample data is ready.

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
