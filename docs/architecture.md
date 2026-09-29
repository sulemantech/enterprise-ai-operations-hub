# Simple architecture

Status: learning design; application implementation has not started.

## What are we building?

A manager asks which jobs have missing contractor documents, reads the reasons, and approves a follow-up to a test inbox. All records are fictional.

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
