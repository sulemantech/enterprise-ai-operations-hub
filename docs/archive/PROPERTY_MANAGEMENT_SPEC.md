# Enterprise AI Operations Hub

## Delivery roadmap

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the repository assessment, daily tasks, six milestones, and production readiness gates. It proposes 30 working days at 3–5 hours per day, expanding the original 10-day demo schedule below. The application has not been implemented yet.

## Project Type

Portfolio-grade AI Enterprise Architecture demonstration.

## Primary Objective

Build a realistic, production-oriented reference implementation showing how an AI capability can be integrated into an existing business environment as a reliable enterprise system.

The project should demonstrate:

> **AI is not just a chatbot. It is a system that combines reasoning, knowledge, tools, workflows, business systems, governance, human approval, and observability.**

The final demo should allow an international client to understand how I approach:

* AI Solution Architecture
* AI Enterprise Architecture
* Agentic AI
* LangGraph
* RAG
* n8n
* API integrations
* business workflow automation
* human-in-the-loop
* AI guardrails
* observability
* evaluation
* enterprise integration

The project should be technically credible but intentionally small enough to build and deploy as a solo portfolio project.

---

# 1. Business Scenario

Build a fictional **Property Management Operations Platform**.

A property-management company receives requests from tenants/customers.

Examples:

* "The AC in apartment 402 isn't working."
* "There is water leaking from my ceiling."
* "What are your office hours?"
* "Can someone come tomorrow?"
* "What's the status of my maintenance request?"
* "I'd like to book an appointment."
* "Can you waive my maintenance fee?"
* "This is an emergency."
* "I want to speak to a human."

The AI system should understand the request, retrieve relevant information, determine whether a business action is required, and execute the appropriate workflow.

The property-management domain is only a demonstration domain.

The architecture should be reusable for:

* healthcare
* hospitality
* education
* automotive
* telecom
* real estate
* professional services
* customer support

---

# 2. Core Architectural Principle

The system must clearly separate:

### Agentic reasoning

Handled primarily by **LangGraph**.

Responsibilities:

* understand request
* classify intent
* manage state
* retrieve knowledge
* select tools
* determine whether approval is needed
* reason over available information
* produce a response

### Deterministic business workflows

Handled primarily by **n8n**.

Responsibilities:

* CRM updates
* calendar operations
* notifications
* follow-up workflows
* scheduled processes
* API orchestration
* deterministic business logic

### Enterprise systems

Examples:

* CRM
* calendar
* notification service
* maintenance/work-order system
* database

### Governance

Responsible for:

* authorization
* validation
* human approval
* audit trail
* high-risk actions
* tool restrictions

The key architectural message is:

> **The LLM should not become the business workflow engine.**

---

# 3. Target Architecture

Initial architecture:

```text
                    CUSTOMER
                       │
             ┌─────────┼─────────┐
             │         │         │
           Web       Voice     WhatsApp
             │         │         │
             └─────────┼─────────┘
                       │
                       ▼
              AI Interaction Layer
                       │
                       ▼
                  LangGraph
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
       RAG           Tools        Guardrails
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                Business Workflow
                     n8n
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
         CRM        Calendar    Email/SMS
          │            │            │
          └────────────┼────────────┘
                       ▼
              Audit / Observability
```

Do not implement every channel initially.

Start with:

**Web → LangGraph → n8n → business system**

Voice can be added later as another channel.

---

# 4. Why LangGraph + n8n

This project should deliberately demonstrate the distinction between the two.

| Concern              | Technology                  |
| -------------------- | --------------------------- |
| Agent state          | LangGraph                   |
| Agent routing        | LangGraph                   |
| Reasoning            | LangGraph + LLM             |
| RAG                  | LangGraph + retrieval layer |
| Tool selection       | LangGraph                   |
| Human approval       | LangGraph/application       |
| Business workflow    | n8n                         |
| CRM integration      | n8n                         |
| Calendar integration | n8n                         |
| Notifications        | n8n                         |
| Scheduled follow-ups | n8n                         |
| Audit                | Application/database        |
| Evaluation           | Python/test framework       |

This separation is an architectural demonstration, not merely a technology choice.

---

# 5. User Interface

Build a simple web application.

The UI does not need to look like a commercial SaaS product.

It should prioritize demonstrating the architecture.

The main screen should contain:

### Conversation

User sends a request.

Example:

> "The AC in apartment 402 isn't working and I'd like someone to come tomorrow."

