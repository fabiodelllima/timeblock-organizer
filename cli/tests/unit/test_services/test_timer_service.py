"""Testes para TimerService."""

from datetime import datetime, timedelta
from time import sleep

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, PauseLog, Task, TimeLog
from src.timeblock.services.timer_service import TimerService


@pytest.fixture
def test_engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_task(test_engine):
    """Cria task de teste."""
    with Session(test_engine) as session:
        task = Task(
            title="Test Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr("src.timeblock.services.timer_service.get_engine_context", mock_get_engine)
    monkeypatch.setattr("src.timeblock.services.event_reordering_service.get_engine_context", mock_get_engine)


class TestStartTimer:
    """Testes para start_timer."""

    def test_start_timer_with_task(self, test_task):
        """Inicia timer para task."""
        timelog, conflicts = TimerService.start_timer(task_id=test_task.id)
        assert timelog.id is not None
        assert timelog.task_id == test_task.id
        assert timelog.start_time is not None
        assert timelog.end_time is None
        assert conflicts == []

    def test_start_timer_returns_tuple(self, test_task):
        """Verifica que retorna tupla."""
        result = TimerService.start_timer(task_id=test_task.id)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_start_timer_with_event(self, test_engine):
        """Inicia timer para event."""
        with Session(test_engine) as session:
            event = Event(
                title="Event",
                scheduled_start=datetime(2025, 10, 20, 10, 0),
                scheduled_end=datetime(2025, 10, 20, 11, 0),
            )
            session.add(event)
            session.commit()
            session.refresh(event)

        timelog, conflicts = TimerService.start_timer(event_id=event.id)
        assert timelog.event_id == event.id
        assert conflicts == []

    def test_start_timer_detects_conflict_with_task(self, test_engine):
        """Detecta conflito ao iniciar timer com task conflitante."""
        with Session(test_engine) as session:
            task1 = Task(
                title="Task 1",
                scheduled_datetime=datetime.now(),
            )
            task2 = Task(
                title="Task 2",
                scheduled_datetime=datetime.now() + timedelta(minutes=30),
            )
            session.add_all([task1, task2])
            session.commit()
            session.refresh(task1)
            session.refresh(task2)

        timelog, conflicts = TimerService.start_timer(task_id=task1.id)

        assert timelog is not None
        assert len(conflicts) > 0

    def test_start_timer_without_id(self):
        """Rejeita sem ID."""
        with pytest.raises(ValueError, match="Exactly one ID must be provided"):
            TimerService.start_timer()

    def test_start_timer_with_multiple_ids(self, test_task):
        """Rejeita múltiplos IDs."""
        with pytest.raises(ValueError, match="Exactly one ID must be provided"):
            TimerService.start_timer(task_id=test_task.id, event_id=1)

    def test_start_timer_when_active_exists(self, test_task, test_engine):
        """Rejeita se já existe timer ativo."""
        TimerService.start_timer(task_id=test_task.id)

        with Session(test_engine) as session:
            task2 = Task(
                title="Task 2",
                scheduled_datetime=datetime(2025, 10, 20, 11, 0),
            )
            session.add(task2)
            session.commit()
            session.refresh(task2)

        with pytest.raises(ValueError, match="Another timer is already active"):
            TimerService.start_timer(task_id=task2.id)


class TestStopTimer:
    """Testes para stop_timer."""

    def test_stop_timer_success(self, test_task):
        """Para timer e calcula duração."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        sleep(1)

        stopped = TimerService.stop_timer(timelog.id)
        assert stopped is not None
        assert stopped.end_time is not None
        assert stopped.duration_seconds > 0

    def test_stop_timer_not_found(self):
        """Retorna None se não existe."""
        assert TimerService.stop_timer(9999) is None

    def test_stop_timer_already_stopped(self, test_task):
        """Rejeita timer já parado."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        TimerService.stop_timer(timelog.id)

        with pytest.raises(ValueError, match="already stopped"):
            TimerService.stop_timer(timelog.id)

    def test_stop_timer_with_pauses(self, test_task, test_engine):
        """Desconta tempo pausado."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)

        with Session(test_engine) as session:
            pause = PauseLog(
                timelog_id=timelog.id,
                pause_start=timelog.start_time + timedelta(seconds=1),
                pause_end=timelog.start_time + timedelta(seconds=3),
            )
            session.add(pause)

            tl = session.get(TimeLog, timelog.id)
            tl.paused_duration = 2
            session.add(tl)
            session.commit()

        sleep(1)
        stopped = TimerService.stop_timer(timelog.id)
        total = (stopped.end_time - stopped.start_time).total_seconds()
        assert stopped.duration_seconds < total


class TestCancelTimer:
    """Testes para cancel_timer."""

    def test_cancel_timer_success(self, test_task):
        """Cancela timer."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)

        assert TimerService.cancel_timer(timelog.id) is True
        assert TimerService.get_active_timer() is None

    def test_cancel_timer_not_found(self):
        """Retorna False se não existe."""
        assert TimerService.cancel_timer(9999) is False

    def test_cancel_timer_already_stopped(self, test_task):
        """Rejeita timer já parado."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        TimerService.stop_timer(timelog.id)

        with pytest.raises(ValueError, match="already stopped"):
            TimerService.cancel_timer(timelog.id)

    def test_cancel_timer_deletes_pauses(self, test_task, test_engine):
        """Deleta pausas associadas."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        pause = TimerService.pause_timer(timelog.id)

        TimerService.cancel_timer(timelog.id)

        with Session(test_engine) as session:
            assert session.get(PauseLog, pause.id) is None


class TestPauseTimer:
    """Testes para pause_timer."""

    def test_pause_timer_success(self, test_task):
        """Pausa timer."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        pause = TimerService.pause_timer(timelog.id)

        assert pause.id is not None
        assert pause.timelog_id == timelog.id
        assert pause.pause_start is not None
        assert pause.pause_end is None

    def test_pause_timer_not_found(self):
        """Erro se timer não existe."""
        with pytest.raises(ValueError, match="not found"):
            TimerService.pause_timer(9999)

    def test_pause_timer_already_stopped(self, test_task):
        """Erro se timer já parado."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        TimerService.stop_timer(timelog.id)

        with pytest.raises(ValueError, match="already stopped"):
            TimerService.pause_timer(timelog.id)


class TestResumeTimer:
    """Testes para resume_timer."""

    def test_resume_timer_success(self, test_task):
        """Retoma timer."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        TimerService.pause_timer(timelog.id)
        sleep(1)

        TimerService.resume_timer(timelog.id)

        resumed = TimerService.get_active_timer()
        assert resumed.paused_duration > 0

    def test_resume_timer_not_found(self):
        """Erro se timer não existe."""
        with pytest.raises(ValueError, match="not found"):
            TimerService.resume_timer(9999)

    def test_resume_timer_no_active_pause(self, test_task):
        """Erro se não há pausa ativa."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)

        with pytest.raises(ValueError, match="No active pause"):
            TimerService.resume_timer(timelog.id)


class TestGetActiveTimer:
    """Testes para get_active_timer."""

    def test_get_active_timer_found(self, test_task):
        """Encontra timer ativo."""
        started, _ = TimerService.start_timer(task_id=test_task.id)
        active = TimerService.get_active_timer()

        assert active is not None
        assert active.id == started.id

    def test_get_active_timer_not_found(self):
        """Retorna None se não há timer."""
        assert TimerService.get_active_timer() is None

    def test_get_active_timer_after_stop(self, test_task):
        """Retorna None após stop."""
        timelog, _ = TimerService.start_timer(task_id=test_task.id)
        TimerService.stop_timer(timelog.id)

        assert TimerService.get_active_timer() is None
