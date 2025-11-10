"""Testes para comando reschedule."""
from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Task
from src.timeblock.services.event_reordering_service import EventReorderingService


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

    monkeypatch.setattr("src.timeblock.services.event_reordering_service.get_engine_context", mock_get_engine)


def test_reschedule_no_conflicts(test_engine):
    """Reschedule sem conflitos."""
    with Session(test_engine) as session:
        task = Task(title="Task", scheduled_datetime=datetime(2025, 10, 26, 10, 0))
        session.add(task)
        session.commit()
        session.refresh(task)

    conflicts = EventReorderingService.detect_conflicts(task.id, "task")
    assert len(conflicts) == 0


def test_reschedule_with_conflicts(test_engine):
    """Reschedule detecta conflitos."""
    with Session(test_engine) as session:
        task1 = Task(title="Task1", scheduled_datetime=datetime(2025, 10, 26, 10, 0))
        task2 = Task(title="Task2", scheduled_datetime=datetime(2025, 10, 26, 10, 30))
        session.add_all([task1, task2])
        session.commit()
        session.refresh(task1)

    conflicts = EventReorderingService.detect_conflicts(task1.id, "task")
    assert len(conflicts) > 0


def test_preview_only_displays(test_engine):
    """Preview não altera nada."""
    with Session(test_engine) as session:
        task1 = Task(title="Task1", scheduled_datetime=datetime(2025, 10, 26, 10, 0))
        task2 = Task(title="Task2", scheduled_datetime=datetime(2025, 10, 26, 10, 30))
        session.add_all([task1, task2])
        session.commit()
        session.refresh(task1)
        session.refresh(task2)
        task1_id = task1.id
        task2_id = task2.id
        original_time = task2.scheduled_datetime

    conflicts = EventReorderingService.detect_conflicts(task1_id, "task")
    proposal = EventReorderingService.propose_reordering(conflicts)

    with Session(test_engine) as session:
        task2_after = session.get(Task, task2_id)
        assert task2_after.scheduled_datetime == original_time
