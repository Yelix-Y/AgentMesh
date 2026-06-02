import pytest

from agentmesh.db.database import init_db
from agentmesh.bus.message_bus import MessageBus
from agentmesh.models.agent import AgentProfile, LLMBackendConfig
from agentmesh.models.message import ACPMessage, MessageType
from agentmesh.runtime.agent import Agent
from agentmesh.runtime.state_machine import AgentState, AgentStateMachine


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr("agentmesh.db.database.DB_PATH", db)
    init_db()


def profile(role: str) -> AgentProfile:
    return AgentProfile(
        name=role,
        role=role,
        personality=f"You are the {role}.",
        working_style="careful",
        specialization="general",
        llm_backend=LLMBackendConfig(provider="mock"),
    )


def test_developer_processes_task_and_hands_off_to_tester():
    bus = MessageBus()
    bus.publish(ACPMessage(
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Build a login API.",
    ))

    dev = Agent(profile("developer"))
    outgoing = dev.process_one()

    assert outgoing is not None
    assert outgoing.sender_id == "developer"
    assert outgoing.recipient_id == "tester"
    assert outgoing.message_type == MessageType.COMPLETION_REPORT
    assert outgoing.body.strip()
    # the tester can now see it
    assert len(bus.poll("tester")) == 1
    # the original message was consumed
    assert len(bus.poll("developer")) == 0
    # agent returns to IDLE, ready for next work
    assert AgentStateMachine("developer").state == AgentState.IDLE


def test_tester_reports_findings_to_reviewer():
    bus = MessageBus()
    bus.publish(ACPMessage(
        sender_id="developer",
        recipient_id="tester",
        message_type=MessageType.COMPLETION_REPORT,
        body="Built the login API.",
    ))
    outgoing = Agent(profile("tester")).process_one()
    assert outgoing is not None
    assert outgoing.recipient_id == "reviewer"
    assert outgoing.message_type == MessageType.COMPLETION_REPORT
    assert len(bus.poll("reviewer")) == 1


def test_reviewer_issues_decision_to_developer():
    bus = MessageBus()
    bus.publish(ACPMessage(
        sender_id="tester",
        recipient_id="reviewer",
        message_type=MessageType.COMPLETION_REPORT,
        body="Tested the login API, found 2 edge cases.",
    ))
    outgoing = Agent(profile("reviewer")).process_one()
    assert outgoing is not None
    assert outgoing.recipient_id == "developer"
    assert outgoing.message_type == MessageType.REVIEW_DECISION
    assert len(bus.poll("developer")) == 1


def test_thread_id_is_preserved_across_handoff():
    bus = MessageBus()
    bus.publish(ACPMessage(
        thread_id="t-123",
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Build a login API.",
    ))
    outgoing = Agent(profile("developer")).process_one()
    assert outgoing.thread_id == "t-123"


def test_agent_records_work_in_own_memory():
    from agentmesh.memory.store import MemoryStore
    bus = MessageBus()
    bus.publish(ACPMessage(
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Build a login API.",
    ))
    Agent(profile("developer")).process_one()
    mem = MemoryStore().read("developer", "short", "developer")
    assert any("Build a login API." in m["content"] for m in mem)


def test_agent_records_event_when_publishing(monkeypatch):
    from agentmesh.runtime.events import EventLog
    bus = MessageBus()
    bus.publish(ACPMessage(
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Build a login API.",
    ))
    Agent(profile("developer"), session_id="sess-1").process_one()
    events = EventLog().read("sess-1")
    assert any(e["actor_id"] == "developer" and e["event_type"] == "message_published"
               for e in events)


def test_process_one_returns_none_when_inbox_empty():
    dev = Agent(profile("developer"))
    assert dev.process_one() is None
