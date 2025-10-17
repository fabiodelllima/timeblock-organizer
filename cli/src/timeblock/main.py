"""Entry point do TimeBlock Organizer CLI."""
import typer
from src.timeblock.commands import init, add, list as list_cmd
from src.timeblock.commands import routine, habit, schedule, task, timer, report

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

if __name__ == "__main__":
    app()
