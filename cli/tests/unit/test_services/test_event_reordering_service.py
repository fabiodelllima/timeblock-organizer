"""Tests for EventReorderingService."""
from datetime import datetime, time
from unittest.mock import patch

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, Habit, HabitInstance, Routine, Tag, Task, TimeLog
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


class TestDetectConflicts:
    """Tests for detect_conflicts."""

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_no_conflicts(self, mock_context, test_engine, session):
        """No conflicts when events don't overlap."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        task = Task(title="Task 1", scheduled_datetime=datetime(2025, 10, 24, 10, 0))
        session.add(task)
        session.commit()
        session.refresh(task)

        conflicts = EventReorderingService.detect_conflicts(task.id, "task")
        assert len(conflicts) == 0

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_event_not_found(self, mock_context, test_engine):
        """Returns empty list when event doesn't exist."""
        mock_context.return_value.__enter__.return_value = test_engine
        conflicts = EventReorderingService.detect_conflicts(9999, "task")
        assert len(conflicts) == 0

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_task_overlaps_with_task(self, mock_context, test_engine, session):
        """Detects conflict between two overlapping tasks."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        task1 = Task(title="Task 1", scheduled_datetime=datetime(2025, 10, 24, 10, 0))
        task2 = Task(title="Task 2", scheduled_datetime=datetime(2025, 10, 24, 10, 30))
        session.add(task1)
        session.add(task2)
        session.commit()
        session.refresh(task1)

        conflicts = EventReorderingService.detect_conflicts(task1.id, "task")
        assert len(conflicts) == 1
        assert conflicts[0].conflicting_event_id == task2.id


class TestGetEventTimes:
    """Tests for _get_event_times."""

    def test_task_times(self):
        """Gets correct start/end for Task."""
        task = Task(title="Task 1", scheduled_datetime=datetime(2025, 10, 24, 10, 0))
        start, end = EventReorderingService._get_event_times(task, "task")
        assert start == datetime(2025, 10, 24, 10, 0)
        assert end == datetime(2025, 10, 24, 11, 0)

    def test_habit_instance_times(self):
        """Gets correct start/end for HabitInstance."""
        habit_instance = HabitInstance(
            habit_id=1,
            date=datetime(2025, 10, 24).date(),
            scheduled_start=time(10, 0),
            scheduled_end=time(11, 0),
        )
        start, end = EventReorderingService._get_event_times(habit_instance, "habit_instance")
        assert start == datetime(2025, 10, 24, 10, 0)
        assert end == datetime(2025, 10, 24, 11, 0)


class TestHasOverlap:
    """Tests for _has_overlap."""

    def test_no_overlap_before(self):
        start1 = datetime(2025, 10, 24, 10, 0)
        end1 = datetime(2025, 10, 24, 11, 0)
        start2 = datetime(2025, 10, 24, 11, 0)
        end2 = datetime(2025, 10, 24, 12, 0)
        assert not EventReorderingService._has_overlap(start1, end1, start2, end2)

    def test_no_overlap_after(self):
        start1 = datetime(2025, 10, 24, 12, 0)
        end1 = datetime(2025, 10, 24, 13, 0)
        start2 = datetime(2025, 10, 24, 10, 0)
        end2 = datetime(2025, 10, 24, 11, 0)
        assert not EventReorderingService._has_overlap(start1, end1, start2, end2)

    def test_partial_overlap(self):
        start1 = datetime(2025, 10, 24, 10, 0)
        end1 = datetime(2025, 10, 24, 11, 30)
        start2 = datetime(2025, 10, 24, 11, 0)
        end2 = datetime(2025, 10, 24, 12, 0)
        assert EventReorderingService._has_overlap(start1, end1, start2, end2)

    def test_complete_overlap(self):
        start1 = datetime(2025, 10, 24, 10, 0)
        end1 = datetime(2025, 10, 24, 12, 0)
        start2 = datetime(2025, 10, 24, 10, 30)
        end2 = datetime(2025, 10, 24, 11, 30)
        assert EventReorderingService._has_overlap(start1, end1, start2, end2)
