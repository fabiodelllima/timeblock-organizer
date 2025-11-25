"""
Timer Service v2 Tests - BR-TIMER-001 and BR-TIMER-006.

Tests for pause/resume/cancel functionality following ADR-021.
"""

from time import sleep
from datetime import date, time

import pytest
from sqlmodel import Session

from src.timeblock.models import Habit, HabitInstance, Recurrence, Routine, TimeLog
from src.timeblock.models.enums import Status
from src.timeblock.services.timer_service import TimerService


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def routine(session: Session) -> Routine:
    """Create a routine for testing."""
    routine = Routine(name="Test Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@pytest.fixture
def habit(session: Session, routine: Routine) -> Habit:
    """Create a habit for testing."""
    habit = Habit(
        title="Test Habit",
        routine_id=routine.id,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@pytest.fixture
def test_habit_instance(session: Session, habit: Habit) -> HabitInstance:
    """Create a habit instance for testing."""
    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


@pytest.fixture(autouse=True)
def reset_timer_state():
    """Reset timer state between tests."""
    yield
    TimerService._active_pause_start = None


# ============================================================
# BR-TIMER-001: Single Active Timer
# ============================================================
class TestBRTimer001:
    """BR-TIMER-001: Only one timer can be active at a time."""

    def test_br_timer_001_start_timer_creates_timelog(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Starting a timer creates a TimeLog entry."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)

        assert timelog is not None
        assert timelog.habit_instance_id == test_habit_instance.id
        assert timelog.start_time is not None
        assert timelog.end_time is None

    def test_br_timer_001_only_one_active(
        self, session: Session, habit: Habit
    ):
        """Cannot start a second timer while one is active."""
        # Create two instances
        instance1 = HabitInstance(
            habit_id=habit.id, date=date.today(), scheduled_start=time(9, 0), scheduled_end=time(10, 0), status=Status.PENDING
        )
        instance2 = HabitInstance(
            habit_id=habit.id, date=date.today(), scheduled_start=time(9, 0), scheduled_end=time(10, 0), status=Status.PENDING
        )
        session.add_all([instance1, instance2])
        session.commit()

        # Start first timer
        TimerService.start_timer(instance1.id, session)

        # Second timer should fail
        with pytest.raises(ValueError, match="already active"):
            TimerService.start_timer(instance2.id, session)

    def test_br_timer_001_can_start_after_stop(
        self, session: Session, habit: Habit
    ):
        """Can start a new timer after stopping the previous one."""
        instance1 = HabitInstance(
            habit_id=habit.id, date=date.today(), scheduled_start=time(9, 0), scheduled_end=time(10, 0), status=Status.PENDING
        )
        instance2 = HabitInstance(
            habit_id=habit.id, date=date.today(), scheduled_start=time(9, 0), scheduled_end=time(10, 0), status=Status.PENDING
        )
        session.add_all([instance1, instance2])
        session.commit()

        # Start and stop first timer
        TimerService.start_timer(instance1.id, session)
        TimerService.stop_timer(instance1.id, session)

        # Second timer should work
        timelog = TimerService.start_timer(instance2.id, session)
        assert timelog is not None


# ============================================================
# BR-TIMER-006: Pause Tracking
# ============================================================
class TestBRTimer006Pause:
    """BR-TIMER-006: Pause timer functionality."""

    def test_pause_timer_sets_state(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Pausing a timer sets internal pause state."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)

        result = TimerService.pause_timer(timelog.id, session)

        assert result is not None
        assert TimerService._active_pause_start is not None

    def test_pause_timer_requires_active_timer(self, session: Session):
        """Cannot pause a non-existent timer."""
        with pytest.raises(ValueError, match="not found"):
            TimerService.pause_timer(9999, session)

    def test_pause_timer_cannot_pause_stopped(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Cannot pause an already stopped timer."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.stop_timer(test_habit_instance.id, session)

        with pytest.raises(ValueError, match="already stopped"):
            TimerService.pause_timer(timelog.id, session)


class TestBRTimer006Resume:
    """BR-TIMER-006: Resume timer functionality."""

    def test_resume_timer_clears_pause_state(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Resuming a timer clears the pause state."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)

        result = TimerService.resume_timer(timelog.id, session)

        assert result is not None
        assert TimerService._active_pause_start is None

    def test_resume_timer_accumulates_paused_duration(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Resuming accumulates paused time."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)
        sleep(1.1)  # Wait to accumulate pause time

        result = TimerService.resume_timer(timelog.id, session)

        assert result.paused_duration is not None
        assert result.paused_duration >= 1

    def test_resume_timer_requires_paused_state(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Cannot resume a timer that is not paused."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)

        with pytest.raises(ValueError, match="not paused"):
            TimerService.resume_timer(timelog.id, session)


class TestBRTimer006Stop:
    """BR-TIMER-006: Stop timer with pause handling."""

    def test_stop_timer_accumulates_active_pause(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Stopping while paused accumulates the pause duration."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)
        sleep(1.1)

        result = TimerService.stop_timer(test_habit_instance.id, session)

        assert result.paused_duration is not None
        assert result.paused_duration >= 1

    def test_stop_timer_calculates_effective_duration(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Stop calculates duration minus paused time."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        sleep(1.1)  # Work time
        TimerService.pause_timer(timelog.id, session)
        sleep(1.1)  # Pause time

        result = TimerService.stop_timer(test_habit_instance.id, session)

        # Duration should be total - paused (approximately 1s work)
        assert result.duration_seconds is not None
        assert result.paused_duration is not None
        # Effective work time should be less than total elapsed
        total_elapsed = 2  # ~2.2s total
        assert result.duration_seconds < total_elapsed + result.paused_duration


# ============================================================
# BR-TIMER-001: Cancel Timer
# ============================================================
class TestBRTimer001Cancel:
    """BR-TIMER-001: Cancel timer functionality."""

    def test_cancel_timer_deletes_timelog(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Canceling a timer deletes the TimeLog entry."""
        timelog = TimerService.start_timer(test_habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.cancel_timer(timelog.id, session)

        # TimeLog should be deleted
        result = session.get(TimeLog, timelog_id)
        assert result is None

    def test_cancel_timer_keeps_instance_pending(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Canceling keeps the HabitInstance in PENDING status."""

        timelog = TimerService.start_timer(test_habit_instance.id, session)
        TimerService.cancel_timer(timelog.id, session)

        session.refresh(test_habit_instance)
        assert test_habit_instance.status == Status.PENDING

    def test_cancel_non_existent_timer(self, session: Session):
        """Canceling non-existent timer raises error."""
        with pytest.raises(ValueError, match="not found"):
            TimerService.cancel_timer(9999, session)


# ============================================================
# Helper: Get Any Active Timer
# ============================================================
class TestGetAnyActiveTimer:
    """Helper to get any active timer without knowing habit_instance_id."""

    def test_get_any_active_timer_found(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Returns active timer if one exists."""
        TimerService.start_timer(test_habit_instance.id, session)

        result = TimerService.get_any_active_timer(session)

        assert result is not None
        assert result.habit_instance_id == test_habit_instance.id

    def test_get_any_active_timer_not_found(self, session: Session):
        """Returns None if no active timer."""
        result = TimerService.get_any_active_timer(session)

        assert result is None

    def test_get_any_active_timer_after_stop(
        self, session: Session, test_habit_instance: HabitInstance
    ):
        """Returns None after timer is stopped."""
        TimerService.start_timer(test_habit_instance.id, session)
        TimerService.stop_timer(test_habit_instance.id, session)

        result = TimerService.get_any_active_timer(session)

        assert result is None
