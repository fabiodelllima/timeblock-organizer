"""Testes Sprint 2.2 - TaskService + EventReorderingService."""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session
from src.timeblock.database import get_engine_context
from src.timeblock.services.task_service import TaskService
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.models.habit import Recurrence


class TestTaskReorderingIntegration:
    """Testes de integração TaskService + EventReorderingService."""
    
    def test_update_without_time_change_no_reorder(self, test_db):
        """Atualizar título/descrição não dispara reordering."""
        now = datetime.now()
        task = TaskService.create_task(
            title="Review code",
            scheduled_datetime=now
        )
        
        updated, proposal = TaskService.update_task(
            task.id,
            title="Review PR",
            description="Check tests"
        )
        
        assert updated.title == "Review PR"
        assert updated.description == "Check tests"
        assert proposal is None
    
    def test_update_time_without_conflicts(self, test_db):
        """Mudar horário sem conflitos retorna None em proposal."""
        now = datetime.now()
        task = TaskService.create_task(
            title="Review code",
            scheduled_datetime=now
        )
        
        new_time = now + timedelta(hours=3)
        updated, proposal = TaskService.update_task(
            task.id,
            scheduled_datetime=new_time
        )
        
        assert updated.scheduled_datetime == new_time
        assert proposal is None
    
    def test_update_time_with_conflicts(self, test_db):
        """Mudar horário causando conflito retorna proposal."""
        now = datetime.now()
        
        task1 = TaskService.create_task(
            title="Task 1",
            scheduled_datetime=now
        )
        
        task2 = TaskService.create_task(
            title="Task 2",
            scheduled_datetime=now + timedelta(hours=1)
        )
        
        new_time = now + timedelta(minutes=30)
        updated, proposal = TaskService.update_task(
            task1.id,
            scheduled_datetime=new_time
        )
        
        assert updated.scheduled_datetime == new_time
        assert proposal is not None
        assert len(proposal.conflicts) > 0
    
    def test_update_time_conflicts_with_habit(self, test_db):
        """Task conflitando com HabitInstance gera proposal."""
        now = datetime.now()
        today = now.date()
        
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            routine = routine_service.create_routine("Test Routine")
        
        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Morning Exercise",
            scheduled_start=now.time(),
            scheduled_end=(now + timedelta(hours=1)).time(),
            recurrence=Recurrence.EVERYDAY
        )
        
        instances = HabitInstanceService.generate_instances(
            habit.id, today, today
        )
        
        task = TaskService.create_task(
            title="Important Call",
            scheduled_datetime=now - timedelta(hours=2)
        )
        
        updated, proposal = TaskService.update_task(
            task.id,
            scheduled_datetime=now + timedelta(minutes=15)
        )
        
        assert updated.scheduled_datetime == now + timedelta(minutes=15)
        assert proposal is not None
        assert len(proposal.conflicts) > 0
    
    def test_update_nonexistent_task(self, test_db):
        """Atualizar task inexistente retorna (None, None)."""
        updated, proposal = TaskService.update_task(
            99999,
            title="New title"
        )
        
        assert updated is None
        assert proposal is None
    
    def test_update_time_to_same_value_no_reorder(self, test_db):
        """Atualizar para mesmo horário não dispara reordering."""
        now = datetime.now()
        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=now
        )
        
        updated, proposal = TaskService.update_task(
            task.id,
            scheduled_datetime=now
        )
        
        assert updated.scheduled_datetime == now
        assert proposal is None
