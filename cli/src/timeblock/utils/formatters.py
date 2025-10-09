"""Rich formatting utilities for terminal output."""

from rich.table import Table

from ..models import Event

# Status color mapping for terminal display
STATUS_COLORS = {
    "planned": "yellow",
    "in_progress": "green",
    "paused": "blue",
    "completed": "dim",
    "cancelled": "red",
}


def create_events_table(events: list[Event], title: str) -> Table:
    """Create a formatted table for events.

    Args:
        events: List of Event objects to display
        title: Table title with optional Rich markup

    Returns:
        Rich Table object ready for printing
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        expand=False,
        width=None,
        box=None,  # Remove box for cleaner look
    )

    # Fixed widths to prevent truncation
    table.add_column("ID", style="dim", min_width=4, no_wrap=True)
    table.add_column("Date", style="cyan", min_width=10, no_wrap=True)
    table.add_column("Title", style="bold", min_width=20, no_wrap=True)
    table.add_column("Time", style="cyan", min_width=13, no_wrap=True)
    table.add_column("Duration", justify="right", min_width=8, no_wrap=True)
    table.add_column("Status", justify="center", min_width=12, no_wrap=True)
    table.add_column("Color", justify="center", min_width=15, no_wrap=True)

    for event in events:
        duration = (event.scheduled_end - event.scheduled_start).total_seconds() / 3600

        # Format status with color
        status_color = STATUS_COLORS.get(event.status.value, "white")
        status_text = f"[{status_color}]{event.status.value}[/{status_color}]"

        # Format color
        color_display = "[dim]-[/dim]"
        if event.color:
            color_display = f"[{event.color}]●[/{event.color}] {event.color}"

        # Format date
        date_str = event.scheduled_start.strftime("%Y-%m-%d")

        # Format time range
        time_str = (
            f"{event.scheduled_start.strftime('%H:%M')} → "
            f"{event.scheduled_end.strftime('%H:%M')}"
        )

        table.add_row(
            str(event.id),
            date_str,
            event.title,
            time_str,
            f"{duration:.1f}h",
            status_text,
            color_display,
        )

    return table
