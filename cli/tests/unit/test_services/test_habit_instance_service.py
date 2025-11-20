"""Testes para HabitInstanceService."""
from datetime import date, datetime, time, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import (
    Habit,
    HabitInstance,
    Status,
    Routine,
)
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.task_service import TaskService


@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    # Mock em todos os services que usam get_engine_context
    monkeypatch.setattr("src.timeblock.services.habit_instance_service.get_engine_context", mock_get_engine)
    monkeypatch.setattr("src.timeblock.services.task_service.get_engine_context", mock_get_engine)
    monkeypatch.setattr("src.timeblock.services.event_reordering_service.get_engine_context", mock_get_engine)


@pytest.fixture
def sample_instance(test_engine):
    with Session(test_engine) as session:
        routine = Routine(name="Test Routine")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence="EVERYDAY"
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            status=Status.PLANNED
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance


class TestAdjustInstanceTimeBasic:
    def test_adjust_time_successfully(self, sample_instance):
        updated, conflicts = HabitInstanceService.adjust_instance_time(
            sample_instance.id, time(9, 0), time(10, 0)
        )
        assert updated.scheduled_start == time(9, 0)
        assert updated.scheduled_end == time(10, 0)
        assert conflicts == []

    def test_adjust_time_invalid(self, sample_instance):
        with pytest.raises(ValueError):
            HabitInstanceService.adjust_instance_time(
                sample_instance.id, time(10, 0), time(9, 0)
            )

    def test_adjust_time_nonexistent(self):
        with pytest.raises(ValueError):
            HabitInstanceService.adjust_instance_time(999, time(9, 0), time(10, 0))

    def test_returns_tuple(self, sample_instance):
        result = HabitInstanceService.adjust_instance_time(
            sample_instance.id, time(9, 0), time(10, 0)
        )
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestConflictDetection:
    def test_detect_conflict_with_task(self, test_engine, sample_instance):
        now = datetime.combine(date.today(), time(9, 30))
        TaskService.create_task("Reunião", now, 60)

        updated, conflicts = HabitInstanceService.adjust_instance_time(
            sample_instance.id, time(9, 0), time(10, 30)
        )

        assert len(conflicts) > 0

    def test_no_conflict_different_day(self, test_engine):
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()
            session.refresh(routine)

            habit = Habit(
                routine_id=routine.id,
                title="Test Habit",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence="EVERYDAY"
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            inst1 = HabitInstance(
                habit_id=habit.id,
                date=date.today(),
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                status=Status.PLANNED
            )
            inst2 = HabitInstance(
                habit_id=habit.id,
                date=date.today() + timedelta(days=1),
                scheduled_start=time(15, 0),
                scheduled_end=time(16, 0),
                status=Status.PLANNED
            )
            session.add_all([inst1, inst2])
            session.commit()
            session.refresh(inst2)

        updated, conflicts = HabitInstanceService.adjust_instance_time(
            inst2.id, time(9, 0), time(10, 0)
        )
        assert conflicts == []
