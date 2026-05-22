# AgentMesh

> **AI Organization Simulator** — digital coworkers that collaborate through natural language.

AgentMesh is NOT a traditional multi-agent orchestration framework.

It is a system of **human-like digital coworkers**. Each agent has personality, memory, specialization, and autonomy. Agents don't call each other as tools — they communicate like colleagues inside a company.

## Core Thesis

> **Better coordination = smarter outcomes**, independent of model size.

Instead of `bigger model = smarter`, we explore whether a small organization of specialized agents can outperform a single super-agent.

## MVP: 3 Digital Coworkers

| Agent | Persona | Responsibility |
|---|---|---|
| **Alex** (Developer) | Pragmatic, detail-oriented | Implement, plan, hand off |
| **Jordan** (Tester) | Skeptical, meticulous | Test, surface edge cases |
| **Morgan** (Reviewer) | Senior, high-standards | Synthesize, decide, enforce quality |

Agents communicate **only through natural language messages**. Knowledge travels through communication, not shared memory.

## How It Works

```
Human → TASK_HANDOFF → Developer
                           ↓ COMPLETION_REPORT (natural language)
                        Tester
                           ↓ COMPLETION_REPORT (findings)
                        Reviewer
                           ↓ REVIEW_DECISION → Developer
```

## Quick Start

```bash
# Install
uv sync --group dev

# Load and validate an agent profile
uv run agentmesh agent load agents/developer.yaml

# Check agent status
uv run agentmesh agent status developer

# Watch the live message stream
uv run agentmesh watch

# Inject a message to an agent
uv run agentmesh agent message developer "Please implement an OAuth refresh token flow."
```

## Architecture

| Module | Description |
|---|---|
| `agentmesh/models/` | Agent profile schema, ACP message types |
| `agentmesh/db/` | SQLite setup, shared schema |
| `agentmesh/bus/` | Message bus — all inter-agent communication |
| `agentmesh/memory/` | Isolated per-agent memory store |
| `agentmesh/runtime/` | Agent state machine |
| `agentmesh/cli.py` | Typer CLI entry point |
| `agents/` | YAML profiles for Developer, Tester, Reviewer |

## Agent State Machine

```
IDLE → READING → PLANNING → EXECUTING → REPORTING → WAITING → (IDLE or READING)
Any state → ESCALATING → IDLE
```

## Development Status

| Slice | Status |
|---|---|
| S1: Project Skeleton + Agent Profile Loader | ✅ Done |
| S2: SQLite Message Bus | ✅ Done |
| S3: Isolated Memory Store | ✅ Done |
| S4: Agent State Machine | ✅ Done |
| S5: CLI Worker Adapter | 🔜 Next |
| S6: ACP + Message Types | 🔜 Next |
| S7: LLM Provider (Anthropic) | 🔜 Next |
| S8: Session & Event Log | 🔜 Next |
| S9: Agent Supervisor | 🔜 Next |
| S10–S12: Developer / Tester / Reviewer Agents | 🔜 Next |
| S13: Human Operator CLI | 🔜 Next |
| S14: 3-Agent MVP Integration | 🔜 Next |

## Running Tests

```bash
uv run pytest tests/ -v
```

22 tests, all passing.

## PRD & Issues

Full product spec and GitHub issues: [#12 PRD](https://github.com/Yelix-Y/AgentMesh/issues/12)
