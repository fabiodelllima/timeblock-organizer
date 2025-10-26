"""Comandos de reordenamento de eventos."""
import typer
from rich.console import Console
from rich.table import Table
from src.timeblock.services.event_reordering_service import EventReorderingService
from src.timeblock.utils.proposal_display import display_proposal

app = typer.Typer(help="Comandos de reordenamento")
console = Console()


@app.command("preview")
def preview(
    event_id: int = typer.Argument(..., help="ID do evento"),
    event_type: str = typer.Option("task", help="Tipo: task, habit_instance, event")
):
    """Visualiza proposta de reordenamento."""
    try:
        conflicts = EventReorderingService.detect_conflicts(event_id, event_type)
        
        if not conflicts:
            console.print("[green]✓[/green] Nenhum conflito detectado")
            return
        
        proposal = EventReorderingService.propose_reordering(conflicts)
        display_proposal(proposal, console)
        
    except ValueError as e:
        console.print(f"[red]Erro:[/red] {e}")
        raise typer.Exit(1)
