"""Shared fixtures for query tests."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, time
from typing import TYPE_CHECKING, Any

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import (
    Event,
    Habit,
    Recurrence,
)
from src.timeblock.models.enums import Status
from src.timeblock.services.routine_service import RoutineService

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def test_engine() -> Engine:
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(
        dbapi_conn: Any,
        connection_record: Any,
    ) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(test_engine: Engine) -> Generator[Session]:
    """Sessão de banco de dados para testes."""
    with Session(test_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def test_db(session: Session) -> Session:
    """Alias para session (compatibilidade com testes antigos)."""
    return session


@pytest.fixture
def routine_service(session: Session) -> RoutineService:
    """Fixture que retorna instância de RoutineService."""
    return RoutineService(session)


@pytest.fixture
def habit_service_helper(
    test_engine: Engine,
) -> Callable[..., Habit]:
    """Helper para criar habits no test_engine."""

    def _create_habit(
        routine_id: int,
        title: str,
        scheduled_start: time,
        scheduled_end: time,
        recurrence: Recurrence,
        color: str | None = None,
    ) -> Habit:
        from src.timeblock.services.habit_service import HabitService

        return HabitService.create_habit(
            routine_id=routine_id,
            title=title,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            recurrence=recurrence,
            color=color,
        )

    return _create_habit


@pytest.fixture
def routine_delete_helper(
    session: Session,
) -> Callable[[int], None]:
    """Helper para deletar routines no test_engine."""

    def _delete_routine(routine_id: int) -> None:
        service = RoutineService(session)
        service.delete_routine(routine_id)

    return _delete_routine


@pytest.fixture
def sample_time_start() -> time:
    """Fixture que retorna hora de início padrão."""
    return time(9, 0)


@pytest.fixture
def sample_time_end() -> time:
    """Fixture que retorna hora de fim padrão."""
    return time(10, 0)


@pytest.fixture
def sample_date() -> datetime:
    """Fixture que retorna data padrão."""
    return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


@pytest.fixture
def sample_event(
    session: Session,
    sample_time_start: time,
    sample_time_end: time,
    sample_date: datetime,
) -> Event:
    """Fixture que cria um evento de exemplo."""
    event = Event(
        title="Sample Event",
        scheduled_datetime=sample_date,
        scheduled_start=sample_time_start,
        scheduled_end=sample_time_end,
        status=Status.PENDING,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@pytest.fixture
def mock_session(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Mock de session para testes de services."""
    from unittest.mock import Mock

    session = Mock()
    session.get.return_value = None
    session.exec.return_value.all.return_value = []
    session.commit.return_value = None
    return session
