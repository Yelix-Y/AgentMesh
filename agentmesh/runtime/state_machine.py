from enum import Enum
from datetime import datetime, timezone

from agentmesh.db.database import get_connection


class AgentState(str, Enum):
    IDLE = "IDLE"
    READING = "READING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REPORTING = "REPORTING"
    WAITING = "WAITING"
    ESCALATING = "ESCALATING"


VALID_TRANSITIONS: dict[AgentState, set[AgentState]] = {
    AgentState.IDLE:       {AgentState.READING, AgentState.ESCALATING},
    AgentState.READING:    {AgentState.PLANNING, AgentState.ESCALATING},
    AgentState.PLANNING:   {AgentState.EXECUTING, AgentState.ESCALATING},
    AgentState.EXECUTING:  {AgentState.REPORTING, AgentState.ESCALATING},
    AgentState.REPORTING:  {AgentState.WAITING, AgentState.IDLE, AgentState.ESCALATING},
    AgentState.WAITING:    {AgentState.READING, AgentState.IDLE, AgentState.ESCALATING},
    AgentState.ESCALATING: {AgentState.IDLE},
}


class AgentStateMachine:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._ensure_state()

    def _ensure_state(self) -> None:
        with get_connection() as conn:
            existing = conn.execute(
                "SELECT state FROM agent_states WHERE agent_id = ?", (self.agent_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO agent_states (agent_id, state, updated_at) VALUES (?, ?, ?)",
                    (self.agent_id, AgentState.IDLE.value, datetime.now(timezone.utc).isoformat()),
                )

    @property
    def state(self) -> AgentState:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT state FROM agent_states WHERE agent_id = ?", (self.agent_id,)
            ).fetchone()
        return AgentState(row["state"])

    def transition(self, new_state: AgentState) -> None:
        current = self.state
        if new_state not in VALID_TRANSITIONS.get(current, set()):
            raise ValueError(
                f"Invalid transition for agent '{self.agent_id}': {current} → {new_state}. "
                f"Valid transitions from {current}: {[s.value for s in VALID_TRANSITIONS[current]]}"
            )
        with get_connection() as conn:
            conn.execute(
                "UPDATE agent_states SET state = ?, updated_at = ? WHERE agent_id = ?",
                (new_state.value, datetime.now(timezone.utc).isoformat(), self.agent_id),
            )

    def escalate(self) -> None:
        with get_connection() as conn:
            conn.execute(
                "UPDATE agent_states SET state = ?, updated_at = ? WHERE agent_id = ?",
                (AgentState.ESCALATING.value, datetime.now(timezone.utc).isoformat(), self.agent_id),
            )
