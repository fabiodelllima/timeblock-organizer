"""Comandos para gerar relatórios."""

from datetime import date, timedelta

import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.task_service import TaskService
from src.timeblock.services.timer_service import TimerService

app = typer.Typer(help="Gerar relatórios e análises")
console = Console()


@app.command("daily")
def daily_report(
    date_filter: str = typer.Option(None, "--date", "-d", help="Data (YYYY-MM-DD, padrão: hoje)"),
):
    """Relatório de produtividade do dia."""
    try:
        target_date = date.fromisoformat(date_filter) if date_filter else date.today()

        instances = HabitInstanceService.list_instances(date=target_date)
        tasks = TaskService.list_tasks(
            start_datetime=target_date, end_datetime=target_date + timedelta(days=1)
        )

        habits_completed = sum(1 for i in instances if i.actual_end)
        habits_total = len(instances)
        tasks_completed = sum(1 for t in tasks if t.completed_datetime)
        tasks_total = len(tasks)

        timelogs = TimerService.get_timelogs_by_date(target_date)
        total_tracked = sum(
            (log.end_time - log.start_time).total_seconds() for log in timelogs if log.end_time
        )
        hours = int(total_tracked // 3600)
        minutes = int((total_tracked % 3600) // 60)

        console.print(f"\n[bold]Relatório Diário - {target_date.strftime('%d/%m/%Y')}[/bold]\n")
        console.print("═" * 50)
        console.print(f"Tempo trackado: {hours}h {minutes}min")
        console.print(
            f"Hábitos: {habits_completed}/{habits_total} completos ({habits_completed / habits_total * 100:.0f}%)"
            if habits_total > 0
            else "Hábitos: 0/0"
        )
        console.print(
            f"Tarefas: {tasks_completed}/{tasks_total} completas ({tasks_completed / tasks_total * 100:.0f}%)"
            if tasks_total > 0
            else "Tarefas: 0/0"
        )
        console.print("═" * 50)

        if instances:
            console.print("\n[bold]Hábitos:[/bold]")
            for inst in instances:
                habit = HabitService.get_habit(inst.habit_id)
                status = "✓" if inst.actual_end else "○"
                console.print(
                    f"{status} {habit.title} ({inst.scheduled_start.strftime('%H:%M')} → {inst.scheduled_end.strftime('%H:%M')})"
                )

        if tasks:
            console.print("\n[bold]Tarefas:[/bold]")
            for task in tasks:
                status = "✓" if task.completed_datetime else "○"
                console.print(
                    f"{status} {task.title} ({task.scheduled_datetime.strftime('%H:%M')})"
                )

        console.print()

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("weekly")
def weekly_report(
    week_offset: int = typer.Option(0, "--week", "-w", help="Semana (0=atual, -1=anterior)"),
):
    """Relatório semanal de produtividade."""
    try:
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)

        console.print("\n[bold]Relatório Semanal[/bold]")
        console.print(
            f"{start_of_week.strftime('%d/%m/%Y')} a {end_of_week.strftime('%d/%m/%Y')}\n"
        )

        table = Table(title="Resumo Diário")
        table.add_column("Dia", style="cyan")
        table.add_column("Hábitos", style="green")
        table.add_column("Tarefas", style="blue")
        table.add_column("Tempo", style="yellow")

        week_habits_completed = 0
        week_habits_total = 0
        week_tasks_completed = 0
        week_tasks_total = 0
        week_time_tracked = 0

        for i in range(7):
            day = start_of_week + timedelta(days=i)

            instances = HabitInstanceService.list_instances(date=day)
            tasks = TaskService.list_tasks(start_datetime=day, end_datetime=day + timedelta(days=1))
            timelogs = TimerService.get_timelogs_by_date(day)

            habits_completed = sum(1 for i in instances if i.actual_end)
            habits_total = len(instances)
            tasks_completed = sum(1 for t in tasks if t.completed_datetime)
            tasks_total = len(tasks)

            day_tracked = sum(
                (log.end_time - log.start_time).total_seconds() for log in timelogs if log.end_time
            )

            week_habits_completed += habits_completed
            week_habits_total += habits_total
            week_tasks_completed += tasks_completed
            week_tasks_total += tasks_total
            week_time_tracked += day_tracked

            hours = int(day_tracked // 3600)
            minutes = int((day_tracked % 3600) // 60)

            table.add_row(
                day.strftime("%d/%m (%a)"),
                f"{habits_completed}/{habits_total}",
                f"{tasks_completed}/{tasks_total}",
                f"{hours}h{minutes:02d}m",
            )

        console.print(table)

        total_hours = int(week_time_tracked // 3600)
        total_minutes = int((week_time_tracked % 3600) // 60)

        console.print("\n[bold]Totais da Semana:[/bold]")
        console.print("═" * 50)
        console.print(f"Tempo trackado: {total_hours}h {total_minutes}min")
        console.print(
            f"Hábitos: {week_habits_completed}/{week_habits_total} ({week_habits_completed / week_habits_total * 100:.0f}%)"
            if week_habits_total > 0
            else "Hábitos: 0/0"
        )
        console.print(
            f"Tarefas: {week_tasks_completed}/{week_tasks_total} ({week_tasks_completed / week_tasks_total * 100:.0f}%)"
            if week_tasks_total > 0
            else "Tarefas: 0/0"
        )
        console.print("═" * 50)
        console.print()

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("habit")
def habit_report(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    days: int = typer.Option(30, "--days", "-d", help="Período em dias"),
):
    """Taxa de conclusão de um hábito."""
    try:
        habit = HabitService.get_habit(habit_id)

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        instances = HabitInstanceService.list_instances(
            habit_id=habit_id, start_date=start_date, end_date=end_date
        )

        if not instances:
            console.print(
                f"Nenhuma instância encontrada para [bold]{habit.title}[/bold] nos últimos {days} dias",
                style="yellow",
            )
            return

        completed = sum(1 for i in instances if i.actual_end)
        total = len(instances)
        completion_rate = (completed / total * 100) if total > 0 else 0

        current_streak = 0
        for inst in reversed(instances):
            if inst.actual_end:
                current_streak += 1
            else:
                break

        console.print(f"\n[bold]Relatório do Hábito:[/bold] {habit.title}\n")
        console.print("═" * 50)
        console.print(
            f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        )
        console.print(f"Total de ocorrências: {total}")
        console.print(f"Concluídas: {completed}")
        console.print(f"Taxa de conclusão: {completion_rate:.1f}%")
        console.print(f"Sequência atual: {current_streak} dia{'s' if current_streak != 1 else ''}")
        console.print("═" * 50)

        console.print("\n[bold]Últimos 7 dias:[/bold]")
        recent = instances[-7:] if len(instances) >= 7 else instances
        for inst in recent:
            status = "✓" if inst.actual_end else "✗"
            console.print(
                f"{status} {inst.date.strftime('%d/%m/%Y')} - {inst.scheduled_start.strftime('%H:%M')} → {inst.scheduled_end.strftime('%H:%M')}"
            )

        console.print()

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("schedule")
def schedule_report(
    weeks: int = typer.Option(1, "--weeks", "-w", help="Número de semanas"),
):
    """Agenda das próximas semanas."""
    try:
        start_date = date.today()
        end_date = start_date + timedelta(weeks=weeks)

        console.print("\n[bold]Agenda[/bold]")
        console.print(f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}\n")

        current = start_date
        while current <= end_date:
            instances = HabitInstanceService.list_instances(date=current)
            tasks = TaskService.list_tasks(
                start_datetime=current, end_datetime=current + timedelta(days=1)
            )

            if instances or tasks:
                console.print(f"\n[bold]{current.strftime('%d/%m/%Y (%A)')}[/bold]")

                for inst in instances:
                    habit = HabitService.get_habit(inst.habit_id)
                    console.print(
                        f"  {inst.scheduled_start.strftime('%H:%M')} → {inst.scheduled_end.strftime('%H:%M')} | {habit.title}"
                    )

                for task in tasks:
                    console.print(
                        f"  {task.scheduled_datetime.strftime('%H:%M')} | {task.title} (tarefa)"
                    )

            current += timedelta(days=1)

        console.print()

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
