"""Testes para HabitInstanceService."""

from datetime import date, time

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Habit, Recurrence, Routine
from src.timeblock.services.habit_instance_service import HabitInstanceService


@pytest.fixture
def test_engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_habit(test_engine):
    """Cria hábito de teste."""
    with Session(test_engine) as session:
        routine = Routine(name="Test Routine", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "src.timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )


class TestGenerateInstances:
    """Testes para generate_instances."""

    def test_generate_instances_everyday(self, test_habit):
        """Gera instâncias EVERYDAY."""
        start = date(2025, 10, 20)  # Monday
        end = date(2025, 10, 23)  # Thursday

        instances = HabitInstanceService.generate_instances(test_habit.id, start, end)

        assert len(instances) == 4
        assert all(i.habit_id == test_habit.id for i in instances)

    def test_generate_instances_weekdays(self, test_engine, test_habit):
        """Gera instâncias WEEKDAYS."""
        with Session(test_engine) as session:
            habit = session.get(Habit, test_habit.id)
            habit.recurrence = Recurrence.WEEKDAYS
            session.add(habit)
            session.commit()

        start = date(2025, 10, 20)  # Monday
        end = date(2025, 10, 26)  # Sunday

        instances = HabitInstanceService.generate_instances(test_habit.id, start, end)

        assert len(instances) == 5  # Mon-Fri only

    def test_generate_instances_weekends(self, test_engine, test_habit):
        """Gera instâncias WEEKENDS."""
        with Session(test_engine) as session:
            habit = session.get(Habit, test_habit.id)
            habit.recurrence = Recurrence.WEEKENDS
            session.add(habit)
            session.commit()

        start = date(2025, 10, 20)  # Monday
        end = date(2025, 10, 26)  # Sunday

        instances = HabitInstanceService.generate_instances(test_habit.id, start, end)

        assert len(instances) == 2  # Sat-Sun only

    def test_generate_instances_specific_day(self, test_engine, test_habit):
        """Gera instâncias para dia específico."""
        with Session(test_engine) as session:
            habit = session.get(Habit, test_habit.id)
            habit.recurrence = Recurrence.MONDAY
            session.add(habit)
            session.commit()

        start = date(2025, 10, 20)  # Monday
        end = date(2025, 10, 27)  # Next Monday

        instances = HabitInstanceService.generate_instances(test_habit.id, start, end)

        assert len(instances) == 2
        assert all(i.date.weekday() == 0 for i in instances)

    def test_generate_instances_avoids_duplicates(self, test_habit):
        """Não cria duplicatas."""
        start = date(2025, 10, 20)
        end = date(2025, 10, 22)

        # Primeira geração
        instances1 = HabitInstanceService.generate_instances(test_habit.id, start, end)
        assert len(instances1) == 3

        # Segunda geração - mesmo período
        instances2 = HabitInstanceService.generate_instances(test_habit.id, start, end)
        assert len(instances2) == 0  # Nenhuma nova

    def test_generate_instances_habit_not_found(self):
        """Erro se hábito não existe."""
        with pytest.raises(ValueError, match="not found"):
            HabitInstanceService.generate_instances(
                9999,
                date(2025, 10, 20),
                date(2025, 10, 22),
            )


class TestGetInstance:
    """Testes para get_instance."""

    def test_get_instance_found(self, test_habit):
        """Busca instância existente."""
        instances = HabitInstanceService.generate_instances(
            test_habit.id,
            date(2025, 10, 20),
            date(2025, 10, 20),
        )

        found = HabitInstanceService.get_instance(instances[0].id)
        assert found is not None
        assert found.id == instances[0].id

    def test_get_instance_not_found(self):
        """Retorna None se não existe."""
        assert HabitInstanceService.get_instance(9999) is None


class TestListInstances:
    """Testes para list_instances."""

    def test_list_instances_all(self, test_habit):
        """Lista todas as instâncias."""
        HabitInstanceService.generate_instances(
            test_habit.id,
            date(2025, 10, 20),
            date(2025, 10, 22),
        )

        instances = HabitInstanceService.list_instances()
        assert len(instances) == 3

    def test_list_instances_by_date(self, test_habit):
        """Filtra por data."""
        HabitInstanceService.generate_instances(
            test_habit.id,
            date(2025, 10, 20),
            date(2025, 10, 22),
        )

        instances = HabitInstanceService.list_instances(date=date(2025, 10, 21))
        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 21)

    def test_list_instances_by_habit(self, test_engine, test_habit):
        """Filtra por hábito."""
        # Criar segundo hábito
        with Session(test_engine) as session:
            habit2 = Habit(
                routine_id=test_habit.routine_id,
                title="Meditation",
                scheduled_start=time(6, 0),
                scheduled_end=time(6, 30),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit2)
            session.commit()
            session.refresh(habit2)

            HabitInstanceService.generate_instances(
                test_habit.id,
                date(2025, 10, 20),
                date(2025, 10, 20),
            )
            HabitInstanceService.generate_instances(
                habit2.id,
                date(2025, 10, 20),
                date(2025, 10, 20),
            )

        instances = HabitInstanceService.list_instances(habit_id=test_habit.id)
        assert len(instances) == 1
        assert instances[0].habit_id == test_habit.id


