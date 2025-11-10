"""Testes para comando habit adjust."""
from datetime import date, time

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Habit, HabitInstance, Routine
from src.timeblock.services.habit_instance_service import HabitInstanceService


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

    monkeypatch.setattr("src.timeblock.services.habit_instance_service.get_engine_context", mock_get_engine)
    monkeypatch.setattr("src.timeblock.services.event_reordering_service.get_engine_context", mock_get_engine)


@pytest.fixture
def sample_instance(test_engine):
    with Session(test_engine) as session:
        routine = Routine(name="Test")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Morning Run",
            scheduled_start=time(6, 0),
            scheduled_end=time(7, 0),
            recurrence="EVERYDAY"
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(6, 0),
            scheduled_end=time(7, 0),
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance


def test_adjust_returns_tuple(sample_instance):
    """Adjust retorna tupla."""
    result = HabitInstanceService.adjust_instance_time(
        sample_instance.id, time(8, 0), time(9, 0)
    )
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_adjust_updates_time(test_engine, sample_instance):
    """Adjust atualiza horário."""
    instance, _ = HabitInstanceService.adjust_instance_time(
        sample_instance.id, time(8, 0), time(9, 0)
    )

    with Session(test_engine) as session:
        updated = session.get(HabitInstance, sample_instance.id)
        assert updated.scheduled_start == time(8, 0)
        assert updated.scheduled_end == time(9, 0)
        assert updated.manually_adjusted is True
        assert updated.user_override is True
