"""Service para gerenciamento de tarefas."""

from datetime import datetime

from sqlmodel import Session, and_, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Task


class TaskService:
    """Serviço de gerenciamento de tarefas."""

    @staticmethod
    def create_task(
        title: str,
        scheduled_datetime: datetime,
        description: str | None = None,
        color: str | None = None,
    ) -> Task:
        """Cria nova tarefa."""
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        if len(title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

        task = Task(
            title=title,
            scheduled_datetime=scheduled_datetime,
            description=description,
            color=color,
        )

        with get_engine_context() as engine, Session(engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def get_task(task_id: int) -> Task:
        """Busca tarefa por ID."""
        with get_engine_context() as engine, Session(engine) as session:
            task = session.get(Task, task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            return task

    @staticmethod
    def list_tasks(start: datetime | None = None, end: datetime | None = None) -> list[Task]:
        """Lista tarefas."""
        with get_engine_context() as engine, Session(engine) as session:
            query = select(Task)

            if start and end:
                query = query.where(
                    and_(Task.scheduled_datetime >= start, Task.scheduled_datetime <= end)
                )
            elif start:
                query = query.where(Task.scheduled_datetime >= start)
            elif end:
                query = query.where(Task.scheduled_datetime <= end)

            query = query.order_by(Task.scheduled_datetime)
            return list(session.exec(query).all())

    @staticmethod
    def list_pending_tasks() -> list[Task]:
        """Lista tarefas pendentes."""
        with get_engine_context() as engine, Session(engine) as session:
            query = select(Task).where(Task.completed_datetime.is_(None))
            query = query.order_by(Task.scheduled_datetime)
            return list(session.exec(query).all())

    @staticmethod
    def complete_task(task_id: int) -> Task:
        """Marca tarefa como completa."""
        with get_engine_context() as engine, Session(engine) as session:
            task = session.get(Task, task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")

            task.completed_datetime = datetime.now()
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def update_task(task_id: int, **kwargs) -> Task:
        """Atualiza campos da tarefa."""
        with get_engine_context() as engine, Session(engine) as session:
            task = session.get(Task, task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")

            for key, value in kwargs.items():
                setattr(task, key, value)

            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def delete_task(task_id: int) -> None:
        """Deleta tarefa."""
        with get_engine_context() as engine, Session(engine) as session:
            task = session.get(Task, task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")

            session.delete(task)
            session.commit()
