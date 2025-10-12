"""Integration tests for init command."""

import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Create isolated database in temp directory."""
    db_file = tmp_path / "test.db"

    # Set environment variable BEFORE importing
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_file))

    # Force reimport to pick up new env var
    import sys

    for module in [
        "src.timeblock.database",
        "src.timeblock.commands.init",
        "src.timeblock.main",
    ]:
        if module in sys.modules:
            del sys.modules[module]

    yield db_file


def test_init_creates_database(isolated_db):
    """Should create database file when it doesn't exist."""
    from src.timeblock.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert "initialized" in result.output.lower()
    assert isolated_db.exists()


def test_init_on_existing_database_decline(isolated_db):
    """Should ask for confirmation when database exists."""
    from src.timeblock.main import app

    runner = CliRunner()

    # First init
    runner.invoke(app, ["init"])

    # Second init - decline with 'n'
    result = runner.invoke(app, ["init"], input="n\n")

    assert result.exit_code == 0
