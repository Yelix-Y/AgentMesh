# AgentMesh — Product Requirements Document (PRD)

## 1. Background

Single-agent applications tend to hit three walls:

- As context grows, the agent loses coherence and stable state.
- A lone agent has no second opinion: mistakes, blind spots, and overconfidence go unchecked.
- "Bigger model" is the only obvious lever, which is expensive and has diminishing returns.

AgentMesh takes a different bet: a small **organization** of specialized coworkers that communicate in natural language. Quality comes from **coordination** — handoffs, reviews, clarifications, and escalation — rather than from a single large model.

## 2. Product Goals

- Build a runnable simulator of digital coworkers that collaborate through natural-language messages.
- Give each agent an isolated memory and a distinct personality / specialization.
- Make every interaction a typed, persisted, observable ACP message.
- Provide a CLI to drive and watch the organization locally.
- Keep backends swappable (mock vs. Anthropic LLM) so the system runs with or without API access.

## 3. User Stories

### Coordinated delivery
As an operator, I hand a task to **Alex** (developer). Alex plans, implements, and hands off a natural-language completion report to **Jordan** (tester), who probes edge cases and reports findings to **Morgan** (reviewer), who issues a review decision back to Alex.

### Clarification and escalation
As an operator, when an agent is blocked or the request is ambiguous, I want it to send a `CLARIFICATION_REQUEST` or `ESCALATION` message back to me instead of guessing.

### Memory continuity, without leakage
As an operator, I want each agent to remember its own prior context across tasks, while being **unable** to read another agent's memory — knowledge should spread only by messaging.

### Observability
As an operator, I want to watch the live stream of messages between agents to understand how a decision was reached.

## 4. MVP Scope

| Capability | In MVP | Notes |
|---|---|---|
| Agent profiles (YAML) | Yes | personality, working_style, specialization, llm_backend, worker |
| Message bus (ACP) | Yes | SQLite-backed publish / poll / consume / get_thread |
| Typed message intents | Yes | TASK_HANDOFF, COMPLETION_REPORT, REVIEW_DECISION, etc. |
| Isolated memory store | Yes | short/long term; cross-agent reads rejected |
| Agent state machine | Yes | IDLE → READING → PLANNING → EXECUTING → REPORTING → WAITING (+ ESCALATING) |
| CLI | Yes | Typer + Rich: agent load / status / message, watch |
| LLM provider (Anthropic) | Planned | abstracted; mock backend works today |
| Web API / Web UI | No | future |
| Kubernetes / distributed | No | future |

## 5. Non-functional Requirements

- **Isolation**: an agent must never read another agent's memory.
- **Testability**: bus, memory store, and state machine must be unit-testable in isolation.
- **Observability**: every message and state change is persisted.
- **Robustness**: an invalid state transition must raise a clear error, not corrupt state.
- **Portability**: runs locally on Python with SQLite, no external services required for the MVP.

## 6. Acceptance Criteria

- Load and validate at least three agent profiles (developer, tester, reviewer).
- Publish a message and have only the intended recipient poll it.
- Retrieve a full conversation thread in chronological order.
- Reading another agent's memory raises `PermissionError`.
- An illegal state transition raises `ValueError`.
- The CLI can inject a human message and stream the live feed.
- A unit-test suite covers the bus, memory, and state machine.
