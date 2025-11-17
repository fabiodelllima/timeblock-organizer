"""Shared fixtures for query tests."""

from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, EventStatus


@pytest.fixture
def test_engine() -> Engine:
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")

    # Habilitar foreign keys no SQLite (CRÍTICO para RESTRICT)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(  # noqa: ARG001
        dbapi_conn: Any,
        connection_record: Any,  # noqa: ARG001
    ) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def sample_event(test_engine: Engine) -> Event:
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


@pytest.fixture
def session(test_engine: Engine) -> Generator[Session]:
    """Sessão de banco de dados para testes."""
    with Session(test_engine) as session:
        yield session
        session.rollback()
