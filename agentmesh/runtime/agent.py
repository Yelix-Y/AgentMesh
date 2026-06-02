from agentmesh.bus.message_bus import MessageBus
from agentmesh.memory.store import MemoryStore
from agentmesh.models.agent import AgentProfile
from agentmesh.models.message import ACPMessage, MessageType
from agentmesh.runtime.events import EventLog
from agentmesh.runtime.llm import LLMProvider, get_provider
from agentmesh.runtime.state_machine import AgentState, AgentStateMachine


ROUTING: dict[tuple[str, MessageType], tuple[MessageType, str]] = {
    ("developer", MessageType.HUMAN_INTERVENTION): (MessageType.COMPLETION_REPORT, "tester"),
    ("developer", MessageType.TASK_HANDOFF): (MessageType.COMPLETION_REPORT, "tester"),
    ("developer", MessageType.REVIEW_DECISION): (MessageType.STATUS_UPDATE, "human"),
    ("tester", MessageType.COMPLETION_REPORT): (MessageType.COMPLETION_REPORT, "reviewer"),
    ("reviewer", MessageType.COMPLETION_REPORT): (MessageType.REVIEW_DECISION, "developer"),
}


class Agent:
    """A single digital coworker: the harness that drives one agent through its
    state machine in response to inbox messages."""

    def __init__(
        self,
        profile: AgentProfile,
        llm: LLMProvider | None = None,
        bus: MessageBus | None = None,
        memory: MemoryStore | None = None,
        session_id: str = "default",
    ):
        self.profile = profile
        self.name = profile.name
        self.session_id = session_id
        self.llm = llm or get_provider(profile.llm_backend)
        self.bus = bus or MessageBus()
        self.memory = memory or MemoryStore()
        self.events = EventLog()
        self.sm = AgentStateMachine(self.name)

    def process_one(self) -> ACPMessage | None:
        inbox = self.bus.poll(self.name)
        if not inbox:
            return None
        incoming = inbox[0]

        route = ROUTING.get((self.profile.role, incoming.message_type))
        if route is None:
            self.bus.consume(incoming.id)
            return None
        out_type, recipient = route

        self.sm.transition(AgentState.READING)
        context = self.memory.read(self.name, "short", self.name)

        self.sm.transition(AgentState.PLANNING)

        self.sm.transition(AgentState.EXECUTING)
        body = self.llm.generate(self.profile, incoming, context)
        self.memory.write(self.name, "short", f"Handled: {incoming.body}")

        self.sm.transition(AgentState.REPORTING)
        outgoing = ACPMessage(
            thread_id=incoming.thread_id,
            sender_id=self.name,
            recipient_id=recipient,
            message_type=out_type,
            body=body,
        )
        self.bus.publish(outgoing)
        self.bus.consume(incoming.id)
        self.events.record(
            self.session_id,
            "message_published",
            self.name,
            {
                "message_id": outgoing.id,
                "thread_id": outgoing.thread_id,
                "message_type": out_type.value,
                "recipient": recipient,
            },
        )

        self.sm.transition(AgentState.IDLE)
        return outgoing
