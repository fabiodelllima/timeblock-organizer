"""Tests for ListPresenter."""

from datetime import UTC, datetime, timedelta
from io import StringIO

from rich.console import Console

from src.timeblock.models import Event, EventStatus
from src.timeblock.utils.event_list_presenter import ListPresenter


def test_show_tables_with_only_past():
    """Should handle case with only past events."""
    output = StringIO()
    console = Console(file=output, force_terminal=True)
    presenter = ListPresenter(console)
    now = datetime.now(UTC)

    past = [
        Event(
            title="Past Event",
            scheduled_start=now - timedelta(days=8),
            scheduled_end=now - timedelta(days=8, hours=-1),
            status=EventStatus.COMPLETED,
        )
    ]

    # Should not crash with empty present and future
    presenter.show_split_view(past, [], [])
    assert "Last Week" in output.getvalue()


def test_show_tables_with_only_present():
    """Should handle case with only present events."""
    output = StringIO()
    console = Console(file=output, force_terminal=True)
    presenter = ListPresenter(console)
    now = datetime.now(UTC)

    present = [
        Event(
            title="Present Event",
            scheduled_start=now - timedelta(days=1),
            scheduled_end=now - timedelta(days=1, hours=-1),
            status=EventStatus.PENDING,
        )
    ]

    # Should not crash with empty past and future
    presenter.show_split_view([], present, [])
    assert "This Week" in output.getvalue()


def test_show_tables_with_only_future():
    """Should handle case with only future events."""
    output = StringIO()
    console = Console(file=output, force_terminal=True)
    presenter = ListPresenter(console)
    now = datetime.now(UTC)

    future = [
        Event(
            title="Future Event",
            scheduled_start=now + timedelta(days=1),
            scheduled_end=now + timedelta(days=1, hours=1),
            status=EventStatus.PENDING,
        )
    ]

    # Should not crash with empty past and present
    presenter.show_split_view([], [], future)
    assert "Next 2 Weeks" in output.getvalue()
