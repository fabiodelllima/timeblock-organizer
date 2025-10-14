"""Add event command."""

from datetime import UTC, datetime, timedelta

import typer
from rich.console import Console
from sqlmodel import Session

from ..database import get_engine_context
from ..models import Event, EventStatus
from ..utils.validators import is_valid_hex_color, parse_time, validate_time_range

console = Console()


def add(
    title: str = typer.Argument(..., help="Event title"),
    start: str | None = typer.Option(
        None, "--start", "-s", help="Start time (HH:MM or HHh/HHhMM)"
    ),
    end: str | None = typer.Option(
        None, "--end", "-e", help="End time (HH:MM or HHhMM)"
    ),
    color: str | None = typer.Option(
        None, "--color", "-c", help="Event color (#RRGGBB)"
    ),
    description: str | None = typer.Option(
        None, "--desc", "-d", help="Event description"
    ),
) -> None:
    """Add a new event to the schedule."""
    try:
        now = datetime.now(UTC)
        scheduled_start = parse_time(start) if start else now
        scheduled_end = parse_time(end) if end else now + timedelta(hours=1)

        # Validate and adjust for midnight crossing
        original_end = scheduled_end
        scheduled_end = validate_time_range(scheduled_start, scheduled_end)

        # Show warning if date was adjusted
        if scheduled_end.date() > original_end.date():
            console.print("[yellow]⚠[/yellow] Event crosses midnight (ends next day)")

        if color and not is_valid_hex_color(color):
            console.print(
                f"[red]✗[/red] Invalid color format: {color}", style="bold red"
            )
            console.print("[dim]Use hex format: #RRGGBB (e.g., #3498db)[/dim]")
            raise typer.Exit(code=1) from None

        with get_engine_context() as engine, Session(engine) as session:
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

            duration = (scheduled_end - scheduled_start).total_seconds() / 3600
            console.print(
                "\n[green]✓[/green] Event created successfully!",
                style="bold green",
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
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating event: {e}", style="bold red")
        raise typer.Exit(code=1) from None
