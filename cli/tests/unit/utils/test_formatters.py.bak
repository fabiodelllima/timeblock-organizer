"""Tests for formatters module."""

from datetime import UTC, datetime, timedelta

from src.timeblock.models import Event, EventStatus
from src.timeblock.utils.formatters import create_events_table


def test_create_table_with_colored_event():
    """Should format event with color."""
    now = datetime.now(UTC)

    events = [
        Event(
            title="Colored Event",
            scheduled_start=now,
            scheduled_end=now + timedelta(hours=1),
            status=EventStatus.PENDING,
            color="#FF5733",  # Test with color
        )
    ]

    table = create_events_table(events, "Test Table")

    # Should create table without errors
    assert table is not None
