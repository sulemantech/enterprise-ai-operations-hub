# Simple workflow

## The question

“Which of these four jobs have missing contractor documents?”

Use the fixed fictional dates in [the sample data](../data/demo/readiness.json). No client access or real email account is needed.

## What we do

1. Read a job and its contractor documents.
2. Check required insurance and licence records using Python.
3. Show a status and reason.
4. Later, explain the result through an AI assistant.
5. Draft a follow-up, let the manager approve it, and send it to a local test inbox through n8n.

## Rules for our first examples

- Both insurance and a trade licence are required.
- Evidence must have been reviewed and marked verified.
- Dates must cover the whole job, including its final day.
- Insurance must meet the fictional policy's configured coverage amount.
- Missing or insufficient evidence blocks readiness; uncertain evidence needs review.

These are invented demonstration requirements, not legal or ISO advice.

| Job | What happens | Result |
| --- | --- | --- |
| JOB-101 | Both documents meet the requirements | READY |
| JOB-102 | Insurance expires before the job ends | BLOCKED |
| JOB-103 | Licence is missing | BLOCKED |
| JOB-104 | Insurance has not yet been reviewed | NEEDS_REVIEW |

READY means these document checks pass. A reminder does not change readiness; new reviewed evidence can.

## Keep the first version small

Use the explicit date window in the fixture, one local demo manager, and structured document metadata. Defer natural-language dates, file uploads/OCR, additional roles, staff training checks, and equipment checks.

The original [detailed workflow](archive/advanced-baseline/docs/WORKFLOW.md) remains a reference for later edge cases. Implement and test those cases progressively instead of learning them all upfront.
