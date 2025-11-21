"""Service para gerenciamento de hábitos."""

from datetime import time

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Habit, Recurrence


class HabitService:
    """Serviço de gerenciamento de hábitos."""

    @staticmethod
    def create_habit(
        routine_id: int,
        title: str,
        scheduled_start: time,
        scheduled_end: time,
        recurrence: Recurrence,
        color: str | None = None,
        session: Session | None = None,
    ) -> Habit:
        """Cria um novo hábito."""
        title = title.strip()
        if not title:
            raise ValueError("Habit title cannot be empty")
        if len(title) > 200:
            raise ValueError("Habit title cannot exceed 200 characters")
        if scheduled_start >= scheduled_end:
            raise ValueError("Start time must be before end time")

        def _create(sess: Session) -> Habit:
            habit = Habit(
                routine_id=routine_id,
                title=title,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                recurrence=recurrence,
                color=color,
            )
            sess.add(habit)
            sess.commit()
            sess.refresh(habit)
            return habit

        if session is not None:
            return _create(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _create(sess)

    @staticmethod
    def get_habit(habit_id: int, session: Session | None = None) -> Habit | None:
        """Busca hábito por ID."""
        def _get(sess: Session) -> Habit | None:
            return sess.get(Habit, habit_id)

        if session is not None:
            return _get(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)

    @staticmethod
    def list_habits(
        routine_id: int | None = None,
        session: Session | None = None,
    ) -> list[Habit]:
        """Lista hábitos, opcionalmente filtrados por rotina."""
        def _list(sess: Session) -> list[Habit]:
            statement = select(Habit)
            if routine_id is not None:
                statement = statement.where(Habit.routine_id == routine_id)
            return list(sess.exec(statement).all())

        if session is not None:
            return _list(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def update_habit(
        habit_id: int,
        title: str | None = None,
        scheduled_start: time | None = None,
        scheduled_end: time | None = None,
        recurrence: Recurrence | None = None,
        color: str | None = None,
        session: Session | None = None,
    ) -> Habit | None:
        """Atualiza hábito existente."""
        def _update(sess: Session) -> Habit | None:
            habit = sess.get(Habit, habit_id)
            if not habit:
                return None

            if title is not None:
                title_stripped = title.strip()
                if not title_stripped:
                    raise ValueError("Habit title cannot be empty")
                if len(title_stripped) > 200:
                    raise ValueError("Habit title cannot exceed 200 characters")
                habit.title = title_stripped
            if scheduled_start is not None:
                habit.scheduled_start = scheduled_start
            if scheduled_end is not None:
                habit.scheduled_end = scheduled_end
            if habit.scheduled_start >= habit.scheduled_end:
                raise ValueError("Start time must be before end time")
            if recurrence is not None:
                habit.recurrence = recurrence
            if color is not None:
                habit.color = color

            sess.add(habit)
            sess.commit()
            sess.refresh(habit)
            return habit

        if session is not None:
            return _update(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _update(sess)

    @staticmethod
    def delete_habit(habit_id: int, session: Session | None = None) -> bool:
        """Remove hábito."""
        def _delete(sess: Session) -> bool:
            habit = sess.get(Habit, habit_id)
            if not habit:
                return False

            sess.delete(habit)
            sess.commit()
            return True

        if session is not None:
            return _delete(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _delete(sess)