class TestAdjustInstanceTime:
    """Testes para adjust_instance_time."""

    def test_adjust_instance_time_success(self, test_habit):
        """Ajusta horários com sucesso."""
        instances = HabitInstanceService.generate_instances(
            test_habit.id,
            date(2025, 10, 20),
            date(2025, 10, 20),
        )

        adjusted = HabitInstanceService.adjust_instance_time(
            instances[0].id,
            time(8, 0),
            time(9, 0),
        )

        assert adjusted is not None
        assert adjusted.scheduled_start == time(8, 0)
        assert adjusted.scheduled_end == time(9, 0)
        assert adjusted.manually_adjusted is True

    def test_adjust_instance_time_not_found(self):
        """Retorna None se não existe."""
        assert HabitInstanceService.adjust_instance_time(9999, time(8, 0), time(9, 0)) is None

    def test_adjust_instance_time_invalid(self, test_habit):
        """Rejeita start >= end."""
        instances = HabitInstanceService.generate_instances(
            test_habit.id,
            date(2025, 10, 20),
            date(2025, 10, 20),
        )

        with pytest.raises(ValueError, match="Start time must be before end time"):
            HabitInstanceService.adjust_instance_time(
                instances[0].id,
                time(10, 0),
                time(9, 0),
            )

    def test_generate_instances_tuesday(self, test_engine):
        """Gera instâncias apenas para terça-feira."""
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Tuesday Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.TUESDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

        instances = HabitInstanceService.generate_instances(
            habit.id,
            date(2025, 10, 13),
            date(2025, 10, 19),  # Segunda a domingo
        )

        # Apenas terça (14/10) deve ser gerada
        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 14)

    def test_generate_instances_wednesday(self, test_engine):
        """Gera instâncias apenas para quarta-feira."""
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Wednesday Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.WEDNESDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

        instances = HabitInstanceService.generate_instances(
            habit.id, date(2025, 10, 13), date(2025, 10, 19)
        )

        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 15)

    def test_generate_instances_thursday(self, test_engine):
        """Gera instâncias apenas para quinta-feira."""
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Thursday Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.THURSDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

        instances = HabitInstanceService.generate_instances(
            habit.id, date(2025, 10, 13), date(2025, 10, 19)
        )

        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 16)

    def test_generate_instances_friday(self, test_engine):
        """Gera instâncias apenas para sexta-feira."""
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Friday Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.FRIDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

        instances = HabitInstanceService.generate_instances(
            habit.id, date(2025, 10, 13), date(2025, 10, 19)
        )

        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 17)

    def test_generate_instances_saturday(self, test_engine):
        """Gera instâncias apenas para sábado."""
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Saturday Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.SATURDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

        instances = HabitInstanceService.generate_instances(
            habit.id, date(2025, 10, 13), date(2025, 10, 19)
        )

        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 18)

    def test_generate_instances_sunday(self, test_engine):
        """Gera instâncias apenas para domingo."""
        with Session(test_engine) as session:
            routine = Routine(name="Test Routine")
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Sunday Habit",
                scheduled_start=time(9, 0),
                scheduled_end=time(10, 0),
                recurrence=Recurrence.SUNDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

        instances = HabitInstanceService.generate_instances(
            habit.id, date(2025, 10, 13), date(2025, 10, 19)
        )

        assert len(instances) == 1
        assert instances[0].date == date(2025, 10, 19)
