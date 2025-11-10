"""Tests for HabitInstance model."""

from datetime import date, time

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance, HabitInstanceStatus
from src.timeblock.models.routine import Routine


@pytest.fixture
def engine():
    """In-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()  # FIX: Fechar conexões


@pytest.fixture
def session(engine):
    """Database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def habit(session):
    """Create test habit."""
    routine = Routine(name="Test")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Exercise",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


def test_habit_instance_creation(session, habit):
    """Test creating a habit instance."""
    instance = HabitInstance(
        habit_id=habit.id,
        date=date(2025, 10, 16),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)

    assert instance.id is not None
    assert instance.date == date(2025, 10, 16)
    assert instance.status == HabitInstanceStatus.PLANNED  # FIX: Usar enum
    assert instance.manually_adjusted is False


def test_habit_instance_manually_adjusted(session, habit):
    """Test manually adjusted instance."""
    instance = HabitInstance(
        habit_id=habit.id,
        date=date(2025, 10, 16),
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        manually_adjusted=True,
    )
    session.add(instance)
    session.commit()

    assert instance.manually_adjusted is True


# NOTA: test_habit_instance_with_actuals REMOVIDO
# RAZÃO: Campos actual_start/actual_end não existem no modelo atual
# TODO: Se necessário, implementar em v1.3.0 como feature de tracking
