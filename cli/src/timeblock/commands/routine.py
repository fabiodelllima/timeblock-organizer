"""Comandos para gerenciar rotinas."""

import typer
from rich.console import Console
from rich.panel import Panel

from src.timeblock.services.routine_service import RoutineService
from src.timeblock.services.habit_service import HabitService

app = typer.Typer(help="Gerenciar rotinas")
console = Console()


@app.command("create")
def create_routine(name: str = typer.Argument(..., help="Nome da rotina")):
    """Cria uma nova rotina."""
    try:
        routine = RoutineService.create_routine(name)
        
        # Output detalhado
        console.print(f"\n✓ Rotina criada com sucesso!\n", style="bold green")
        console.print(f"ID: {routine.id}")
        console.print(f"Nome: [bold]{routine.name}[/bold]")
        console.print(f"Status: {'Ativa' if routine.is_active else 'Inativa'}")
        
        # Perguntar se quer ativar
        if not routine.is_active:
            if typer.confirm("\nAtivar esta rotina agora?", default=True):
                RoutineService.activate_routine(routine.id)
                console.print("✓ Rotina ativada", style="green")
                
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
        active_tag = " [ATIVA]" if r.is_active else ""
        console.print(f"{status} [bold]{r.name}[/bold] (ID: {r.id}){active_tag}")
    console.print()


@app.command("activate")
def activate_routine(routine_id: int = typer.Argument(..., help="ID da rotina")):
    """Ativa uma rotina (desativa outras automaticamente)."""
    try:
        # Buscar rotina antes de ativar para mostrar nome
        routine = RoutineService.get_routine(routine_id)
        
        # Verificar se já está ativa
        if routine.is_active:
            console.print(f"ℹ️  [bold]{routine.name}[/bold] já está ativa", style="cyan")
            return
        
        # Buscar rotina ativa atual
        current_active = RoutineService.get_active_routine()
        
        # Ativar nova rotina
        RoutineService.activate_routine(routine_id)
        
        # Output detalhado
        console.print(f"\n✓ Rotina ativada: [bold]{routine.name}[/bold] (ID: {routine.id})", style="green")
        
        if current_active:
            console.print(f"  [bold]{current_active.name}[/bold] foi desativada", style="dim")
            
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("deactivate")
def deactivate_routine(routine_id: int = typer.Argument(..., help="ID da rotina")):
    """Desativa uma rotina."""
    try:
        routine = RoutineService.get_routine(routine_id)
        
        if not routine.is_active:
            console.print(f"ℹ️  [bold]{routine.name}[/bold] já está inativa", style="cyan")
            return
        
        RoutineService.deactivate_routine(routine_id)
        console.print(f"✓ Rotina desativada: [bold]{routine.name}[/bold] (ID: {routine.id})", style="green")
        
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("delete")
def delete_routine(
    routine_id: int = typer.Argument(..., help="ID da rotina"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta uma rotina e todos os seus hábitos."""
    try:
        routine = RoutineService.get_routine(routine_id)
        habits = HabitService.list_habits(routine_id)
        
        # Warning detalhado se houver hábitos
        if habits and not force:
            console.print(f"\n⚠️  [bold red]ATENÇÃO[/bold red]: Esta rotina contém {len(habits)} hábito(s):\n")
            
            for i, h in enumerate(habits, 1):
                rec_display = h.recurrence.value.replace('_', ' ').title()
                console.print(f"{i}. [bold]{h.title}[/bold] ({rec_display} {h.scheduled_start.strftime('%H:%M')} → {h.scheduled_end.strftime('%H:%M')})")
            
            console.print("\n[red]Todos os hábitos e suas instâncias agendadas serão deletados.[/red]\n")
            
            if not typer.confirm("Confirma a exclusão?", default=False):
                console.print("Cancelado.", style="yellow")
                return
        
        # Deletar
        RoutineService.delete_routine(routine_id)
        
        # Output detalhado
        console.print(f"\n✓ Rotina deletada: [bold]{routine.name}[/bold] (ID: {routine.id})", style="green")
        if habits:
            console.print(f"✓ {len(habits)} hábito(s) deletado(s)", style="green")
            
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
