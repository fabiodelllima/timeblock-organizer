"""Add event command."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import typer
from rich.console import Console
from sqlmodel import Session

from ..database import get_engine
from ..models import Event, EventStatus
from ..utils.validators import is_valid_hex_color, parse_time, validate_time_range

console = Console()


def add(
    title: str = typer.Argument(..., help="Event title"),
    start: Optional[str] = typer.Option(
        None, "--start", "-s", help="Start time (HH:MM)"
    ),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End time (HH:MM)"),
    color: Optional[str] = typer.Option(
        None, "--color", "-c", help="Event color (#RRGGBB)"
    ),
    description: Optional[str] = typer.Option(
        None, "--desc", "-d", help="Event description"
    ),
) -> None:
    """Add a new event to the schedule.

    Examples:
        timeblock add "Study Python"
        timeblock add "Meeting" --start "14:00" --end "15:30"
        timeblock add "Workout" -s "07:00" -e "08:00" -c "#FF5733"
    """
    try:
        now = datetime.now(timezone.utc)

        # Parse start time (default: now)
        if start:
            scheduled_start = parse_time(start, now)
        else:
            scheduled_start = now

        # Parse end time (default: start + 1 hour)
        if end:
            scheduled_end = parse_time(end, now)
        else:
            scheduled_end = scheduled_start + timedelta(hours=1)

        # Validate time range
        validate_time_range(scheduled_start, scheduled_end)

        # Validate color format
        if color and not is_valid_hex_color(color):
            console.print(
                f"[red]✗[/red] Invalid color format: {color}", style="bold red"
            )
            console.print("[dim]Use hex format: #RRGGBB (e.g., #3498db)[/dim]")
            raise typer.Exit(code=1)

        # Create event
        engine = get_engine()
        with Session(engine) as session:
            event = Event(
                title=title,
                description=description,
                color=color,
                status=EventStatus.PLANNED,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
            )

            session.add(event)
            session.commit()
            session.refresh(event)
            created = event

            # Success message
            duration = (scheduled_end - scheduled_start).total_seconds() / 3600
            console.print(
                f"\n[green]✓[/green] Event created successfully!", style="bold green"
            )
            console.print(f"[dim]ID: {created.id}[/dim]")
            console.print(f"[bold]{created.title}[/bold]")

            if created.description:
                console.print(f"[dim]{created.description}[/dim]")

            console.print(
                f"[cyan]{scheduled_start.strftime('%H:%M')}[/cyan] → "
                f"[cyan]{scheduled_end.strftime('%H:%M')}[/cyan] "
                f"[dim]({duration:.1f}h)[/dim]"
            )

            if created.color:
                console.print(f"[dim]Color: {created.color}[/dim]")

            console.print()

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}", style="bold red")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating event: {e}", style="bold red")
        raise typer.Exit(code=1)
