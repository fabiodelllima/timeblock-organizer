"""Comandos para gerenciar instâncias de hábitos."""

from datetime import date
from datetime import time as dt_time

import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.services.habit_instance_service import HabitInstanceService

app = typer.Typer(help="Gerenciar instâncias de hábitos")
console = Console()


@app.command("generate")
def generate_instances(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    start: str = typer.Option(..., "--from", help="Data início (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--to", help="Data fim (YYYY-MM-DD)"),
):
    """Gera instâncias de um hábito para período."""
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)

        instances = HabitInstanceService.generate_instances(habit_id, start_date, end_date)

        console.print(f"✓ {len(instances)} instâncias geradas", style="green")
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_instances(
    date_filter: str = typer.Option(None, "--date", "-d", help="Filtrar por data (YYYY-MM-DD)"),
    habit_id: int = typer.Option(None, "--habit", "-h", help="Filtrar por hábito"),
):
    """Lista instâncias de hábitos."""
    try:
        date_obj = date.fromisoformat(date_filter) if date_filter else None
        instances = HabitInstanceService.list_instances(date=date_obj, habit_id=habit_id)

        if not instances:
            console.print("Nenhuma instância encontrada.", style="yellow")
            return

        table = Table(title="Instâncias")
        table.add_column("ID", style="cyan")
        table.add_column("Hábito ID", style="magenta")
        table.add_column("Data", style="white")
        table.add_column("Horário", style="blue")
        table.add_column("Ajustado", style="yellow")

        for inst in instances:
            adjusted = "✓" if inst.manually_adjusted else "✗"
            table.add_row(
                str(inst.id),
                str(inst.habit_id),
                inst.date.isoformat(),
                f"{inst.scheduled_start.strftime('%H:%M')} → {inst.scheduled_end.strftime('%H:%M')}",
                adjusted,
            )

        console.print(table)
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("adjust")
def adjust_instance(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(..., "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Nova hora fim (HH:MM)"),
):
    """Ajusta horário de uma instância."""
    try:
        start_time = dt_time.fromisoformat(start)
        end_time = dt_time.fromisoformat(end)

        instance = HabitInstanceService.adjust_instance_time(instance_id, start_time, end_time)
        console.print(f"✓ Instância {instance.id} ajustada", style="green")
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
