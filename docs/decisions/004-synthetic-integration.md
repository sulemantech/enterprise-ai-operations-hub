# ADR-004: independent synthetic integration environment

Status: Accepted as design direction; not implemented beyond initial fixtures.
Date: 2026-09-29.

## Context

Client data and production-system access are unavailable without consent. We need repeatable examples and observable integration behavior while assessing an unvalidated business opportunity.

## Decision

Use invented contractors, jobs, reviewed evidence metadata, and company requirements. Build a small internal business API and capture messages in a local test inbox. Label the demonstration and its policies clearly. Defer real client adapters and document extraction.

## Alternatives

- Wait for client data/access: more representative, but blocks independent learning and development.
- Use anonymised client exports: may retain sensitive or identifying details and still requires appropriate authorisation.
- Connect an unrelated external CRM immediately: demonstrates that vendor's API but adds accounts and mapping work without proving the chosen business workflow.

## Consequences

The demo can run independently and repeatedly. It cannot establish compatibility with FocusIMS APIs, real policy accuracy, or actual client savings. Synthetic scenarios must include failures and ambiguity, not only successful examples.

## Verification

Fixtures contain only invented records and non-deliverable example addresses. Messages remain in a test inbox. Setup requires no client credentials. Evaluation results are labelled as synthetic.

## Revisit when

The client validates the problem and authorises a defined integration scope. Confirm API contracts and data handling before adding an adapter.
