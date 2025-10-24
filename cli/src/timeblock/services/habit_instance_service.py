"""Service para gerenciamento de instâncias de hábitos."""

from datetime import date, time, timedelta

from sqlmodel import Session, and_, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Habit, HabitInstance, HabitInstanceStatus, Recurrence


class HabitInstanceService:
    """Serviço de gerenciamento de instâncias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date,
    ) -> list[HabitInstance]:
        """Gera instâncias de hábito para período."""
        with get_engine_context() as engine, Session(engine) as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                raise ValueError(f"Habit {habit_id} not found")

            instances = []
            current_date = start_date

            while current_date <= end_date:
                if HabitInstanceService._should_create_instance(habit.recurrence, current_date):
                    # Verificar se já existe
                    existing = session.exec(
                        select(HabitInstance).where(
                            and_(
                                HabitInstance.habit_id == habit_id,
                                HabitInstance.date == current_date,
                            )
                        )
                    ).first()

                    if not existing:
                        instance = HabitInstance(
                            habit_id=habit_id,
                            date=current_date,
                            scheduled_start=habit.scheduled_start,
                            scheduled_end=habit.scheduled_end,
                        )
                        session.add(instance)
                        instances.append(instance)

                current_date += timedelta(days=1)

            session.commit()
            for instance in instances:
                session.refresh(instance)

            return instances

    @staticmethod
    def _should_create_instance(recurrence: Recurrence, date: date) -> bool:
        """Verifica se deve criar instância para a data."""
        weekday = date.weekday()  # 0=Monday, 6=Sunday

        if recurrence == Recurrence.EVERYDAY:
            return True
        elif recurrence == Recurrence.WEEKDAYS:
            return weekday < 5
        elif recurrence == Recurrence.WEEKENDS:
            return weekday >= 5
        elif recurrence == Recurrence.MONDAY:
            return weekday == 0
        elif recurrence == Recurrence.TUESDAY:
            return weekday == 1
        elif recurrence == Recurrence.WEDNESDAY:
            return weekday == 2
        elif recurrence == Recurrence.THURSDAY:
            return weekday == 3
        elif recurrence == Recurrence.FRIDAY:
            return weekday == 4
        elif recurrence == Recurrence.SATURDAY:
            return weekday == 5
        elif recurrence == Recurrence.SUNDAY:
            return weekday == 6

        return False

    @staticmethod
    def get_instance(instance_id: int) -> HabitInstance | None:
        """Busca instância por ID."""
        with get_engine_context() as engine, Session(engine) as session:
            return session.get(HabitInstance, instance_id)

    @staticmethod
    def list_instances(
        date: date | None = None,
        habit_id: int | None = None,
    ) -> list[HabitInstance]:
        """Lista instâncias com filtros opcionais."""
        with get_engine_context() as engine, Session(engine) as session:
            statement = select(HabitInstance)

            if date is not None:
                statement = statement.where(HabitInstance.date == date)
            if habit_id is not None:
                statement = statement.where(HabitInstance.habit_id == habit_id)

            return list(session.exec(statement).all())

    @staticmethod
    def adjust_instance_time(
        instance_id: int,
        new_start: time,
        new_end: time,
    ) -> HabitInstance | None:
        """Ajusta horários de instância."""
        if new_start >= new_end:
            raise ValueError("Start time must be before end time")

        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                return None

            instance.scheduled_start = new_start
            instance.scheduled_end = new_end
            instance.manually_adjusted = True
            instance.user_override = True

            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