The AI responds.

### Execution information

Show:

* intent
* retrieved knowledge
* proposed action
* tool call
* approval status
* workflow status
* final result

For example:

```text
Intent
Maintenance Request

Customer
John Smith

Property
Building A / Apartment 402

Action
Create Maintenance Work Order

Approval
Required

Workflow
n8n → Maintenance Workflow

Result
Work Order WO-1042 created
```

---

# 6. LangGraph Agent

Use LangGraph with an explicit state model.

Possible state:

```python
class AgentState:
    messages
    user_id
    conversation_id
    intent
    retrieved_context
    tool_calls
    proposed_action
    approval_required
    approval_status
    execution_result
    final_response
```

The exact implementation should be decided during development.

Do not blindly copy this model.

The agent should have explicit stages.

Example:

```text
START
  ↓
Understand Request
  ↓
Classify Intent
  ↓
Need Knowledge?
  ├── Yes → Retrieve Knowledge
  └── No
  ↓
Need Business Action?
  ├── No → Generate Response
  └── Yes
        ↓
     Validate Request
        ↓
     Check Permission
        ↓
     Approval Required?
       ├── Yes → Human Approval
       └── No
        ↓
     Execute Tool
        ↓
     Verify Result
        ↓
     Generate Response
```

Avoid uncontrolled autonomous behavior.

---

# 7. Intent Categories

Initial intents:

```text
FAQ
MAINTENANCE_REQUEST
APPOINTMENT
REQUEST_STATUS
BILLING
EMERGENCY
ESCALATION
UNKNOWN
```

The exact categories can evolve during development.

The system should support ambiguous requests.

Example:

> "Something is wrong with my apartment."

The system should ask for clarification rather than inventing an action.

---

# 8. RAG System

Create a small fictional knowledge base.

Documents:

* maintenance policy
* emergency procedures
* office hours
* appointment policy
* tenant responsibilities
* maintenance SLA
* billing policy
* property information
* escalation policy

Implement:

```text
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Store
   ↓
Retrieval
   ↓
Relevant Context
   ↓
LLM Response
```

Use PostgreSQL + pgvector unless there is a strong reason to choose something else.

The system should clearly distinguish:

### Knowledge question

> "What is the maintenance response time?"

→ RAG

### Business action

> "My AC is broken. Send someone tomorrow."

→ Tool/workflow

### Sensitive action

> "Waive my $500 charge."

→ Human approval

---

# 9. Tools

Create explicit tools.

Initial tools:

```text
get_customer()
get_property()
get_maintenance_request()
create_maintenance_request()
get_available_slots()
schedule_appointment()
send_notification()
escalate_to_human()
```

Tools should have:

* typed inputs
* validation
* clear outputs
* error handling
* authorization checks

Do not allow the LLM to directly manipulate the database.

Instead:

```text
Agent
  ↓
Tool
  ↓
Application logic
  ↓
Database/API
```

---

# 10. n8n Workflows

## Workflow A — Maintenance

```text
Webhook
 ↓
Validate payload
 ↓
Create/update CRM record
 ↓
Create maintenance request
 ↓
Determine notification
 ↓
Send notification
 ↓
Return result
```

## Workflow B — Appointment

```text
Webhook
 ↓
Validate request
 ↓
Check calendar
 ↓
Create appointment
 ↓
Update CRM
 ↓
Send confirmation
 ↓
Return result
```

## Workflow C — Follow-up

```text
Scheduled trigger
 ↓
Find open requests
 ↓
Check status
 ↓
Identify requests requiring follow-up
 ↓
Send notification
 ↓
Update CRM
```

The workflows should be deterministic.

The LLM should not decide the sequence of CRM → calendar → SMS operations.

---

# 11. Human-in-the-Loop

Demonstrate at least one sensitive workflow.

Example:

> "Please waive my $500 maintenance charge."

The system should:

```text
Request
 ↓
Intent
 ↓
Sensitive Action
 ↓
Approval Required
 ↓
Human Review
 ↓
Approve / Reject
 ↓
Business Workflow
```

The approval decision must be recorded.

The agent should never bypass the approval requirement simply because the user asks again.

---

# 12. Guardrails

Implement basic enterprise controls.

### Input validation

Required information must exist before a tool is executed.

### Authorization

Users should only be allowed to perform actions they are authorized to perform.

### Tool validation

Validate every tool argument.

### High-risk actions

Require human approval.

### RAG grounding

