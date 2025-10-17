"""Comandos para gerenciar rotinas."""

import typer
from rich.console import Console

from src.timeblock.services.routine_service import RoutineService

app = typer.Typer(help="Gerenciar rotinas")
console = Console()


@app.command("create")
def create_routine(name: str = typer.Argument(..., help="Nome da rotina")):
    """Cria uma nova rotina."""
    try:
        routine = RoutineService.create_routine(name)
        console.print(
            f"✓ Rotina criada: [bold]{routine.name}[/bold] (ID: {routine.id})", style="green"
        )
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_routines(all: bool = typer.Option(False, "--all", help="Incluir inativas")):
    """Lista rotinas."""
    routines = RoutineService.list_routines(active_only=not all)

    if not routines:
        console.print("Nenhuma rotina encontrada.", style="yellow")
        return

    console.print(f"\n[bold]{'Todas as Rotinas' if all else 'Rotinas Ativas'}[/bold]\n")
    for r in routines:
        status = "✓" if r.is_active else "✗"
        console.print(f"{status} [bold]{r.name}[/bold] (ID: {r.id})")


@app.command("activate")
def activate_routine(routine_id: int = typer.Argument(..., help="ID da rotina")):
    """Ativa uma rotina."""
    try:
        RoutineService.activate_routine(routine_id)
        console.print(f"✓ Rotina {routine_id} ativada", style="green")
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("deactivate")
def deactivate_routine(routine_id: int = typer.Argument(..., help="ID da rotina")):
    """Desativa uma rotina."""
    try:
        RoutineService.deactivate_routine(routine_id)
        console.print(f"✓ Rotina {routine_id} desativada", style="green")
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("delete")
def delete_routine(
    routine_id: int = typer.Argument(..., help="ID da rotina"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta uma rotina."""
    if not force:
        confirm = typer.confirm(f"Deletar rotina {routine_id}?")
        if not confirm:
            console.print("Cancelado.", style="yellow")
            return

    try:
        RoutineService.delete_routine(routine_id)
        console.print(f"✓ Rotina {routine_id} deletada", style="green")
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
