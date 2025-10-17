"""Entry point do TimeBlock Organizer CLI."""
import typer
from src.timeblock.commands import init, add, list as list_cmd
from src.timeblock.commands import routine

app = typer.Typer(
    name="timeblock",
    help="TimeBlock Organizer - Gerenciador de tempo via CLI",
    add_completion=False,
)

app.command("init")(init.init_db)
app.command("add")(add.add_event)
app.command("list")(list_cmd.list_events)
app.add_typer(routine.app, name="routine")


if __name__ == "__main__":
    app()