Policy answers should be grounded in retrieved information.

### Action verification

The agent must not claim that something happened unless the underlying operation succeeded.

Bad:

> "Your appointment has been booked."

when the calendar API failed.

Correct:

> "I couldn't complete the booking because the calendar service returned an error."

---

# 13. Audit Trail

Every meaningful action should generate an event.

Example:

```json
{
  "conversation_id": "conv_123",
  "user_id": "user_42",
  "intent": "maintenance_request",
  "action": "create_work_order",
  "approval_required": true,
  "approval_status": "approved",
  "tool": "create_maintenance_request",
  "result": "success",
  "timestamp": "..."
}
```

Create a simple operations timeline:

```text
09:31 Request received

09:31 Intent:
     Maintenance Request

09:31 Knowledge retrieved

09:32 Work order proposed

09:32 Approval requested

09:34 Approved

09:34 Work order created

09:34 Confirmation sent
```

---

# 14. Observability

Capture:

* conversation ID
* user ID
* agent state
* node transitions
* tool calls
* tool results
* workflow execution ID
* latency
* errors
* approval events
* final outcome

Where practical:

* model
* token usage
* estimated cost
* retrieved documents
* evaluation result

The purpose is to show that the system can be operated and diagnosed after deployment.

---

# 15. Evaluation

Create a small evaluation suite.

### Normal

* office hours
* maintenance request
* appointment
* request status

### Ambiguous

* "I have a problem."
* "Can someone come tomorrow?"
* "It's urgent."

### Sensitive

* fee waiver
* cancellation
* escalation

### Off-topic

* unrelated questions

### Adversarial

* prompt injection attempts
* attempts to bypass approval
* invalid tool parameters

Measure:

* intent accuracy
* retrieval quality
* tool selection
* correct escalation
* authorization behavior
* groundedness
* successful workflow completion
* failure handling

---

# 16. Technology Stack

Initial stack:

### Backend

* Python
* FastAPI
* LangGraph
* Pydantic

### AI

Configurable LLM provider.

Do not hard-code the entire application around one model.

### Database

PostgreSQL

### Vector search

pgvector

### Workflow

n8n

### Frontend

React / Next.js

### Deployment

Docker Compose locally.

Use simple deployment infrastructure initially.

Avoid unnecessary cloud architecture.

---

# 17. Repository Structure

Start approximately with:

```text
enterprise-ai-operations-hub/

├── apps/
│   ├── api/
│   └── web/
│
├── agent/
│   ├── graph/
│   ├── state/
│   ├── nodes/
│   ├── tools/
│   ├── guardrails/
│   └── prompts/
│
├── rag/
│   ├── ingestion/
│   ├── retrieval/
│   └── documents/
│
├── integrations/
│   ├── crm/
│   ├── calendar/
│   └── notifications/
│
├── workflows/
│   └── n8n/
│
├── database/
│
├── evaluations/
│
├── docs/
│   ├── architecture.md
│   ├── workflows.md
│   ├── security.md
│   └── decisions/
│
├── docker-compose.yml
├── .env.example
├── README.md
└── PROJECT_PLAN.md
```

Do not create unnecessary directories just for appearance.

---

# 18. Architecture Decision Records

Document important decisions.

Examples:

```text
ADR-001
Why LangGraph is used for agent orchestration

ADR-002
Why n8n handles deterministic workflows

ADR-003
Why the LLM cannot directly access the database

ADR-004
Why sensitive actions require human approval

ADR-005
Why RAG and business actions are separated

ADR-006
Why model providers are abstracted
```

Each ADR should explain:

```text
Context
Decision
Alternatives
Trade-offs
Consequences
```

---

# 19. 10-Day Development Plan

The target is **10 focused working days**.

Assume approximately **3–5 focused hours per day**.

The goal is not merely to write code.

Every day should produce:

1. working software
2. tests
3. architectural understanding
4. documentation
5. a demonstrable outcome

---

## DAY 1 — Architecture & Foundation

### Objective

Create the project foundation and validate the architecture before implementing business logic.

### Tasks

* initialize repository
* establish Python project
* establish frontend
* establish FastAPI
* establish PostgreSQL
* establish Docker Compose
* configure environment variables
* create initial architecture document
* create initial ADRs
* create PROJECT_PLAN.md

### Architectural discussion

Decide:

* monorepo vs separate repositories
* API boundaries
* database boundaries
* LangGraph location
* n8n integration boundary
* configuration strategy
* local development architecture

