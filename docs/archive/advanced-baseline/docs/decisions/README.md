# Architecture decision records

ADRs explain why we chose an approach under particular constraints. They record trade-offs, not only the chosen technology.

The accepted records below capture the direction already selected in this conversation. Accepted means a design decision is agreed; it does not mean implemented or verified. Open implementation choices remain in [architecture.md](../architecture.md).

| ADR | Decision | Status |
| --- | --- | --- |
| [001](001-application-boundaries.md) | Modular application with server-owned business authority | Accepted |
| [002](002-rules-and-ai.md) | Deterministic readiness; AI for interpretation and explanation | Accepted |
| [003](003-approval-and-recovery.md) | Durable approvals tied to action versions; explicit recovery | Accepted |
| [004](004-synthetic-integration.md) | Synthetic business API and test inbox for first release | Accepted |

For a new record use: title, status, context, decision, alternatives, consequences, verification, and revisit trigger. Date the record. Use Proposed while an important choice is unresolved. Preserve old decisions when superseding them and link the replacement.
