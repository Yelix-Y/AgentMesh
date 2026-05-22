import pytest
from pathlib import Path
from agentmesh.models.loader import load_profile
from agentmesh.models.agent import AgentProfile


AGENTS_DIR = Path(__file__).parent.parent / "agents"


def test_load_developer_profile():
    profile = load_profile(AGENTS_DIR / "developer.yaml")
    assert profile.name == "developer"
    assert profile.role == "developer"
    assert profile.llm_backend.provider == "anthropic"


def test_load_tester_profile():
    profile = load_profile(AGENTS_DIR / "tester.yaml")
    assert profile.name == "tester"
    assert profile.role == "tester"


def test_load_reviewer_profile():
    profile = load_profile(AGENTS_DIR / "reviewer.yaml")
    assert profile.name == "reviewer"
    assert profile.role == "reviewer"


def test_invalid_profile_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: x\nrole: janitor\n")
    with pytest.raises(Exception):
        load_profile(bad)


def test_missing_profile_raises():
    with pytest.raises(FileNotFoundError):
        load_profile("/nonexistent/profile.yaml")
