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
    ) -> Habit:
        """Cria um novo hábito."""
        title = title.strip()
        if not title:
            raise ValueError("Habit title cannot be empty")
        if len(title) > 200:
            raise ValueError("Habit title cannot exceed 200 characters")
        if scheduled_start >= scheduled_end:
            raise ValueError("Start time must be before end time")

        habit = Habit(
            routine_id=routine_id,
            title=title,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            recurrence=recurrence,
            color=color,
        )

        with get_engine_context() as engine, Session(engine) as session:
            session.add(habit)
            session.commit()
            session.refresh(habit)
            return habit

    @staticmethod
    def get_habit(habit_id: int) -> Habit | None:
        """Busca hábito por ID."""
        with get_engine_context() as engine, Session(engine) as session:
            return session.get(Habit, habit_id)

    @staticmethod
    def list_habits(routine_id: int | None = None) -> list[Habit]:
        """Lista hábitos, opcionalmente filtrados por rotina."""
        with get_engine_context() as engine, Session(engine) as session:
            statement = select(Habit)
            if routine_id is not None:
                statement = statement.where(Habit.routine_id == routine_id)
            return list(session.exec(statement).all())

    @staticmethod
    def update_habit(
        habit_id: int,
        title: str | None = None,
        scheduled_start: time | None = None,
        scheduled_end: time | None = None,
        recurrence: Recurrence | None = None,
        color: str | None = None,
    ) -> Habit | None:
        """Atualiza hábito existente."""
        with get_engine_context() as engine, Session(engine) as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                return None

            if title is not None:
                title = title.strip()
                if not title:
                    raise ValueError("Habit title cannot be empty")
                if len(title) > 200:
                    raise ValueError("Habit title cannot exceed 200 characters")
                habit.title = title

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

            session.add(habit)
            session.commit()
            session.refresh(habit)
            return habit

    @staticmethod
    def delete_habit(habit_id: int) -> bool:
        """Remove hábito."""
        with get_engine_context() as engine, Session(engine) as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                return False
            session.delete(habit)
            session.commit()
            return True
