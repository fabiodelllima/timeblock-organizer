"""Comandos para gerenciar hábitos."""

from datetime import date
from datetime import time as dt_time

import typer
from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from rich.console import Console
from sqlmodel import Session

from src.timeblock.database import get_engine_context
from src.timeblock.models import Recurrence
from src.timeblock.models.enums import SkipReason
from src.timeblock.models.habit_instance import HabitInstance
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.utils.conflict_display import display_conflicts

app = typer.Typer(help="Gerenciar hábitos")
console = Console()


@app.command("create")
def create_habit(
    title: str = typer.Option(..., "--title", "-t", help="Título do hábito"),
    start: str = typer.Option(..., "--start", "-s", help="Hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Hora fim (HH:MM)"),
    repeat: str = typer.Option(..., "--repeat", "-r", help="Padrão de repetição"),
    color: str = typer.Option(None, "--color", "-c", help="Cor do hábito"),
    routine: int = typer.Option(None, "--routine", help="ID da rotina (padrão: ativa)"),
    generate: int = typer.Option(None, "--generate", "-g", help="Gerar instâncias (meses)"),
):
    """Cria um novo hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            # DEBUG
            from sqlmodel import select

            all_inst = session.exec(select(HabitInstance)).all()
            console.print(f"[yellow][DEBUG] Instances: {[i.id for i in all_inst]}[/yellow]")
            routine_service = RoutineService(session)

            # Determinar rotina
            if routine is None:
                active_routine = routine_service.get_active_routine()
                if active_routine is None:
                    console.print(
                        "[red]✗ Nenhuma rotina ativa. Crie e ative uma rotina primeiro.[/red]"
                    )
                    raise typer.Exit(1)
                console.print(
                    f"Rotina ativa: [bold]{active_routine.name}[/bold] (ID: {active_routine.id})"
                )
                if not typer.confirm("Criar hábito nesta rotina?", default=True):
                    routine_id = typer.prompt("ID da rotina", type=int)
                else:
                    routine_id = active_routine.id
            else:
                routine_id = routine

            # Validar rotina existe
            routine_obj = routine_service.get_routine(routine_id)
            if routine_obj is None:
                console.print(f"[red]✗ Rotina {routine_id} não encontrada[/red]")
                raise typer.Exit(1)

            # Parse recurrence
            try:
                rec = Recurrence(repeat.upper())
            except ValueError:
                valid = ", ".join([r.value for r in Recurrence])
                console.print(f"[red]✗ Recorrência inválida. Use: {valid}[/red]")
                raise typer.Exit(1)

            # Parse times
            start_time = dt_time.fromisoformat(start)
            end_time = dt_time.fromisoformat(end)

            # Criar hábito
            habit = HabitService.create_habit(
                routine_id=routine_id,
                title=title,
                scheduled_start=start_time,
                scheduled_end=end_time,
                recurrence=rec,
                color=color,
            )

            console.print("\n[green]✓ Hábito criado com sucesso![/green]\n")
            console.print(f"ID: [cyan]{habit.id}[/cyan]")
            console.print(f"Título: [bold]{habit.title}[/bold]")
            console.print(
                f"Horário: {habit.scheduled_start.strftime('%H:%M')} - {habit.scheduled_end.strftime('%H:%M')}"
            )
            console.print(f"Recorrência: {habit.recurrence.value}")

            if generate:
                start_date = date.today()
                end_date = start_date + relativedelta(months=generate)

                instances = HabitInstanceService.generate_instances(
                    habit_id=habit.id,
                    start_date=start_date,
                    end_date=end_date,
                )
                console.print(f"\n[green]✓ {len(instances)} instâncias geradas[/green]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_habits(
    routine: str = typer.Option("active", "--routine", "-R", help="Filtrar: active, all ou ID"),
):
    """Lista hábitos."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)

            # Determinar rotina
            if routine == "active":
                active_routine = routine_service.get_active_routine()
                if active_routine is None:
                    console.print("[red]✗ Nenhuma rotina ativa[/red]")
                    raise typer.Exit(1)
                routine_id = active_routine.id
                title = f"Hábitos - {active_routine.name} (ativa)"
            elif routine == "all":
                routine_id = None
                title = "Todos os Hábitos"
            else:
                routine_id = int(routine)
                routine_obj = routine_service.get_routine(routine_id)
                if routine_obj is None:
                    console.print(f"[red]✗ Rotina {routine_id} não encontrada[/red]")
                    raise typer.Exit(1)
                title = f"Hábitos - {routine_obj.name}"

            # Buscar hábitos
            if routine_id:
                habits = HabitService.list_habits(routine_id)
            else:
                habits = HabitService.list_all_habits()

            if not habits:
                console.print("[yellow]Nenhum hábito encontrado.[/yellow]")
                return

            console.print(f"\n[bold]{title}[/bold]\n")
            for h in habits:
                rec = h.recurrence.value.replace("_", " ").title()
                console.print(
                    f"[cyan]{h.id}[/cyan] [bold]{h.title}[/bold] "
                    f"({rec} {h.scheduled_start.strftime('%H:%M')}-{h.scheduled_end.strftime('%H:%M')})"
                )
            console.print()

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("update")
def update_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    title: str = typer.Option(None, "--title", "-t", help="Novo título"),
    start: str = typer.Option(None, "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Nova hora fim (HH:MM)"),
    repeat: str = typer.Option(None, "--repeat", "-r", help="Novo padrão"),
    color: str = typer.Option(None, "--color", "-c", help="Nova cor"),
):
    """Atualiza um hábito."""
    try:
        habit = HabitService.get_habit(habit_id)
        if habit is None:
            console.print(f"[red]✗ Hábito {habit_id} não encontrado[/red]")
            raise typer.Exit(1)

        updates = {}
        if title:
            updates["title"] = title
        if start:
            updates["scheduled_start"] = dt_time.fromisoformat(start)
        if end:
            updates["scheduled_end"] = dt_time.fromisoformat(end)
        if repeat:
            try:
                updates["recurrence"] = Recurrence(repeat.upper())
            except ValueError:
                valid = ", ".join([r.value for r in Recurrence])
                console.print(f"[red]✗ Recorrência inválida. Use: {valid}[/red]")
                raise typer.Exit(1)
        if color:
            updates["color"] = color

        if not updates:
            console.print("[yellow]Nenhuma alteração especificada.[/yellow]")
            return

        HabitService.update_habit(habit_id, **updates)
        console.print(f"[green]✓ Hábito atualizado: [bold]{habit.title}[/bold][/green]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta um hábito."""
    try:
        habit = HabitService.get_habit(habit_id)
        if habit is None:
            console.print(f"[red]✗ Hábito {habit_id} não encontrado[/red]")
            raise typer.Exit(1)

        if not force:
            if not typer.confirm(f"Deletar hábito '{habit.title}'?", default=False):
                console.print("[yellow]Cancelado.[/yellow]")
                return

        HabitService.delete_habit(habit_id)
        console.print(f"[green]✓ Hábito deletado: [bold]{habit.title}[/bold][/green]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("adjust")
def adjust_instance(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(..., "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Nova hora fim (HH:MM)"),
):
    """
    Ajusta horário de instância específica de hábito.

    Este comando modifica apenas a instância especificada. O hábito na rotina
    e outras instâncias permanecem inalterados.
    """
    try:
        new_start = dt_time.fromisoformat(start)
        new_end = dt_time.fromisoformat(end)

        _instance, conflicts = HabitInstanceService.adjust_instance_time(
            instance_id, new_start, new_end
        )

        console.print(f"[green]✓ Instância {instance_id} ajustada: {new_start} - {new_end}[/green]")

        # Exibir conflitos se houver
        if conflicts:
            console.print("\n[yellow]⚠ Atenção: O ajuste resultou em conflitos:[/yellow]")
            display_conflicts(conflicts, console)

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("skip")
def skip_instance(
    instance_id: int = typer.Argument(..., help="ID da instância do hábito"),
    category: str = typer.Option(
        None,
        "--category",
        "-c",
        help="Categoria do skip (HEALTH|WORK|FAMILY|TRAVEL|WEATHER|LACK_RESOURCES|EMERGENCY|OTHER)",
    ),
    note: str = typer.Option(None, "--note", "-n", help="Nota opcional (máx 500 chars)"),
):
    """
    Marca instância de hábito como skipped (pulada) com categorização.

    Exemplos:
        timeblock habit skip 42 --category WORK --note "Reunião urgente"
        timeblock habit skip 42 --category HEALTH
    """
    try:
        # Validar categoria
        if category is None:
            console.print("[red]Categoria obrigatória. Use --category[/red]")
            console.print("\nCategorias válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        # Converter categoria string para enum
        try:
            skip_reason = SkipReason[category.upper()]
        except KeyError:
            console.print(f"[red]Categoria inválida: {category}[/red]")
            console.print("\nCategorias válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        # Validar tamanho da nota
        if note and len(note) > 500:
            console.print("[red]Nota muito longa (máximo 500 caracteres)[/red]")
            raise typer.Exit(1)

        # Executar skip
        with get_engine_context() as engine, Session(engine) as session:
            service = HabitInstanceService()
            service.skip_habit_instance(
                habit_instance_id=instance_id,
                skip_reason=skip_reason,
                skip_note=note,
                session=session,
            )

            # Mapear enum para português
            category_pt = {
                "health": "Saúde",
                "work": "Trabalho",
                "family": "Família",
                "travel": "Viagem",
                "weather": "Clima",
                "lack_resources": "Falta de recursos",
                "emergency": "Emergência",
                "other": "Outro",
            }

            console.print("[green]Hábito marcado como skipped[/green]")
            console.print(f"  Categoria: {category_pt.get(skip_reason.value, skip_reason.value)}")
            if note:
                console.print(f"  Nota: {note}")

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            console.print(f"[red]HabitInstance {instance_id} não encontrada[/red]")
            raise typer.Exit(2)
        elif "timer" in error_msg.lower():
            console.print("[red]Pare o timer antes de marcar skip[/red]")
            raise typer.Exit(1)
        elif "completed" in error_msg.lower():
            console.print("[red]Não é possível skip de instância completada[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)
