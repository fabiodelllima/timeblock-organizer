"""Comandos para gerenciar hábitos."""

from datetime import time as dt_time, date
from dateutil.relativedelta import relativedelta

import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.models import Recurrence
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.services.habit_instance_service import HabitInstanceService

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
        # Determinar rotina
        if routine is None:
            active_routine = RoutineService.get_active_routine()
            if active_routine is None:
                console.print("✗ Nenhuma rotina ativa. Crie e ative uma rotina primeiro.", style="red")
                raise typer.Exit(1)
            
            console.print(f"Rotina ativa: [bold]{active_routine.name}[/bold] (ID: {active_routine.id})")
            if not typer.confirm("Criar hábito nesta rotina?", default=True):
                routine_id = typer.prompt("ID da rotina", type=int)
            else:
                routine_id = active_routine.id
        else:
            routine_id = routine
        
        # Parse times
        start_time = dt_time.fromisoformat(start)
        end_time = dt_time.fromisoformat(end)

        # Parse recurrence
        rec = Recurrence(repeat.lower())

        # Criar hábito
        habit = HabitService.create_habit(
            routine_id=routine_id,
            title=title,
            scheduled_start=start_time,
            scheduled_end=end_time,
            recurrence=rec,
            color=color,
        )

        # Output detalhado
        console.print(f"\n✓ Hábito criado com sucesso!\n", style="bold green")
        console.print("═" * 40)
        console.print(f"ID: {habit.id}")
        console.print(f"Título: [bold]{habit.title}[/bold]")
        console.print(f"Rotina: {RoutineService.get_routine(routine_id).name} (ID: {routine_id})")
        console.print(f"Horário: {habit.scheduled_start.strftime('%H:%M')} → {habit.scheduled_end.strftime('%H:%M')}")
        
        # Calcular duração
        duration = (dt_time.fromisoformat(end).hour * 60 + dt_time.fromisoformat(end).minute) - \
                   (dt_time.fromisoformat(start).hour * 60 + dt_time.fromisoformat(start).minute)
        hours = duration // 60
        minutes = duration % 60
        duration_str = f"{hours}h {minutes}min" if hours > 0 else f"{minutes}min"
        console.print(f"Duração: {duration_str}")
        
        rec_display = habit.recurrence.value.replace('_', ' ').title()
        console.print(f"Repetição: {rec_display}")
        if habit.color:
            console.print(f"Cor: {habit.color}")
        console.print("═" * 40)
        
        # Geração de instâncias
        instances_generated = False
        if generate is not None:
            months = generate
        else:
            if typer.confirm("\nGerar instâncias automaticamente?", default=True):
                months = typer.prompt("Por quantos meses?", type=int, default=3, 
                                     show_choices=False, 
                                     show_default=True)
            else:
                months = None
        
        if months:
            start_date = date.today()
            end_date = start_date + relativedelta(months=months)
            instances = HabitInstanceService.generate_instances(habit.id, start_date, end_date)
            console.print(f"\n✓ {len(instances)} instâncias geradas ({start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')})", style="green")
            instances_generated = True
        
        if not instances_generated:
            console.print("\nℹ️  Use 'timeblock schedule generate' para gerar instâncias depois", style="cyan")

    except (ValueError, KeyError) as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_habits(
    routine: str = typer.Option("active", "--routine", "-R", help="Filtrar: active, all ou ID")
):
    """Lista hábitos."""
    try:
        # Determinar rotina
        if routine == "active":
            active_routine = RoutineService.get_active_routine()
            if active_routine is None:
                console.print("✗ Nenhuma rotina ativa", style="red")
                raise typer.Exit(1)
            routine_id = active_routine.id
            title = f"Hábitos - {active_routine.name} (ativa)"
        elif routine == "all":
            routine_id = None
            title = "Todos os Hábitos"
        else:
            routine_id = int(routine)
            routine_obj = RoutineService.get_routine(routine_id)
            title = f"Hábitos - {routine_obj.name}"
        
        habits = HabitService.list_habits(routine_id)

        if not habits:
            console.print("Nenhum hábito encontrado.", style="yellow")
            return

        table = Table(title=title)
        table.add_column("ID", style="cyan", no_wrap=True)
        if routine == "all":
            table.add_column("Rotina", style="magenta")
        table.add_column("Título", style="white")
        table.add_column("Horário", style="blue")
        table.add_column("Repetição", style="green")
        table.add_column("Cor", style="yellow")

        for h in habits:
            rec_display = h.recurrence.value.replace('_', ' ').title()
            row = [
                str(h.id),
            ]
            if routine == "all":
                routine_name = RoutineService.get_routine(h.routine_id).name
                row.append(routine_name)
            
            row.extend([
                h.title,
                f"{h.scheduled_start.strftime('%H:%M')} → {h.scheduled_end.strftime('%H:%M')}",
                rec_display,
                h.color or "—",
            ])
            table.add_row(*row)

        console.print()
        console.print(table)
        console.print()
        
    except (ValueError, KeyError) as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("update")
def update_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    title: str = typer.Option(None, "--title", "-t", help="Novo título"),
    start: str = typer.Option(None, "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Nova hora fim (HH:MM)"),
    repeat: str = typer.Option(None, "--repeat", "-r", help="Nova repetição"),
    color: str = typer.Option(None, "--color", "-c", help="Nova cor"),
):
    """Atualiza um hábito."""
    try:
        # Buscar hábito atual
        habit_old = HabitService.get_habit(habit_id)
        
        updates = {}
        if title:
            updates["title"] = title
        if start:
            updates["scheduled_start"] = dt_time.fromisoformat(start)
        if end:
            updates["scheduled_end"] = dt_time.fromisoformat(end)
        if repeat:
            updates["recurrence"] = Recurrence(repeat.lower())
        if color:
            updates["color"] = color

        if not updates:
            console.print("Nenhuma atualização especificada.", style="yellow")
            return

        habit = HabitService.update_habit(habit_id, **updates)
        
        # Output detalhado
        console.print(f"\n✓ Hábito atualizado com sucesso!\n", style="bold green")
        console.print(f"[bold]{habit.title}[/bold] (ID: {habit.id})")
        
        if "scheduled_start" in updates or "scheduled_end" in updates:
            old_time = f"{habit_old.scheduled_start.strftime('%H:%M')} → {habit_old.scheduled_end.strftime('%H:%M')}"
            new_time = f"{habit.scheduled_start.strftime('%H:%M')} → {habit.scheduled_end.strftime('%H:%M')}"
            console.print(f"Horário: {new_time} (alterado de {old_time})")
        
        console.print(f"Rotina: {RoutineService.get_routine(habit.routine_id).name}")
        
    except (ValueError, KeyError) as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("delete")
def delete_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta um hábito."""
    try:
        habit = HabitService.get_habit(habit_id)
        
        if not force:
            console.print(f"\nDeletar hábito: [bold]{habit.title}[/bold] (ID: {habit_id})?")
            if not typer.confirm("Confirma?", default=False):
                console.print("Cancelado.", style="yellow")
                return

        HabitService.delete_habit(habit_id)
        console.print(f"✓ Hábito deletado: [bold]{habit.title}[/bold] (ID: {habit_id})", style="green")
        
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
