import pytest
from agentmesh.db.database import init_db
from agentmesh.runtime.state_machine import AgentStateMachine, AgentState


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr("agentmesh.db.database.DB_PATH", db)
    init_db()


def test_initial_state_is_idle():
    sm = AgentStateMachine("developer")
    assert sm.state == AgentState.IDLE


def test_valid_transition_idle_to_reading():
    sm = AgentStateMachine("developer")
    sm.transition(AgentState.READING)
    assert sm.state == AgentState.READING


def test_full_happy_path():
    sm = AgentStateMachine("developer")
    sm.transition(AgentState.READING)
    sm.transition(AgentState.PLANNING)
    sm.transition(AgentState.EXECUTING)
    sm.transition(AgentState.REPORTING)
    sm.transition(AgentState.WAITING)
    sm.transition(AgentState.IDLE)
    assert sm.state == AgentState.IDLE


def test_invalid_transition_raises():
    sm = AgentStateMachine("developer")
    with pytest.raises(ValueError, match="Invalid transition"):
        sm.transition(AgentState.EXECUTING)  # Can't jump from IDLE to EXECUTING


def test_escalate_from_any_state():
    for start_state in [AgentState.IDLE, AgentState.READING, AgentState.PLANNING,
                        AgentState.EXECUTING, AgentState.REPORTING, AgentState.WAITING]:
        sm = AgentStateMachine(f"agent-{start_state.value}")
        # get to the desired state
        transitions = {
            AgentState.IDLE: [],
            AgentState.READING: [AgentState.READING],
            AgentState.PLANNING: [AgentState.READING, AgentState.PLANNING],
            AgentState.EXECUTING: [AgentState.READING, AgentState.PLANNING, AgentState.EXECUTING],
            AgentState.REPORTING: [AgentState.READING, AgentState.PLANNING, AgentState.EXECUTING, AgentState.REPORTING],
            AgentState.WAITING: [AgentState.READING, AgentState.PLANNING, AgentState.EXECUTING, AgentState.REPORTING, AgentState.WAITING],
        }
        for t in transitions[start_state]:
            sm.transition(t)
        sm.escalate()
        assert sm.state == AgentState.ESCALATING


def test_state_persists_across_instances():
    sm1 = AgentStateMachine("persistent-agent")
    sm1.transition(AgentState.READING)
    sm2 = AgentStateMachine("persistent-agent")
    assert sm2.state == AgentState.READING


def test_separate_agents_have_independent_states():
    sm_dev = AgentStateMachine("dev")
    sm_test = AgentStateMachine("test")
    sm_dev.transition(AgentState.READING)
    assert sm_test.state == AgentState.IDLE
