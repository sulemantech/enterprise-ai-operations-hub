# Simple workflow

## Business context

Primary use: a FocusIMS-context operations manager investigating contractor evidence for a fictional trade business, Demo Field Services (`ORG-DEMO`). Secondary potential use: a FocusBIS consultant preparing contractor evidence for internal review. No real client data or integration is used.

## The question

“Why is JOB-102 blocked, which company procedure applies, and what should we request from the contractor?”

## Questions and delivery scope

| Question | Source | Availability |
| --- | --- | --- |
| Why is JOB-102 blocked? | Job, documents, policy and rule result | CLI graph implemented and demonstrated |
| Is JOB-101 ready under these checks? | Operational assessment | Existing tool capability |
| Is the job ready? | Job ID clarification | Demonstrated |
| Is JOB-9999 ready? | Job lookup | Missing-job handling demonstrated |
| Which jobs overlap 5–11 October 2026? | Database date-window query | API/browser; no conversational list tool yet |
| Which procedure requires full-job insurance cover? | Versioned procedure passage | Session 13 target |
| Why does JOB-104 need review, and what should happen next? | Assessment and review procedure | Assessment exists; citation planned |
| Draft a request for updated evidence. | Finding, contact and follow-up instructions | Sessions 15–16 |
| Was the approved request delivered? | Stored execution records | Sessions 17–18 |
| Prepare contractor evidence references for an internal review. | Findings, procedures and action history | Later extension, not an implemented audit report |

Out of scope now: company-wide ISO verdicts, certification, legal advice, authenticity checks, OCR and full finding registers. The rule function returns one overall status/reason, not all possible gaps. Natural-language dates remain deferred.

Use the fixed fictional dates in [the sample data](../data/demo/readiness.json). No client access or real email account is needed.

## What we do

1. Read a job and its contractor documents.
2. Check required insurance and licence records using Python.
3. Show a status and reason.
4. Explain the result through the implemented CLI AI assistant.
5. Next, retrieve the matching company procedure and cite its section/version.
6. Later, draft a follow-up, let the manager approve it, and send it to a local test inbox through n8n.
7. Later, retain evidence references and action outcomes for review.

## Rules for our first examples

- Both insurance and a trade licence are required.
- A job without an assigned contractor is blocked.
- Evidence must have been reviewed and marked verified.
- Dates must cover the whole job, including its final day.
- Insurance must meet the fictional policy's configured coverage amount.
- Missing or insufficient evidence blocks readiness; uncertain evidence needs review.

These are invented demonstration requirements, not legal or ISO advice.

The first [knowledge-base procedure](knowledge/contractor_approval_procedure.md) applies only to `DEMO-CONTRACTOR-001`, version 1. Other generated policies need their own matching passages; never substitute this procedure's insurance threshold for another policy.

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
