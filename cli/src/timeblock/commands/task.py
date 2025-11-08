"""Comandos para gerenciar tarefas."""

from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.services.task_service import TaskService
from src.timeblock.utils.conflict_display import display_conflicts

app = typer.Typer(help="Gerenciar tarefas")
console = Console()


@app.command("create")
def create_task(
    title: str = typer.Option(..., "--title", "-t", help="Título da tarefa"),
    scheduled: str = typer.Option(..., "--datetime", "-D", help="Data/hora (YYYY-MM-DD HH:MM)"),
    description: str = typer.Option(None, "--desc", help="Descrição"),
    color: str = typer.Option(None, "--color", "-c", help="Cor"),
):
    """Cria uma nova tarefa."""
    try:
        scheduled_dt = datetime.fromisoformat(scheduled)
        task = TaskService.create_task(title, scheduled_dt, description, color)

        console.print("\n[green]✓ Tarefa criada com sucesso![/green]\n")
        console.print("═" * 40)
        console.print(f"ID: {task.id}")
        console.print(f"Título: [bold]{task.title}[/bold]")
        console.print(f"Programado: {task.scheduled_datetime.strftime('%d/%m/%Y às %H:%M')}")
        if task.description:
            console.print(f"Descrição: {task.description}")
        if task.color:
            console.print(f"Cor: {task.color}")
        console.print("═" * 40)
        console.print()

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_tasks(
    start: str = typer.Option(None, "--from", help="Data início (YYYY-MM-DD HH:MM)"),
    end: str = typer.Option(None, "--to", help="Data fim (YYYY-MM-DD HH:MM)"),
    pending: bool = typer.Option(False, "--pending", "-p", help="Apenas pendentes"),
):
    """Lista tarefas."""
    try:
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else None

        if pending:
            tasks = TaskService.list_pending_tasks()
            title = "Tarefas Pendentes"
        else:
            tasks = TaskService.list_tasks(start_dt, end_dt)
            if start_dt and end_dt:
                title = f"Tarefas ({start_dt.strftime('%d/%m/%Y')} a {end_dt.strftime('%d/%m/%Y')})"
            else:
                title = "Tarefas"

        if not tasks:
            console.print("[yellow]Nenhuma tarefa encontrada.[/yellow]")
            return

        table = Table(title=title)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Título", style="white")
        table.add_column("Programado", style="blue")
        table.add_column("Status", style="green")

        for t in tasks:
            status = "✓ Completa" if t.completed_datetime else "○ Pendente"
            table.add_row(
                str(t.id),
                t.title,
                t.scheduled_datetime.strftime("%d/%m/%Y %H:%M"),
                status,
            )

        console.print()
        console.print(table)
        console.print()

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("check")
def check_task(task_id: int = typer.Argument(..., help="ID da tarefa")):
    """Marca tarefa como completa."""
    try:
        task = TaskService.complete_task(task_id)

        scheduled = task.scheduled_datetime
        completed = task.completed_datetime
        diff = completed - scheduled
        diff_minutes = int(diff.total_seconds() / 60)

        console.print("\n[green]✓ Tarefa concluída![/green]\n")
        console.print(f"[bold]{task.title}[/bold] (ID: {task.id})")
        console.print(f"Programado: {scheduled.strftime('%d/%m/%Y às %H:%M')}")
        console.print(f"Concluído: {completed.strftime('%d/%m/%Y às %H:%M')}")

        if diff_minutes > 0:
            console.print(f"Status: [yellow]{diff_minutes}min de atraso[/yellow]")
        elif diff_minutes < 0:
            console.print(f"Status: [green]{abs(diff_minutes)}min de antecipação[/green]")
        else:
            console.print("Status: [green]No horário![/green]")
        console.print()

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("update")
def update_task(
    task_id: int = typer.Argument(..., help="ID da tarefa"),
    title: str = typer.Option(None, "--title", "-t", help="Novo título"),
    scheduled: str = typer.Option(None, "--datetime", "-D", help="Nova data/hora (YYYY-MM-DD HH:MM)"),
    description: str = typer.Option(None, "--desc", help="Nova descrição"),
):
    """Atualiza uma tarefa."""
    try:
        # Parse scheduled datetime if provided
        scheduled_dt = datetime.fromisoformat(scheduled) if scheduled else None

        # Update task and get conflicts
        task, conflicts = TaskService.update_task(
            task_id,
            title=title,
            scheduled_datetime=scheduled_dt,
            description=description,
        )

        # Display updated task info
        console.print("\n[green]✓ Tarefa atualizada com sucesso![/green]\n")
        console.print("═" * 40)
        console.print(f"ID: {task.id}")
        console.print(f"Título: [bold]{task.title}[/bold]")
        console.print(f"Programado: {task.scheduled_datetime.strftime('%d/%m/%Y às %H:%M')}")
        if task.description:
            console.print(f"Descrição: {task.description}")
        console.print("═" * 40)
        console.print()

        # Display conflicts if any
        if conflicts:
            console.print("[yellow]⚠ Atenção: A atualização resultou em conflitos:[/yellow]")
            display_conflicts(conflicts, console)

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_task(
    task_id: int = typer.Argument(..., help="ID da tarefa"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta uma tarefa."""
    try:
        task = TaskService.get_task(task_id)

        if not force:
            console.print(f"\nDeletar tarefa: [bold]{task.title}[/bold] (ID: {task_id})?")
            if not typer.confirm("Confirma?", default=False):
                console.print("[yellow]Cancelado.[/yellow]")
                return

        TaskService.delete_task(task_id)
        console.print(
            f"[green]✓ Tarefa deletada: [bold]{task.title}[/bold] (ID: {task_id})[/green]"
        )

    except ValueError as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)
