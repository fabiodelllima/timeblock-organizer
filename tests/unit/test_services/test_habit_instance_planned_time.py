"""Testes de preservação do horário planejado em HabitInstance.

BRs validadas:
- BR-HABITINSTANCE-008: Preservação do Horário Planejado
"""

from datetime import date, time

import pytest
from sqlmodel import Session

from timeblock.models import (
    Habit,
    HabitInstance,
    Routine,
    Status,
)
from timeblock.services.habit_instance_service import HabitInstanceService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock engine context para os services usados neste módulo."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )
    monkeypatch.setattr(
        "timeblock.services.event_reordering_service.get_engine_context",
        mock_get_engine,
    )


@pytest.fixture
def habit_with_instance(session: Session) -> HabitInstance:
    """Cria hábito das 7h às 8h com uma instância PENDING para hoje."""
    routine = Routine(name="Planned Time Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Planned Time Habit",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence="EVERYDAY",
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)

    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


class TestPlannedTimePreservation:
    """Tests for BR-HABITINSTANCE-008: planned time survives adjustment."""

    def test_adjust_preserves_original_time(self, habit_with_instance: HabitInstance) -> None:
        """Adjusting the effective time leaves the planned time untouched.

        The original values are captured on first adjustment when absent, since
        that is the last moment the pre-adjustment schedule is still known.
        """
        updated, _ = HabitInstanceService.adjust_instance_time(
            habit_with_instance.id, time(9, 0), time(10, 0)
        )
        assert updated.scheduled_start == time(9, 0)
        assert updated.scheduled_end == time(10, 0)
        assert updated.original_scheduled_start == time(7, 0)
        assert updated.original_scheduled_end == time(8, 0)

    def test_second_adjust_does_not_overwrite_original(
        self, habit_with_instance: HabitInstance
    ) -> None:
        """Once captured, the planned time is immutable across further adjustments."""
        HabitInstanceService.adjust_instance_time(habit_with_instance.id, time(9, 0), time(10, 0))
        updated, _ = HabitInstanceService.adjust_instance_time(
            habit_with_instance.id, time(11, 0), time(12, 0)
        )
        assert updated.original_scheduled_start == time(7, 0)
        assert updated.original_scheduled_end == time(8, 0)

    def test_adjust_increments_adjustment_count(
        self, habit_with_instance: HabitInstance
    ) -> None:
        """Each effective time change increments the counter."""
        first, _ = HabitInstanceService.adjust_instance_time(
            habit_with_instance.id, time(9, 0), time(10, 0)
        )
        assert first.adjustment_count == 1
        second, _ = HabitInstanceService.adjust_instance_time(
            habit_with_instance.id, time(11, 0), time(12, 0)
        )
        assert second.adjustment_count == 2

    def test_noop_adjust_does_not_increment(self, habit_with_instance: HabitInstance) -> None:
        """Adjusting to the values already in place does not inflate the counter."""
        updated, _ = HabitInstanceService.adjust_instance_time(
            habit_with_instance.id, time(7, 0), time(8, 0)
        )
        assert updated.adjustment_count == 0

    def test_generate_populates_original_time(self, session: Session) -> None:
        """generate_instances fixes the planned time from the habit template."""
        routine = Routine(name="Generate Routine")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Generate Habit",
            scheduled_start=time(6, 30),
            scheduled_end=time(7, 15),
            recurrence="EVERYDAY",
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        created = HabitInstanceService.generate_instances(
            habit.id, date.today(), date.today(), session=session
        )

        assert created
        for instance in created:
            assert instance.original_scheduled_start == time(6, 30)
            assert instance.original_scheduled_end == time(7, 15)
            assert instance.adjustment_count == 0
