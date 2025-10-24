"""Task service."""
from datetime import datetime
from sqlmodel import Session, select
from src.timeblock.database import get_engine_context
from ..models import Task


class TaskService:
    """Service for managing tasks."""

    @staticmethod
    def create_task(
        title: str,
        scheduled_datetime: datetime,
        description: str | None = None,
        color: str | None = None,
        tag_id: int | None = None,
    ) -> Task:
        """Create a new task."""
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        with get_engine_context() as engine, Session(engine) as session:
            task = Task(
                title=title,
                scheduled_datetime=scheduled_datetime,
                description=description,
                color=color,
                tag_id=tag_id,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def get_task(task_id: int) -> Task | None:
        """Get a task by ID. Returns None if not found."""
        with get_engine_context() as engine, Session(engine) as session:
            return session.get(Task, task_id)

    @staticmethod
    def list_tasks(
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Task]:
        """List all tasks, optionally filtered by date range."""
        with get_engine_context() as engine, Session(engine) as session:
            statement = select(Task)
            if start:
                statement = statement.where(Task.scheduled_datetime >= start)
            if end:
                statement = statement.where(Task.scheduled_datetime <= end)
            return list(session.exec(statement).all())

    @staticmethod
    def list_pending_tasks() -> list[Task]:
        """List tasks that are not completed."""
        with get_engine_context() as engine, Session(engine) as session:
            statement = select(Task).where(Task.completed_datetime.is_(None))
            return list(session.exec(statement).all())

    @staticmethod
    def update_task(
        task_id: int,
        title: str | None = None,
        scheduled_datetime: datetime | None = None,
        description: str | None = None,
        color: str | None = None,
        tag_id: int | None = None,
        started_at: datetime | None = None,
    ) -> Task | None:
        """Update a task. Returns None if not found."""
        with get_engine_context() as engine, Session(engine) as session:
            task = session.get(Task, task_id)
            if not task:
                return None

            if title is not None:
                title = title.strip()
                if not title:
                    raise ValueError("Title cannot be empty")
                if len(title) > 200:
                    raise ValueError("Title cannot exceed 200 characters")
                task.title = title
            if scheduled_datetime is not None:
                task.scheduled_datetime = scheduled_datetime
            if description is not None:
                task.description = description
            if color is not None:
                task.color = color
            if tag_id is not None:
                task.tag_id = tag_id
            if started_at is not None:
                task.started_at = started_at

            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def complete_task(task_id: int) -> Task | None:
        """Mark a task as completed. Returns None if not found."""
        with get_engine_context() as engine, Session(engine) as session:
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
        """Delete a task. Returns True if deleted, False if not found."""
        with get_engine_context() as engine, Session(engine) as session:
            task = session.get(Task, task_id)
            if not task:
                return False

            session.delete(task)
            session.commit()
            return True
