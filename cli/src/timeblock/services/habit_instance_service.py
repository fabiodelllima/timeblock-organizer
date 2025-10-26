"""Service para gerenciamento de instâncias de hábitos."""

from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Habit, HabitInstance, Recurrence
from .event_reordering_service import EventReorderingService


class HabitInstanceService:
    """Serviço de gerenciamento de instâncias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int, start_date: date, end_date: date
    ) -> list[HabitInstance]:
        """Gera instâncias de hábito para período."""
        with get_engine_context() as engine, Session(engine) as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                raise ValueError(f"Habit {habit_id} not found")

            instances = []
            current = start_date
            while current <= end_date:
                if HabitInstanceService._should_create_for_date(
                    habit.recurrence, current
                ):
                    instance = HabitInstance(
                        habit_id=habit_id,
                        date=current,
                        scheduled_start=habit.scheduled_start,
                        scheduled_end=habit.scheduled_end,
                        status="PLANNED",
                    )
                    session.add(instance)
                    instances.append(instance)

                current += timedelta(days=1)

            session.commit()
            for instance in instances:
                session.refresh(instance)
            return instances

    @staticmethod
    def adjust_instance_time(
        instance_id: int,
        new_start: time | None = None,
        new_end: time | None = None,
    ) -> tuple[Optional[HabitInstance], Optional["ReorderingProposal"]]:
        """Ajusta horário de instância e detecta conflitos."""
        # Validação
        if new_start is not None and new_end is not None and new_start >= new_end:
            raise ValueError("Start time must be before end time")
        
        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                raise ValueError(f"HabitInstance {instance_id} not found")

            time_changed = False
            
            if new_start is not None and new_start != instance.scheduled_start:
                instance.scheduled_start = new_start
                time_changed = True
            
            if new_end is not None and new_end != instance.scheduled_end:
                instance.scheduled_end = new_end
                time_changed = True

            if time_changed:
                instance.manually_adjusted = True
                instance.user_override = True

            session.add(instance)
            session.commit()
            session.refresh(instance)
        
        proposal = None
        if time_changed:
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=instance_id,
                event_type="habit_instance"
            )
            
            if conflicts:
                proposal = EventReorderingService.propose_reordering(conflicts)
        
        return instance, proposal

    @staticmethod
    def mark_completed(instance_id: int) -> HabitInstance | None:
        """Marca instância como completa."""
        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                return None

            instance.status = "COMPLETED"
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    @staticmethod
    def mark_skipped(instance_id: int) -> HabitInstance | None:
        """Marca instância como pulada."""
        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                return None

            instance.status = "SKIPPED"
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    @staticmethod
    def _should_create_for_date(recurrence: Recurrence, target_date: date) -> bool:
        """Determina se deve criar instância para data."""
        weekday = target_date.weekday()
        
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
