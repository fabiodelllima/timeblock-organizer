"""Comandos de reordenamento de eventos."""
import typer
from rich.console import Console
from src.timeblock.services.event_reordering_service import EventReorderingService
from src.timeblock.utils.proposal_display import display_proposal, confirm_apply_proposal

app = typer.Typer(help="Comandos de reordenamento")
console = Console()


@app.callback(invoke_without_command=True)
def reschedule(
    ctx: typer.Context,
    event_id: int = typer.Argument(None, help="ID do evento"),
    event_type: str = typer.Option("task", help="Tipo: task, habit_instance, event"),
    auto_approve: bool = typer.Option(False, "--auto-approve", "-y", help="Aplicar sem confirmação"),
):
    """Detecta conflitos e reorganiza eventos."""
    # Se subcomando foi chamado, não executar
    if ctx.invoked_subcommand is not None:
        return
    
    if event_id is None:
        console.print("[red]Erro: event_id é obrigatório[/red]")
        raise typer.Exit(1)
    
    try:
        conflicts = EventReorderingService.detect_conflicts(event_id, event_type)
        
        if not conflicts:
            console.print("[green]✓[/green] Nenhum conflito detectado")
            return
        
        proposal = EventReorderingService.propose_reordering(conflicts)
        display_proposal(proposal, console)
        
        if auto_approve or confirm_apply_proposal():
            EventReorderingService.apply_reordering(proposal)
            console.print("\n[green]✓ Reordenamento aplicado![/green]\n")
        else:
            console.print("\n[yellow]Cancelado[/yellow]\n")
        
    except ValueError as e:
        console.print(f"[red]Erro:[/red] {e}")
        raise typer.Exit(1)


@app.command("preview")
def preview(
    event_id: int = typer.Argument(..., help="ID do evento"),
    event_type: str = typer.Option("task", help="Tipo: task, habit_instance, event")
):
    """Visualiza proposta sem aplicar."""
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
