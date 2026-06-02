# AgentMesh Structure, Explained Simply

AgentMesh is like a tiny company made of AI workers.

A human gives one job. The workers talk to each other with messages until the job is finished.

## The Tiny Company

There are three main workers:

| Worker | Job |
|---|---|
| Alex / Developer | Builds the thing |
| Jordan / Tester | Checks if it works |
| Morgan / Reviewer | Decides if it is good enough |

They do not secretly share brains.

They only know what someone sends them in a message.

## The Message Path

The job moves like this:

```text
Human
  -> Developer
  -> Tester
  -> Reviewer
  -> Developer
  -> Human
```

Example:

```text
Human: Please build a login API.
Developer: I built it. Tester, please check it.
Tester: I tested it. Reviewer, please review it.
Reviewer: Approved.
Developer: Human, the job is done.
```

## The Main Folders

| Folder | Simple meaning |
|---|---|
| `agents\` | The worker cards. Each YAML file describes one worker. |
| `agentmesh\models\` | The shapes of things, like messages and worker profiles. |
| `agentmesh\bus\` | The mailbox. Workers send and receive messages here. |
| `agentmesh\memory\` | Each worker's private notebook. |
| `agentmesh\db\` | The SQLite database setup. |
| `agentmesh\runtime\` | The engine that makes workers move, think, and reply. |
| `agentmesh\cli.py` | The command-line buttons humans use. |
| `tests\` | Checks that prove the system still works. |
| `docs\` | Product notes, roadmap, and design ideas. |

## The Important Runtime Pieces

| File | What it does |
|---|---|
| `runtime\agent.py` | Runs one worker for one message. |
| `runtime\supervisor.py` | Watches all workers and keeps the company moving. |
| `runtime\events.py` | Writes down what happened, like a history book. |
| `runtime\llm.py` | Gives workers a brain: mock brain or Anthropic brain. |
| `runtime\state_machine.py` | Makes sure a worker moves in the right order. |

## Worker States

A worker moves through states like a simple checklist:

```text
IDLE
  -> READING
  -> PLANNING
  -> EXECUTING
  -> REPORTING
  -> IDLE
```

Simple meaning:

| State | Meaning |
|---|---|
| `IDLE` | Waiting |
| `READING` | Reading a message |
| `PLANNING` | Thinking what to do |
| `EXECUTING` | Doing the work |
| `REPORTING` | Sending the answer |

## Why This Project Is Special

Many AI systems use one big AI.

AgentMesh tries another idea:

> A small team that talks clearly may do better than one lonely AI.

The most important rules are:

1. Workers talk by messages.
2. Each worker has private memory.
3. Every message is saved.
4. The human can watch what happened.
5. The system can run locally with a mock brain.

## How To Show The MVP

Run:

```bash
uv run agentmesh run "Build a login API." --agents-dir agents --provider mock
```

You should see:

```text
human -> developer
developer -> tester
tester -> reviewer
reviewer -> developer
developer -> human
```

That is the MVP: a tiny AI company finishing one job by talking.
