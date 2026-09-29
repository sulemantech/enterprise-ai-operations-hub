# Decisions: short version

Current learning approach:

1. Start with a Python function and fixture data so we can understand the rules.
2. Add one technology at a time after the previous step works.
3. Keep readiness decisions in ordinary code; AI helps ask and explain.
4. Use fictional records and a local email capture inbox.
5. Require server-checked approval for the exact draft before sending.
6. Add full production controls after the local flow is understood and before shared deployment.

The detailed ADRs 001–004 in this directory are optional design references. Their production-level verification requirements are deferred to Phase 2; they do not prescribe today's implementation order. In particular, durable restart recovery from ADR-003 is a later exercise, while the basic approval check remains part of the first local demo.

The earlier baseline is preserved in [the archive](../archive/advanced-baseline/docs/decisions/README.md). Add or update a detailed ADR when an actual implementation choice needs it. No ADR reading assignment is required to start coding.
