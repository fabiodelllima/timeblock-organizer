"""Testes para comando reschedule."""
import pytest
from typer.testing import CliRunner
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.main import app
from src.timeblock.models import Task

runner = CliRunner()


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
def conflicting_tasks(test_engine):
    """Cria tasks que conflitam."""
    with Session(test_engine) as session:
        task1 = Task(title="Task 1", scheduled_datetime=datetime.now())
        task2 = Task(title="Task 2", scheduled_datetime=datetime.now() + timedelta(minutes=30))
        session.add_all([task1, task2])
        session.commit()
        session.refresh(task1)
        session.refresh(task2)
        return task1, task2


def test_preview_no_conflicts(test_engine):
    """Testa preview sem conflitos."""
    with Session(test_engine) as session:
        task = Task(title="Solo Task", scheduled_datetime=datetime.now())
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id
    
    result = runner.invoke(app, ["reschedule", "preview", str(task_id)])
    assert result.exit_code == 0
    assert "Nenhum conflito" in result.stdout


def test_preview_with_conflicts(conflicting_tasks):
    """Testa preview com conflitos."""
    task1, task2 = conflicting_tasks
    
    result = runner.invoke(app, ["reschedule", "preview", str(task1.id)])
    assert result.exit_code == 0
    assert "Conflitos Detectados" in result.stdout
    assert "Mudanças Propostas" in result.stdout


def test_preview_event_not_found_shows_no_conflicts(test_engine):
    """Evento inexistente retorna sem conflitos."""
    result = runner.invoke(app, ["reschedule", "preview", "999"])
    assert result.exit_code == 0
    assert "Nenhum conflito" in result.stdout


def test_preview_with_event_type_option(conflicting_tasks):
    """Testa preview especificando tipo de evento."""
    task1, _ = conflicting_tasks
    
    result = runner.invoke(app, ["reschedule", "preview", str(task1.id), "--event-type", "task"])
    assert result.exit_code == 0
