"""List events command."""

import calendar
from datetime import datetime, timezone
from typing import Optional

import typer
from rich.console import Console
from sqlmodel import Session

from ..database import get_engine
from ..utils.date_helpers import (
    add_months,
    get_day_bounds,
    get_month_bounds,
    get_week_bounds,
    parse_offset,
)
from ..utils.formatters import create_events_table
from ..utils.queries import fetch_events_in_range

console = Console()


def list_events(
    past: bool = typer.Option(False, "--past", help="Show only last week"),
    future: bool = typer.Option(False, "--future", help="Show current + next 2 weeks"),
    all_events: bool = typer.Option(
        False, "--all", help="Show all events in 3 tables (current | past | future)"
    ),
    week: Optional[str] = typer.Option(
        None, "--week", help="Show specific week (0=current, 1=next, -1=last, +1=next)"
    ),
    month: Optional[str] = typer.Option(
        None,
        "--month",
        help="Show specific month (0=current, 1-12=month number, +1=next, -1=last)",
    ),
    day: Optional[str] = typer.Option(
        None, "--day", help="Show specific day (0=today, +1=tomorrow, -1=yesterday)"
    ),
    year: Optional[int] = typer.Option(
        None, "--year", help="Year for --month filter (defaults to current year)"
    ),
    no_filter: bool = typer.Option(
        False, "--no-filter", help="Show all events without filtering"
    ),
) -> None:
    """List scheduled events.

    Default: Shows 2 tables (last week + current/next 2 weeks)

    Examples:
        timeblock list                     # Default: 2 tables
        timeblock list --past              # Only last week
        timeblock list --future            # Only current + 2 next weeks
        timeblock list --all               # 3 tables: current | past | future

        timeblock list --week 0            # Current week
        timeblock list --week 1            # Next week
        timeblock list --week -1           # Last week
        timeblock list --week +2           # 2 weeks ahead

        timeblock list --month 0           # Current month
        timeblock list --month 5           # May of current year
        timeblock list --month 12          # December of current year
        timeblock list --month +1          # Next month
        timeblock list --month -1          # Last month
        timeblock list --month 5 --year 2026  # May 2026

        timeblock list --day 0             # Today
        timeblock list --day +1            # Tomorrow
        timeblock list --day -1            # Yesterday

        timeblock list --no-filter         # All events (raw list)
    """
    try:
        engine = get_engine()
        with Session(engine) as session:

            # Mutually exclusive flags check
            flags = [
                past,
                future,
                all_events,
                week is not None,
                month is not None,
                day is not None,
                no_filter,
            ]
            if sum(flags) > 1:
                console.print(
                    "[red]✗[/red] Cannot combine multiple filter flags",
                    style="bold red",
                )
                raise typer.Exit(code=1)

            # NO FILTER: Show all events
            if no_filter:
                events = fetch_events_in_range(session, ascending=False)

                if not events:
                    console.print("[yellow]No events found.[/yellow]")
                    return

                table = create_events_table(
                    f"[bold]All Events[/bold] [dim]({len(events)} total)[/dim]", events
                )
                console.print()
                console.print(table)
                console.print()
                return

            # DAY FILTER: Show specific day
            if day is not None:
                day_offset = parse_offset(day)
                day_start, day_end = get_day_bounds(day_offset)
                events = fetch_events_in_range(
                    session, day_start, day_end, ascending=True
                )

                # Day label
                if day_offset == 0:
                    day_label = "Today"
                elif day_offset == 1:
                    day_label = "Tomorrow"
                elif day_offset == -1:
                    day_label = "Yesterday"
                else:
                    day_label = f"Day {day_offset:+d}"

                date_str = day_start.strftime("%b %d, %Y")

                if not events:
                    console.print(f"[yellow]No events found for {day_label}.[/yellow]")
                    return

                table = create_events_table(
                    f"[bold]{day_label}[/bold] [dim]({date_str} • {len(events)} events)[/dim]",
                    events,
                )
                console.print()
                console.print(table)
                console.print()
                return

            # MONTH FILTER: Show specific month
            if month is not None:
                # Handle current month ('0')
                if month == "0":
                    now = datetime.now(timezone.utc)
                    month_num = now.month
                    target_year = now.year
                else:
                    # Check if it's an offset (starts with + or -)
                    is_offset = month.startswith("+") or month.startswith("-")
                    month_offset = parse_offset(month)

                    # If offset OR out of valid month range, treat as relative
                    if is_offset or month_offset < 1 or month_offset > 12:
                        now = datetime.now(timezone.utc)
                        target_date = add_months(now, month_offset)
                        month_num = target_date.month
                        target_year = target_date.year
                    else:
                        # Direct month number (1-12)
                        month_num = month_offset
                        target_year = year if year else datetime.now(timezone.utc).year

                month_start, month_end = get_month_bounds(month_num, target_year)
                events = fetch_events_in_range(
                    session, month_start, month_end, ascending=True
                )

                month_name = calendar.month_name[month_num]

                if not events:
                    console.print(
                        f"[yellow]No events found for {month_name} {target_year}.[/yellow]"
                    )
                    return

                table = create_events_table(
                    f"[bold]{month_name} {target_year}[/bold] [dim]({len(events)} events)[/dim]",
                    events,
                )
                console.print()
                console.print(table)
                console.print()
                return

            # WEEK FILTER: Show specific week
            if week is not None:
                week_offset = parse_offset(week)
                week_start, week_end = get_week_bounds(week_offset)
                events = fetch_events_in_range(
                    session, week_start, week_end, ascending=True
                )

                # Week label
                if week_offset == 0:
                    week_label = "Current Week"
                else:
                    week_label = f"Week {week_offset:+d}"

                date_range = (
                    f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"
                )

                if not events:
                    console.print(f"[yellow]No events found for {week_label}.[/yellow]")
                    return

                table = create_events_table(
                    f"[bold]{week_label}[/bold] [dim]({date_range} • {len(events)} events)[/dim]",
                    events,
                )
                console.print()
                console.print(table)
                console.print()
                return

            # --PAST: Only last week
            if past:
                last_week_start, last_week_end = get_week_bounds(-1)
                events = fetch_events_in_range(
                    session, last_week_start, last_week_end, ascending=True
                )

                if not events:
                    console.print("[yellow]No events found for last week.[/yellow]")
                    return

                date_range = f"{last_week_start.strftime('%b %d')} - {last_week_end.strftime('%b %d')}"
                table = create_events_table(
                    f"[bold]Last Week[/bold] [dim]({date_range} • {len(events)} events)[/dim]",
                    events,
                )
                console.print()
                console.print(table)
                console.print()
                return

            # --FUTURE: Current + next 2 weeks (3 weeks total)
            if future:
                current_week_start, _ = get_week_bounds(0)
                _, third_week_end = get_week_bounds(2)
                events = fetch_events_in_range(
                    session, current_week_start, third_week_end, ascending=True
                )

                if not events:
                    console.print(
                        "[yellow]No events found for current + next 2 weeks.[/yellow]"
                    )
                    return

                date_range = f"{current_week_start.strftime('%b %d')} - {third_week_end.strftime('%b %d')}"
                table = create_events_table(
                    f"[bold]Current + Next 2 Weeks[/bold] [dim]({date_range}) • {len(events)} events[/dim]",
                    events,
                )
                console.print()
                console.print(table)
                console.print()
                return

            # --ALL: 3 tables (current | past | future)
            if all_events:
                current_week_start, current_week_end = get_week_bounds(0)

                # Table 1: Current week
                current_events = fetch_events_in_range(
                    session, current_week_start, current_week_end, ascending=True
                )

                # Table 2: All past (before current week)
                past_events = fetch_events_in_range(
                    session, end=current_week_start, ascending=False
                )

                # Table 3: All future (after current week)
                future_events = fetch_events_in_range(
                    session, start=current_week_end, ascending=True
                )

                console.print()

                # Show current week
                if current_events:
                    date_range = f"{current_week_start.strftime('%b %d')} - {current_week_end.strftime('%b %d')}"
                    table = create_events_table(
                        f"[bold]Current Week[/bold] [dim]({date_range} • {len(current_events)} events)[/dim]",
                        current_events,
                    )
                    console.print(table)
                    console.print()
                else:
                    console.print("[dim]No events in current week[/dim]\n")

                # Show past
                if past_events:
                    table = create_events_table(
                        f"[bold]All Past Events[/bold] [dim]({len(past_events)} events)[/dim]",
                        past_events,
                    )
                    console.print(table)
                    console.print()
                else:
                    console.print("[dim]No past events[/dim]\n")

                # Show future
                if future_events:
                    table = create_events_table(
                        f"[bold]All Future Events[/bold] [dim]({len(future_events)} events)[/dim]",
                        future_events,
                    )
                    console.print(table)
                    console.print()
                else:
                    console.print("[dim]No future events[/dim]\n")

                return

            # DEFAULT: 2 tables (last week + current/next 2 weeks)
            last_week_start, last_week_end = get_week_bounds(-1)
            current_week_start, _ = get_week_bounds(0)
            _, third_week_end = get_week_bounds(2)

            # Table 1: Last week
            last_week_events = fetch_events_in_range(
                session, last_week_start, last_week_end, ascending=True
            )

            # Table 2: Current + next 2 weeks
            upcoming_events = fetch_events_in_range(
                session, current_week_start, third_week_end, ascending=True
            )

            console.print()

            # Show last week
            if last_week_events:
                date_range = f"{last_week_start.strftime('%b %d')} - {last_week_end.strftime('%b %d')}"
                table = create_events_table(
                    f"[bold]Last Week[/bold] [dim]({date_range} • {len(last_week_events)} events)[/dim]",
                    last_week_events,
                )
                console.print(table)
                console.print()
            else:
                console.print("[dim]No events last week[/dim]\n")

            # Show upcoming
            if upcoming_events:
                date_range = f"{current_week_start.strftime('%b %d')} - {third_week_end.strftime('%b %d')}"
                table = create_events_table(
                    f"[bold]Current + Next 2 Weeks[/bold] [dim]({date_range} • {len(upcoming_events)} events)[/dim]",
                    upcoming_events,
                )
                console.print(table)
                console.print()
            else:
                console.print("[dim]No upcoming events[/dim]\n")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}", style="bold red")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error listing events: {e}", style="bold red")
        raise typer.Exit(code=1)
