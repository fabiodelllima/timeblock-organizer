"""Integration tests for add command - edge cases."""

import pytest
from sqlmodel import Session, select
from typer.testing import CliRunner

from src.timeblock.database import get_engine
from src.timeblock.main import app
from src.timeblock.models import Event


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


class TestAddEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_add_one_minute_event(self, isolated_db, runner):
        """Should handle very short events."""
        result = runner.invoke(
            app,
            ["add", "Quick Check", "-s", "10:00", "-e", "10:01"],
        )
        assert result.exit_code == 0
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            duration = (event.scheduled_end - event.scheduled_start).total_seconds()
            assert duration == 60

    def test_add_event_crossing_midnight_success(self, isolated_db, runner):
        """Should handle events that cross midnight."""
        result = runner.invoke(
            app,
            ["add", "Night Shift", "-s", "23:00", "-e", "01:00"],
        )
        assert result.exit_code == 0

    def test_add_long_title(self, isolated_db, runner):
        """Should handle long event titles."""
        long_title = "A" * 200
        result = runner.invoke(
            app,
            ["add", long_title, "-s", "10:00", "-e", "11:00"],
        )
        assert result.exit_code == 0
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.title == long_title

    def test_add_special_characters_in_title(self, isolated_db, runner):
        """Should handle special characters in title."""
        result = runner.invoke(
            app,
            [
                "add",
                "Meeting: Q&A (Part 1) - Review #2",
                "-s",
                "10:00",
                "-e",
                "11:00",
            ],
        )
        assert result.exit_code == 0
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.title == "Meeting: Q&A (Part 1) - Review #2"

    def test_add_empty_description(self, isolated_db, runner):
        """Should handle empty description gracefully."""
        result = runner.invoke(
            app,
            [
                "add",
                "Meeting",
                "-s",
                "10:00",
                "-e",
                "11:00",
                "--desc",
                "",
            ],
        )
        assert result.exit_code == 0
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.description == ""

    def test_add_midnight_event(self, isolated_db, runner):
        """Should handle events at midnight."""
        result = runner.invoke(
            app,
            ["add", "Midnight Task", "-s", "00:00", "-e", "01:00"],
        )
        assert result.exit_code == 0
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.scheduled_start.hour == 0
            assert event.scheduled_start.minute == 0
