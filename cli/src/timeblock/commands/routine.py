"""Comandos para gerenciar rotinas."""

import typer
from rich.console import Console
from sqlmodel import Session

from src.timeblock.database import get_engine_context
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService

app = typer.Typer(help="Gerenciar rotinas")
console = Console()


@app.command("create")
def create_routine(name: str = typer.Argument(..., help="Nome da rotina")):
    """Cria uma nova rotina."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            service = RoutineService(session)
            routine = service.create_routine(name)
            session.commit()

            console.print("\n[green]✓ Rotina criada com sucesso![/green]\n")
            console.print(f"ID: {routine.id}")
            console.print(f"Nome: [bold]{routine.name}[/bold]")
            console.print(f"Status: {'Ativa' if routine.is_active else 'Inativa'}")

            if not routine.is_active and routine.id is not None:
                if typer.confirm("\nAtivar esta rotina agora?", default=True):
                    service.activate_routine(routine.id)
                    session.commit()
                    console.print("[green]✓ Rotina ativada[/green]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_routines(all: bool = typer.Option(False, "--all", help="Incluir inativas")):
    """Lista rotinas."""
    with get_engine_context() as engine, Session(engine) as session:
        service = RoutineService(session)
        routines = service.list_routines(active_only=not all)

        if not routines:
            console.print("[yellow]Nenhuma rotina encontrada.[/yellow]")
            return

        console.print(f"\n[bold]{'Todas as Rotinas' if all else 'Rotinas Ativas'}[/bold]\n")
        for r in routines:
            status = "[green]✓[/green]" if r.is_active else "[dim]✗[/dim]"
            active_tag = " [ATIVA]" if r.is_active else ""
            console.print(f"{status} [bold]{r.name}[/bold] (ID: {r.id}){active_tag}")
        console.print()


@app.command("activate")
def activate_routine(routine_id: int = typer.Argument(..., help="ID da rotina")):
    """Ativa uma rotina (desativa outras automaticamente)."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            service = RoutineService(session)
            routine = service.get_routine(routine_id)

            if routine is None:
                console.print(f"[red]✗ Erro: Rotina {routine_id} não encontrada[/red]")
                raise typer.Exit(1)

            if routine.is_active:
                console.print(f"[cyan]i[/cyan] [bold]{routine.name}[/bold] já está ativa")
                return

            current_active = service.get_active_routine()
            service.activate_routine(routine_id)
            session.commit()

            console.print(
                f"\n[green]✓ Rotina ativada: [bold]{routine.name}[/bold] (ID: {routine.id})[/green]"
            )

            if current_active:
                console.print(f"  [dim][bold]{current_active.name}[/bold] foi desativada[/dim]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("deactivate")
def deactivate_routine(routine_id: int = typer.Argument(..., help="ID da rotina")):
    """Desativa uma rotina."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            service = RoutineService(session)
            routine = service.get_routine(routine_id)

            if routine is None:
                console.print(f"[red]✗ Erro: Rotina {routine_id} não encontrada[/red]")
                raise typer.Exit(1)

            if not routine.is_active:
                console.print(f"[cyan]i[/cyan] [bold]{routine.name}[/bold] já está inativa")
                return

            service.deactivate_routine(routine_id)
            session.commit()
            console.print(
                f"[green]✓ Rotina desativada: [bold]{routine.name}[/bold] (ID: {routine.id})[/green]"
            )

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_routine(
    routine_id: int = typer.Argument(..., help="ID da rotina"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta uma rotina e todos os seus hábitos."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            habit_service = HabitService(session)

            routine = routine_service.get_routine(routine_id)

            if routine is None:
                console.print(f"[red]✗ Erro: Rotina {routine_id} não encontrada[/red]")
                raise typer.Exit(1)

            habits = habit_service.list_habits(routine_id)

            if habits and not force:
                console.print(
                    f"\n[red]! ATENÇÃO:[/red] Esta rotina contém {len(habits)} hábito(s):\n"
                )

                for i, h in enumerate(habits, 1):
                    rec_display = h.recurrence.value.replace("_", " ").title()
                    console.print(
                        f"{i}. [bold]{h.title}[/bold] ({rec_display} {h.scheduled_start.strftime('%H:%M')} -> {h.scheduled_end.strftime('%H:%M')})"
                    )

                console.print(
                    "\n[red]Todos os hábitos e suas instâncias agendadas serão deletados.[/red]\n"
                )

                if not typer.confirm("Confirma a exclusão?", default=False):
                    console.print("[yellow]Cancelado.[/yellow]")
                    return

            routine_service.delete_routine(routine_id)
            session.commit()

            console.print(
                f"\n[green]✓ Rotina deletada: [bold]{routine.name}[/bold] (ID: {routine.id})[/green]"
            )
            if habits:
                console.print(f"[green]✓ {len(habits)} hábito(s) deletado(s)[/green]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)
