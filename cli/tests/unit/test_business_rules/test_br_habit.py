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

from src.timeblock.models import Habit, Recurrence, Routine
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService


class TestBRHabit001TitleValidation:
    """BR-HABIT-001: Title Validation."""

    def test_br_habit_001_empty_title_rejected(self, test_engine, routine_service):
        """BR-HABIT-001: Título vazio deve ser rejeitado."""
        routine = routine_service("Test Routine")

        with pytest.raises(ValueError, match="cannot be empty"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="   ",  # Apenas espaços
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_001_long_title_rejected(self, test_engine, routine_service):
        """BR-HABIT-001: Título > 200 caracteres deve ser rejeitado."""
        routine = routine_service("Test Routine")

        with pytest.raises(ValueError, match="cannot exceed 200"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="A" * 201,
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_001_whitespace_trimmed(self, test_engine, routine_service):
        """BR-HABIT-001: Whitespace deve ser removido automaticamente."""
        routine = routine_service("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="  Morning Meditation  ",
            scheduled_start=time(6, 0),
            scheduled_end=time(7, 0),
            recurrence=Recurrence.EVERYDAY,
        )

        assert habit.title == "Morning Meditation"  # Sem espaços


class TestBRHabit002TimeRangeValidation:
    """BR-HABIT-002: Time Range Validation."""

    def test_br_habit_002_start_before_end_required(self, test_engine, routine_service):
        """BR-HABIT-002: Start deve ser antes de end."""
        routine = routine_service("Test Routine")

        # Válido: start < end
        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Valid Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
        )

        assert habit.scheduled_start < habit.scheduled_end

    def test_br_habit_002_equal_times_rejected(self, test_engine, routine_service):
        """BR-HABIT-002: Start == end é inválido."""
        routine = routine_service("Test Routine")

        with pytest.raises(ValueError, match="Start time must be before"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="Invalid Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(9, 0),  # Igual
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_002_end_before_start_rejected(self, test_engine, routine_service):
        """BR-HABIT-002: End antes de start é inválido."""
        routine = routine_service("Test Routine")

        with pytest.raises(ValueError, match="Start time must be before"):
            HabitService.create_habit(
                routine_id=routine.id,
                title="Invalid Habit",
                scheduled_start=time(10, 0),
                scheduled_end=time(9, 0),  # Antes
                recurrence=Recurrence.EVERYDAY,
            )


class TestBRHabit003RoutineAssociation:
    """BR-HABIT-003: Routine Association."""

    def test_br_habit_003_requires_routine_id(self, test_engine, routine_service):
        """BR-HABIT-003: routine_id é obrigatório."""
        # Tentar criar Habit diretamente sem routine_id
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

    def test_br_habit_003_invalid_routine_rejected(self, test_engine, routine_service):
        """BR-HABIT-003: routine_id deve existir."""
        with pytest.raises(IntegrityError):
            HabitService.create_habit(
                routine_id=99999,  # ID inexistente
                title="Invalid Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_003_routine_delete_blocked(self, test_engine, routine_service, routine_delete_helper, habit_service_helper):
        """BR-HABIT-003: Delete routine com habits é bloqueado."""
        routine = routine_service("Test Routine")

        habit_service_helper(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
        )

        # Tentar deletar routine deve falhar
        with pytest.raises(IntegrityError):
            routine_delete_helper(routine.id)


class TestBRHabit004RecurrencePattern:
    """BR-HABIT-004: Recurrence Pattern."""

    def test_br_habit_004_valid_recurrence_accepted(self, test_engine, routine_service):
        """BR-HABIT-004: Todos padrões válidos devem ser aceitos."""
        routine = routine_service("Test Routine")

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
            )
            assert habit.recurrence == pattern

    def test_br_habit_004_invalid_recurrence_rejected(self, test_engine, routine_service):
        """BR-HABIT-004: String inválida deve ser rejeitada."""
        routine = routine_service("Test Routine")

        # Tentar criar com string inválida diretamente
        with Session(test_engine) as session:
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

    def test_br_habit_005_color_optional(self, test_engine, routine_service):
        """BR-HABIT-005: Color é opcional."""
        routine = routine_service("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="No Color Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
        )

        assert habit.color is None

    def test_br_habit_005_valid_hex_color(self, test_engine, routine_service):
        """BR-HABIT-005: Hex color válido é aceito."""
        routine = routine_service("Test Routine")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Colored Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
            color="#FF5733",
        )

        assert habit.color == "#FF5733"
