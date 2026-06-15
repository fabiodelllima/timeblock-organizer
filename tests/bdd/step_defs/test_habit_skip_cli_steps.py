"""Step definitions para BR-CLI-HABIT-SKIP-001 (Comando CLI habit skip).

Conecta cenários Gherkin do arquivo habit_skip_cli.feature com código Python.
"""

from __future__ import annotations

import shlex
from contextlib import contextmanager
from datetime import date, time
from typing import TYPE_CHECKING

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session
from typer.testing import CliRunner

from timeblock.commands.habit import actions
from timeblock.main import app
from timeblock.models.enums import Status
from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.routine import Routine

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from sqlalchemy.engine import Engine

scenarios("../features/habit_skip_cli.feature")


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_engine_context(test_engine: Engine, monkeypatch: MonkeyPatch) -> None:
    @contextmanager
    def mock_get_engine_context():
        yield test_engine

    monkeypatch.setattr(actions, "get_engine_context", mock_get_engine_context)


@given('an active routine "Rotina Matinal" exists', target_fixture="test_routine_cli")
def criar_rotina_cli(session: Session) -> Routine:
    """Cria rotina ativa para testes."""
    routine = Routine(name="Rotina Matinal", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@given(
    parsers.parse('a habit "{habit_name}" with ID 1 exists'),
    target_fixture="test_habit_cli",
)
def criar_habit_cli(session: Session, test_routine_cli: Routine, habit_name: str) -> Habit:
    """Cria habit na rotina."""
    assert test_routine_cli.id is not None
    habit_obj = Habit(
        routine_id=test_routine_cli.id,
        title=habit_name,
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit_obj)
    session.commit()
    session.refresh(habit_obj)
    return habit_obj


@given(
    "a HabitInstance with ID 42 for today exists",
    target_fixture="test_instance_cli",
)
def criar_instance_cli(session: Session, test_habit_cli: Habit) -> HabitInstance:
    """Cria HabitInstance com ID 42 para hoje."""
    assert test_habit_cli.id is not None
    instance = HabitInstance(
        id=42,
        habit_id=test_habit_cli.id,
        date=date.today(),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


@when(parsers.parse('the user executes command "{command}"'))
def executar_comando(cli_runner: CliRunner, command: str, session: Session) -> None:
    """Executa comando CLI."""
    result = cli_runner.invoke(app, shlex.split(command))
    session.info = {
        "cli_result": result,
        "exit_code": result.exit_code,
        "output": result.stdout,
    }


@then("the command should succeed")
def verificar_sucesso(session: Session) -> None:
    """Verifica que comando teve sucesso."""
    info = getattr(session, "info", {})
    result = info.get("cli_result")
    assert result is not None
    assert result.exit_code == 0, f"Comando falhou: {result.stdout}"


@then("the command should fail")
def verificar_falha(session: Session) -> None:
    """Verifica que comando falhou."""
    info = getattr(session, "info", {})
    result = info.get("cli_result")
    assert result is not None
    assert result.exit_code != 0


@then(parsers.parse('the output should contain "{text}"'))
def verificar_output_contem(session: Session, text: str) -> None:
    """Verifica que output contém texto."""
    info = getattr(session, "info", {})
    output = info.get("output", "")
    assert text.lower() in output.lower(), f"'{text}' não encontrado em: {output}"


@then(parsers.parse("HabitInstance {instance_id:d} should have status {status_name}"))
def verificar_status_cli(session: Session, instance_id: int, status_name: str) -> None:
    """Verifica status da instância."""
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.status.name == status_name


@then(parsers.parse("HabitInstance {instance_id:d} should have skip_reason {reason_name}"))
def verificar_skip_reason_cli(session: Session, instance_id: int, reason_name: str) -> None:
    """Verifica skip_reason da instância."""
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_reason is not None
    assert instance.skip_reason.name == reason_name


@then(parsers.parse('HabitInstance {instance_id:d} should have skip_note "{note}"'))
def verificar_skip_note_cli(session: Session, instance_id: int, note: str) -> None:
    """Verifica skip_note da instância."""
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_note == note


@then(parsers.parse("HabitInstance {instance_id:d} should have skip_note NULL"))
def verificar_skip_note_null_cli(session: Session, instance_id: int) -> None:
    """Verifica que skip_note é None."""
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_note is None


@then(parsers.parse("HabitInstance {instance_id:d} should have substatus {substatus_name}"))
def verificar_substatus_cli(session: Session, instance_id: int, substatus_name: str) -> None:
    """Verifica not_done_substatus da instância."""
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.not_done_substatus is not None
    assert instance.not_done_substatus.name == substatus_name


@then(parsers.parse("HabitInstance {instance_id:d} should have skip_reason NULL"))
def verificar_skip_reason_null_cli(session: Session, instance_id: int) -> None:
    """Verifica que skip_reason é None."""
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_reason is None