### Deliverable

Running:

```text
Frontend
   ↓
FastAPI
   ↓
Database
```

No agent yet.

---

# DAY 2 — First LangGraph Vertical Slice

### Objective

Get the smallest useful agent working.

Build:

```text
Browser
 ↓
FastAPI
 ↓
LangGraph
 ↓
LLM
 ↓
Response
```

### Tasks

* define initial state
* create graph
* create basic agent node
* connect LLM
* expose API endpoint
* connect frontend
* add basic tests

### Deliverable

User enters a message and receives an AI response through LangGraph.

Do not add RAG, tools, n8n, or complex routing yet.

---

# DAY 3 — State & Controlled Routing

### Objective

Move from a generic chatbot to a controlled agent workflow.

Implement:

```text
Request
 ↓
Intent
 ↓
Route
```

Add initial intents.

Add:

* explicit state
* routing
* clarification path
* unknown intent
* basic conversation state

### Deliverable

The system can distinguish:

```text
FAQ
Maintenance
Appointment
Status
Emergency
Escalation
Unknown
```

and route accordingly.

---

# DAY 4 — RAG

### Objective

Give the agent reliable business knowledge.

Tasks:

* create sample documents
* ingestion pipeline
* chunking
* embeddings
* pgvector
* retrieval
* context injection
* citation/source metadata if appropriate
* grounded response tests

### Deliverable

Example:

> "How long does maintenance normally take?"

The answer comes from the property-management knowledge base rather than model memory.

---

# DAY 5 — Business Tools

### Objective

Give the agent the ability to perform controlled actions.

Implement first tools:

```text
get_customer
get_property
create_maintenance_request
get_maintenance_request
```

Use typed schemas.

Add validation.

Add error handling.

### Deliverable

Example:

```text
User
 ↓
"My AC is broken"
 ↓
Agent
 ↓
Maintenance tool
 ↓
Work order created
 ↓
Agent confirms actual result
```

---

# DAY 6 — n8n Integration

### Objective

Separate agent reasoning from deterministic business workflow.

Build:

```text
LangGraph
 ↓
Webhook
 ↓
n8n
 ↓
Business workflow
 ↓
Result
 ↓
LangGraph
 ↓
User
```

Implement maintenance workflow first.

### Deliverable

A real end-to-end:

```text
User
→ Agent
→ Tool
→ n8n
→ Business system
→ Result
→ User
```

This is the first major portfolio milestone.

---

# DAY 7 — Human Approval

### Objective

Introduce governance.

Create a sensitive action.

Example:

```text
Fee Waiver
```

Implement:

```text
Agent
 ↓
Sensitive Action
 ↓
Approval Required
 ↓
Human
 ↓
Approve / Reject
 ↓
n8n
```

Persist approval state.

Prevent bypassing approval.

### Deliverable

A working human-in-the-loop workflow.

---

# DAY 8 — Enterprise Integrations

### Objective

Add realistic business-system integrations.

Implement:

* CRM
* calendar
* email/SMS

Use mocked services first if external credentials are unavailable.

Build appointment workflow:

```text
User
 ↓
Agent
 ↓
Calendar
 ↓
CRM
 ↓
Notification
```

### Deliverable

Appointment scheduling workflow.

---

# DAY 9 — Observability & Evaluation

### Objective

Make the system measurable and diagnosable.

Implement:

* audit events
* execution timeline
* workflow IDs
* errors
* latency
* evaluation dataset
* automated tests

Add adversarial cases.

### Deliverable

A client can see not only:

> "The AI answered."

but also:

> "Here is what the AI decided, what it retrieved, which tool it used, what n8n executed, whether approval was required, and what actually happened."

---

# DAY 10 — Demo & Deployment

### Objective

Turn the engineering project into a portfolio demonstration.

Polish:

### User interface

* conversation
* action status
* workflow status

### Operations view

* intent
* retrieved context
* tools
* approval
* workflow
* result

### Architecture view

Show:

```text
Channels
 ↓
AI Layer
 ↓
LangGraph
 ↓
RAG / Tools / Guardrails
 ↓
n8n
 ↓
Enterprise Systems
 ↓
Observability
```

### Documentation

Complete:

* README
* architecture
* ADRs
* setup instructions
* demo scenarios
* evaluation results
* limitations

### Deployment

Deploy the demo.

---

# 20. Final Demonstration Scenario

The primary demo should be:

### User

