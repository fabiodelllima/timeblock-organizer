"""Utilitários para exibir conflitos de eventos."""

from rich.console import Console
from rich.table import Table

from src.timeblock.services.event_reordering_models import Conflict


def display_conflicts(conflicts: list[Conflict], console: Console) -> None:
    """
    Exibe conflitos de forma estruturada.

    Args:
        conflicts: Lista de conflitos detectados
        console: Console do Rich para output
    """
    if not conflicts:
        console.print("[green]✓ Nenhum conflito detectado[/green]")
        return

    console.print(f"\n[yellow]⚠ {len(conflicts)} conflito(s) detectado(s)[/yellow]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Evento 1", style="cyan")
    table.add_column("Horário", style="cyan")
    table.add_column("Evento 2", style="yellow")
    table.add_column("Horário", style="yellow")
    table.add_column("Sobreposição", style="red")

    for conflict in conflicts:
        # Calcula sobreposição
        overlap_start = max(conflict.triggered_start, conflict.conflicting_start)
        overlap_end = min(conflict.triggered_end, conflict.conflicting_end)
        overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)

        # Formata tipo de evento
        type_map = {
            "task": "Task",
            "habit_instance": "Hábito",
            "event": "Evento",
        }

        event1_type = type_map.get(conflict.triggered_event_type, conflict.triggered_event_type)
        event2_type = type_map.get(conflict.conflicting_event_type, conflict.conflicting_event_type)

        table.add_row(
            f"{event1_type} #{conflict.triggered_event_id}",
            f"{conflict.triggered_start.strftime('%H:%M')}-{conflict.triggered_end.strftime('%H:%M')}",
            f"{event2_type} #{conflict.conflicting_event_id}",
            f"{conflict.conflicting_start.strftime('%H:%M')}-{conflict.conflicting_end.strftime('%H:%M')}",
            f"{overlap_minutes} min",
        )

    console.print(table)
    console.print(
        "\n[dim]Use comandos específicos (habit adjust, task update) "
        "para ajustar eventos conforme necessário[/dim]\n"
    )
