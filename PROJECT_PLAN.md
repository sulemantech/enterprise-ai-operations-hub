# Product Delivery Plan

## Product Objective

Demonstrate a controlled contractor-evidence workflow for an operations manager: assess assigned evidence against a job and applicable procedure, explain a finding with source citations, and prepare an approved follow-up. The first reference scenario is JOB-102, where insurance evidence expires before the job ends.

This plan tracks product capability and evidence of readiness. The repository currently contains a local evaluation prototype using synthetic data; it is not an authorised client system or production deployment.

## Current Demonstration

- Deterministic readiness rules return structured statuses and reasons for missing, unverified, insufficient, or date-invalid contractor evidence.
- FastAPI exposes date-window assessments backed by PostgreSQL; the React dashboard presents counts, search, explanations, and follow-up state.
- FastAPI invokes LangGraph for question handling; retrieval is scoped by organisation and policy version, with citations checked against retrieved passages.
- Follow-up drafts are stored and editable. Approval records the exact message version; the API refuses unapproved or modified text.
- Approved test follow-ups are dispatched through an authenticated n8n webhook. The local workflow has been exercised with Mailpit, and delivery status is recorded independently of readiness.
- Local-only development access and Hellō OIDC login with signed API sessions and membership/role checks are implemented.

## Delivery Stages

| Stage | Objective | Acceptance evidence | State |
| --- | --- | --- | --- |
| Evidence assessment | Return consistent readiness and reason codes for assigned contractor evidence | Fixed JOB-101–JOB-104 examples and automated rule/API tests pass | Implemented |
| Operational dashboard | Let a manager review jobs by date, search/filter, and inspect explanations | Browser calls authenticated FastAPI endpoints and displays loading, empty, and error states | Implemented |
| Procedure-grounded explanation | Explain a finding without changing the deterministic result | Retrieved policy passages are version-scoped and returned citations are validated | Implemented; broader evaluation pending |
| Approved follow-up | Prepare, edit, approve, dispatch, and display test delivery state | Exact-text approval enforced; authenticated n8n delivery recorded; test email appears in Mailpit | Locally exercised |
| Delivery reconciliation | Give an operator a safe way to resolve an uncertain outcome | An unknown delivery can be reconciled against the workflow before a retry is allowed | Not implemented |
| Production security and operations | Establish complete identity, tenant boundaries, audit, recovery, and deployment controls | Security review and operational acceptance criteria pass | Not ready |
| Client validation | Verify the workflow and integration fit with authorised stakeholders | Confirmed user task, authoritative records/procedure, access approval, and measurable evaluation criteria | Not started |

## Priority Work

### 1. Resolve uncertain deliveries safely

Add an operator-only reconciliation process for `delivery_unknown` records. It must identify the corresponding n8n execution, capture the outcome and evidence, prevent accidental duplicate sends, and expose the resolution in the dashboard. A retry must remain unavailable until reconciliation establishes that no message was sent.

### 2. Complete security controls

- Apply and test organisation scoping to every repository query and state-changing operation.
- Implement and test CSRF protection for browser-authenticated state changes.
- Add auditable membership provisioning and administrator workflows.
- Review session lifetime, cookie attributes, secret handling, access logging, and rate/cost limits.

### 3. Validate quality and operations

- Build repeatable evaluation cases for explanations, unsupported questions, citation accuracy, and retrieval failures.
- Exercise n8n/mailbox outage, timeout, duplicate, partial-send, and database-restart scenarios.
- Define monitoring, backup/restore, release rollback, and incident response.
- Establish a stakeholder-approved pilot evaluation using authorised data only after security gates pass.

## Release Gates

No production or client-data release until all of the following are true:

1. Business owner confirms requirements, policies, and the intended decision workflow.
2. Security review verifies identity, tenant isolation, CSRF, secrets, auditability, and least privilege.
3. Delivery recovery prevents duplicate or untracked follow-ups and has an operational owner.
4. AI answers are evaluated against an agreed test set; the deterministic rule result remains authoritative.
5. Deployment, data retention, backup, support, and incident processes are approved.
6. Any product integration is explicitly authorised and tested against its supported API and data model.

## Scope Boundaries

The current demonstration uses fictional organisations, jobs, contractors, evidence, and procedures. It does not establish legal, safety, regulatory, or ISO compliance; authorise work; or replace an authoritative business system. File upload/OCR, automatic policy authoring, broad document-type checks, and live product integrations remain out of scope until a stakeholder validates their need and provides approved sources.
