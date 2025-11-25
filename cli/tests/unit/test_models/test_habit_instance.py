"""Testes para o modelo HabitInstance."""

from datetime import date, time

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance, Status
from src.timeblock.models.routine import Routine


@pytest.fixture
def engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    """Sessão de banco de dados."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def habit(session):
    """Cria hábito de teste."""
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
    """Testa criação de instância de hábito."""
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
    assert instance.status == Status.PENDING
