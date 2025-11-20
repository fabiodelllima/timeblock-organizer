"""Testes unitários para BR-HABIT-SKIP-001.

Skip de HabitInstance com categorização.
Valida regras de negócio para skip com SkipReason e nota opcional.
"""

from datetime import date, datetime, time

import pytest
from sqlmodel import Session

from src.timeblock.models.enums import DoneSubstatus, NotDoneSubstatus, SkipReason, Status
from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance
from src.timeblock.models.routine import Routine
from src.timeblock.models.time_log import TimeLog
from src.timeblock.services.habit_instance_service import HabitInstanceService


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


class TestBRHabitSkip001BasicSkip:
    """Cenários 1-4: Skip básico com diferentes categorias."""

    def test_br_habit_skip_001_scenario_001_skip_with_health_and_note(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 1: Skip com categoria HEALTH e nota."""
        assert habit.id is not None

        # DADO
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

        # QUANDO
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.HEALTH,
            skip_note="Gripe, febre 38°C",
            session=session
        )

        # ENTÃO
        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert result.skip_reason == SkipReason.HEALTH
        assert result.skip_note == "Gripe, febre 38°C"
        assert result.done_substatus is None
        assert result.completion_percentage is None

    def test_br_habit_skip_001_scenario_002_skip_work_without_note(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 2: Skip com categoria WORK sem nota."""
        assert habit.id is not None

        # DADO
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

        # QUANDO
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.WORK,
            skip_note=None,
            session=session
        )

        # ENTÃO
        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert result.skip_reason == SkipReason.WORK
        assert result.skip_note is None

    def test_br_habit_skip_001_scenario_003_skip_family(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 3: Skip com categoria FAMILY."""
        assert habit.id is not None

        # DADO
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

        # QUANDO
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.FAMILY,
            skip_note="Aniversário do filho",
            session=session
        )

        # ENTÃO
        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert result.skip_reason == SkipReason.FAMILY
        assert result.skip_note == "Aniversário do filho"

    def test_br_habit_skip_001_scenario_004_skip_weather(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 4: Skip com categoria WEATHER."""
        assert habit.id is not None

        # DADO
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

        # QUANDO
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.WEATHER,
            skip_note="Chuva forte",
            session=session
        )

        # ENTÃO
        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert result.skip_reason == SkipReason.WEATHER
        assert result.skip_note == "Chuva forte"


class TestBRHabitSkip001ReskipAndValidation:
    """Cenários 5-6: Re-skip e validação."""

    def test_br_habit_skip_001_scenario_005_reskip_changes_category(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 5: Re-skip muda categoria."""
        assert habit.id is not None

        # DADO: Instance já skipped com WORK
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            status=Status.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            skip_reason=SkipReason.WORK,
            skip_note="Reunião",
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        assert instance.id is not None

        # QUANDO: Re-skip com HEALTH
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.HEALTH,
            skip_note="Descobri que estava doente",
            session=session
        )

        # ENTÃO
        assert result.skip_reason == SkipReason.HEALTH
        assert result.skip_note == "Descobri que estava doente"
        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED

    def test_br_habit_skip_001_scenario_006_validates_consistency(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 6: Validação de consistência após skip."""
        assert habit.id is not None

        # DADO
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

        # QUANDO
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.EMERGENCY,
            skip_note=None,
            session=session
        )

        # ENTÃO: Validação deve passar (não lança exceção)
        result.validate_status_consistency()

        # Verificar consistência manual
        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert result.skip_reason == SkipReason.EMERGENCY
        assert result.done_substatus is None


