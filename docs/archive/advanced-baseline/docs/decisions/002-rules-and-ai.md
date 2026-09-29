# ADR-002: deterministic readiness with AI interpretation and explanation

Status: Accepted as design direction; not implemented.
Date: 2026-09-29.

## Context

The same job, evidence, and requirement version must yield the same readiness findings. Missing information must remain visible. Users also benefit from natural-language questions and explanations.

## Decision

Pure domain functions calculate readiness using structured reviewed metadata and versioned requirement configuration. LangGraph interprets requests, asks clarifying questions, calls typed tools, and prepares explanations/proposals. RAG retrieves version-matched policy passages for explanation. Model output cannot change readiness or grant permission.

## Alternatives

- Ask an LLM to determine readiness from documents: handles varied language but makes fixed rules harder to reproduce and introduces extraction uncertainty. Document extraction can later propose metadata for review.
- A dashboard with no AI: simpler and may already solve the user's need; retain structured assessment as a usable path. Validate whether conversational investigation actually improves the task.
- Use vector search for operational facts: convenient natural-language access, but freshness and approximate retrieval are unsuitable for authoritative dates and assignments.

## Consequences

Business outcomes are independently testable and remain available when AI fails. We must keep structured rules and explanatory policy versions aligned. AI adds provider cost and latency, which need measured justification.

## Verification

Known and boundary cases produce exact reason codes without a model. Empty retrieval cannot change the findings. Adversarial requests cannot waive missing evidence. Measure explanation grounding and date interpretation separately from rule correctness.

## Revisit when

New requirements genuinely require interpretation. First define review authority and uncertainty handling; do not silently replace code with a prompt.
