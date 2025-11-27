"""List events command with flexible filtering options."""

import typer
from rich.console import Console
from sqlmodel import Session

from ..database import get_engine_context
from ..utils.event_date_filters import DateFilterBuilder
from ..utils.event_list_presenter import ListPresenter
from ..utils.queries import fetch_events_in_range

console = Console()


def list_events(
    all_events: bool = typer.Option(False, "--all", "-a", help="Show all events"),
    limit: int = typer.Option(None, "--limit", "-l", help="Max number of events"),
    month: str = typer.Option(None, "--month", "-m", help="Month: 1-12 or +/-N"),
    week: str = typer.Option(None, "--week", "-w", help="Week: 0 (this), +N (next N), -N (last N)"),
    day: str = typer.Option(None, "--day", "-d", help="Day: 0 (today), +/-N"),
) -> None:
    """List scheduled events with flexible filtering.

    By default, shows events from the next 2 weeks.

    Examples:
        timeblock list                    # Next 2 weeks (default)
        timeblock list --week 0           # This week only
        timeblock list --week +4          # Next 4 weeks
        timeblock list --week -1          # Last week
        timeblock list --all              # All events
        timeblock list --month +1         # Next month
        timeblock list --day 0            # Today
        timeblock list --limit 10         # Just 10 events
    """
    try:
        # Build date filter from CLI arguments
        filter_builder = DateFilterBuilder()
        start, end, limit_val = filter_builder.build_from_args(
            all_events=all_events,
            limit=limit,
            month=month,
            week=week,
            day=day,
        )

        # Fetch events from database
        with get_engine_context() as engine:
            with Session(engine) as session:
                if limit_val:
                    # Use limit without date filter, newest first
                    events = fetch_events_in_range(session, start=None, end=None, ascending=False)[
                        :limit_val
                    ]
                else:
                    # Use date range filter, newest first
                    events = fetch_events_in_range(session, start=start, end=end, ascending=False)

        # Present results
        presenter = ListPresenter(console)
        if not events:
            filter_desc = _describe_filter(all_events, limit, month, week, day)
            presenter.show_no_events(filter_desc)
            return

        # Choose presentation style
        if all_events or limit:
            # Simple single table
            title = "All Events" if all_events else f"Latest {limit} Events"
            presenter.show_single_table(events, title)
        else:
            # Split view by time period
            past, present, future = presenter.split_by_time(events)
            presenter.show_split_view(past, present, future)

    except Exception as error:
        console.print(f"[red]✗[/red] Error: {error}", style="bold red")
        raise typer.Exit(code=1) from None


def _describe_filter(all_events, limit, month, week, day) -> str:
    """Generate human-readable filter description."""
    if limit:
        return f" (showing latest {limit})"
    if all_events:
        return ""
    if month:
        return f" for month {month}"
    if week:
        return f" for week {week}"
    if day:
        return f" for day {day}"
    return " for next 2 weeks"
