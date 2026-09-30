# Simple architecture

Status: rules, database, API/browser and separate CLI LangGraph workflow implemented. JOB-102, missing-ID and unknown-job CLI paths were manually demonstrated. Retrieval, approval and delivery remain planned.

## What are we building?

A manager investigates contractor evidence in the FocusIMS supplier-management business context. The target journey connects facts, findings, procedure citations and approved follow-ups. All records are fictional; no FocusIMS or FocusBIS integration exists.

## Current flow and retrieval boundary

```text
Browser -> FastAPI -> repository + readiness rules -> PostgreSQL facts
CLI question -> LangGraph -> assessment service -> repository + readiness rules
                         -> model explanation
Next: matching procedure passages -> cited explanation
```

The operational database supplies assignments, dates and coverage. The planned knowledge base supplies company procedures. PostgreSQL/pgvector will store a derived search index; source Markdown stays versioned in the project. Filter passages by organisation, policy ID and exact version before semantic ranking. Missing text must be reported and cannot alter the rules result.

The graph's prompts do not guarantee factual accuracy. Broader automated checks and evaluations remain needed. The current assessment returns one overall reason, not a complete audit finding register. The browser and CLI are separate entry points today.

See [knowledge sources and context](knowledge/README.md) and [question scope](WORKFLOW.md).

## Start with this

```text
Sample JSON data -> Python function -> Job status and reason
```

JSON is a text format for storing structured data. Our first Python function reads job and document dates and returns a result. This makes the business behavior understandable before we add other tools.

## Add one piece at a time

| Piece | Its simple job | When |
| --- | --- | --- |
| Python | Check the document requirements | First |
| FastAPI | Let another program request that check through HTTP | After the function works |
| PostgreSQL | Save and read records in a database | After the API works |
| React | Display results and buttons in a browser | After stored records work |
| LLM | Interpret a question and explain known results | After the ordinary app works |
| LangGraph | Organise the AI steps and their shared state | After one model call works |
| RAG with pgvector | Find relevant policy text to support an answer | After the graph works |
| n8n | Run the approved follow-up workflow | After proposals work |

Docker helps run supporting services such as PostgreSQL and n8n. Introduce it when we need the first service.

## The eventual local flow

```text
Manager uses React
    -> FastAPI receives the request
    -> LangGraph coordinates the question
    -> Python reads PostgreSQL and checks requirements
    -> Relevant policy text helps explain the result
    -> Manager approves an exact message
    -> Server checks that approval
    -> n8n sends to a local test inbox
    -> Browser shows the actual result
```

React and LangGraph use the same business checks. AI cannot change a rule result or approve its own message.

## Three rules to remember now

1. Python code decides whether document requirements pass.
2. The server requires approval before executing a follow-up.
3. The UI reports success only after the operation succeeds.

Our first local approval records the exact draft that was approved. Editing it requires approval again. A local demo user is only a development convenience; real authentication comes before shared deployment.

## Learn later

Restart recovery, expired approvals, duplicate prevention, service permissions, detailed audit records, backups, and deployment. These remain required for production preparation. We will teach them through concrete failures after the first local flow works.

The earlier [detailed architecture](archive/advanced-baseline/docs/architecture.md) is preserved as optional reference. It is not today's reading assignment. See the [short decisions](decisions/README.md) for our current choices.
