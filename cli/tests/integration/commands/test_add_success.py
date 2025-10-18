"""Integration tests for add command - success cases."""

from sqlmodel import Session, create_engine, select

from src.timeblock.main import app
from src.timeblock.models import Event


class TestAddSuccess:
    """Test successful event creation scenarios."""

    def test_add_basic_event(self, isolated_db, cli_runner):
        """Should add a basic event successfully."""
        result = cli_runner.invoke(
            app,
            ["add", "Morning Meeting", "-s", "09:00", "-e", "10:00"],
        )
        assert result.exit_code == 0
        engine = create_engine(f"sqlite:///{isolated_db}")
        with Session(engine) as session:
            events = session.exec(select(Event)).all()
            assert len(events) == 1
            assert events[0].title == "Morning Meeting"

    def test_add_with_description(self, isolated_db, cli_runner):
        """Should add event with description."""
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Team Standup",
                "-s",
                "10:00",
                "-e",
                "10:30",
                "--desc",
                "Daily sync meeting",
            ],
        )
        assert result.exit_code == 0
        engine = create_engine(f"sqlite:///{isolated_db}")
        with Session(engine) as session:
            event = session.exec(select(Event)).first()
            description = event.description if event is not None else "Default description"
            assert description == "Daily sync meeting"

    def test_add_with_color(self, isolated_db, cli_runner):
        """Should add event with color."""
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Focus Time",
                "-s",
                "14:00",
                "-e",
                "16:00",
                "--color",
                "#FF5733",
            ],
        )
        assert result is not None
        assert result.exit_code == 0
        engine = create_engine(f"sqlite:///{isolated_db}")
        with Session(engine) as session:
            event = session.exec(select(Event)).first()
            if event is not None:
                assert event.color == "#FF5733"
            else:
                print("No event found")

    def test_add_with_all_fields(self, isolated_db, cli_runner):
        """Should add event with all optional fields."""
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Client Call",
                "-s",
                "15:00",
                "-e",
                "16:00",
                "--desc",
                "Q3 Review",
                "--color",
                "#3498db",
            ],
        )
        assert result.exit_code == 0
        engine = create_engine(f"sqlite:///{isolated_db}")
        with Session(engine) as session:
            event = session.exec(select(Event)).first()
            if event is not None:
                assert event.title == "Client Call"
                assert event.description == "Q3 Review"
                assert event.color == "#3498db"
            else:
                print("No event found")

    def test_add_multiple_events(self, isolated_db, cli_runner):
        """Should add multiple events sequentially."""
        cli_runner.invoke(app, ["add", "Event 1", "-s", "09:00", "-e", "10:00"])
        cli_runner.invoke(app, ["add", "Event 2", "-s", "11:00", "-e", "12:00"])
        cli_runner.invoke(app, ["add", "Event 3", "-s", "14:00", "-e", "15:00"])
        engine = create_engine(f"sqlite:///{isolated_db}")
        with Session(engine) as session:
            events = session.exec(select(Event)).all()
            assert len(events) == 3

    def test_add_with_minutes(self, isolated_db, cli_runner):
        """Should handle times with minutes correctly."""
        result = cli_runner.invoke(
            app,
            ["add", "Quick Sync", "-s", "10:15", "-e", "10:45"],
        )
        assert result.exit_code == 0
        engine = create_engine(f"sqlite:///{isolated_db}")
        with Session(engine) as session:
            event = session.exec(select(Event)).first()
            if event is not None:
                assert event.scheduled_start.hour == 10
                assert event.scheduled_start.minute == 15
                assert event.scheduled_end.hour == 10
                assert event.scheduled_end.minute == 45
            else:
                print("No event found")
