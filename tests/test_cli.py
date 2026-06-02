import pytest
from typer.testing import CliRunner

from agentmesh.db.database import init_db
from agentmesh.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr("agentmesh.db.database.DB_PATH", db)
    init_db()


def test_run_command_drives_full_cycle():
    result = runner.invoke(
        app,
        ["run", "Build a login API.", "--agents-dir", "agents", "--max-steps", "50"],
    )
    assert result.exit_code == 0, result.output
    assert "REVIEW_DECISION" in result.output
    assert "developer" in result.output and "tester" in result.output
