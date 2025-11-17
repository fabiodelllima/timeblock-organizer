"""Fixtures para testes de integração."""

from datetime import UTC, datetime, time

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, create_engine

from src.timeblock.models import Habit, Recurrence, Routine, Task


@pytest.fixture(scope="function")
def integration_engine():
    """Engine de DB em memória para testes de integração."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, echo=False
    )
    # Criar todas as tabelas
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def integration_session(integration_engine: Engine):
    """Sessão de DB para testes de integração."""
    with Session(integration_engine) as session:
        yield session


@pytest.fixture
def test_db(integration_session: Session):
    """Alias para integration_session (compatibilidade)."""
    return integration_session


@pytest.fixture
def sample_routine(integration_session: Session):
    """Rotina de exemplo para testes de integração."""
    routine = Routine(name="Test Routine", is_active=True)
    integration_session.add(routine)
    integration_session.commit()
    integration_session.refresh(routine)
    return routine


@pytest.fixture
def sample_habits(integration_session: Session, sample_routine: Routine):
    """Hábitos de exemplo para testes de integração."""
    habit1 = Habit(
        routine_id=sample_routine.id,
        title="Exercise",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    habit2 = Habit(
        routine_id=sample_routine.id,
        title="Reading",
        scheduled_start=time(20, 0),
        scheduled_end=time(21, 0),
        recurrence=Recurrence.WEEKDAYS,
    )
    integration_session.add(habit1)
    integration_session.add(habit2)
    integration_session.commit()
    integration_session.refresh(habit1)
    integration_session.refresh(habit2)
    return [habit1, habit2]


@pytest.fixture
def sample_task(integration_session: Session):
    """Task de exemplo para testes de integração."""
    task = Task(
        title="Dentist Appointment",
        scheduled_datetime=datetime.now(UTC),
    )
    integration_session.add(task)
    integration_session.commit()
    integration_session.refresh(task)
    return task
