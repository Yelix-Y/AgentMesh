import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from agentmesh.db.database import init_db, DB_PATH
from agentmesh.bus.message_bus import MessageBus
from agentmesh.models.message import ACPMessage, MessageType


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Each test gets its own fresh SQLite database."""
    db = tmp_path / "test.db"
    monkeypatch.setattr("agentmesh.db.database.DB_PATH", db)
    init_db()


def make_message(sender: str, recipient: str, mtype=MessageType.TASK_HANDOFF, body="hello") -> ACPMessage:
    return ACPMessage(sender_id=sender, recipient_id=recipient, message_type=mtype, body=body)


def test_publish_and_poll():
    bus = MessageBus()
    msg = make_message("developer", "tester")
    bus.publish(msg)
    messages = bus.poll("tester")
    assert len(messages) == 1
    assert messages[0].body == "hello"
    assert messages[0].sender_id == "developer"


def test_poll_returns_only_recipient_messages():
    bus = MessageBus()
    bus.publish(make_message("developer", "tester", body="for tester"))
    bus.publish(make_message("developer", "reviewer", body="for reviewer"))
    assert len(bus.poll("tester")) == 1
    assert len(bus.poll("reviewer")) == 1
    assert bus.poll("tester")[0].body == "for tester"


def test_consume_marks_as_read():
    bus = MessageBus()
    msg = make_message("developer", "tester")
    bus.publish(msg)
    assert len(bus.poll("tester")) == 1
    bus.consume(msg.id)
    assert len(bus.poll("tester")) == 0


def test_thread_grouping():
    bus = MessageBus()
    thread_id = "thread-abc"
    m1 = ACPMessage(thread_id=thread_id, sender_id="developer", recipient_id="tester",
                    message_type=MessageType.TASK_HANDOFF, body="first")
    m2 = ACPMessage(thread_id=thread_id, sender_id="tester", recipient_id="developer",
                    message_type=MessageType.CLARIFICATION_REQUEST, body="second")
    bus.publish(m1)
    bus.publish(m2)
    thread = bus.get_thread(thread_id)
    assert len(thread) == 2
    assert thread[0].body == "first"
    assert thread[1].body == "second"


def test_inbox_isolation():
    bus = MessageBus()
    bus.publish(make_message("human", "developer", body="task"))
    assert len(bus.poll("tester")) == 0
    assert len(bus.poll("reviewer")) == 0
