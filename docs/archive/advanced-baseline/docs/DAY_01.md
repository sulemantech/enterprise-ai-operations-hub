# Day 1: understand the workflow and prepare your environment

## Today's outcome

Explain how the four example jobs are assessed and establish whether your local Python and Docker tools work. No model account, client data, or CRM account is needed today.

The first implementation will be a small deterministic assessment service. Before building it, establish what correct results look like.

## 1. Walk through the data (30–45 minutes)

Open [the workflow](WORKFLOW.md) and [the synthetic dataset](../data/demo/readiness.json).

All jobs use the invented policy `DEMO-CONTRACTOR-001`. It requires verified insurance and trade-licence metadata covering the entire job. The insurance threshold is an arbitrary demo setting.

In your IDE PowerShell terminal:

```powershell
$demo = Get-Content -Raw -Encoding UTF8 .\data\demo\readiness.json | ConvertFrom-Json
$demo.jobs | Format-Table id, start_date, end_date, contractor_ids
$demo.documents | Format-Table id, contractor_id, type, review_status, valid_to
```

Work out each job's status before checking `expected_results`.

Questions to explain in your own words:

1. Why is JOB-102 blocked even though the insurance is valid when the job starts?
2. Why does JOB-104 need review even though its dates cover the job?
3. If we send CON-003 a reminder, should JOB-103 become ready?
4. If an old insurance record is expired but a verified renewal covers the job, which evidence should satisfy the requirement?

Expected reasoning: cover the entire job; unreviewed metadata is uncertain; reminders do not supply missing evidence; a qualifying verified renewal can satisfy the requirement.

## 2. Understand the first code boundary (20 minutes)

Read sections 1–4 of [the architecture](architecture.md) and [ADR-002](decisions/002-rules-and-ai.md). Complete the five-question exercise in [the learning path](LEARNING_PATH.md). Explain your reasoning before moving on; this replaces the brief code-boundary discussion with guided architecture practice.

The first useful function will conceptually be:

```text
assess(job, contractor_documents, policy)
    -> status, reason_codes, evidence_references
```

It receives records and applies explicit rules. It does not call an LLM, send messages, or alter evidence. This lets us test business correctness directly. FastAPI will expose this behavior; LangGraph will later call it as a tool.

## 3. Check tools in your terminal (15–30 minutes)

Run commands separately so one failure does not obscure the others:

```powershell
py --version
python --version
node --version
npm --version
git --version
docker --version
docker compose version
docker info --format '{{.ServerVersion}}'
```

Open Docker Desktop before the last command. Share version lines and errors only; avoid posting configuration files or credentials.

Observed in the assistant session during planning:

- Node: v20.19.4; Git: 2.39.2.windows.1.
- Python launcher found but could not start its configured interpreter.
- Docker CLI: 20.10.23; Compose and daemon checks could not read the user's Docker configuration because access was denied.
- These observations do not prove your own terminal has the same problem. Verify there before reinstalling or changing permissions.

We will choose compatible supported runtime versions before installing dependencies. Tool detection alone is not a compatibility check.

## 4. Sketch one follow-up (20–30 minutes)

Use JOB-103. Write a short draft requesting the missing licence evidence from `three@example.invalid`. Identify the job, missing record, and the manager who must approve the draft. This address is deliberately non-deliverable; the eventual workflow captures mail locally.

Explain what must be stored before execution: approved recipient, exact message, task details, action version, reviewer, expiry, and assessment source versions.

## 5. Close the session

- [ ] I can explain each expected status.
- [ ] I understand the difference between readiness, evidence review, and follow-up status.
- [ ] I have checked Python, Node/npm, Git, and Docker in my own terminal.
- [ ] I can describe one proposed action and its approval boundary.
- [ ] I have stated my daily availability and experience with Python, React, Docker, and LangGraph/n8n so the pace can be adjusted.

Send the tool results and any unclear rule. Next session: scaffold the API and explain each file as we add it. The business rules will then be implemented in small steps against these examples.
