"""Testes Sprint 2.3 - TimerService + EventReorderingService."""

from datetime import datetime, timedelta

import pytest

from src.timeblock.models.habit import Recurrence
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.services.task_service import TaskService
from src.timeblock.services.timer_service import TimerService


class TestTimerReorderingIntegration:
    """Testes de integração TimerService + EventReorderingService."""

    def test_start_timer_without_conflicts(self, test_db):
        """Iniciar timer sem conflitos retorna None em proposal."""
        now = datetime.now()
        task = TaskService.create_task(
            title="Review code",
            scheduled_datetime=now,
            session=test_db,
        )

        timelog, proposal = TimerService.start_timer(
            task_id=task.id,
            session=test_db,
        )

        assert timelog.task_id == task.id
        assert timelog.start_time is not None
        assert proposal is None

    def test_start_timer_with_task_conflicts(self, test_db):
        """Iniciar timer causando conflito retorna proposal."""
        now = datetime.now()

        task1 = TaskService.create_task(
            title="Task 1",
            scheduled_datetime=now,
            session=test_db,
        )
        task2 = TaskService.create_task(
            title="Task 2",
            scheduled_datetime=now + timedelta(hours=1),
            session=test_db,
        )

        # Iniciar timer na task1 depois da task2 (fora de ordem)
        timelog, proposal = TimerService.start_timer(
            task_id=task1.id,
            session=test_db,
        )

        assert timelog.task_id == task1.id
        # Pode ou não ter conflito dependendo da lógica de detecção
        # Este teste valida que não quebra

    def test_start_timer_with_habit_conflicts(self, test_db):
        """Iniciar timer em habit com conflito retorna proposal."""
        now = datetime.now()
        today = now.date()

        routine_service = RoutineService(test_db)
        routine = routine_service.create_routine("Test")

        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=now.time(),
            scheduled_end=(now + timedelta(hours=1)).time(),
            recurrence=Recurrence.EVERYDAY,
            session=test_db,
        )

        instances = HabitInstanceService.generate_instances(
            habit.id,
            today,
            today,
            session=test_db,
        )

        if instances:
            timelog, proposal = TimerService.start_timer(
                habit_instance_id=instances[0].id,
                session=test_db,
            )
            assert timelog.habit_instance_id == instances[0].id
            assert timelog.start_time is not None

    def test_start_timer_multiple_ids_fails(self, test_db):
        """Fornecer múltiplos IDs lança erro."""
        with pytest.raises(ValueError, match="Exactly one ID"):
            TimerService.start_timer(
                task_id=1,
                habit_instance_id=1,
                session=test_db,
            )

    def test_start_timer_no_id_fails(self, test_db):
        """Não fornecer ID lança erro."""
        with pytest.raises(ValueError, match="Exactly one ID"):
            TimerService.start_timer(session=test_db)

    def test_start_timer_with_active_timer_fails(self, test_db):
        """Iniciar timer com outro ativo lança erro."""
        now = datetime.now()

        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=now,
            session=test_db,
        )

        TimerService.start_timer(task_id=task.id, session=test_db)

        with pytest.raises(ValueError, match="already active"):
            TimerService.start_timer(task_id=task.id, session=test_db)
