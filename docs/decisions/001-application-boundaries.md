# ADR-001: modular application with server-owned business authority

Status: Accepted as design direction; not implemented.
Date: 2026-09-29.

## Context

One developer is building a small operations demo. Both the browser and AI workflows need the same permissions and business rules. Multiple independently deployed business services would increase setup and failure paths.

## Decision

Use one modular Python application for API, business services, and LangGraph orchestration. Keep readiness rules independent of frameworks. n8n runs deterministic integration sequences through authenticated application APIs. Application services own business records and approvals.

## Alternatives

- Microservices: allow independent deployment and scaling, but require more network contracts, distributed diagnostics, and operations than this scope justifies.
- Put business rules in n8n nodes: quick for a small workflow, but duplicates authority when UI/API operations need the same rules.
- Implement every workflow in Python: reduces runtime components, but drops the selected n8n integration demonstration. It remains reasonable if workflow overhead later outweighs its value.

## Consequences

One place enforces business authority and can be tested without a model. Module boundaries require discipline because code shares a process. n8n still introduces a network and recovery boundary; a modular monolith does not remove external failures.

## Verification

Direct API and graph-tool paths invoke the same services. Negative tests reject forbidden changes regardless of entry point. n8n has no business database write credentials.

## Revisit when

Measurements show a component needs independent scaling or a separate team owns its deployment. Do not split merely because the repository grows.
