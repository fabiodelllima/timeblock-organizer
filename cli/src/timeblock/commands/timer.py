"""Comandos para gerenciar timer de tracking."""

import json
import time
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.task_service import TaskService
from src.timeblock.services.timer_service import TimerService
from src.timeblock.utils.conflict_display import display_conflicts

app = typer.Typer(help="Gerenciar timer de tracking")
console = Console()


def _get_selected_schedule():
    """Recupera schedule selecionado do contexto."""
    config_path = Path.home() / ".timeblock_context"
    if not config_path.exists():
        return None
    try:
        config = json.loads(config_path.read_text())
        return config.get("selected_schedule")
    except Exception:
        return None


def _display_timer(timelog_id: int):
    """Mostra timer ativo com atualização em tempo real."""
    with Live(refresh_per_second=1, console=console) as live:
        while True:
            try:
                timelog = TimerService.get_timelog(timelog_id)

                if timelog.end_time:
                    break

                # Calcular tempo decorrido
                elapsed = datetime.now() - timelog.start_time
                total_seconds = int(elapsed.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                # Determinar atividade
                if timelog.habit_instance_id:
                    instance = HabitInstanceService.get_instance(timelog.habit_instance_id)
                    habit = HabitService.get_habit(instance.habit_id)
                    activity = f"{habit.title} ({instance.date.strftime('%d/%m/%Y')})"
                elif timelog.task_id:
                    task = TaskService.get_task(timelog.task_id)
                    activity = f"{task.title}"
                else:
                    activity = "Atividade"

                # Criar display
                text = Text()
                text.append("[>] ", style="bold cyan")
                text.append(f"{hours:02d}:{minutes:02d}:{seconds:02d}", style="bold cyan")
                text.append(" | ", style="dim")
                text.append(activity, style="bold white")
                text.append(" | ", style="dim")

                # Status
                if hasattr(timelog, "paused") and timelog.paused:
                    text.append("[||] Pausado", style="yellow")
                else:
                    text.append("[>] Em andamento", style="green")

                info = f"\n\nIniciado: {timelog.start_time.strftime('%H:%M')}\n"

                # Pausas (se houver)
                pause_count = 0  # Implementar lógica de pausas no service
                if pause_count > 0:
                    info += f"Pausas: {pause_count}\n"

                info += "\nComandos: [yellow]pause[/] | [green]stop[/] | [red]cancel[/]"

                panel = Panel(text.append(info), title="Timer Ativo", border_style="cyan")

                live.update(panel)
                time.sleep(1)

            except KeyboardInterrupt:
                console.print(
                    "\n\nTimer ainda ativo. Use 'timeblock timer stop' ou 'timer cancel'",
                    style="yellow",
                )
                return
            except Exception as e:
                console.print(f"\n[red]✗ Erro: {e}[/red]")
                return


@app.command("start")
def start_timer(
    schedule: int = typer.Option(None, "--schedule", "-s", help="ID da instância agendada"),
    task: int = typer.Option(None, "--task", "-t", help="ID da tarefa"),
):
    """
    Inicia timer (workflow A: direto ou B: via select).

    Se houver conflitos de horário, o timer será iniciado normalmente
    mas os conflitos serão exibidos para o usuário.
    """
    try:
        # Verificar se já existe timer ativo
        active = TimerService.get_active_timer()
        if active:
            console.print(
                "[red]✗ Já existe um timer ativo. Use 'timer stop' ou 'timer cancel' primeiro.[/red]"
            )
            raise typer.Exit(1)

        timelog = None
        conflicts = None

        # Workflow A: direto com flags
        if schedule or task:
            # Buscar detalhes
            if schedule:
                instance = HabitInstanceService.get_instance(schedule)
                habit = HabitService.get_habit(instance.habit_id)
                activity = f"{habit.title} ({instance.date.strftime('%d/%m/%Y')})"
            else:
                task_obj = TaskService.get_task(task)
                activity = task_obj.title

            # Confirmar
            if not typer.confirm(f"Iniciar timer para {activity}?", default=True):
                console.print("[yellow]Cancelado.[/yellow]")
                return

            # Iniciar
            if schedule:
                timelog, conflicts = TimerService.start_timer(habit_instance_id=schedule)
            else:
                timelog, conflicts = TimerService.start_timer(task_id=task)

        # Workflow B: via select
        else:
            selected = _get_selected_schedule()
            if not selected:
                console.print(
                    "[red]✗ Nenhuma instância selecionada. "
                    "Use 'timeblock schedule select <id>' ou '--schedule <id>'[/red]"
                )
                raise typer.Exit(1)

            instance = HabitInstanceService.get_instance(selected)
            habit = HabitService.get_habit(instance.habit_id)

            if not typer.confirm(f"Iniciar timer para {habit.title}?", default=True):
                console.print("[yellow]Cancelado.[/yellow]")
                return

            timelog, conflicts = TimerService.start_timer(habit_instance_id=selected)

        console.print(
            f"\n[green]✓ Timer iniciado às {timelog.start_time.strftime('%H:%M')}![/green]\n"
        )

        # Exibir conflitos se houver, mas não bloqueia
        if conflicts:
            console.print("[yellow]⚠ Atenção: Conflitos detectados no horário atual:[/yellow]")
            display_conflicts(conflicts, console)
            console.print(
                "[dim]Timer foi iniciado. Você pode ajustar eventos conflitantes depois.[/dim]\n"
            )

        # Display interativo
        _display_timer(timelog.id)

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("pause")
def pause_timer():
    """Pausa o timer ativo."""
    try:
        active = TimerService.get_active_timer()
        if not active:
            console.print("[red]✗ Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        TimerService.pause_timer(active.id)
        console.print("[yellow][||] Timer pausado[/yellow]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("resume")
def resume_timer():
    """Retoma timer pausado."""
    try:
        active = TimerService.get_active_timer()
        if not active:
            console.print("[red]✗ Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        TimerService.resume_timer(active.id)
        console.print("[green][>] Timer retomado[/green]")

        # Mostrar display novamente
        _display_timer(active.id)

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("stop")
def stop_timer():
    """Finaliza e salva o timer."""
    try:
        active = TimerService.get_active_timer()
        if not active:
            console.print("[red]✗ Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        # Parar timer
        timelog = TimerService.stop_timer(active.id)

        # Calcular duração
        duration = timelog.end_time - timelog.start_time
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Output
        console.print("\n[green]✓ Timer finalizado![/green]\n")
        console.print(f"Duração total: {hours}h {minutes}min {seconds}s")
        console.print(f"Início: {timelog.start_time.strftime('%H:%M')}")
        console.print(f"Fim: {timelog.end_time.strftime('%H:%M')}")
        console.print()

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("cancel")
def cancel_timer():
    """Cancela timer sem salvar."""
    try:
        active = TimerService.get_active_timer()
        if not active:
            console.print("[red]✗ Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        if not typer.confirm("Cancelar timer? (não será salvo)", default=False):
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        TimerService.cancel_timer(active.id)
        console.print("[yellow]✓ Timer cancelado (não salvo)[/yellow]")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def timer_status():
    """Mostra status do timer atual."""
    try:
        active = TimerService.get_active_timer()

        if not active:
            console.print("[yellow]Nenhum timer ativo[/yellow]")
            return

        # Calcular tempo decorrido
        elapsed = datetime.now() - active.start_time
        total_seconds = int(elapsed.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Determinar atividade
        if active.habit_instance_id:
            instance = HabitInstanceService.get_instance(active.habit_instance_id)
            habit = HabitService.get_habit(instance.habit_id)
            activity = f"{habit.title} ({instance.date.strftime('%d/%m/%Y')})"
        elif active.task_id:
            task = TaskService.get_task(active.task_id)
            activity = task.title
        else:
            activity = "Atividade"

        console.print(f"\n[bold]Timer Ativo:[/bold] {activity}")
        console.print(f"Tempo decorrido: {hours:02d}:{minutes:02d}:{seconds:02d}")
        console.print(f"Iniciado: {active.start_time.strftime('%H:%M')}\n")

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)
