"""Tests for Task model."""
from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models.task import Task


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


def test_task_creation(session):
    """Test creating a task."""
    task = Task(
        title="Doctor Appointment",
        scheduled_datetime=datetime(2025, 10, 17, 14, 0),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.id is not None
    assert task.title == "Doctor Appointment"
    assert task.completed_datetime is None


def test_task_completion(session):
    """Test completing a task."""
    task = Task(
        title="Task",
        scheduled_datetime=datetime(2025, 10, 17, 10, 0),
        completed_datetime=datetime(2025, 10, 17, 10, 30),
    )
    session.add(task)
    session.commit()

    assert task.completed_datetime is not None


def test_task_with_description(session):
    """Test task with description and color."""
    task = Task(
        title="Meeting",
        scheduled_datetime=datetime(2025, 10, 17, 15, 0),
        description="Quarterly review",
        color="#FF5733",
    )
    session.add(task)
    session.commit()

    assert task.description == "Quarterly review"
    assert task.color == "#FF5733"
