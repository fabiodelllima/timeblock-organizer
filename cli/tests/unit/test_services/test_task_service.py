"""Testes para TaskService."""

from datetime import datetime

import pytest
from sqlmodel import SQLModel, create_engine

from src.timeblock.services.task_service import TaskService


@pytest.fixture
def test_engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr("src.timeblock.services.task_service.get_engine_context", mock_get_engine)


class TestCreateTask:
    """Testes para create_task."""

    def test_create_task_success(self):
        """Cria tarefa com sucesso."""
        task = TaskService.create_task(
            title="Dentist",
            scheduled_datetime=datetime(2025, 10, 20, 14, 0),
        )
        assert task.id is not None
        assert task.title == "Dentist"
        assert task.scheduled_datetime == datetime(2025, 10, 20, 14, 0)

    def test_create_task_with_description(self):
        """Cria tarefa com descrição."""
        task = TaskService.create_task(
            title="Meeting",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
            description="Discuss Q4 results",
        )
        assert task.description == "Discuss Q4 results"

    def test_create_task_with_color(self):
        """Cria tarefa com cor."""
        task = TaskService.create_task(
            title="Important",
            scheduled_datetime=datetime(2025, 10, 20, 15, 0),
            color="#FF0000",
        )
        assert task.color == "#FF0000"

    def test_create_task_strips_whitespace(self):
        """Remove espaços do título."""
        task = TaskService.create_task(
            title="  Task  ",
            scheduled_datetime=datetime(2025, 10, 20, 12, 0),
        )
        assert task.title == "Task"

    def test_create_task_with_empty_title(self):
        """Rejeita título vazio."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TaskService.create_task(
                title="   ",
                scheduled_datetime=datetime(2025, 10, 20, 12, 0),
            )

    def test_create_task_with_title_too_long(self):
        """Rejeita título muito longo."""
        with pytest.raises(ValueError, match="cannot exceed 200"):
            TaskService.create_task(
                title="X" * 201,
                scheduled_datetime=datetime(2025, 10, 20, 12, 0),
            )


class TestGetTask:
    """Testes para get_task."""

    def test_get_task_found(self):
        """Busca tarefa existente."""
        created = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )
        found = TaskService.get_task(created.id)
        assert found is not None
        assert found.id == created.id

    def test_get_task_not_found(self):
        """Retorna None se não existe."""
        assert TaskService.get_task(9999) is None


class TestListTasks:
    """Testes para list_tasks."""

    def test_list_tasks_all(self):
        """Lista todas as tarefas."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks()
        assert len(tasks) == 3

    def test_list_tasks_with_start(self):
        """Filtra por data inicial."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks(start=datetime(2025, 10, 21, 0, 0))
        assert len(tasks) == 2

    def test_list_tasks_with_end(self):
        """Filtra por data final."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks(end=datetime(2025, 10, 21, 23, 59))
        assert len(tasks) == 2

    def test_list_tasks_with_range(self):
        """Filtra por período."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks(
            start=datetime(2025, 10, 21, 0, 0),
            end=datetime(2025, 10, 21, 23, 59),
        )
        assert len(tasks) == 1
        assert tasks[0].title == "Task 2"


class TestCompleteTask:
    """Testes para complete_task."""

    def test_complete_task_success(self):
        """Completa tarefa com sucesso."""
        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )

        completed = TaskService.complete_task(task.id)
        assert completed is not None
        assert completed.completed_datetime is not None

    def test_complete_task_not_found(self):
        """Retorna None se não existe."""
        assert TaskService.complete_task(9999) is None


class TestDeleteTask:
    """Testes para delete_task."""

    def test_delete_task_success(self):
        """Remove tarefa com sucesso."""
        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )

        assert TaskService.delete_task(task.id) is True
        assert TaskService.get_task(task.id) is None

    def test_delete_task_not_found(self):
        """Retorna False se não existe."""
        assert TaskService.delete_task(9999) is False
