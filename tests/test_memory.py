import pytest
from agentmesh.db.database import init_db
from agentmesh.memory.store import MemoryStore


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr("agentmesh.db.database.DB_PATH", db)
    init_db()


def test_write_and_read_short_term():
    store = MemoryStore()
    store.write("developer", "short", "Working on OAuth refresh flow")
    entries = store.read("developer", "short", requesting_agent_id="developer")
    assert len(entries) == 1
    assert "OAuth" in entries[0]["content"]


def test_write_and_read_long_term():
    store = MemoryStore()
    store.write("reviewer", "long", "Past review: always check token expiry edge cases")
    entries = store.read("reviewer", "long", requesting_agent_id="reviewer")
    assert len(entries) == 1


def test_isolation_prevents_cross_agent_read():
    store = MemoryStore()
    store.write("developer", "short", "secret developer context")
    with pytest.raises(PermissionError):
        store.read("developer", "short", requesting_agent_id="tester")


def test_clear_short_term_preserves_long_term():
    store = MemoryStore()
    store.write("tester", "short", "current task context")
    store.write("tester", "long", "past experience")
    store.clear_short_term("tester")
    assert len(store.read("tester", "short", requesting_agent_id="tester")) == 0
    assert len(store.read("tester", "long", requesting_agent_id="tester")) == 1


def test_multiple_entries_ordered_by_time():
    store = MemoryStore()
    store.write("developer", "short", "first")
    store.write("developer", "short", "second")
    entries = store.read("developer", "short", requesting_agent_id="developer")
    assert entries[0]["content"] == "first"
    assert entries[1]["content"] == "second"
