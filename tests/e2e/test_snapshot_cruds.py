"""Snapshot tests para modais CRUD e estados resultantes do dashboard.

Cobre todos os CRUDs de cada panel: routines (via agenda), habits e tasks.
Captura o estado visual com o modal aberto e os estados resultantes
após operações CRUD (done, skipped, timer running).

Referências:
    - ADR-034: Dashboard-first CRUD
    - ADR-037: Padrão de keybindings da TUI
    - ADR-038: Dashboard Interaction Patterns
    - Sprint 5.5 Fase 5
"""

from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.database.engine import create_db_and_tables
from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Task
from timeblock.models.enums import (
    DoneSubstatus,
    NotDoneSubstatus,
    SkipReason,
    Status,
    TimerStatus,
)
from timeblock.models.time_log import TimeLog
from timeblock.tui.app import TimeBlockApp
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel

# Determinismo do snapshot do timer ativo (follow-up do #66): o loader
# calcula o elapsed como now() - start_time. Sob a fixture autouse com
# tick=True — necessaria para que os timers do dashboard (set_interval/
# set_timer) nao pendurem o asyncio —, now() avanca em tempo real e um
# render lento assa um segundo diferente do render rapido. Congelamos
# apenas o now() do loader, sem tocar em time.monotonic().
_TIMER_FIXED_NOW = datetime(2025, 6, 16, 9, 0, 0)


class _FixedNowDatetime(datetime):
    @classmethod
    def now(cls, tz=None):  # type: ignore[override]
        return _TIMER_FIXED_NOW


@pytest.fixture(autouse=True)
def _isolated_snapshot_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Banco temporário isolado para snapshots."""
    db_path = tmp_path / "snapshot_cruds.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()


def _make_app() -> TimeBlockApp:
    """Cria instância da app para snapshot."""
    return TimeBlockApp()


def _seed_routine() -> None:
    """Cria rotina ativa no banco."""
    with get_engine_context() as engine, Session(engine) as session:
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()


def _seed_routine_and_habit() -> None:
    """Cria rotina + hábito + instância do dia."""
    with get_engine_context() as engine, Session(engine) as session:
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Leitura",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()


def _seed_task() -> None:
    """Cria task no banco."""
    with get_engine_context() as engine, Session(engine) as session:
        task = Task(
            title="Revisar Relatório",
            scheduled_datetime=datetime.combine(date.today(), time(14, 0)),
            original_scheduled_datetime=datetime.combine(date.today(), time(14, 0)),
        )
        session.add(task)
        session.commit()


async def _wait(pilot, n: int = 3) -> None:
    """Aguarda n ciclos de pause."""
    for _ in range(n):
        await pilot.pause()


# =========================================================================
# Routines — CRUD via Agenda (BR-TUI-016)
# =========================================================================


class TestRoutineCrudSnapshots:
    """Snapshots dos modais CRUD de rotinas."""

    def test_snapshot_routine_create_modal(self, snap_compare) -> None:
        """n sem rotina abre FormModal de criação."""

        async def run_before(pilot) -> None:
            await _wait(pilot)
            await pilot.press("n")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_routine_edit_modal(self, snap_compare) -> None:
        """e no agenda abre FormModal de edição pré-preenchido."""
        _seed_routine()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(AgendaPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("e")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_routine_delete_dialog(self, snap_compare) -> None:
        """x no agenda abre ConfirmDialog de deleção."""
        _seed_routine()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(AgendaPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("x")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# Habits — CRUD + Quick Actions (BR-TUI-017, BR-TUI-022, BR-TUI-024)
# =========================================================================


class TestHabitCrudSnapshots:
    """Snapshots dos modais CRUD e quick actions de hábitos."""

    def test_snapshot_habit_create_modal(self, snap_compare) -> None:
        """n no habits panel abre FormModal de criação."""
        _seed_routine()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("n")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_habit_edit_modal(self, snap_compare) -> None:
        """e no habits panel abre FormModal pré-preenchido."""
        _seed_routine_and_habit()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("e")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_habit_delete_dialog(self, snap_compare) -> None:
        """x no habits panel abre ConfirmDialog."""
        _seed_routine_and_habit()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("x")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_habit_done_modal(self, snap_compare) -> None:
        """v no habits panel abre modal de DoneSubstatus."""
        _seed_routine_and_habit()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("v")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_habit_skip_modal(self, snap_compare) -> None:
        """s no habits panel abre modal de SkipReason."""
        _seed_routine_and_habit()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("s")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# Tasks — CRUD (BR-TUI-018)
# =========================================================================


class TestTaskCrudSnapshots:
    """Snapshots dos modais CRUD de tasks."""

    def test_snapshot_task_create_modal(self, snap_compare) -> None:
        """n no tasks panel abre FormModal de criação."""

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("n")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_task_edit_modal(self, snap_compare) -> None:
        """e no tasks panel abre FormModal pré-preenchido."""
        _seed_task()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("e")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )

    def test_snapshot_task_delete_dialog(self, snap_compare) -> None:
        """x no tasks panel abre ConfirmDialog."""
        _seed_task()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("x")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# Estados resultantes (BR-TUI-003)
# =========================================================================


class TestDashboardStateSnapshots:
    """Snapshots do dashboard em estados resultantes de operações."""

    def test_snapshot_dashboard_habit_done(self, snap_compare) -> None:
        """Dashboard com hábito marcado como done (FULL, 100%)."""
        with get_engine_context() as engine, Session(engine) as session:
            routine = Routine(name="Rotina Matinal", is_active=True)
            session.add(routine)
            session.commit()
            session.refresh(routine)

            habit = Habit(
                routine_id=routine.id,
                title="Leitura",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            instance = HabitInstance(
                habit_id=habit.id,
                date=date.today(),
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                status=Status.DONE,
                done_substatus=DoneSubstatus.FULL,
                completion_percentage=100,
            )
            session.add(instance)
            session.commit()

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )

    def test_snapshot_dashboard_habit_skipped(self, snap_compare) -> None:
        """Dashboard com hábito skipado (SKIPPED_JUSTIFIED, saúde)."""
        with get_engine_context() as engine, Session(engine) as session:
            routine = Routine(name="Rotina Matinal", is_active=True)
            session.add(routine)
            session.commit()
            session.refresh(routine)

            habit = Habit(
                routine_id=routine.id,
                title="Leitura",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            instance = HabitInstance(
                habit_id=habit.id,
                date=date.today(),
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                status=Status.NOT_DONE,
                not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
                skip_reason=SkipReason.HEALTH,
                skip_note="Gripe",
            )
            session.add(instance)
            session.commit()

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )

    def test_snapshot_dashboard_timer_running(
        self, snap_compare, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Dashboard com timer ativo em hábito."""
        with get_engine_context() as engine, Session(engine) as session:
            routine = Routine(name="Rotina Matinal", is_active=True)
            session.add(routine)
            session.commit()
            session.refresh(routine)

            habit = Habit(
                routine_id=routine.id,
                title="Leitura",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            instance = HabitInstance(
                habit_id=habit.id,
                date=date.today(),
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                status=Status.PENDING,
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)

            timelog = TimeLog(
                habit_instance_id=instance.id,
                start_time=_TIMER_FIXED_NOW - timedelta(hours=1, minutes=25),
                status=TimerStatus.RUNNING,
            )
            session.add(timelog)
            session.commit()

        monkeypatch.setattr("timeblock.tui.screens.dashboard.loader.datetime", _FixedNowDatetime)
        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )


