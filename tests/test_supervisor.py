import pytest

from agentmesh.db.database import init_db
from agentmesh.bus.message_bus import MessageBus
from agentmesh.models.agent import AgentProfile, LLMBackendConfig
from agentmesh.models.message import ACPMessage, MessageType
from agentmesh.runtime.supervisor import Supervisor


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


def team() -> list[AgentProfile]:
    return [profile("developer"), profile("tester"), profile("reviewer")]


def test_supervisor_runs_full_handoff_test_review_cycle():
    bus = MessageBus()
    bus.publish(ACPMessage(
        thread_id="t-1",
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Build a login API.",
    ))

    result = Supervisor(team(), session_id="s1").run(max_steps=50)

    thread = bus.get_thread("t-1")
    hops = [(m.sender_id, m.recipient_id, m.message_type) for m in thread]
    assert ("developer", "tester", MessageType.COMPLETION_REPORT) in hops
    assert ("tester", "reviewer", MessageType.COMPLETION_REPORT) in hops
    assert ("reviewer", "developer", MessageType.REVIEW_DECISION) in hops
    assert ("developer", "human", MessageType.STATUS_UPDATE) in hops
    assert result.quiescent is True
    assert result.steps <= 50


def test_supervisor_quiescent_immediately_when_no_work():
    result = Supervisor(team(), session_id="s2").run(max_steps=50)
    assert result.quiescent is True
    assert result.messages_published == 0


def test_supervisor_respects_max_steps_and_does_not_hang():
    bus = MessageBus()
    bus.publish(ACPMessage(
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Build a login API.",
    ))
    result = Supervisor(team(), session_id="s3").run(max_steps=1)
    assert result.steps == 1
    assert result.quiescent is False
