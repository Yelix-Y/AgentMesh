from dataclasses import dataclass
from enum import Enum

from agentmesh.models.agent import AgentProfile
from agentmesh.runtime.agent import Agent
from agentmesh.runtime.events import EventLog, EventType
from agentmesh.runtime.llm import LLMProvider


class SessionStatus(str, Enum):
    QUIESCENT = "quiescent"
    MAX_STEPS = "max_steps"
    FAILED = "failed"


@dataclass
class SessionResult:
    steps: int
    messages_published: int
    messages_consumed: int
    messages_ignored: int
    status: SessionStatus

    @property
    def quiescent(self) -> bool:
        return self.status is SessionStatus.QUIESCENT


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
        consumed = 0
        ignored = 0
        self.events.record(self.session_id, EventType.SESSION_STARTED, "supervisor")
        try:
            while steps < max_steps:
                steps += 1
                progressed = False
                for agent in self.agents:
                    step = agent.process_next()
                    progressed = progressed or step.progressed
                    published += step.published
                    consumed += step.consumed
                    ignored += step.ignored
                if not progressed:
                    self.events.record(
                        self.session_id,
                        EventType.SESSION_QUIESCENT,
                        "supervisor",
                        {
                            "steps": steps,
                            "messages_published": published,
                            "messages_consumed": consumed,
                            "messages_ignored": ignored,
                        },
                    )
                    return SessionResult(
                        steps=steps,
                        messages_published=published,
                        messages_consumed=consumed,
                        messages_ignored=ignored,
                        status=SessionStatus.QUIESCENT,
                    )
        except Exception as exc:
            self.events.record(
                self.session_id,
                EventType.SESSION_FAILED,
                "supervisor",
                {
                    "steps": steps,
                    "messages_published": published,
                    "messages_consumed": consumed,
                    "messages_ignored": ignored,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )
            raise

        self.events.record(
            self.session_id,
            EventType.SESSION_MAX_STEPS,
            "supervisor",
            {
                "steps": steps,
                "messages_published": published,
                "messages_consumed": consumed,
                "messages_ignored": ignored,
            },
        )
        return SessionResult(
            steps=steps,
            messages_published=published,
            messages_consumed=consumed,
            messages_ignored=ignored,
            status=SessionStatus.MAX_STEPS,
        )