# =========================================================================
# Métricas com dados simulados (BR-TUI-003)
# =========================================================================


class TestMetricsSnapshots:
    """Snapshots do MetricsPanel com dados realistas de 7 dias."""

    def test_snapshot_metrics_7day_mixed(self, snap_compare) -> None:
        """Dashboard com 7 dias de hábitos: streak, pct, heatmap."""
        with get_engine_context() as engine, Session(engine) as session:
            routine = Routine(name="Rotina Matinal", is_active=True)
            session.add(routine)
            session.commit()
            session.refresh(routine)

            habit = Habit(
                routine_id=routine.id,
                title="Leitura",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            today = date.today()
            statuses = [
                # dia -6: done
                (today - timedelta(days=6), Status.DONE, DoneSubstatus.FULL, None, None),
                # dia -5: done
                (today - timedelta(days=5), Status.DONE, DoneSubstatus.FULL, None, None),
                # dia -4: skipped
                (
                    today - timedelta(days=4),
                    Status.NOT_DONE,
                    None,
                    NotDoneSubstatus.SKIPPED_JUSTIFIED,
                    SkipReason.HEALTH,
                ),
                # dia -3: done
                (today - timedelta(days=3), Status.DONE, DoneSubstatus.PARTIAL, None, None),
                # dia -2: done
                (today - timedelta(days=2), Status.DONE, DoneSubstatus.FULL, None, None),
                # dia -1: done
                (today - timedelta(days=1), Status.DONE, DoneSubstatus.OVERDONE, None, None),
                # hoje: pending
                (today, Status.PENDING, None, None, None),
            ]

            for d, status, done_sub, notdone_sub, skip_r in statuses:
                inst = HabitInstance(
                    habit_id=habit.id,
                    date=d,
                    scheduled_start=time(9, 0),
                    scheduled_end=time(10, 0),
                    status=status,
                    done_substatus=done_sub,
                    not_done_substatus=notdone_sub,
                    skip_reason=skip_r,
                )
                session.add(inst)

            session.commit()

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )

    def test_snapshot_metrics_perfect_streak(self, snap_compare) -> None:
        """Dashboard com 7 dias consecutivos done — streak perfeito."""
        with get_engine_context() as engine, Session(engine) as session:
            routine = Routine(name="Rotina Matinal", is_active=True)
            session.add(routine)
            session.commit()
            session.refresh(routine)

            habit = Habit(
                routine_id=routine.id,
                title="Meditação",
                scheduled_start=time(7, 0),
                scheduled_end=time(7, 30),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            today = date.today()
            for i in range(7):
                d = today - timedelta(days=6 - i)
                status = Status.DONE if d != today else Status.PENDING
                done_sub = DoneSubstatus.FULL if status == Status.DONE else None
                inst = HabitInstance(
                    habit_id=habit.id,
                    date=d,
                    scheduled_start=time(7, 0),
                    scheduled_end=time(7, 30),
                    status=status,
                    done_substatus=done_sub,
                )
                session.add(inst)

            session.commit()

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )
