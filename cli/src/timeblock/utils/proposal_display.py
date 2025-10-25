"""Helper para exibição de propostas de reordenamento."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from typing import Optional
from datetime import datetime

from src.timeblock.services.event_reordering_models import ReorderingProposal


def display_proposal(proposal: Optional[ReorderingProposal]) -> None:
    """Exibe proposta de reordenamento formatada."""
    if not proposal or not proposal.proposed_changes:
        return
    
    console = Console()
    console.print("\n[yellow]⚠ CONFLITO DE AGENDA DETECTADO[/yellow]\n")
    
    table = Table(title="Reordenamento Proposto")
    table.add_column("Evento", style="cyan")
    table.add_column("Horário Atual", style="white")
    table.add_column("Horário Proposto", style="green")
    table.add_column("Shift", style="yellow")
    
    for change in proposal.proposed_changes:
        shift_min = int((change.proposed_start - change.current_start).total_seconds() / 60)
        
        table.add_row(
            change.event_title,
            f"{_format_time(change.current_start)} → {_format_time(change.current_end)}",
            f"{_format_time(change.proposed_start)} → {_format_time(change.proposed_end)}",
            f"{shift_min:+d} min"
        )
    
    console.print(table)
    
    stats = Panel(
        f"[bold]Eventos afetados:[/bold] {len(proposal.proposed_changes)}\n"
        f"[bold]Shift total:[/bold] {proposal.estimated_duration_shift:+d} minutos",
        title="Resumo",
        border_style="blue"
    )
    console.print(stats)


def confirm_apply_proposal() -> bool:
    """Pergunta se usuário quer aplicar proposta."""
    return Confirm.ask(
        "\n[bold]Aplicar reordenamento?[/bold]",
        default=False
    )


def _format_time(dt: datetime) -> str:
    """Formata datetime para HH:MM."""
    return dt.strftime("%H:%M")
