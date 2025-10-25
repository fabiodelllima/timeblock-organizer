"""Testes de integração entre HabitInstanceService e EventReorderingService."""
import pytest
from datetime import date, time
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.models import Habit, HabitInstance, Routine, Recurrence
from src.timeblock.database import get_engine_context
from sqlmodel import Session


@pytest.fixture
def setup_habit(test_db):
    """Cria rotina e hábito para testes."""
    with get_engine_context() as engine, Session(engine) as session:
        routine = Routine(name="Test Routine", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)
        
        habit = Habit(
            title="Morning Exercise",
            routine_id=routine.id,
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        
        return habit


def test_adjust_instance_time_without_conflicts(setup_habit):
    """Ajustar horário sem conflitos retorna lista vazia."""
    habit = setup_habit
    instances = HabitInstanceService.generate_instances(
        habit.id, date.today(), date.today()
    )
    
    instance, conflicts = HabitInstanceService.adjust_instance_time(
        instances[0].id,
        time(6, 0),
        time(7, 0)
    )
    
    assert instance.scheduled_start == time(6, 0)
    assert instance.scheduled_end == time(7, 0)
    assert instance.user_override is True
    assert len(conflicts) == 0


def test_adjust_instance_time_with_conflicts(setup_habit):
    """Ajustar horário com conflitos detecta corretamente."""
    habit = setup_habit
    instances = HabitInstanceService.generate_instances(
        habit.id, date.today(), date.today()
    )
    
    # Criar segunda instância no mesmo horário
    with get_engine_context() as engine, Session(engine) as session:
        conflicting = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0)
        )
        session.add(conflicting)
        session.commit()
    
    # Ajustar para conflitar
    instance, conflicts = HabitInstanceService.adjust_instance_time(
        instances[0].id,
        time(8, 0),
        time(9, 0)
    )
    
    assert len(conflicts) > 0
    assert conflicts[0].triggered_event_id == instances[0].id
