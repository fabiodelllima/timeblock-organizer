"""Comandos para gerenciar tarefas."""
from datetime import datetime
import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.services.task_service import TaskService

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
        
        # Output detalhado
        console.print(f"\n✓ Tarefa criada com sucesso!\n", style="bold green")
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
        console.print(f"✗ Erro: {e}", style="red")
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
            console.print("Nenhuma tarefa encontrada.", style="yellow")
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
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)



@app.command("start")
def start_task(task_id: int = typer.Argument(..., help="ID da tarefa")):
    """Marca tarefa como iniciada."""
    try:
        task = TaskService.get_task(task_id)
        
        if task.started_at:
            console.print(f"[yellow][!][/yellow] Tarefa já foi iniciada em {task.started_at.strftime('%d/%m/%Y às %H:%M')}")
            return
        
        # Marcar como iniciada
        task.started_at = datetime.now()
        TaskService.update_task(task_id, started_at=task.started_at)
        
        console.print(f"\n✓ Tarefa iniciada!\n", style="bold green")
        console.print(f"[bold]{task.title}[/bold] (ID: {task.id})")
        console.print(f"Início: {task.started_at.strftime('%d/%m/%Y às %H:%M')}\n")
        
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)

@app.command("check")
def check_task(task_id: int = typer.Argument(..., help="ID da tarefa")):
    """Marca tarefa como completa."""
    try:
        task = TaskService.complete_task(task_id)
        
        # Calcular diferença
        scheduled = task.scheduled_datetime
        completed = task.completed_datetime
        diff = completed - scheduled
        diff_minutes = int(diff.total_seconds() / 60)
        
        # Output detalhado
        console.print(f"\n✓ Tarefa concluída!\n", style="bold green")
        console.print(f"[bold]{task.title}[/bold] (ID: {task.id})")
        console.print(f"Programado: {scheduled.strftime('%d/%m/%Y às %H:%M')}")
        console.print(f"Concluído: {completed.strftime('%d/%m/%Y às %H:%M')}")
        
        if diff_minutes > 0:
            console.print(f"Status: [yellow]{diff_minutes}min de atraso[/yellow]")
        elif diff_minutes < 0:
            console.print(f"Status: [green]{abs(diff_minutes)}min de antecipação[/green]")
        else:
            console.print(f"Status: [green]No horário![/green]")
        console.print()
        
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
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
                console.print("Cancelado.", style="yellow")
                return
        
        TaskService.delete_task(task_id)
        console.print(f"✓ Tarefa deletada: [bold]{task.title}[/bold] (ID: {task_id})", style="green")
        
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
