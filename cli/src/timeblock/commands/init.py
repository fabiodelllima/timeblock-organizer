"""Initialize database command."""

from pathlib import Path

import typer
from rich.console import Console

from ..database import create_db_and_tables, get_db_path

console = Console()


def init():
    """Initialize the database."""
    db_path = Path(get_db_path())

    if db_path.exists():
        confirm = typer.confirm(
            f"Database already exists at {db_path}. Reinitialize?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Initialization cancelled.[/yellow]")
            raise typer.Exit()

    try:
        create_db_and_tables()
        console.print(
            f"[green]✓[/green] Database initialized at {db_path}",
            style="bold green",
        )
    except Exception as e:
        console.print(
            f"[red]✗[/red] Error initializing database: {e}",
            style="bold red",
        )
        raise typer.Exit(code=1)
