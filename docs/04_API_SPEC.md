# AgentMesh — API & Schema Specification

AgentMesh ships as a Python package plus a Typer CLI. This document specifies the CLI surface, the Python engine API, and the core Pydantic schemas. A FastAPI layer can wrap these later without changing the model.

## 1. CLI API

The CLI is `agentmesh` (Typer + Rich). It initializes the SQLite database on every invocation.

### Load and validate an agent profile
```bash
agentmesh agent load agents/developer.yaml
```
Prints a table of the parsed `AgentProfile`. Exits non-zero on a missing file or validation error.

### Show an agent's status
```bash
agentmesh agent status developer
```
Shows the agent's current state and unread-inbox summary (count, latest sender, latest message type).

### Inject a message from the human operator
```bash
agentmesh agent message developer "Please implement an OAuth refresh token flow."
```
Publishes a `HUMAN_INTERVENTION` message from `human` to the named agent.

### Watch the live message stream
```bash
agentmesh watch --interval 1.0
```
Streams every message between agents, color-coded by `MessageType`, until interrupted.

## 2. Python Engine API

### Message bus
```python
from agentmesh.bus.message_bus import MessageBus
from agentmesh.models.message import ACPMessage, MessageType

bus = MessageBus()

bus.publish(ACPMessage(
    sender_id="alex",
    recipient_id="jordan",
    message_type=MessageType.COMPLETION_REPORT,
    body="Implemented the refresh flow. Watch the clock-skew edge case.",
))

inbox = bus.poll("jordan")          # unread messages, oldest first
bus.consume(inbox[0].id)            # mark as read
thread = bus.get_thread(inbox[0].thread_id)  # full conversation
```

### Memory store (isolated per agent)
```python
from agentmesh.memory.store import MemoryStore

mem = MemoryStore()
mem.write("alex", "short", "Currently working on OAuth refresh.")
mem.write("alex", "long", "Project uses single-use refresh tokens.")

mine = mem.read("alex", "long", requesting_agent_id="alex")   # OK
mem.read("alex", "long", requesting_agent_id="jordan")        # raises PermissionError
mem.clear_short_term("alex")
```

### Agent state machine
```python
from agentmesh.runtime.state_machine import AgentStateMachine, AgentState

sm = AgentStateMachine("alex")
sm.transition(AgentState.READING)
sm.transition(AgentState.PLANNING)
sm.transition(AgentState.EXECUTING)
sm.escalate()                       # → ESCALATING from any state
```

### Profile loading
```python
from agentmesh.models.loader import load_profile, load_profiles_from_dir

profile = load_profile("agents/developer.yaml")
profiles = load_profiles_from_dir("agents/")
```

## 3. Core Schemas

### AgentProfile
```python
class LLMBackendConfig(BaseModel):
    provider: Literal["anthropic", "mock"] = "mock"
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.7
    max_tokens: int = 4096

class WorkerConfig(BaseModel):
    type: Literal["mock", "bash"] = "mock"
    timeout_seconds: int = 60

class AgentProfile(BaseModel):
    name: str
    role: Literal["developer", "tester", "reviewer"]
    personality: str       # natural-language persona
    working_style: str     # how the agent approaches work
    specialization: str    # what the agent is expert in
    llm_backend: LLMBackendConfig
    worker: WorkerConfig
```

### ACPMessage
```python
class MessageType(str, Enum):
    TASK_HANDOFF = "TASK_HANDOFF"
    CLARIFICATION_REQUEST = "CLARIFICATION_REQUEST"
    STATUS_UPDATE = "STATUS_UPDATE"
    COMPLETION_REPORT = "COMPLETION_REPORT"
    REJECTION = "REJECTION"
    ESCALATION = "ESCALATION"
    REVIEW_REQUEST = "REVIEW_REQUEST"
    REVIEW_DECISION = "REVIEW_DECISION"
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"

class ACPMessage(BaseModel):
    id: str                # uuid
    thread_id: str         # uuid; groups a conversation
    sender_id: str
    recipient_id: str
    message_type: MessageType
    body: str              # natural-language content
    metadata: dict[str, Any]
    created_at: datetime
    read: bool
```

## 4. Future REST Mapping

| CLI / Engine capability | Future REST endpoint |
|---|---|
| `agent load` | `POST /agents` |
| `agent status` | `GET /agents/{name}` |
| `agent message` | `POST /agents/{name}/messages` |
| `bus.get_thread` | `GET /threads/{thread_id}` |
| `watch` | `GET /messages/stream` (SSE/WebSocket) |
