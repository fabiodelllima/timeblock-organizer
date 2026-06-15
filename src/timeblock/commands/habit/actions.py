"""Ações pontuais para hábitos (adjust, skip)."""

from datetime import time as dt_time

import typer
from rich.console import Console
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.models.enums import SkipReason
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.utils.conflict_display import display_conflicts
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)

console = Console()


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

        console.print(f"[green]Instância {instance_id} ajustada: {new_start} - {new_end}[/green]")

        if conflicts:
            console.print("\n[yellow]Atenção: O ajuste resultou em conflitos:[/yellow]")
            display_conflicts(conflicts, console)

    except ValueError as e:
        logger.warning("Erro de validação: %s", e)
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def skip_instance(
    instance_id: int = typer.Argument(..., help="ID da instância do hábito"),
    reason: str = typer.Option(
        None,
        "--reason",
        "-r",
        help="Razão do skip (HEALTH|WORK|FAMILY|TRAVEL|WEATHER|LACK_RESOURCES|EMERGENCY|OTHER)",
    ),
    unjustified: bool = typer.Option(
        False,
        "--unjustified",
        "-u",
        help="Marca skip sem justificativa",
    ),
    note: str = typer.Option(None, "--note", "-n", help="Nota opcional (máx 500 chars)"),
):
    """
    Marca instância de hábito como skipped (pulada).

    Exemplos:
        timeblock habit skip 42 --reason WORK --note "Reunião urgente"
        timeblock habit skip 42 --unjustified
    """
    try:
        if reason is not None and unjustified:
            console.print("[red]--reason e --unjustified são mutuamente exclusivos[/red]")
            raise typer.Exit(1)

        if reason is None and not unjustified:
            console.print("[red]Informe uma razão com --reason ou use --unjustified[/red]")
            console.print("\nRazões válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        skip_reason: SkipReason | None
        if unjustified:
            skip_reason = None
        else:
            try:
                skip_reason = SkipReason[reason.upper()]
            except KeyError:
                logger.warning("Razão inválida fornecida")
                console.print(f"[red]Razão inválida: {reason}[/red]")
                console.print("\nRazões válidas:")
                console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
                console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
                raise typer.Exit(1)

        if note and len(note) > 500:
            console.print("[red]Nota muito longa (máximo 500 caracteres)[/red]")
            raise typer.Exit(1)

        with get_engine_context() as engine, Session(engine) as session:
            service = HabitInstanceService()
            service.skip_habit_instance(
                habit_instance_id=instance_id,
                skip_reason=skip_reason,
                skip_note=note,
                session=session,
            )

            console.print("[green]Hábito marcado como skipped[/green]")
            if skip_reason is None:
                console.print("  Razão: sem justificativa")
            else:
                reason_pt = {
                    "health": "Saúde",
                    "work": "Trabalho",
                    "family": "Família",
                    "travel": "Viagem",
                    "weather": "Clima",
                    "lack_resources": "Falta de recursos",
                    "emergency": "Emergência",
                    "other": "Outro",
                }
                console.print(f"  Razão: {reason_pt.get(skip_reason.value, skip_reason.value)}")
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
