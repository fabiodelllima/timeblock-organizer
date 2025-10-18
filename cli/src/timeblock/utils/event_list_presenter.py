"""Presentation layer for displaying event lists in terminal."""

from datetime import UTC, datetime, timedelta

from rich.console import Console

from ..models import Event
from .formatters import create_events_table


class ListPresenter:
    """Handles terminal presentation of event lists using Rich."""

    def __init__(self, console: Console):
        """Initialize with Rich console.

        Args:
            console: Rich Console instance for output.
        """
        self.console = console

    def show_no_events(self, filter_desc: str = ""):
        """Show message when no events are found.

        Args:
            filter_desc: Optional filter description (e.g., " for month +1").
        """
        self.console.print(f"[yellow]No events found{filter_desc}.[/yellow]")
        self.console.print(
            '[dim]Create an event with: timeblock add "Event Title" --start 09:00 --end 10:00[/dim]'
        )

    def show_single_table(self, events: list[Event], title: str):
        """Display a single formatted table of events.

        Args:
            events: List of Event objects to display.
            title: Title to show above the table.
        """
        table = create_events_table(events, title)
        self.console.print()
        self.console.print(table)
        self.console.print()

    def show_split_view(
        self,
        past_events: list[Event],
        present_events: list[Event],
        future_events: list[Event],
    ):
        """Display events split into three time-based tables.

        Args:
            past_events: Events from last week.
            present_events: Events from this week.
            future_events: Events from next 2 weeks.
        """
        if past_events:
            self.show_single_table(past_events, "Last Week")

        if present_events:
            self.show_single_table(present_events, "This Week")

        if future_events:
            self.show_single_table(future_events, "Next 2 Weeks")

        # Display summary count
        total = len(past_events) + len(present_events) + len(future_events)
        self.console.print(f"[dim]Total: {total} events[/dim]")

    def split_by_time(self, events: list[Event]) -> tuple[list[Event], list[Event], list[Event]]:
        """Split events into past, present, and future.

        Time periods:
        - Past: More than 7 days ago
        - Present: Last 7 days until now
        - Future: From now onwards

        Args:
            events: Complete list of events to split.

        Returns:
            Tuple of (past_events, present_events, future_events)
        """
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)

        # SQLite returns naive datetimes, convert to aware for comparison
        past = [e for e in events if e.scheduled_start.replace(tzinfo=UTC) < week_ago]

        present = [e for e in events if week_ago <= e.scheduled_start.replace(tzinfo=UTC) < now]

        future = [e for e in events if e.scheduled_start.replace(tzinfo=UTC) >= now]

        return (past, present, future)
