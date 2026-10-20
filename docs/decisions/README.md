# Decisions: short version

Current architecture principles:

1. Keep readiness decisions deterministic; AI assists investigation and explanation.
2. Use synthetic records and a local email capture inbox until approved data and environments are available.
3. Require server-checked approval of the exact draft before dispatch.
4. Keep delivery status separate from readiness status.
5. Complete production controls before shared or client-data deployment.

The detailed ADRs 001–004 in this directory record design context and consequences. Production-level verification requirements remain open; in particular, durable restart recovery and operator reconciliation are not yet complete.

The earlier baseline is preserved in [the archive](../archive/advanced-baseline/docs/decisions/README.md). Add or update an ADR when an implementation choice changes materially.
