"""Comandos para visualização de conflitos de eventos."""
from datetime import datetime

import typer
from rich.console import Console

from src.timeblock.services.event_reordering_service import EventReorderingService
from src.timeblock.utils.conflict_display import display_conflicts

app = typer.Typer(help="Comandos de detecção de conflitos")
console = Console()


@app.command("conflicts")
def show_conflicts(
    event_id: int = typer.Option(None, "--event-id", help="ID do evento específico"),
    event_type: str = typer.Option(None, "--event-type", help="Tipo: task, habit_instance, event"),
    date: str = typer.Option(None, "--date", help="Data específica (YYYY-MM-DD)"),
):
    """
    Visualiza conflitos detectados.

    Exemplos:
        timeblock reschedule conflicts --event-id 42 --event-type task
        timeblock reschedule conflicts --date 2025-11-08
    """
    if event_id and event_type:
        # Conflitos de um evento específico
        try:
            conflicts = EventReorderingService.detect_conflicts(event_id, event_type)
            display_conflicts(conflicts, console)
        except ValueError as e:
            console.print(f"[red]✗ Erro: {e}[/red]")
            raise typer.Exit(1)

    elif date:
        # Conflitos de um dia específico
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            conflicts = EventReorderingService.get_conflicts_for_day(parsed_date)
            display_conflicts(conflicts, console)
        except ValueError:
            console.print("[red]✗ Formato de data inválido. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)

    else:
        console.print(
            "[red]✗ Especifique --event-id e --event-type OU --date[/red]\n"
            "\nExemplos:\n"
            "  timeblock reschedule conflicts --event-id 42 --event-type task\n"
            "  timeblock reschedule conflicts --date 2025-11-08"
        )
        raise typer.Exit(1)
