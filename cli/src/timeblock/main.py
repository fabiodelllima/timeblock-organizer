"""Entry point for TimeBlock CLI."""

import typer
from rich.console import Console

from .commands import add as add_cmd
from .commands import init as init_cmd
from .commands import list as list_cmd

app = typer.Typer(
    name="timeblock",
    help="TimeBlock Organizer - Time blocking & timesheet tracker",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"[bold green]TimeBlock v{__version__}[/bold green]")


@app.command()
def init():
    """Initialize database and create tables."""
    init_cmd.init()


@app.command()
def add(
    title: str = typer.Argument(..., help="Event title"),
    start: str = typer.Option(None, "--start", "-s", help="Start time (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="End time (HH:MM)"),
    color: str = typer.Option(None, "--color", "-c", help="Event color (#RRGGBB)"),
    description: str = typer.Option(None, "--desc", "-d", help="Event description"),
):
    """Add a new event to the schedule."""
    add_cmd.add(title, start, end, color, description)


app.command(name="list")(list_cmd.list_events)


if __name__ == "__main__":
    app()
