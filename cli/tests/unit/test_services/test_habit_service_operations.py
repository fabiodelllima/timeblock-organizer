"""Testes para HabitService - operações de update e delete."""

from datetime import time

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Recurrence, Routine
from src.timeblock.services.habit_service import HabitService


@pytest.fixture
def test_engine():
    """Engine SQLite em memória para testes."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_routine(test_engine):
    """Cria rotina de teste."""
    with Session(test_engine) as session:
        routine = Routine(name="Test Routine", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)
        return routine


@pytest.fixture
def test_habit(test_routine):
    """Cria hábito de teste."""
    return HabitService.create_habit(
        routine_id=test_routine.id,
        title="Test Habit",
        scheduled_start=time(10, 0),
        scheduled_end=time(11, 0),
        recurrence=Recurrence.EVERYDAY,
    )


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr("src.timeblock.services.habit_service.get_engine_context", mock_get_engine)


class TestUpdateHabit:
    """Testes para update_habit."""

    def test_update_habit_title(self, test_habit):
        """Atualiza título."""
        updated = HabitService.update_habit(test_habit.id, title="Novo Título")
        assert updated is not None
        assert updated.title == "Novo Título"

    def test_update_habit_times(self, test_habit):
        """Atualiza horários."""
        updated = HabitService.update_habit(
            test_habit.id,
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
        )
        assert updated.scheduled_start == time(8, 0)
        assert updated.scheduled_end == time(9, 0)

    def test_update_habit_recurrence(self, test_habit):
        """Atualiza recorrência."""
        updated = HabitService.update_habit(
            test_habit.id,
            recurrence=Recurrence.WEEKDAYS,
        )
        assert updated.recurrence == Recurrence.WEEKDAYS

    def test_update_habit_color(self, test_habit):
        """Atualiza cor."""
        updated = HabitService.update_habit(test_habit.id, color="#FF5733")
        assert updated.color == "#FF5733"

    def test_update_habit_multiple_fields(self, test_habit):
        """Atualiza múltiplos campos."""
        updated = HabitService.update_habit(
            test_habit.id,
            title="Atualizado",
            scheduled_start=time(6, 0),
            color="#123456",
        )
        assert updated.title == "Atualizado"
        assert updated.scheduled_start == time(6, 0)
        assert updated.color == "#123456"

    def test_update_habit_not_found(self):
        """Retorna None para ID inexistente."""
        assert HabitService.update_habit(9999, title="Teste") is None

    def test_update_habit_with_empty_title(self, test_habit):
        """Rejeita título vazio."""
        with pytest.raises(ValueError, match="cannot be empty"):
            HabitService.update_habit(test_habit.id, title="   ")

    def test_update_habit_with_title_too_long(self, test_habit):
        """Rejeita título muito longo."""
        with pytest.raises(ValueError, match="cannot exceed 200"):
            HabitService.update_habit(test_habit.id, title="X" * 201)

    def test_update_habit_with_invalid_times(self, test_habit):
        """Rejeita start >= end."""
        with pytest.raises(ValueError, match="Start time must be before end time"):
            HabitService.update_habit(
                test_habit.id,
                scheduled_start=time(15, 0),
                scheduled_end=time(14, 0),
            )


class TestDeleteHabit:
    """Testes para delete_habit."""

    def test_delete_habit_success(self, test_habit):
        """Remove hábito com sucesso."""
        assert HabitService.delete_habit(test_habit.id) is True
        assert HabitService.get_habit(test_habit.id) is None

    def test_delete_habit_not_found(self):
        """Retorna False para ID inexistente."""
        assert HabitService.delete_habit(9999) is False
