"""Testes unitários para TimerService (v2 - MVP).

Valida Business Rules:
- BR-TIMER-001: Single Active Timer Constraint
- BR-TIMER-006: Pause Tracking (MVP com paused_duration)
"""

from datetime import date, datetime, time
from time import sleep

import pytest
from sqlmodel import Session, select

from src.timeblock.models.enums import DoneSubstatus, Status
from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance
from src.timeblock.models.routine import Routine
from src.timeblock.models.time_log import TimeLog
from src.timeblock.services.timer_service import TimerService


@pytest.fixture
def routine(session: Session) -> Routine:
    """Cria Routine para testes de timer."""
    routine = Routine(name="Test Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@pytest.fixture
def habit(session: Session, routine: Routine) -> Habit:
    """Cria Habit para testes de timer."""
    assert routine.id is not None

    habit = Habit(
        routine_id=routine.id,
        title="Academia",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    assert habit.id is not None
    return habit


@pytest.fixture
def test_habit_instance(session: Session, habit: Habit) -> HabitInstance:
    """Cria HabitInstance PENDING para testes de timer."""
    assert habit.id is not None

    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    assert instance.id is not None
    return instance


class TestBRTimer001:
    """BR-TIMER-001: Single Active Timer Constraint."""

    def test_br_timer_001_only_one_active(self, session: Session, test_habit_instance: HabitInstance):
        """Apenas um timer pode estar ativo por vez."""
        assert test_habit_instance.id is not None

        # DADO: Timer iniciado
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        assert timelog.end_time is None

        # QUANDO: Tentar iniciar outro timer (mesma instance)
        # ENTÃO: Deve falhar
        with pytest.raises(ValueError, match="Timer already active"):
            TimerService.start_timer(test_habit_instance.id, session)

    def test_br_timer_001_stopped_allows_new_start(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Timer stopped permite novo start (nova sessão)."""
        assert test_habit_instance.id is not None

        # DADO: Timer stopped
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        sleep(0.1)
        TimerService.stop_timer(timelog.id, session)

        # QUANDO: Iniciar novo timer (nova sessão)
        # ENTÃO: Deve permitir
        timelog2 = TimerService.start_timer(test_habit_instance.id, session)
        assert timelog2.id != timelog.id
        assert timelog2.end_time is None


class TestBRTimer006Pause:
    """BR-TIMER-006: Pause Tracking - Validações de pause."""

    def test_pause_timer_success(self, session: Session, test_habit_instance: HabitInstance):
        """Pausa timer com sucesso."""
        assert test_habit_instance.id is not None

        # DADO: Timer ativo
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        assert timelog.end_time is None

        # QUANDO: Pausar timer
        paused = TimerService.pause_timer(timelog.id, session)

        # ENTÃO: Timer continua sem end_time (ainda ativo, mas pausado)
        assert paused.id == timelog.id
        assert paused.end_time is None
        # paused_duration ainda não foi persistido (apenas marcou início)

    def test_pause_timer_already_stopped(self, session: Session, test_habit_instance: HabitInstance):
        """Erro ao pausar timer já stopped."""
        assert test_habit_instance.id is not None

        # DADO: Timer stopped
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        sleep(0.1)
        TimerService.stop_timer(timelog.id, session)

        # QUANDO: Tentar pausar timer stopped
        # ENTÃO: Deve falhar
        with pytest.raises(ValueError, match="already stopped"):
            TimerService.pause_timer(timelog.id, session)

    def test_pause_timer_already_paused(self, session: Session, test_habit_instance: HabitInstance):
        """Erro ao pausar timer já pausado."""
        assert test_habit_instance.id is not None

        # DADO: Timer pausado
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)

        # QUANDO: Tentar pausar novamente
        # ENTÃO: Deve falhar
        with pytest.raises(ValueError, match="already paused"):
            TimerService.pause_timer(timelog.id, session)


class TestBRTimer006Resume:
    """BR-TIMER-006: Pause Tracking - Resume e acumulação."""

    def test_resume_timer_success(self, session: Session, test_habit_instance: HabitInstance):
        """Resume timer com sucesso e persiste paused_duration."""
        assert test_habit_instance.id is not None

        # DADO: Timer pausado
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)
        sleep(0.1)

        # QUANDO: Resume timer
        resumed = TimerService.resume_timer(timelog.id, session)

        # ENTÃO: paused_duration foi persistido
        assert resumed.paused_duration is not None
        assert resumed.paused_duration > 0
        assert resumed.end_time is None  # Timer continua ativo

    def test_resume_timer_accumulates_duration(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Múltiplas pausas acumulam em paused_duration."""
        assert test_habit_instance.id is not None

        # DADO: Timer com múltiplas pausas
        timelog = TimerService.start_timer(test_habit_instance.id, session)

        # Pausa 1
        TimerService.pause_timer(timelog.id, session)
        sleep(0.1)
        TimerService.resume_timer(timelog.id, session)
        first_pause = timelog.paused_duration or 0

        # Pausa 2
        TimerService.pause_timer(timelog.id, session)
        sleep(0.1)
        resumed = TimerService.resume_timer(timelog.id, session)

        # ENTÃO: paused_duration acumulou ambas pausas
        assert resumed.paused_duration is not None
        assert resumed.paused_duration > first_pause

    def test_resume_timer_not_paused(self, session: Session, test_habit_instance: HabitInstance):
        """Erro ao resumir timer não pausado."""
        assert test_habit_instance.id is not None

        # DADO: Timer ativo (não pausado)
        timelog = TimerService.start_timer(test_habit_instance.id, session)

        # QUANDO: Tentar resume sem pause
        # ENTÃO: Deve falhar
        with pytest.raises(ValueError, match="not paused"):
            TimerService.resume_timer(timelog.id, session)


class TestBRTimer006Stop:
    """BR-TIMER-006: Stop timer com pause ativo."""

    def test_stop_while_paused_accumulates(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Stop enquanto pausado acumula última pausa."""
        assert test_habit_instance.id is not None

        # DADO: Timer pausado
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)
        sleep(0.2)

        # QUANDO: Stop sem resume
        stopped = TimerService.stop_timer(timelog.id, session)

        # ENTÃO: paused_duration foi acumulado antes de finalizar
        assert stopped.paused_duration is not None
        assert stopped.paused_duration > 0
        assert stopped.end_time is not None
        assert stopped.duration_seconds is not None

        # Duração efetiva = tempo total - pausas
        total_duration = (stopped.end_time - stopped.start_time).total_seconds()
        assert stopped.duration_seconds < total_duration

    def test_multiple_pauses_accumulated(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Múltiplas pausas são acumuladas no stop."""
        assert test_habit_instance.id is not None

        # DADO: Timer com 2 pausas + resume + pausa final
        timelog = TimerService.start_timer(test_habit_instance.id, session)

        # Pausa 1
        TimerService.pause_timer(timelog.id, session)
        sleep(0.1)
        TimerService.resume_timer(timelog.id, session)

        # Pausa 2
        TimerService.pause_timer(timelog.id, session)
        sleep(0.1)
        TimerService.resume_timer(timelog.id, session)

        # Pausa 3 (não resume)
        TimerService.pause_timer(timelog.id, session)
        sleep(0.1)

        # QUANDO: Stop com pausa ativa
        stopped = TimerService.stop_timer(timelog.id, session)

        # ENTÃO: Todas as pausas foram acumuladas
        assert stopped.paused_duration is not None
        assert stopped.paused_duration >= 300  # ~300ms (3 pausas * 100ms)


class TestBRTimer001Cancel:
    """BR-TIMER-001: Cancel timer (reset sem salvar)."""

    def test_cancel_timer_deletes_timelog(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Cancel deleta TimeLog sem salvar."""
        assert test_habit_instance.id is not None

        # DADO: Timer ativo
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        timelog_id = timelog.id
        assert timelog_id is not None

        # QUANDO: Cancel timer
        TimerService.cancel_timer(timelog_id, session)

        # ENTÃO: TimeLog foi deletado
        deleted = session.get(TimeLog, timelog_id)
        assert deleted is None

    def test_cancel_timer_keeps_instance_pending(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Cancel mantém HabitInstance como PENDING."""
        assert test_habit_instance.id is not None

        # DADO: Timer ativo
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        assert test_habit_instance.status == Status.PENDING

        # QUANDO: Cancel timer
        TimerService.cancel_timer(timelog.id, session)

        # ENTÃO: Instance continua PENDING
        session.refresh(test_habit_instance)
        assert test_habit_instance.status == Status.PENDING
        assert test_habit_instance.done_substatus is None

    def test_cancel_non_existent_timer(self, session: Session):
        """Erro ao cancelar timer inexistente."""
        # QUANDO: Cancel timer que não existe
        # ENTÃO: Deve falhar
        with pytest.raises(ValueError, match="not found"):
            TimerService.cancel_timer(99999, session)


class TestGetAnyActiveTimer:
    """Helper method para CLI - busca qualquer timer ativo."""

    def test_get_any_active_timer_found(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Encontra timer ativo sem precisar de habit_instance_id."""
        assert test_habit_instance.id is not None

        # DADO: Timer ativo
        started = TimerService.start_timer(test_habit_instance.id, session)

        # QUANDO: Buscar qualquer timer ativo
        active = TimerService.get_any_active_timer(session)

        # ENTÃO: Encontrou o timer
        assert active is not None
        assert active.id == started.id

    def test_get_any_active_timer_not_found(self, session: Session):
        """Retorna None se não há timer ativo."""
        # QUANDO: Buscar sem timer ativo
        active = TimerService.get_any_active_timer(session)

        # ENTÃO: Retorna None
        assert active is None

    def test_get_any_active_timer_after_stop(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Retorna None após stop (timer não está mais ativo)."""
        assert test_habit_instance.id is not None

        # DADO: Timer stopped
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        sleep(0.1)
        TimerService.stop_timer(timelog.id, session)

        # QUANDO: Buscar timer ativo
        active = TimerService.get_any_active_timer(session)

        # ENTÃO: Retorna None
        assert active is None


@pytest.fixture(autouse=True)
def reset_timer_state():
    """Limpa estado de pause entre testes."""
    yield
    # Cleanup após cada teste
    TimerService._active_pause_start = None
