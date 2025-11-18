"""Task service com detecção de conflitos."""

from datetime import datetime

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context

from ..models import Task
from .event_reordering_models import Conflict
from .event_reordering_service import EventReorderingService


class TaskService:
    """Service for managing tasks."""

    @staticmethod
    def create_task(
        title: str,
        scheduled_datetime: datetime,
        description: str | None = None,
        color: str | None = None,
        tag_id: int | None = None,
        session: Session | None = None,
    ) -> Task:
        """Create a new task.
        Args:
            title: Task title
            scheduled_datetime: When task is scheduled
            description: Optional description
            color: Optional color
            tag_id: Optional tag reference
            session: Optional session (for tests/transactions)
        """
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        def _create(sess: Session) -> Task:
            task = Task(
                title=title,
                scheduled_datetime=scheduled_datetime,
                description=description,
                color=color,
                tag_id=tag_id,
            )
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            return task
        if session is not None:
            return _create(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _create(sess)

    @staticmethod
    def get_task(task_id: int, session: Session | None = None) -> Task | None:
        """Get a task by ID.
        Args:
            task_id: ID of task to retrieve
            session: Optional session (for tests/transactions)
        """
        def _get(sess: Session) -> Task | None:
            return sess.get(Task, task_id)
        if session is not None:
            return _get(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)

    @staticmethod
    def list_tasks(
        start: datetime | None = None,
        end: datetime | None = None,
        session: Session | None = None,
    ) -> list[Task]:
        """List all tasks, optionally filtered by date range.
        Args:
            start: Optional start datetime filter
            end: Optional end datetime filter
            session: Optional session (for tests/transactions)
        """
        def _list(sess: Session) -> list[Task]:
            statement = select(Task)
            if start:
                statement = statement.where(Task.scheduled_datetime >= start)
            if end:
                statement = statement.where(Task.scheduled_datetime <= end)
            return list(sess.exec(statement).all())
        if session is not None:
            return _list(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def list_pending_tasks(session: Session | None = None) -> list[Task]:
        """List tasks that are not completed.
        Args:
            session: Optional session (for tests/transactions)
        """
        def _list(sess: Session) -> list[Task]:
            statement = select(Task).where(Task.completed_datetime.is_(None))
            return list(sess.exec(statement).all())
        if session is not None:
            return _list(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def update_task(
        task_id: int,
        title: str | None = None,
        scheduled_datetime: datetime | None = None,
        description: str | None = None,
        tag_id: int | None = None,
        session: Session | None = None,
    ) -> tuple[Task | None, list[Conflict] | None]:
        """Atualiza task existente.
        Se horário for alterado, detecta conflitos e retorna informações.
        Não aplica nenhuma resolução automática.
        Args:
            task_id: ID da task a atualizar
            title: Novo título (opcional)
            scheduled_datetime: Novo horário (opcional)
            description: Nova descrição (opcional)
            tag_id: Nova tag (opcional)
            session: Optional session (for tests/transactions)
        Returns:
            Tupla (task atualizada, lista de conflitos se horário mudou)
        """
        def _update(sess: Session) -> tuple[Task | None, bool]:
            task = sess.get(Task, task_id)
            if not task:
                return None, False
            datetime_changed = (
                scheduled_datetime is not None
                and scheduled_datetime != task.scheduled_datetime
            )
            if title is not None:
                title_stripped = title.strip()
                if not title_stripped:
                    raise ValueError("Title cannot be empty")
                if len(title_stripped) > 200:
                    raise ValueError("Title cannot exceed 200 characters")
                task.title = title_stripped
            if scheduled_datetime is not None:
                task.scheduled_datetime = scheduled_datetime
            if description is not None:
                task.description = description
            if tag_id is not None:
                task.tag_id = tag_id
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            return task, datetime_changed
        if session is not None:
            task, datetime_changed = _update(session)
        else:
            with get_engine_context() as engine, Session(engine) as sess:
                task, datetime_changed = _update(sess)
        # Detecta conflitos se horário mudou, mas não propõe resolução
        conflicts = None
        if datetime_changed and task:
            conflicts = EventReorderingService.detect_conflicts(task_id, "task")
        return task, conflicts

    @staticmethod
    def complete_task(task_id: int, session: Session | None = None) -> Task | None:
        """Mark a task as completed.
        Args:
            task_id: ID of task to complete
            session: Optional session (for tests/transactions)
        """
        def _complete(sess: Session) -> Task | None:
            task = sess.get(Task, task_id)
            if not task:
                return None
            task.completed_datetime = datetime.now()
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            return task
        if session is not None:
            return _complete(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _complete(sess)

    @staticmethod
    def delete_task(task_id: int, session: Session | None = None) -> bool:
        """Delete a task.
        Args:
            task_id: ID of task to delete
            session: Optional session (for tests/transactions)
        """
        def _delete(sess: Session) -> bool:
            task = sess.get(Task, task_id)
            if not task:
                return False
            sess.delete(task)
            sess.commit()
            return True
        if session is not None:
            return _delete(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _delete(sess)
