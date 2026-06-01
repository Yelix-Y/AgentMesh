# AgentMesh — Development Roadmap

The roadmap is organized as vertical slices (S1–S14). Each slice delivers a working, testable capability toward the 3-agent MVP.

## Status Overview

| Slice | Description | Status |
|---|---|---|
| S1 | Project skeleton + agent profile loader | ✅ Done |
| S2 | SQLite message bus | ✅ Done |
| S3 | Isolated memory store | ✅ Done |
| S4 | Agent state machine | ✅ Done |
| S5 | CLI worker adapter | 🔜 Next |
| S6 | ACP + message types (full set) | 🔜 Next |
| S7 | LLM provider (Anthropic) | 🔜 Next |
| S8 | Session & event log | 🔜 Next |
| S9 | Agent supervisor | 🔜 Next |
| S10–S12 | Developer / Tester / Reviewer agents | 🔜 Next |
| S13 | Human operator CLI | 🔜 Next |
| S14 | 3-agent MVP integration | 🔜 Next |

## Phase 1 — Foundations (Done)

**Goal:** establish the substrate agents communicate over.

- **S1 Skeleton + profile loader** — Python package, `AgentProfile` schema, YAML loader for `agents/*.yaml`.
- **S2 Message bus** — SQLite-backed `publish` / `poll` / `consume` / `get_thread`.
- **S3 Isolated memory** — per-agent short/long memory; cross-agent reads raise `PermissionError`.
- **S4 State machine** — `IDLE → READING → PLANNING → EXECUTING → REPORTING → WAITING` with `ESCALATING`, enforced transitions.

**Acceptance:** profiles load and validate; messages route only to their recipient; memory isolation holds; illegal transitions are rejected. Covered by the unit-test suite.

## Phase 2 — Bringing Agents to Life (Next)

**Goal:** turn profiles into autonomous coworkers that read their inbox, think, act, and reply.

- **S5 CLI worker adapter** — let an agent execute work (mock and bash worker types) and report results.
- **S6 ACP message types** — exercise the full intent set (handoff, clarification, status, completion, rejection, escalation, review request/decision).
- **S7 LLM provider (Anthropic)** — swap the `mock` backend for real reasoning via `llm_backend` config.

**Acceptance:** an agent can receive a `TASK_HANDOFF`, run through its state machine, and emit a `COMPLETION_REPORT`.

## Phase 3 — Orchestration & Observability (Next)

**Goal:** run the organization end-to-end and make it auditable.

- **S8 Session & event log** — record every message and state change into `events`.
- **S9 Agent supervisor** — a loop that polls inboxes, advances state machines, and keeps agents running.

**Acceptance:** a full session can be replayed from the event log.

## Phase 4 — The 3-Agent MVP (Next)

**Goal:** Alex → Jordan → Morgan deliver a task purely through natural-language messages.

- **S10–S12** — implement the Developer (Alex), Tester (Jordan), and Reviewer (Morgan) behaviors.
- **S13 Human operator CLI** — submit tasks, inject messages, and watch the stream.
- **S14 Integration** — the three agents collaborate to completion with no direct function calls between them.

**Acceptance:** a human hands off a task and observes a complete handoff → test → review → decision cycle on `agentmesh watch`.

## Future Directions (Optional)

- FastAPI service layer and a web visualization of the live message stream.
- Postgres / Redis for multi-process deployments.
- Semantic long-term memory via a vector store.
- Larger organizations (more roles) to test the "coordination beats scale" thesis.
