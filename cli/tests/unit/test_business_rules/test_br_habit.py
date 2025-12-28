"""Testes unitários para Business Rules de Habit.

Valida as 5 BRs principais:
- BR-HABIT-001: Title Validation
- BR-HABIT-002: Time Range Validation
- BR-HABIT-003: Routine Association
- BR-HABIT-004: Recurrence Pattern
- BR-HABIT-005: Optional Color
"""

from datetime import time

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.timeblock.models import Habit, Recurrence
from src.timeblock.services.habit_service import HabitService


class TestBRHabit001TitleValidation:
    """BR-HABIT-001: Title Validation."""

    def test_br_habit_001_empty_title_rejected(self, session, routine_service):
        """BR-HABIT-001: Título vazio deve ser rejeitado."""
        routine = routine_service.create_routine("Test Routine")

        with pytest.raises(ValueError, match="cannot be empty"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="   ",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
                session=session,
            )

    def test_br_habit_001_long_title_rejected(self, session, routine_service):
        """BR-HABIT-001: Título > 200 caracteres deve ser rejeitado."""
        routine = routine_service.create_routine("Test Routine")

        with pytest.raises(ValueError, match="cannot exceed 200"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="A" * 201,
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
                session=session,
            )

    def test_br_habit_001_whitespace_trimmed(self, session, routine_service):
        """BR-HABIT-001: Whitespace deve ser removido automaticamente."""
        routine = routine_service.create_routine("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="  Morning Meditation  ",
            scheduled_start=time(6, 0),
            scheduled_end=time(7, 0),
            recurrence=Recurrence.EVERYDAY,
            session=session,
        )

        assert habit.title == "Morning Meditation"


class TestBRHabit002TimeRangeValidation:
    """BR-HABIT-002: Time Range Validation."""

    def test_br_habit_002_start_before_end_required(self, session, routine_service):
        """BR-HABIT-002: Start deve ser antes de end."""
        routine = routine_service.create_routine("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Valid Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
            session=session,
        )

        assert habit.scheduled_start < habit.scheduled_end

    def test_br_habit_002_equal_times_rejected(self, session, routine_service):
        """BR-HABIT-002: Start == end é inválido."""
        routine = routine_service.create_routine("Test Routine")

        with pytest.raises(ValueError, match="Start time must be before"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="Invalid Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(9, 0),
                recurrence=Recurrence.EVERYDAY,
                session=session,
            )

    def test_br_habit_002_end_before_start_rejected(self, session, routine_service):
        """BR-HABIT-002: End antes de start é inválido."""
        routine = routine_service.create_routine("Test Routine")

        with pytest.raises(ValueError, match="Start time must be before"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="Invalid Habit",
                scheduled_start=time(10, 0),
                scheduled_end=time(9, 0),
                recurrence=Recurrence.EVERYDAY,
                session=session,
            )


class TestBRHabit003RoutineAssociation:
    """BR-HABIT-003: Routine Association."""

    def test_br_habit_003_requires_routine_id(self, test_engine):
        """BR-HABIT-003: routine_id é obrigatório."""
        with Session(test_engine) as session:
            with pytest.raises(IntegrityError):
                habit = Habit(
                    title="Orphan Habit",
                    scheduled_start=time(9, 0),
                    scheduled_end=time(10, 0),
                    recurrence=Recurrence.EVERYDAY,
                )
                session.add(habit)
                session.commit()

    def test_br_habit_003_invalid_routine_rejected(self, session):
        """BR-HABIT-003: routine_id deve existir."""
        with pytest.raises(IntegrityError):
            HabitService.create_habit(
                routine_id=99999,
                title="Invalid Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
                session=session,
            )


class TestBRHabit004RecurrencePattern:
    """BR-HABIT-004: Recurrence Pattern."""

    def test_br_habit_004_valid_recurrence_accepted(self, session, routine_service):
        """BR-HABIT-004: Todos padrões válidos devem ser aceitos."""
        routine = routine_service.create_routine("Test Routine")

        valid_patterns = [
            Recurrence.MONDAY,
            Recurrence.WEEKDAYS,
            Recurrence.WEEKENDS,
            Recurrence.EVERYDAY,
        ]

        for pattern in valid_patterns:
            habit = HabitService.create_habit(
                routine_id=routine.id,
                title=f"Habit {pattern.value}",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=pattern,
                session=session,
            )
            assert habit.recurrence == pattern

    def test_br_habit_004_invalid_recurrence_rejected(self, session, routine_service):
        """BR-HABIT-004: String inválida deve ser rejeitada."""
        routine = routine_service.create_routine("Test Routine")

        with pytest.raises(ValueError):
            habit = Habit(
                routine_id=routine.id,
                title="Invalid Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence="INVALID_PATTERN",  # type: ignore
            )
            session.add(habit)
            session.commit()


class TestBRHabit005OptionalColor:
    """BR-HABIT-005: Optional Color."""

    def test_br_habit_005_color_optional(self, session, routine_service):
        """BR-HABIT-005: Color é opcional."""
        routine = routine_service.create_routine("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="No Color Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
            session=session,
        )

        assert habit.color is None

    def test_br_habit_005_valid_hex_color(self, session, routine_service):
        """BR-HABIT-005: Hex color válido é aceito."""
        routine = routine_service.create_routine("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Colored Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
            color="#FF5733",
            session=session,
        )

        assert habit.color == "#FF5733"
