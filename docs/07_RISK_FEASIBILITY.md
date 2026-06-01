# AgentMesh — Risk, Feasibility & Innovation Analysis

## 1. Feasibility by Capability

| Capability | Description | Feasibility | Innovation | Value |
|---|---|---|---|---|
| Message bus (ACP) | Typed natural-language messages over SQLite | Easy | Coordination as messaging, not tool-calling | Core nervous system |
| Isolated memory | Per-agent memory, no cross-agent reads | Medium | Knowledge spreads only by communication | Prevents context pollution, models real teams |
| Agent state machine | Enforced lifecycle per agent | Easy | Explicit, auditable agent behavior | Predictable, debuggable runtime |
| Personality profiles | NL persona / working style / specialization | Easy | Agents as colleagues, not functions | Emergent, human-like collaboration |
| LLM provider abstraction | Mock today, Anthropic next | Medium | Runs offline or with real reasoning | Testable without API spend |
| Agent supervisor | Polling loop driving the org | Medium | Autonomous, message-driven progress | End-to-end MVP |
| Observability (watch + events) | Live stream + event log | Easy | Replayable decision trail | Trust and debuggability |

## 2. Key Risks

### 2.1 Unstable LLM output
**Risk:** an agent emits an unusable or off-protocol message.
**Mitigation:** typed `MessageType` constrains intent; the Reviewer (Morgan) acts as a quality gate; escalate on uncertainty instead of guessing.

### 2.2 Coordination breakdown (deadlock / ping-pong)
**Risk:** agents wait on each other forever, or bounce a task back and forth.
**Mitigation:** the state machine has explicit `WAITING` and `ESCALATING` states; unresolved loops escalate to the human via `ESCALATION`.

### 2.3 Memory pollution / leakage
**Risk:** one agent's context contaminates another's.
**Mitigation:** memory is physically isolated per `agent_id`; `MemoryStore.read` raises `PermissionError` on cross-agent access. Knowledge can only cross boundaries as an explicit message.

### 2.4 Worker execution risk
**Risk:** a `bash` worker runs something dangerous or hangs.
**Mitigation:** `worker.timeout_seconds`, a `mock` default, and (future) command constraints / process isolation.

### 2.5 Scope creep
**Risk:** pulling in FastAPI, Redis, Postgres, and Kubernetes too early dilutes the MVP.
**Mitigation:** CLI-first, SQLite-first, single-process. Service-ization is explicitly deferred.

## 3. Where the Innovation Lies

AgentMesh's novelty is not a single new technique — it is the **architectural stance**:

- **Communication, not invocation.** Agents coordinate exclusively through typed natural-language messages. There is no tool-call graph between agents.
- **Memory isolation as a first-class constraint.** Modeling real teams, knowledge must be *communicated* to spread, which forces explicit, auditable handoffs.
- **Coordination as the lever for intelligence.** The central hypothesis — *better coordination beats a bigger model* — is testable: vary the protocol and roles, hold the model fixed, measure outcome quality.
- **Observable by construction.** Because every capability is a message, the whole collaboration is streamable and replayable.

## 4. Suggested Metrics

Once the MVP runs end-to-end, track:

- Number of agent roles (target: 3 — developer, tester, reviewer).
- Number of ACP message types exercised (target: full set of 9).
- Task completion rate without human escalation.
- Average messages per completed task (coordination overhead).
- Memory-isolation violations (target: 0 — enforced by `PermissionError`).
- Fraction of sessions fully replayable from the event log (target: 100%).
- Outcome quality at fixed model size, with vs. without the review step (the core thesis test).
