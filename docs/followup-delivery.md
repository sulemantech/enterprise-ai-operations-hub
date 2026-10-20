# Test-only follow-up delivery

## What changed

The **Send to test workflow** action calls FastAPI, not n8n directly. FastAPI checks the manager session, verifies the exact approved text, and allows only `@example.invalid` recipients. It then sends the approved recipient, subject, body, draft ID, and approval ID to n8n's header-authenticated `POST /followup-send` webhook.

Before the network request, FastAPI records one delivery attempt per approval and marks the draft as sending. Repeated requests for that approval return the saved outcome instead of calling n8n again. A timeout or unexpected response is recorded as `unknown`; do not retry an unknown attempt until the n8n execution has been checked. This prevents duplicate requests but does not yet automate reconciliation.

`sent` means the n8n workflow's email node returned successfully. It does not prove that a person received or read the email. The `.invalid` recipient domain is intentionally reserved and cannot receive real email; use a local capture inbox such as Mailpit for workflow testing, not production SMTP.

The job list displays the latest follow-up status separately from readiness. Sending a request does not clear a blocker; readiness changes only after updated evidence is recorded and the job is reassessed. An `unknown` or in-progress delivery disables starting another follow-up from that row until the outcome is reconciled.

## Configure a local test

1. Import and activate `n8n/followup-send.json` in your local n8n instance.
2. Configure its Header Auth credential to use header name `Authorization` and value `Bearer <your-local-token>`.
3. Set `N8N_FOLLOWUP_WEBHOOK_URL` to the active webhook URL shown by n8n, normally `http://localhost:5678/webhook/followup-send` for a local instance.
4. Set `N8N_FOLLOWUP_WEBHOOK_TOKEN` to the same local token. Keep it in `.env`; never commit or paste it into chat.
5. Use a local SMTP capture inbox and verify the n8n recipient condition still accepts only addresses ending in `@example.invalid`.
6. Apply the schema migration with `alembic upgrade head`, restart FastAPI, then create, review, and approve a draft before choosing **Send to test workflow**.

The URL and token are optional. Without them, the API responds with `503` before recording or sending a delivery attempt. Outside development, FastAPI requires an HTTPS n8n URL and rejects loopback targets. Do not allow real recipients in this prototype.

## Outcome states

| State | Meaning | Safe next action |
| --- | --- | --- |
| `sending` | An attempt was claimed; request may be underway | Wait/check n8n execution; do not submit again |
| `sent` | n8n confirmed the matching draft and approval IDs | Review the n8n execution and capture-inbox message |
| `rejected` | n8n returned its explicit test-recipient rejection | Fix the test workflow/configuration before a new approval |
| `unknown` | Timeout, server error, or unexpected response; n8n may have acted | Reconcile the n8n execution manually; do not retry |

This is a learning integration, not production delivery infrastructure. Durable retries, automated reconciliation, operational alerts, CSRF protection, and a security review remain outstanding.
