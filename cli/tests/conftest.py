"""Global pytest configuration."""

from pathlib import Path

import pytest

from src.timeblock.database import create_db_and_tables


@pytest.fixture(scope="session", autouse=True)
def backup_real_db():
    """Backup real database before tests, restore after."""
    real_db = Path("data/timeblock.db")
    backup = Path("data/timeblock.db.backup")
    # Backup if exists
    if real_db.exists():
        real_db.rename(backup)
    yield
    # Restore
    if backup.exists():
        if real_db.exists():
            real_db.unlink()
        backup.rename(real_db)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create temporary test database with tables."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()
    yield db_path
"""Shared fixtures for query tests."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, EventStatus


@pytest.fixture(scope="function")
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def now_time():
    """Fixed datetime for consistent testing."""
    return datetime.now(UTC)


@pytest.fixture
def sample_events(test_db, now_time):
    """Populate database with 5 sample events."""
    events = [
        Event(
            title="Event 1",
            scheduled_start=now_time - timedelta(days=2),
            scheduled_end=now_time - timedelta(days=2, hours=-1),
            status=EventStatus.COMPLETED,
        ),
        Event(
            title="Event 2",
            scheduled_start=now_time - timedelta(days=1),
            scheduled_end=now_time - timedelta(days=1, hours=-1),
            status=EventStatus.COMPLETED,
        ),
        Event(
            title="Event 3",
            scheduled_start=now_time,
            scheduled_end=now_time + timedelta(hours=1),
            status=EventStatus.PLANNED,
        ),
        Event(
            title="Event 4",
            scheduled_start=now_time + timedelta(days=1),
            scheduled_end=now_time + timedelta(days=1, hours=1),
            status=EventStatus.PLANNED,
        ),
        Event(
            title="Event 5",
            scheduled_start=now_time + timedelta(days=2),
            scheduled_end=now_time + timedelta(days=2, hours=1),
            status=EventStatus.PLANNED,
        ),
    ]

    with Session(test_db) as session:
        for event in events:
            session.add(event)
        session.commit()

    return events
