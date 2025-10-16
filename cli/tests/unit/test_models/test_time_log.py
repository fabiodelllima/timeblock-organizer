"""Tests for TimeLog model."""
from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models.time_log import TimeLog


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


def test_time_log_creation(session):
    """Test creating a time log."""
    log = TimeLog(
        start_time=datetime(2025, 10, 16, 7, 0),
        end_time=datetime(2025, 10, 16, 8, 0),
        duration_seconds=3600,
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    assert log.id is not None
    assert log.duration_seconds == 3600


def test_time_log_with_notes(session):
    """Test time log with notes."""
    log = TimeLog(
        start_time=datetime(2025, 10, 16, 9, 0),
        notes="Productive session",
    )
    session.add(log)
    session.commit()

    assert log.notes == "Productive session"


def test_time_log_in_progress(session):
    """Test time log without end time."""
    log = TimeLog(start_time=datetime(2025, 10, 16, 10, 0))
    session.add(log)
    session.commit()

    assert log.end_time is None
    assert log.duration_seconds is None
