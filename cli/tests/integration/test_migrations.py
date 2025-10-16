"""Tests for database migrations."""
import tempfile
from pathlib import Path

import pytest
from sqlmodel import Session, create_engine, select

from src.timeblock.database.migrations import migrate_v2
from src.timeblock.models import Habit, HabitInstance, Routine, Task, TimeLog


@pytest.fixture
def temp_db():
    """Temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    yield db_path
    
    db_path.unlink(missing_ok=True)


def test_migrate_v2_creates_tables(temp_db, capsys):
    """Test that migrate_v2 creates all new tables."""
    migrate_v2(temp_db)
    
    captured = capsys.readouterr()
    assert "✓ Tabelas v2.0 criadas" in captured.out
    
    # Verify tables exist
    engine = create_engine(f"sqlite:///{temp_db}")
    with Session(engine) as session:
        routine = Routine(name="Test")
        session.add(routine)
        session.commit()
        
        result = session.exec(select(Routine)).first()
        assert result.name == "Test"


def test_migrate_v2_creates_routine_table(temp_db):
    """Test Routine table creation."""
    migrate_v2(temp_db)
    
    engine = create_engine(f"sqlite:///{temp_db}")
    with Session(engine) as session:
        routine = Routine(name="Morning Routine", is_active=True)
        session.add(routine)
        session.commit()
        
        assert routine.id is not None


def test_migrate_v2_creates_habit_table(temp_db):
    """Test Habit table creation."""
    from datetime import time
    from src.timeblock.models import Recurrence
    
    migrate_v2(temp_db)
    
    engine = create_engine(f"sqlite:///{temp_db}")
    with Session(engine) as session:
        routine = Routine(name="Test")
        session.add(routine)
        session.commit()
        
        habit = Habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        
        assert habit.id is not None


def test_migrate_v2_creates_habit_instance_table(temp_db):
    """Test HabitInstance table creation."""
    from datetime import date, time
    from src.timeblock.models import Recurrence
    
    migrate_v2(temp_db)
    
    engine = create_engine(f"sqlite:///{temp_db}")
    with Session(engine) as session:
        routine = Routine(name="Test")
        session.add(routine)
        session.commit()
        
        habit = Habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        
        instance = HabitInstance(
            habit_id=habit.id,
            date=date(2025, 10, 16),
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
        )
        session.add(instance)
        session.commit()
        
        assert instance.id is not None


def test_migrate_v2_creates_task_table(temp_db):
    """Test Task table creation."""
    from datetime import datetime
    
    migrate_v2(temp_db)
    
    engine = create_engine(f"sqlite:///{temp_db}")
    with Session(engine) as session:
        task = Task(
            title="Doctor Appointment",
            scheduled_datetime=datetime(2025, 10, 17, 14, 0),
        )
        session.add(task)
        session.commit()
        
        assert task.id is not None


def test_migrate_v2_creates_time_log_table(temp_db):
    """Test TimeLog table creation."""
    from datetime import datetime
    
    migrate_v2(temp_db)
    
    engine = create_engine(f"sqlite:///{temp_db}")
    with Session(engine) as session:
        log = TimeLog(
            start_time=datetime(2025, 10, 16, 7, 0),
            end_time=datetime(2025, 10, 16, 8, 0),
            duration_seconds=3600,
        )
        session.add(log)
        session.commit()
        
        assert log.id is not None