> "The AC in apartment 402 isn't working and I'd like someone to come tomorrow."

### System

```text
Intent:
Maintenance Request

Customer:
John Smith

Property:
Apartment 402

Knowledge:
Maintenance SLA retrieved

Action:
Schedule maintenance

Calendar:
Available slot found

Approval:
Not required

Workflow:
n8n Maintenance Workflow

CRM:
Updated

Notification:
Sent

Result:
Work order created
```

Then demonstrate the sensitive case.

### User

> "Waive my $500 maintenance charge."

### System

```text
Intent:
Billing / Fee Adjustment

Risk:
Sensitive Action

Action:
Fee Waiver

Approval:
Required

Status:
Waiting for human approval
```

Then approve it.

The system executes the workflow and records the decision.

This pair of demonstrations tells the complete architectural story.

---

# 21. Optional Phase 2 — Voice

Do not make voice part of the initial 10-day critical path.

After the core system works, add:

```text
Voice
 ↓
Vapi / Retell
 ↓
Same Agent API
 ↓
Same LangGraph
 ↓
Same n8n workflows
```

This demonstrates an important architectural property:

> **The business logic is not coupled to the user interface.**

Voice is simply another channel.

This can become a separate portfolio extension.

---

# 22. Optional Phase 2 — WhatsApp

Similarly:

```text
WhatsApp
 ↓
Channel Adapter
 ↓
Same Agent Platform
```

No duplication of business logic.

---

# 23. Codex Operating Instructions

Codex should act as my **peer programmer and senior architecture partner**.

Do not behave as an autonomous developer who implements the entire specification without discussion.

### At the beginning of every milestone

First explain:

1. What we are building.
2. Why it matters.
3. The relevant architecture.
4. What decisions need to be made.
5. What the smallest useful implementation is.

Then wait for confirmation where a meaningful architectural decision is involved.

### During implementation

* implement incrementally
* keep changes small
* explain important code
* run tests
* inspect failures
* fix issues
* avoid speculative abstractions
* avoid unnecessary frameworks
* avoid premature optimization

### When there are multiple approaches

Explain:

```text
Option A
Advantages
Disadvantages

Option B
Advantages
Disadvantages

Recommendation based on project requirements
```

Do not silently choose an architecture with significant consequences.

### Challenge me

If I propose something overly complex:

Explain why.

If I am mixing responsibilities:

Point it out.

If an abstraction is premature:

Say so.

If a design creates future scaling/security problems:

Explain them.

The objective is not to agree with every decision.

The objective is to build a technically sound system together.

### Do not over-engineer

This is a portfolio demonstration.

Do not introduce:

* Kubernetes
* Kafka
* microservices
* service meshes
* complex event buses
* unnecessary cloud infrastructure

unless there is a concrete requirement.

A well-designed modular monolith is acceptable.

---

# 24. Definition of Success

The project succeeds when an international client can look at it and understand:

> "This person knows how to take AI and integrate it into a real business architecture."

The demo should demonstrate:

* agentic reasoning
* explicit state
* RAG
* controlled tools
* deterministic workflows
* n8n
* enterprise integrations
* human approval
* guardrails
* auditability
* evaluation
* observability
* architecture documentation

The number of technologies is secondary.

The central demonstration is:

> **AI capability → reliable enterprise system**

---

# 25. First Instruction to Codex

When starting the project, give Codex this instruction:

> Read `PROJECT_SPEC.md` completely.
>
> Do not start implementing the entire project.
>
> Act as my peer programmer and senior AI architecture partner.
>
> First analyze the specification and identify:
>
> 1. architectural risks
> 2. missing requirements
> 3. unnecessary complexity
> 4. decisions that should be made now
> 5. decisions that should be deferred
> 6. the smallest viable Phase 1 architecture
>
> Then propose Day 1 implementation tasks.
>
> Do not implement Day 2 or later.
>
> We will work milestone by milestone, testing each milestone before moving forward.
>
> Challenge my architectural decisions when appropriate rather than simply agreeing with them.

---

# 26. Final Portfolio Positioning

The project should ultimately be presented as:

**Enterprise AI Operations Hub**

### One-line description

> A reference architecture demonstrating how agentic AI, RAG, deterministic workflows, enterprise systems, and human governance can be combined into a production-oriented business automation platform.

### The architectural message

> **Don't put the whole business process inside the LLM. Put AI inside the business architecture.**

That should be the central idea behind the entire project.