class TestBRHabitSkip001Errors:
    """Cenários 7-10: Validações e erros."""

    def test_br_habit_skip_001_scenario_007_error_instance_not_found(
        self, session: Session
    ):
        """CENÁRIO 7: Erro - HabitInstance não existe."""
        service = HabitInstanceService()

        with pytest.raises(ValueError, match="HabitInstance 99999 not found"):
            service.skip_habit_instance(
                habit_instance_id=99999,
                skip_reason=SkipReason.HEALTH,
                skip_note=None,
                session=session
            )

    def test_br_habit_skip_001_scenario_008_error_note_too_long(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 8: Erro - Nota muito longa (>500 chars)."""
        assert habit.id is not None

        # DADO
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

        # QUANDO: Nota com 501 caracteres
        long_note = "A" * 501
        service = HabitInstanceService()

        # ENTÃO
        with pytest.raises(ValueError, match="Skip note must be <= 500 characters"):
            service.skip_habit_instance(
                habit_instance_id=instance.id,
                skip_reason=SkipReason.HEALTH,
                skip_note=long_note,
                session=session
            )

    def test_br_habit_skip_001_scenario_009_error_timer_active(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 9: Erro - Timer ativo."""
        assert habit.id is not None

        # DADO: Instance com timer ativo
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

        # Timer ativo (sem end_time)
        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=datetime.now(),
            end_time=None,
        )
        session.add(timelog)
        session.commit()

        # QUANDO
        service = HabitInstanceService()

        # ENTÃO
        with pytest.raises(ValueError, match="Cannot skip with active timer"):
            service.skip_habit_instance(
                habit_instance_id=instance.id,
                skip_reason=SkipReason.HEALTH,
                skip_note=None,
                session=session
            )

    def test_br_habit_skip_001_scenario_010_error_already_completed(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 10: Erro - Instância já completada."""
        assert habit.id is not None

        # DADO: Instance DONE
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            status=Status.DONE,
            done_substatus=DoneSubstatus.FULL,
            completion_percentage=100,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        assert instance.id is not None

        # QUANDO
        service = HabitInstanceService()

        # ENTÃO
        with pytest.raises(ValueError, match="Cannot skip completed instance"):
            service.skip_habit_instance(
                habit_instance_id=instance.id,
                skip_reason=SkipReason.HEALTH,
                skip_note=None,
                session=session
            )


class TestBRHabitSkip001CompletionFields:
    """Cenário 11: Skip limpa campos de completion."""

    def test_br_habit_skip_001_scenario_011_clears_completion_fields(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 11: Skip limpa campos de completion anteriores."""
        assert habit.id is not None

        # DADO: Instance tinha DONE (usuário desfez)
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            status=Status.PENDING,  # Voltou para PENDING
            done_substatus=DoneSubstatus.FULL,  # Campos antigos
            completion_percentage=95,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        assert instance.id is not None

        # QUANDO: Skip
        service = HabitInstanceService()
        result = service.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.HEALTH,
            skip_note=None,
            session=session
        )

        # ENTÃO: Campos limpos
        assert result.done_substatus is None
        assert result.completion_percentage is None
        assert result.status == Status.NOT_DONE
        assert result.skip_reason == SkipReason.HEALTH


class TestBRHabitSkip001AllCategories:
    """Cenário 12: Skip com todas as 8 categorias."""

    def test_br_habit_skip_001_scenario_012_all_categories(
        self, session: Session, habit: Habit
    ):
        """CENÁRIO 12: Skip com todas as 8 categorias."""
        assert habit.id is not None

        categories = [
            SkipReason.HEALTH,
            SkipReason.WORK,
            SkipReason.FAMILY,
            SkipReason.TRAVEL,
            SkipReason.WEATHER,
            SkipReason.LACK_RESOURCES,
            SkipReason.EMERGENCY,
            SkipReason.OTHER,
        ]

        service = HabitInstanceService()

        for category in categories:
            # Criar instance
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

            # Skip
            result = service.skip_habit_instance(
                habit_instance_id=instance.id,
                skip_reason=category,
                skip_note=None,
                session=session
            )

            # Validar
            assert result.status == Status.NOT_DONE
            assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
            assert result.skip_reason == category
