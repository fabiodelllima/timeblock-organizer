"""Step definitions para BR-CLI-HABIT-SKIP-001 (Comando CLI habit skip)."""

from __future__ import annotations

import shlex
from contextlib import contextmanager
from datetime import date, time
from typing import TYPE_CHECKING

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session
from typer.testing import CliRunner

from src.timeblock.commands import habit
from src.timeblock.main import app
from src.timeblock.models.enums import Status
from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance
from src.timeblock.models.routine import Routine

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
    def mock_get_engine_context():  # type: ignore[no-untyped-def]
        yield test_engine

    monkeypatch.setattr(habit, "get_engine_context", mock_get_engine_context)


@given('que existe uma rotina ativa "Rotina Matinal"', target_fixture="test_routine_cli")
def criar_rotina_cli(session: Session) -> Routine:
    routine = Routine(name="Rotina Matinal", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@given(parsers.parse('existe um habit "{habit_name}" com ID 1'), target_fixture="test_habit_cli")
def criar_habit_cli(session: Session, test_routine_cli: Routine, habit_name: str) -> Habit:
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


@given("existe uma HabitInstance com ID 42 para hoje", target_fixture="test_instance_cli")
def criar_instance_cli(session: Session, test_habit_cli: Habit) -> HabitInstance:
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


@when(parsers.parse('usuário executa comando "{command}"'))
def executar_comando(cli_runner: CliRunner, command: str, session: Session) -> None:
    result = cli_runner.invoke(app, shlex.split(command))
    session.info = {"cli_result": result, "exit_code": result.exit_code, "output": result.stdout}  # type: ignore[attr-defined]


@then("comando deve ter sucesso")
def verificar_sucesso(session: Session) -> None:
    info = getattr(session, "info", {})
    result = info.get("cli_result")
    assert result is not None
    assert result.exit_code == 0, f"Comando falhou: {result.stdout}"


@then("comando deve falhar")
def verificar_falha(session: Session) -> None:
    info = getattr(session, "info", {})
    result = info.get("cli_result")
    assert result is not None
    assert result.exit_code != 0


@then(parsers.parse('output deve conter "{text}"'))
def verificar_output_contem(session: Session, text: str) -> None:
    info = getattr(session, "info", {})
    output = info.get("output", "")
    assert text.lower() in output.lower(), f"'{text}' não encontrado em: {output}"


@then(parsers.parse("HabitInstance {instance_id:d} deve ter status {status_name}"))
def verificar_status_cli(session: Session, instance_id: int, status_name: str) -> None:
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.status.name == status_name


@then(parsers.parse("HabitInstance {instance_id:d} deve ter skip_reason {reason_name}"))
def verificar_skip_reason_cli(session: Session, instance_id: int, reason_name: str) -> None:
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_reason is not None
    assert instance.skip_reason.name == reason_name


@then(parsers.parse('HabitInstance {instance_id:d} deve ter skip_note "{note}"'))
def verificar_skip_note_cli(session: Session, instance_id: int, note: str) -> None:
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_note == note


@then(parsers.parse("HabitInstance {instance_id:d} deve ter skip_note NULL"))
def verificar_skip_note_null_cli(session: Session, instance_id: int) -> None:
    session.expire_all()
    instance = session.get(HabitInstance, instance_id)
    assert instance is not None
    assert instance.skip_note is None
