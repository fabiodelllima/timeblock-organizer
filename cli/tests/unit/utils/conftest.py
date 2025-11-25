"""Fixtures específicas para testes de utils."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, select

from src.timeblock.models.event import Event, EventStatus


@pytest.fixture
def now_time() -> datetime:
    """Datetime de referência para testes."""
    return datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)


@pytest.fixture
def sample_events(test_db: Session, now_time: datetime):
    """Cria 5 eventos de exemplo para testes de query."""
    for i in range(1, 6):
        days_offset = i - 3
        event_datetime = now_time + timedelta(days=days_offset)

        event = Event(
            title=f"Event {i}",
            scheduled_start=event_datetime,
            scheduled_end=event_datetime + timedelta(hours=1),
            status=EventStatus.PLANNED,
        )
        test_db.add(event)

    test_db.commit()

    statement = select(Event)
    results = test_db.exec(statement)
    return results.all()
