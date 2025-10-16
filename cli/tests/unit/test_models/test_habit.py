"""Tests for Habit model."""
from datetime import time

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.routine import Routine


@pytest.fixture
def engine():
    """In-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def routine(session):
    """Create test routine."""
    routine = Routine(name="Test Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


def test_habit_creation(session, routine):
    """Test creating a habit."""
    habit = Habit(
        routine_id=routine.id,
        title="Morning Exercise",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.WEEKDAYS,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)

    assert habit.id is not None
    assert habit.title == "Morning Exercise"
    assert habit.scheduled_start == time(7, 0)
    assert habit.scheduled_end == time(8, 0)
    assert habit.recurrence == Recurrence.WEEKDAYS


def test_habit_with_color(session, routine):
    """Test habit with color."""
    habit = Habit(
        routine_id=routine.id,
        title="Test",
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        recurrence=Recurrence.EVERYDAY,
        color="#FF5733",
    )
    session.add(habit)
    session.commit()

    assert habit.color == "#FF5733"


def test_recurrence_enum():
    """Test all recurrence values."""
    assert Recurrence.MONDAY.value == "MONDAY"
    assert Recurrence.WEEKDAYS.value == "WEEKDAYS"
    assert Recurrence.EVERYDAY.value == "EVERYDAY"
