"""Service para gerenciamento de tarefas."""

from datetime import datetime
from typing import Optional

from sqlmodel import Session, select, and_

from src.timeblock.database import get_engine_context
from src.timeblock.models import Task


class TaskService:
    """Serviço de gerenciamento de tarefas."""

    @staticmethod
    def create_task(
        title: str,
        scheduled_datetime: datetime,
        description: Optional[str] = None,
        color: Optional[str] = None,
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
        
        with get_engine_context() as engine:
            with Session(engine) as session:
                session.add(task)
                session.commit()
                session.refresh(task)
                return task

    @staticmethod
    def get_task(task_id: int) -> Optional[Task]:
        """Busca tarefa por ID."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                return session.get(Task, task_id)

    @staticmethod
    def list_tasks(
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> list[Task]:
        """Lista tarefas com filtro opcional de período."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                statement = select(Task)
                
                if start is not None and end is not None:
                    statement = statement.where(
                        and_(
                            Task.scheduled_datetime >= start,
                            Task.scheduled_datetime <= end,
                        )
                    )
                elif start is not None:
                    statement = statement.where(Task.scheduled_datetime >= start)
                elif end is not None:
                    statement = statement.where(Task.scheduled_datetime <= end)
                
                return list(session.exec(statement).all())

    @staticmethod
    def complete_task(task_id: int) -> Optional[Task]:
        """Marca tarefa como completa."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                task = session.get(Task, task_id)
                if not task:
                    return None
                
                task.completed_datetime = datetime.now()
                session.add(task)
                session.commit()
                session.refresh(task)
                return task

    @staticmethod
    def delete_task(task_id: int) -> bool:
        """Remove tarefa."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                task = session.get(Task, task_id)
                if not task:
                    return False
                session.delete(task)
                session.commit()
                return True
