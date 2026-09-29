# ADR-003: durable approval and explicit recovery

Status: Accepted as design direction; not implemented.
Date: 2026-09-29.

## Context

Follow-ups create tasks and messages. A user may edit a draft, evidence may change, processes may restart, and webhook responses may be lost after successful execution.

## Decision

Persist approval for an immutable action version containing exact recipient, message, task details, source versions, actor, and expiry. The application revalidates permission and source freshness when execution is claimed. Record durable action/step outcomes and use database uniqueness constraints for idempotent task creation. Keep graph checkpoints separate from business authorisation. Unknown email delivery is reconciled or reviewed before resend.

## Alternatives

- In-memory approval: minimal code, but restart loses state and cannot support durable review.
- Model confirmation or a UI-only approval button: useful interaction, but insufficient authority when an endpoint can be called directly.
- Retry the entire workflow after every timeout: simple, but can duplicate successful side effects.
- One transaction for all steps: database transactions do not include independent SMTP delivery.

## Consequences

More persistent states and failure tests are required. Task creation can be idempotent while email outcome remains uncertain. A draft edit invalidates approval, introducing another review step. Evidence freshness is checked at execution claim; future changes do not retroactively cancel an already issued message.

## Verification

Exercise restart while pending, repeated approval, changed payload, expiry, stale evidence, duplicate webhook, task success/email failure, and lost delivery acknowledgement. No unapproved operation executes; uncertain outcomes are not displayed as successful.

## Revisit when

A real provider offers delivery lookup or idempotency support, or customer policy requires different approval scope/expiry. Preserve explicit authority and recovery guarantees when adapting.
