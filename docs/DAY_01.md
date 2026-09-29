# Day 1: one example, one setup check

## Today's goal

Understand JOB-102 and confirm that Python runs. You do not need to learn Docker, React, LangGraph, or n8n today.

## The example

JOB-102 runs from 6 to 9 October 2026. Its contractor's insurance expires on 7 October.

Our fictional rule says insurance must cover the whole job. Therefore the result is BLOCKED because it expires before the job finishes.

The first function we will build expresses this comparison:

```text
insurance expiry date >= job end date
```

Later we add the other checks. This is the beginning of the business logic that the API and AI will both use.

## Your next action

In your IDE PowerShell terminal, run:

```powershell
py --version
```

If it fails, try:

```powershell
python --version
```

Send the version line or error. Python could not launch in the assistant's earlier session; your terminal may work differently. We will resolve this before writing the first function.

One understanding question: if the insurance expires on 9 October, does it cover this job under our inclusive-date rule?

That is enough for today. The next session is a small Python function using [our sample data](../data/demo/readiness.json).
