"""Shared fixtures for query tests."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, EventStatus


@pytest.fixture
def test_engine():
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def sample_event(test_engine):
    """Cria evento de exemplo para testes."""
    with Session(test_engine) as session:
        event = Event(
            title="Sample Event",
            scheduled_start=datetime.now(UTC),
            scheduled_end=datetime.now(UTC) + timedelta(hours=1),
            status=EventStatus.PLANNED,
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
