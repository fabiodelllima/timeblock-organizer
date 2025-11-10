"""Comandos para gerenciar agenda de hábitos."""

import json
from datetime import date
from datetime import time as dt_time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.services.event_reordering_service import EventReorderingService
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.utils.proposal_display import confirm_apply_proposal, display_proposal

app = typer.Typer(help="Gerenciar agenda de hábitos")
console = Console()


@app.command("generate")
def generate_instances(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    start: str = typer.Option(..., "--from", help="Data início (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--to", help="Data fim (YYYY-MM-DD)"),
):
    """Gera instâncias de um hábito para período."""
    try:
        habit = HabitService.get_habit(habit_id)
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)

        instances = HabitInstanceService.generate_instances(habit_id, start_date, end_date)

        console.print(
            f"\n[OK] {len(instances)} hábitos gerados para [bold]{habit.title}[/bold]", style="green"
        )
        console.print(
            f"  Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}\n"
        )

    except ValueError as e:
        console.print(f"[X] Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_instances(
    date_filter: str = typer.Option(None, "--date", "-d", help="Filtrar por data (YYYY-MM-DD)"),
    habit_id: int = typer.Option(None, "--habit", "-h", help="Filtrar por hábito"),
):
    """Lista instâncias agendadas."""
    try:
        date_obj = date.fromisoformat(date_filter) if date_filter else None
        instances = HabitInstanceService.list_instances(date=date_obj, habit_id=habit_id)

        if not instances:
            console.print("Nenhum hábito agendado encontrado.", style="yellow")
            return

        # Título da tabela
        if date_filter and habit_id:
            habit = HabitService.get_habit(habit_id)
            title = f"Agenda - {habit.title} em {date_obj.strftime('%d/%m/%Y')}"
        elif date_filter:
            title = f"Agenda - {date_obj.strftime('%d/%m/%Y')}"
        elif habit_id:
            habit = HabitService.get_habit(habit_id)
            title = f"Agenda - {habit.title}"
        else:
            title = "Agenda"

        table = Table(title=title)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Hábito", style="white")
        table.add_column("Data", style="magenta")
        table.add_column("Horário", style="blue")
        table.add_column("Ajustado", style="yellow")

        for inst in instances:
            habit = HabitService.get_habit(inst.habit_id)
            adjusted = "[OK]" if inst.manually_adjusted else "—"
            table.add_row(
                str(inst.id),
                habit.title,
                inst.date.strftime("%d/%m/%Y"),
                f"{inst.scheduled_start.strftime('%H:%M')} → {inst.scheduled_end.strftime('%H:%M')}",
                adjusted,
            )

        console.print()
        console.print(table)
        console.print()

    except ValueError as e:
        console.print(f"[X] Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("edit")
def edit_instance(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(..., "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Nova hora fim (HH:MM)"),
):
    """Edita horário de uma instância agendada."""
    try:
        # Buscar instância original
        instance_old = HabitInstanceService.get_instance(instance_id)
        habit = HabitService.get_habit(instance_old.habit_id)

        start_time = dt_time.fromisoformat(start)
        end_time = dt_time.fromisoformat(end)

        # Adjust instance time and get reordering proposal
        instance, proposal = HabitInstanceService.adjust_instance_time(
            instance_id, start_time, end_time
        )

        # Display reordering proposal if conflicts detected
        if proposal:
            display_proposal(proposal)

            if confirm_apply_proposal():
                EventReorderingService.apply_reordering(proposal)
                console.print("\n[OK] Reordenamento aplicado com sucesso!\n", style="bold green")
            else:
                console.print("\n[!] Reordenamento cancelado. Horário ajustado mas agenda não foi reorganizada.\n", style="yellow")

        # Output detalhado
        console.print("\n[OK] Agenda editada com sucesso!\n", style="bold green")
        console.print(f"[bold]{habit.title}[/bold] em {instance.date.strftime('%d/%m/%Y')}")
        console.print(
            f"Horário: {instance.scheduled_start.strftime('%H:%M')} → {instance.scheduled_end.strftime('%H:%M')}"
        )
        console.print(
            f"(alterado de {instance_old.scheduled_start.strftime('%H:%M')} → {instance_old.scheduled_end.strftime('%H:%M')})\n"
        )

    except ValueError as e:
        console.print(f"[X] Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("select")
def select_instance(instance_id: int = typer.Argument(..., help="ID da instância")):
    """Seleciona instância para uso posterior (timer)."""
    try:
        instance = HabitInstanceService.get_instance(instance_id)
        habit = HabitService.get_habit(instance.habit_id)

        # Salvar contexto em arquivo temporário
        config = {"selected_schedule": instance_id}
        config_path = Path.home() / ".timeblock_context"
        config_path.write_text(json.dumps(config))

        # Output
        console.print(f"\n[OK] Selecionado: [bold]{habit.title}[/bold]", style="green")
        console.print(f"  Data: {instance.date.strftime('%d/%m/%Y')}")
        console.print(
            f"  Horário: {instance.scheduled_start.strftime('%H:%M')} → {instance.scheduled_end.strftime('%H:%M')}\n"
        )
        console.print("Use 'timeblock timer start' para iniciar timer", style="dim")

    except ValueError as e:
        console.print(f"[X] Erro: {e}", style="red")
        raise typer.Exit(1)
