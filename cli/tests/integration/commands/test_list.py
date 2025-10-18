"""Integration tests for list command."""

from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine
from typer.testing import CliRunner

from src.timeblock.main import app
from src.timeblock.models import Event, EventStatus


@pytest.fixture(scope="function")
def isolated_db(monkeypatch):
    """Create isolated in-memory database for each test."""
    # Create in-memory engine
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Create context manager that yields our test engine
    @contextmanager
    def mock_engine_context():
        try:
            yield engine
        finally:
            pass  # Don't dispose during test

    # Mock get_engine_context to return our test engine
    monkeypatch.setattr("src.timeblock.database.get_engine_context", mock_engine_context)
    monkeypatch.setattr("src.timeblock.commands.list.get_engine_context", mock_engine_context)

    # Create tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def test_list_command_works(isolated_db):
    """List command should execute without errors."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0


def test_list_shows_created_events(isolated_db):
    """List command should show events that were created."""
    # Create test events directly in database
    now = datetime.now(UTC)
    events = [
        Event(
            title="Morning Meeting",
            scheduled_start=now + timedelta(days=1),
            scheduled_end=now + timedelta(days=1, hours=1),
            status=EventStatus.PLANNED,
        ),
        Event(
            title="Lunch Break",
            scheduled_start=now + timedelta(days=1, hours=5),
            scheduled_end=now + timedelta(days=1, hours=6),
            status=EventStatus.PLANNED,
        ),
    ]

    with Session(isolated_db) as session:
        for event in events:
            session.add(event)
        session.commit()

    # Run list command
    runner = CliRunner()
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Morning Meeting" in result.output
    assert "Lunch Break" in result.output


def test_list_empty_db_works(isolated_db):
    """List command should work with empty database."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
