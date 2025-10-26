"""Testes para EventReorderingService.apply_reordering()."""
import pytest
from datetime import datetime, time, date, timedelta
from sqlmodel import Session, create_engine, SQLModel
from src.timeblock.models import (
    Routine, Habit, HabitInstance, Task, Event, TimeLog, Tag
)
from src.timeblock.services.event_reordering_service import EventReorderingService
from src.timeblock.services.event_reordering_models import (
    ReorderingProposal, ProposedChange, EventPriority, Conflict, ConflictType
)


@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    from contextlib import contextmanager
    
    @contextmanager
    def mock_get_engine():
        yield test_engine
    
    monkeypatch.setattr("src.timeblock.services.event_reordering_service.get_engine_context", mock_get_engine)


@pytest.fixture
def sample_task(test_engine):
    with Session(test_engine) as session:
        task = Task(
            title="Test Task",
            scheduled_datetime=datetime(2025, 10, 26, 10, 0),
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@pytest.fixture
def sample_instance(test_engine):
    with Session(test_engine) as session:
        routine = Routine(name="Test Routine")
        session.add(routine)
        session.commit()
        session.refresh(routine)
        
        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence="EVERYDAY"
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        
        instance = HabitInstance(
            habit_id=habit.id,
            date=date(2025, 10, 26),
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance


class TestApplyReordering:
    def test_apply_empty_proposal(self):
        """Proposta vazia retorna False."""
        proposal = ReorderingProposal(conflicts=[], proposed_changes=[], estimated_duration_shift=0)
        result = EventReorderingService.apply_reordering(proposal)
        assert result is False
    
    def test_apply_updates_task_time(self, test_engine, sample_task):
        """Aplica mudança em Task."""
        new_time = datetime(2025, 10, 26, 14, 0)
        proposal = ReorderingProposal(
            conflicts=[],
            proposed_changes=[
                ProposedChange(
                    event_id=sample_task.id,
                    event_type="task",
                    event_title="Test Task",
                    current_start=sample_task.scheduled_datetime,
                    current_end=sample_task.scheduled_datetime + timedelta(hours=1),
                    proposed_start=new_time,
                    proposed_end=new_time + timedelta(hours=1),
                    priority=EventPriority.LOW,
                    reason="Test"
                )
            ],
            estimated_duration_shift=0
        )
        
        result = EventReorderingService.apply_reordering(proposal)
        assert result is True
        
        # Verificar atualização
        with Session(test_engine) as session:
            updated = session.get(Task, sample_task.id)
            assert updated.scheduled_datetime == new_time
    
    def test_apply_updates_habit_instance_time(self, test_engine, sample_instance):
        """Aplica mudança em HabitInstance."""
        new_start = time(9, 0)
        new_end = time(10, 0)
        proposal = ReorderingProposal(
            conflicts=[],
            proposed_changes=[
                ProposedChange(
                    event_id=sample_instance.id,
                    event_type="habit_instance",
                    event_title="Test Habit",
                    current_start=datetime.combine(sample_instance.date, sample_instance.scheduled_start),
                    current_end=datetime.combine(sample_instance.date, sample_instance.scheduled_end),
                    proposed_start=datetime.combine(sample_instance.date, new_start),
                    proposed_end=datetime.combine(sample_instance.date, new_end),
                    priority=EventPriority.LOW,
                    reason="Test"
                )
            ],
            estimated_duration_shift=0
        )
        
        result = EventReorderingService.apply_reordering(proposal)
        assert result is True
        
        # Verificar atualização
        with Session(test_engine) as session:
            updated = session.get(HabitInstance, sample_instance.id)
            assert updated.scheduled_start == new_start
            assert updated.scheduled_end == new_end
            assert updated.user_override is False  # Automático
    
    def test_apply_multiple_changes(self, test_engine, sample_task, sample_instance):
        """Aplica múltiplas mudanças."""
        proposal = ReorderingProposal(
            conflicts=[],
            proposed_changes=[
                ProposedChange(
                    event_id=sample_task.id,
                    event_type="task",
                    event_title="Test Task",
                    current_start=sample_task.scheduled_datetime,
                    current_end=sample_task.scheduled_datetime + timedelta(hours=1),
                    proposed_start=datetime(2025, 10, 26, 15, 0),
                    proposed_end=datetime(2025, 10, 26, 16, 0),
                    priority=EventPriority.LOW,
                    reason="Test"
                ),
                ProposedChange(
                    event_id=sample_instance.id,
                    event_type="habit_instance",
                    event_title="Test Habit",
                    current_start=datetime.combine(sample_instance.date, sample_instance.scheduled_start),
                    current_end=datetime.combine(sample_instance.date, sample_instance.scheduled_end),
                    proposed_start=datetime.combine(sample_instance.date, time(11, 0)),
                    proposed_end=datetime.combine(sample_instance.date, time(12, 0)),
                    priority=EventPriority.LOW,
                    reason="Test"
                )
            ],
            estimated_duration_shift=0
        )
        
        result = EventReorderingService.apply_reordering(proposal)
        assert result is True
        
        # Verificar ambos atualizados
        with Session(test_engine) as session:
            updated_task = session.get(Task, sample_task.id)
            updated_instance = session.get(HabitInstance, sample_instance.id)
            
            assert updated_task.scheduled_datetime == datetime(2025, 10, 26, 15, 0)
            assert updated_instance.scheduled_start == time(11, 0)
