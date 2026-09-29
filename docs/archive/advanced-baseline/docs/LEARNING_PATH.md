# Architecture learning through implementation

## How we will work

The goal is for you to make and defend architecture decisions, implement the boundaries, and diagnose failures. Reading documents alone will not establish expertise; repeated design, testing, and operation build it.

For each milestone:

1. Explain the business problem and constraints in your own words.
2. Predict behavior for one normal case and one failure before coding.
3. Compare at least two approaches and state the trade-off.
4. Implement a small slice together and explain the important code.
5. Run a test that could disprove our design assumption.
6. Teach the design back in a short walkthrough and update the ADR if evidence changes it.

Ask for an explanation whenever a term is unfamiliar. We will adjust depth based on your answers rather than assume experience you have not stated.

## Milestone practice

| Milestone | Concepts | Practical exercise | Evidence of understanding |
| --- | --- | --- | --- |
| M1 | Domain model, invariants, pure functions, boundaries | Evaluate JOB-102; add an expiry-equals-end-date case | Explain why the check belongs in code and predict the boundary result |
| M2 | Authentication, authorisation, ownership, transactions | Attempt an out-of-scope record lookup | Identify the enforcing server boundary and explain why hiding a UI button is insufficient |
| M3 | Tool contracts, retrieval, grounding, uncertainty | Remove the matching policy passage; inject an instruction into retrieved text | Explain what still works, what must be withheld, and why tool permissions remain enforced |
| M4 | Idempotency, approval scope, state machines, partial failure | Lose the response after task creation; then retry | Show one task and explain why email may still have an unknown outcome |
| M5 | Evaluation design, observability, cost and latency | Compare a correct answer with an unsupported fluent answer | Separate rule correctness, model quality, and business value in the report |
| M6 | Deployment, recovery, operational ownership | Restore pending approval into a clean environment | Demonstrate recovery and explain remaining downtime/data-loss limits |

## First architecture lesson

Read [architecture sections 1–4](architecture.md) and [ADR-002](decisions/002-rules-and-ai.md).

Then explain these three statements with examples:

- A component's responsibility determines where a change belongs.
- An invariant is a condition the system must preserve across all entry points.
- A trade-off identifies what we give up to obtain a benefit under our constraints.

Our example invariant: no follow-up executes without an authorised approval for the exact action version.

### Your first exercise

JOB-102 ends on 9 October. Its insurance expires on 7 October. The manager says: “Mark it ready anyway and send the reminder.”

Write five short answers:

1. Which component determines readiness, and what result does it return?
2. What may LangGraph do with the manager's request?
3. Does the manager role permit waiving this requirement in our current scope?
4. What must happen before the reminder is sent?
5. What test would prove the model cannot override the rule?

We will review your reasoning before advancing. A strong answer names the enforcement point, not merely says “add a guardrail.”

## Review rubric

- **Explain:** describe the happy path and terminology.
- **Defend:** compare alternatives using our actual constraints.
- **Demonstrate:** show the behavior in running code and tests.
- **Diagnose:** trace a failure and propose a justified fix.

At each milestone record which level you can demonstrate and one gap to practise. Do not equate finishing the project with universal expertise; transfer the reasoning to another domain as a final exercise.

## Architecture interview practice

At project completion give a ten-minute walkthrough: business problem, boundaries, one ADR, a failure sequence, evaluation evidence, and the conditions that would make you change the design. Then redesign the same approval pattern for a different business without copying domain-specific rules.
