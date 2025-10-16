"""Tests for Routine model."""
from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

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


def test_routine_creation(session):
    """Test creating a routine."""
    routine = Routine(name="Morning Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    assert routine.id is not None
    assert routine.name == "Morning Routine"
    assert routine.is_active is True
    assert isinstance(routine.created_at, datetime)


def test_routine_defaults(session):
    """Test default values."""
    routine = Routine(name="Test")
    session.add(routine)
    session.commit()

    assert routine.is_active is True
    assert routine.created_at is not None


def test_routine_deactivation(session):
    """Test deactivating routine."""
    routine = Routine(name="Test", is_active=False)
    session.add(routine)
    session.commit()

    assert routine.is_active is False
