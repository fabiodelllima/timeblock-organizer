"""Entry point do TimeBlock Organizer CLI."""

import typer

from src.timeblock.commands import add, habit, init, report, routine, schedule, tag, task, timer
from src.timeblock.commands import list as list_cmd

app = typer.Typer(
    name="timeblock",
    help="TimeBlock Organizer - Gerenciador de tempo via CLI",
    add_completion=False,
)

# Comandos v1.0
app.command("init")(init.init)
app.command("add")(add.add)
app.command("list")(list_cmd.list_events)

# Comandos v2.0
app.add_typer(routine.app, name="routine")
app.add_typer(habit.app, name="habit")
app.add_typer(schedule.app, name="schedule")
app.add_typer(task.app, name="task")
app.add_typer(timer.app, name="timer")
app.add_typer(report.app, name="report")
app.add_typer(tag.app, name="tag")


@app.command()
def version():
    """Display version information."""
    typer.echo("TimeBlock v0.1.0")
    typer.echo("CLI para gerenciamento de tempo e hábitos")


if __name__ == "__main__":
    app()
