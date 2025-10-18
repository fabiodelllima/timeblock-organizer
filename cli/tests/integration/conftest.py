"""Fixtures para testes de integração."""

from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, create_engine


@pytest.fixture(scope="function")
def integration_engine():
    """Engine de DB em memória para testes de integração."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, echo=False
    )

    # Criar todas as tabelas diretamente
    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def integration_session(integration_engine):
    """Sessão de DB para testes de integração."""
    with Session(integration_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def sample_routine(integration_session):
    """Rotina de exemplo para testes."""
    from src.timeblock.models.routine import Routine

    routine = Routine(name="Test Routine", is_active=True, created_at=datetime.now())
    integration_session.add(routine)
    integration_session.commit()
    integration_session.refresh(routine)
    return routine


@pytest.fixture
def sample_habits(integration_session, sample_routine):
    """Lista de hábitos de exemplo."""
    from datetime import time

    from src.timeblock.models.habit import Habit, Recurrence

    habits = [
        Habit(
            routine_id=sample_routine.id,
            title="Exercise",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.WEEKDAYS,
            color="#FF5733",
        ),
        Habit(
            routine_id=sample_routine.id,
            title="Reading",
            scheduled_start=time(20, 0),
            scheduled_end=time(21, 0),
            recurrence=Recurrence.EVERYDAY,
            color="#33C4FF",
        ),
    ]
    for habit in habits:
        integration_session.add(habit)
    integration_session.commit()
    for habit in habits:
        integration_session.refresh(habit)
    return habits


@pytest.fixture
def sample_task(integration_session):
    """Task de exemplo para testes."""
    from src.timeblock.models.task import Task

    task = Task(
        title="Dentist Appointment",
        scheduled_datetime=datetime(2025, 10, 20, 14, 0),
        description="Regular checkup",
    )
    integration_session.add(task)
    integration_session.commit()
    integration_session.refresh(task)
    return task
