from dataclasses import dataclass

from agentmesh.models.agent import AgentProfile
from agentmesh.runtime.agent import Agent
from agentmesh.runtime.events import EventLog
from agentmesh.runtime.llm import LLMProvider


@dataclass
class SessionResult:
    steps: int
    messages_published: int
    quiescent: bool


class Supervisor:
    """Drives a team of agents: polls every inbox, advances each agent's state
    machine, and keeps going until the organization goes quiet (no agent has
    anything left to do) or a step budget is exhausted."""

    def __init__(
        self,
        profiles: list[AgentProfile],
        session_id: str = "default",
        llm: LLMProvider | None = None,
    ):
        self.session_id = session_id
        self.events = EventLog()
        self.agents = [
            Agent(p, llm=llm, session_id=session_id) for p in profiles
        ]

    def run(self, max_steps: int = 100) -> SessionResult:
        steps = 0
        published = 0
        self.events.record(self.session_id, "session_started", "supervisor")
        while steps < max_steps:
            steps += 1
            progressed = False
            for agent in self.agents:
                outgoing = agent.process_one()
                if outgoing is not None:
                    progressed = True
                    published += 1
            if not progressed:
                self.events.record(self.session_id, "session_quiescent", "supervisor")
                return SessionResult(steps=steps, messages_published=published, quiescent=True)
        return SessionResult(steps=steps, messages_published=published, quiescent=False)
