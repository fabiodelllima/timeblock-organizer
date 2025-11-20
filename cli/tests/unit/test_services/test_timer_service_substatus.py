"""Testes unitários para BR-TIMER-006.

Cálculo automático de substatus ao parar timer de HabitInstance.
Valida completion percentage e mapeamento para substatus correto.
"""

from datetime import date, datetime, time, timedelta

import pytest
from sqlmodel import Session

from src.timeblock.models.enums import DoneSubstatus, Status
from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance
from src.timeblock.models.routine import Routine
from src.timeblock.models.time_log import TimeLog
from src.timeblock.services.timer_service import TimerService


@pytest.fixture
def routine(session: Session) -> Routine:
    """Cria Routine para testes."""
    routine = Routine(name="Test Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@pytest.fixture
def habit(session: Session, routine: Routine) -> Habit:
    """Cria Habit para testes."""
    assert routine.id is not None, "Routine must have ID after commit"

    habit = Habit(
        routine_id=routine.id,
        title="Test Habit",
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)

    assert habit.id is not None, "Habit must have ID after commit"
    return habit


class TestBRTimer006CalculateSubstatus:
    """Cenários 1-6: Timer stop calcula substatus baseado em completion."""

    def test_scenario_001_stop_calculates_partial_75_percent(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 1: Timer stop com 75% completion -> PARTIAL."""
        assert habit.id is not None

        # DADO: HabitInstance com meta 60 minutos
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),  # 60 min meta
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Timer iniciado
        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        # Criar TimeLog ativo
        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None, "TimeLog must have ID after commit"

        # QUANDO: Para timer após 45 minutos (75%)
        from unittest.mock import patch
        stop_time = start_time + timedelta(minutes=45)

        with patch('src.timeblock.services.timer_service.datetime') as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            result_timelog = timer_service.stop_timer(
                timelog_id=timelog.id,
                session=session
            )

        # Refresh instance para pegar mudanças
        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.PARTIAL
        assert instance.completion_percentage == 75
        assert instance.not_done_substatus is None
        assert result_timelog.duration_seconds == 2700  # 45min

    def test_scenario_002_stop_calculates_full_90_percent(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 2: Timer stop com 90% completion -> FULL."""
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 54 minutos = 90%
        from unittest.mock import patch
        stop_time = start_time + timedelta(minutes=54)

        with patch('src.timeblock.services.timer_service.datetime') as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 90
        assert instance.not_done_substatus is None

    def test_scenario_003_stop_calculates_full_100_percent(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 3: Timer stop com 100% completion -> FULL."""
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 60 minutos = 100%
        from unittest.mock import patch
        stop_time = start_time + timedelta(minutes=60)

        with patch('src.timeblock.services.timer_service.datetime') as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 100

    def test_scenario_005_stop_calculates_overdone_130_percent(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 5: Timer stop com 130% completion -> OVERDONE."""
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 78 minutos = 130%
        from unittest.mock import patch
        stop_time = start_time + timedelta(minutes=78)

        with patch('src.timeblock.services.timer_service.datetime') as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.OVERDONE
        assert instance.completion_percentage == 130

    def test_scenario_006_stop_calculates_excessive_200_percent(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 6: Timer stop com 200% completion -> EXCESSIVE."""
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 120 minutos = 200%
        from unittest.mock import patch
        stop_time = start_time + timedelta(minutes=120)

        with patch('src.timeblock.services.timer_service.datetime') as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.EXCESSIVE
        assert instance.completion_percentage == 200


class TestBRTimer006Validation:
    """Cenário 7-8: Validações e erros."""

    def test_scenario_007_validates_consistency_after_stop(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 7: Validação de consistência após stop."""
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO
        from unittest.mock import patch
        stop_time = start_time + timedelta(minutes=55)

        with patch('src.timeblock.services.timer_service.datetime') as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO: Validação deve passar
        instance.validate_status_consistency()  # Não deve lançar exceção

        # Verificar consistência manual
        assert instance.status == Status.DONE
        assert instance.done_substatus is not None
        assert instance.not_done_substatus is None
        assert instance.skip_reason is None

    def test_scenario_008_error_no_active_timer(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 8: Timer stop sem timer ativo -> ValueError."""
        assert habit.id is not None

        # DADO: HabitInstance sem timer ativo
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()

        # QUANDO: Tentar parar timer inexistente
        # ENTÃO: Deve lançar ValueError
        with pytest.raises(ValueError, match="TimeLog 99999 not found"):
            timer_service.stop_timer(timelog_id=99999, session=session)
