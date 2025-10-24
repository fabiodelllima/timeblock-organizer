"""Tests for EventReorderingService priority calculation."""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, EventStatus, Task
from src.timeblock.services.event_reordering_models import Conflict, ConflictType, EventPriority
from src.timeblock.services.event_reordering_service import EventReorderingService


@pytest.fixture
def test_engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(test_engine):
    """Session fixture."""
    with Session(test_engine) as session:
        yield session


class TestCalculatePriorities:
    """Tests for calculate_priorities."""

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_in_progress_is_critical(self, mock_context, test_engine, session):
        """IN_PROGRESS events get CRITICAL priority."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        event = Event(
            title="Event 1",
            status=EventStatus.IN_PROGRESS,
            scheduled_start=datetime(2025, 10, 24, 10, 0),
            scheduled_end=datetime(2025, 10, 24, 11, 0),
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        conflicts = [
            Conflict(
                triggered_event_id=1,
                triggered_event_type="event",
                conflicting_event_id=event.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=datetime(2025, 10, 24, 10, 0),
                triggered_end=datetime(2025, 10, 24, 11, 0),
                conflicting_start=datetime(2025, 10, 24, 10, 30),
                conflicting_end=datetime(2025, 10, 24, 11, 30),
            )
        ]
        
        priorities = EventReorderingService.calculate_priorities(conflicts)
        assert priorities[(event.id, "event")] == EventPriority.CRITICAL

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_paused_is_high(self, mock_context, test_engine, session):
        """PAUSED events get HIGH priority."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        event = Event(
            title="Event 1",
            status=EventStatus.PAUSED,
            scheduled_start=datetime(2025, 10, 24, 10, 0),
            scheduled_end=datetime(2025, 10, 24, 11, 0),
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        conflicts = [
            Conflict(
                triggered_event_id=1,
                triggered_event_type="event",
                conflicting_event_id=event.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=datetime(2025, 10, 24, 10, 0),
                triggered_end=datetime(2025, 10, 24, 11, 0),
                conflicting_start=datetime(2025, 10, 24, 10, 30),
                conflicting_end=datetime(2025, 10, 24, 11, 30),
            )
        ]
        
        priorities = EventReorderingService.calculate_priorities(conflicts)
        assert priorities[(event.id, "event")] == EventPriority.HIGH

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_planned_soon_is_normal(self, mock_context, test_engine, session):
        """PLANNED events starting < 1h get NORMAL priority."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        now = datetime.now()
        event = Event(
            title="Event 1",
            status=EventStatus.PLANNED,
            scheduled_start=now + timedelta(minutes=30),
            scheduled_end=now + timedelta(minutes=90),
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        conflicts = [
            Conflict(
                triggered_event_id=1,
                triggered_event_type="event",
                conflicting_event_id=event.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=now,
                triggered_end=now + timedelta(hours=1),
                conflicting_start=now + timedelta(minutes=30),
                conflicting_end=now + timedelta(minutes=90),
            )
        ]
        
        priorities = EventReorderingService.calculate_priorities(conflicts)
        assert priorities[(event.id, "event")] == EventPriority.NORMAL

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_planned_later_is_low(self, mock_context, test_engine, session):
        """PLANNED events starting > 1h get LOW priority."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        now = datetime.now()
        event = Event(
            title="Event 1",
            status=EventStatus.PLANNED,
            scheduled_start=now + timedelta(hours=2),
            scheduled_end=now + timedelta(hours=3),
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        conflicts = [
            Conflict(
                triggered_event_id=1,
                triggered_event_type="event",
                conflicting_event_id=event.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=now,
                triggered_end=now + timedelta(hours=1),
                conflicting_start=now + timedelta(hours=2),
                conflicting_end=now + timedelta(hours=3),
            )
        ]
        
        priorities = EventReorderingService.calculate_priorities(conflicts)
        assert priorities[(event.id, "event")] == EventPriority.LOW

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_task_deadline_soon_is_critical(self, mock_context, test_engine, session):
        """Task with deadline < 24h gets CRITICAL priority."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        now = datetime.now()
        task = Task(
            title="Task 1",
            scheduled_datetime=now + timedelta(hours=2),
            completed_datetime=now + timedelta(hours=20),
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        conflicts = [
            Conflict(
                triggered_event_id=1,
                triggered_event_type="task",
                conflicting_event_id=task.id,
                conflicting_event_type="task",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=now,
                triggered_end=now + timedelta(hours=1),
                conflicting_start=now + timedelta(hours=2),
                conflicting_end=now + timedelta(hours=3),
            )
        ]
        
        priorities = EventReorderingService.calculate_priorities(conflicts)
        assert priorities[(task.id, "task")] == EventPriority.CRITICAL
