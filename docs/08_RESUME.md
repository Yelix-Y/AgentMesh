# Résumé Description — AgentMesh (AI Organization Simulator)

## Project Name

AgentMesh — AI Organization Simulator (multi-agent collaboration via natural-language communication)

## Tech Stack

Python · Pydantic · Typer · Rich · SQLite · asyncio · Anthropic LLM

## Résumé Summary

Designed and built **AgentMesh**, an AI Organization Simulator in which specialized digital coworkers (Developer, Tester, Reviewer) collaborate **purely through typed natural-language messages** rather than tool/function calls. Architected a SQLite-backed Agent Communication Protocol (ACP) message bus, isolated per-agent memory with enforced cross-agent read protection, and a validated agent state machine. Built a Typer/Rich CLI to load agents, inject operator messages, and stream the live inter-agent feed. The system tests the thesis that **better coordination — not a bigger model — yields smarter outcomes.**

## Core Features & Implementation

1. **Natural-language agent communication (ACP)**
   Designed a typed message protocol (`TASK_HANDOFF`, `COMPLETION_REPORT`, `REVIEW_DECISION`, `CLARIFICATION_REQUEST`, `ESCALATION`, …) carried over a SQLite message bus with `publish` / `poll` / `consume` / `get_thread`. Agents coordinate as colleagues — no agent calls another agent's code.

2. **Isolated per-agent memory**
   Built a memory store with short- and long-term entries scoped to each agent. Cross-agent reads raise `PermissionError`, guaranteeing that knowledge spreads only through explicit messages — eliminating context pollution by construction.

3. **Agent state machine**
   Implemented a persisted lifecycle (`IDLE → READING → PLANNING → EXECUTING → REPORTING → WAITING`, plus `ESCALATING`) with a validated transition table that rejects illegal transitions, making agent behavior predictable and auditable.

4. **Personality-driven agent profiles**
   Modeled agents (Alex/Developer, Jordan/Tester, Morgan/Reviewer) via YAML profiles capturing personality, working style, and specialization in natural language, plus swappable LLM and worker backends (`anthropic` / `mock`).

5. **Observable, replayable collaboration**
   Persisted every message and state change; built `agentmesh watch` to stream the live, color-coded message feed and an event log enabling full session replay.

6. **Developer-friendly CLI**
   Delivered a Typer + Rich CLI (`agent load`, `agent status`, `agent message`, `watch`) for loading/validating profiles, inspecting agent state and inboxes, injecting human messages, and observing the organization in real time.

## Quantifiable Highlights

- 3 specialized agent roles collaborating through messages, not function calls.
- 9 typed ACP message intents over a single message-bus abstraction.
- Memory isolation enforced in code (cross-agent reads → `PermissionError`).
- 7-state agent lifecycle with a validated transition table.
- Unit-test suite covering the message bus, memory store, and state machine.
- Runs fully offline with a mock backend; swaps to Anthropic via config.

## Interview Talking Points

- **Why communication instead of tool-calling:** modeling a real team forces explicit, auditable handoffs and lets coordination — not scale — drive quality.
- **Why memory isolation:** prevents context pollution and makes knowledge transfer observable; it is the architectural backbone of the "agents as colleagues" idea.
- **Why a state machine:** turns fuzzy agent behavior into a predictable, debuggable, replayable lifecycle.
- **The central thesis:** holding the model fixed, does adding coordination (handoff → test → review) measurably improve outcomes? AgentMesh is the testbed.
