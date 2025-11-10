"""Testes Sprint 2.4 - HabitInstanceService + EventReorderingService."""
from datetime import date, datetime, time

from sqlmodel import Session

from src.timeblock.database import get_engine_context
from src.timeblock.models.habit import Recurrence
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.services.task_service import TaskService


class TestHabitInstanceReorderingIntegration:
    """Testes de integração HabitInstanceService + EventReorderingService."""

    def test_adjust_without_time_change_no_reorder(self, test_db):
        """Ajustar sem mudar horário não dispara reordering."""
        today = date.today()

        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            routine = routine_service.create_routine("Test")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.EVERYDAY
        )

        instances = HabitInstanceService.generate_instances(
            habit.id, today, today
        )

        # Ajustar com mesmo horário
        updated, proposal = HabitInstanceService.adjust_instance_time(
            instances[0].id,
            new_start=time(8, 0)
        )

        assert updated is not None
        assert proposal is None

    def test_adjust_time_without_conflicts(self, test_db):
        """Ajustar horário sem conflitos retorna None."""
        today = date.today()

        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            routine = routine_service.create_routine("Test")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.EVERYDAY
        )

        instances = HabitInstanceService.generate_instances(
            habit.id, today, today
        )

        updated, proposal = HabitInstanceService.adjust_instance_time(
            instances[0].id,
            new_start=time(10, 0),
            new_end=time(11, 0)
        )

        assert updated.scheduled_start == time(10, 0)
        assert updated.scheduled_end == time(11, 0)
        assert proposal is None

    def test_adjust_time_with_task_conflict(self, test_db):
        """Ajustar causando conflito com task retorna proposal."""
        today = date.today()
        now = datetime.now()

        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            routine = routine_service.create_routine("Test")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.EVERYDAY
        )

        instances = HabitInstanceService.generate_instances(
            habit.id, today, today
        )

        # Criar task no horário que habit será ajustado
        task = TaskService.create_task(
            title="Meeting",
            scheduled_datetime=datetime.combine(today, time(10, 30))
        )

        # Ajustar habit para conflitar com task
        updated, proposal = HabitInstanceService.adjust_instance_time(
            instances[0].id,
            new_start=time(10, 0),
            new_end=time(11, 0)
        )

        assert updated.scheduled_start == time(10, 0)
        assert proposal is not None
        assert len(proposal.conflicts) > 0

    def test_adjust_nonexistent_instance(self, test_db):
        """Ajustar instância inexistente retorna (None, None)."""
        updated, proposal = HabitInstanceService.adjust_instance_time(
            99999,
            new_start=time(10, 0)
        )

        assert updated is None
        assert proposal is None

    def test_mark_completed(self, test_db):
        """Marcar como completo atualiza status."""
        today = date.today()

        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            routine = routine_service.create_routine("Test")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.EVERYDAY
        )

        instances = HabitInstanceService.generate_instances(
            habit.id, today, today
        )

        completed = HabitInstanceService.mark_completed(instances[0].id)

        assert completed is not None
        assert completed.status == "COMPLETED"
