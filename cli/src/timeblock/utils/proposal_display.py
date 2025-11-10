"""Formatação de propostas de reordenamento."""
import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.services.event_reordering_models import ReorderingProposal


def display_proposal(proposal: ReorderingProposal, console: Console):
    """Exibe proposta formatada."""

    # Conflitos
    console.print("\n[bold red]⚠ Conflitos Detectados:[/bold red]")
    conflicts_table = Table(show_header=True)
    conflicts_table.add_column("Evento 1")
    conflicts_table.add_column("Evento 2")
    conflicts_table.add_column("Tipo")

    for conflict in proposal.conflicts:
        conflicts_table.add_row(
            f"{conflict.triggered_event_type} #{conflict.triggered_event_id}",
            f"{conflict.conflicting_event_type} #{conflict.conflicting_event_id}",
            conflict.conflict_type.value
        )

    console.print(conflicts_table)

    # Mudanças propostas
    console.print("\n[bold yellow]>>> MUDANÇAS PROPOSTAS:[/bold yellow]")
    changes_table = Table(show_header=True)
    changes_table.add_column("Evento")
    changes_table.add_column("Horário Atual")
    changes_table.add_column("Horário Proposto")
    changes_table.add_column("Prioridade")

    for change in proposal.proposed_changes:
        changes_table.add_row(
            f"{change.event_title}",
            f"{change.current_start.strftime('%H:%M')} - {change.current_end.strftime('%H:%M')}",
            f"{change.proposed_start.strftime('%H:%M')} - {change.proposed_end.strftime('%H:%M')}",
            change.priority.name
        )

    console.print(changes_table)

    # Resumo
    console.print(f"\n[bold]Atraso estimado:[/bold] {proposal.estimated_duration_shift} minutos")


def confirm_apply_proposal() -> bool:
    """Pede confirmação para aplicar proposta."""
    return typer.confirm("\nAplicar reordenamento?")
