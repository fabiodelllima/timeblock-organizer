"""Initialize database command."""

from pathlib import Path

import typer
from rich.console import Console

from ..database import DB_PATH, create_db_and_tables

console = Console()


def init() -> None:
    """Initialize TimeBlock database.

    Creates SQLite database and all required tables if they don't exist.
    """
    try:
        # Check if database already exists
        db_path = Path(DB_PATH)  # Converter string para Path
        if db_path.exists():
            console.print(
                f"[yellow]⚠[/yellow]  Database already exists at: {DB_PATH}",
                style="yellow",
            )

            # Ask for confirmation to reinitialize
            if not typer.confirm(
                "Do you want to reinitialize? This will NOT delete existing data"
            ):
                console.print("[dim]Initialization cancelled.[/dim]")
                raise typer.Abort()

        # Create database and tables
        console.print("[cyan]Creating database...[/cyan]")
        create_db_and_tables()

        # Success message
        console.print(
            f"\n[green]✓[/green] Database initialized successfully!",
            style="bold green",
        )
        console.print(f"[dim]Location: {DB_PATH}[/dim]\n")

    except typer.Abort:
        # User cancelled
        pass
    except Exception as e:
        console.print(
            f"\n[red]✗[/red] Error initializing database: {e}", style="bold red"
        )
        raise typer.Exit(code=1)
