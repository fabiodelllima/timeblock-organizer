"""Testes para HabitService - operações CRUD."""

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


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr("src.timeblock.services.habit_service.get_engine_context", mock_get_engine)


class TestCreateHabit:
    """Testes para create_habit."""

    def test_create_habit_success(self, test_routine):
        """Cria hábito com sucesso."""
        habit = HabitService.create_habit(
            routine_id=test_routine.id,
            title="Exercício",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        assert habit.id is not None
        assert habit.title == "Exercício"
        assert habit.routine_id == test_routine.id

    def test_create_habit_with_color(self, test_routine):
        """Cria hábito com cor."""
        habit = HabitService.create_habit(
            routine_id=test_routine.id,
            title="Meditação",
            scheduled_start=time(6, 0),
            scheduled_end=time(6, 30),
            recurrence=Recurrence.WEEKDAYS,
            color="#FF5733",
        )
        assert habit.color == "#FF5733"

    def test_create_habit_strips_whitespace(self, test_routine):
        """Remove espaços do título."""
        habit = HabitService.create_habit(
            routine_id=test_routine.id,
            title="  Leitura  ",
            scheduled_start=time(20, 0),
            scheduled_end=time(21, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        assert habit.title == "Leitura"

    def test_create_habit_with_empty_title(self, test_routine):
        """Rejeita título vazio."""
        with pytest.raises(ValueError, match="cannot be empty"):
            HabitService.create_habit(
                routine_id=test_routine.id,
                title="   ",
                scheduled_start=time(10, 0),
                scheduled_end=time(11, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_create_habit_with_title_too_long(self, test_routine):
        """Rejeita título muito longo."""
        with pytest.raises(ValueError, match="cannot exceed 200"):
            HabitService.create_habit(
                routine_id=test_routine.id,
                title="X" * 201,
                scheduled_start=time(10, 0),
                scheduled_end=time(11, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_create_habit_with_invalid_times(self, test_routine):
        """Rejeita start >= end."""
        with pytest.raises(ValueError, match="Start time must be before end time"):
            HabitService.create_habit(
                routine_id=test_routine.id,
                title="Inválido",
                scheduled_start=time(10, 0),
                scheduled_end=time(9, 0),
                recurrence=Recurrence.EVERYDAY,
            )


class TestGetHabit:
    """Testes para get_habit."""

    def test_get_habit_found(self, test_routine):
        """Busca hábito existente."""
        created = HabitService.create_habit(
            routine_id=test_routine.id,
            title="Yoga",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        found = HabitService.get_habit(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.title == "Yoga"

    def test_get_habit_not_found(self):
        """Retorna None para ID inexistente."""
        assert HabitService.get_habit(9999) is None


class TestListHabits:
    """Testes para list_habits."""

    def test_list_habits_all(self, test_routine, test_engine):
        """Lista todos os hábitos."""
        with Session(test_engine) as session:
            routine2 = Routine(name="Routine 2", is_active=True)
            session.add(routine2)
            session.commit()
            session.refresh(routine2)

            HabitService.create_habit(
                routine_id=test_routine.id,
                title="Habit 1",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            HabitService.create_habit(
                routine_id=routine2.id,
                title="Habit 2",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.WEEKDAYS,
            )

        habits = HabitService.list_habits()
        assert len(habits) == 2

    def test_list_habits_by_routine(self, test_routine, test_engine):
        """Filtra hábitos por rotina."""
        with Session(test_engine) as session:
            routine2 = Routine(name="Routine 2", is_active=True)
            session.add(routine2)
            session.commit()
            session.refresh(routine2)

            HabitService.create_habit(
                routine_id=test_routine.id,
                title="Habit 1",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            HabitService.create_habit(
                routine_id=routine2.id,
                title="Habit 2",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.WEEKDAYS,
            )

        habits = HabitService.list_habits(routine_id=test_routine.id)
        assert len(habits) == 1
        assert habits[0].routine_id == test_routine.id

    def test_list_habits_empty(self):
        """Retorna lista vazia."""
        assert HabitService.list_habits() == []
