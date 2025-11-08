"""Service para gerenciamento de instâncias de hábitos."""

from datetime import date, time, timedelta

from sqlmodel import Session

from src.timeblock.database import get_engine_context
from src.timeblock.models import Habit, HabitInstance, Recurrence
from src.timeblock.utils.logger import get_logger

from .event_reordering_models import Conflict
from .event_reordering_service import EventReorderingService

logger = get_logger(__name__)


class HabitInstanceService:
    """Serviço de gerenciamento de instâncias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int, start_date: date, end_date: date
    ) -> list[HabitInstance]:
        """Gera instâncias de hábito para período."""
        logger.info(
            f"Gerando instâncias para habit_id={habit_id}, "
            f"período={start_date} até {end_date}"
        )

        with get_engine_context() as engine, Session(engine) as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                logger.error(f"Hábito não encontrado: habit_id={habit_id}")
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

            logger.info(
                f"Criadas {len(instances)} instâncias para habit_id={habit_id}"
            )
            return instances

    @staticmethod
    def adjust_instance_time(
        instance_id: int,
        new_start: time | None = None,
        new_end: time | None = None,
    ) -> tuple[HabitInstance | None, list[Conflict] | None]:
        """
        Ajusta horário de instância específica.

        Apenas esta instância é modificada. O Habit na Routine permanece inalterado.
        Retorna conflitos detectados mas não aplica nenhuma resolução automática.

        Args:
            instance_id: ID da instância a ajustar
            new_start: Novo horário de início (opcional)
            new_end: Novo horário de fim (opcional)

        Returns:
            Tupla (instância atualizada, lista de conflitos detectados ou None)
        """
        logger.debug(
            f"Ajustando horário instance_id={instance_id}, "
            f"new_start={new_start}, new_end={new_end}"
        )

        # Validação
        if new_start is not None and new_end is not None and new_start >= new_end:
            logger.warning(
                f"Horário inválido para instance_id={instance_id}: "
                f"start={new_start} >= end={new_end}"
            )
            raise ValueError("Start time must be before end time")

        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                logger.error(f"Instância não encontrada: instance_id={instance_id}")
                raise ValueError(f"HabitInstance {instance_id} not found")

            time_changed = False

            if new_start is not None and new_start != instance.scheduled_start:
                instance.scheduled_start = new_start
                time_changed = True

            if new_end is not None and new_end != instance.scheduled_end:
                instance.scheduled_end = new_end
                time_changed = True

            if time_changed:
                logger.info(
                    f"Horário ajustado para instance_id={instance_id}, "
                    f"novo horário={instance.scheduled_start}-{instance.scheduled_end}"
                )

            session.add(instance)
            session.commit()
            session.refresh(instance)

        # Detecta conflitos mas não propõe resolução automática
        conflicts = None
        if time_changed:
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=instance_id,
                event_type="habit_instance"
            )

            if conflicts:
                logger.warning(
                    f"Conflitos detectados para instance_id={instance_id}: "
                    f"{len(conflicts)} conflito(s)"
                )

        return instance, conflicts

    @staticmethod
    def mark_completed(instance_id: int) -> HabitInstance | None:
        """Marca instância como completa."""
        logger.debug(f"Marcando como completa: instance_id={instance_id}")

        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                logger.warning(
                    f"Tentativa de completar instância inexistente: "
                    f"instance_id={instance_id}"
                )
                return None

            instance.status = "COMPLETED"
            session.add(instance)
            session.commit()
            session.refresh(instance)

            logger.info(f"Instância completada: instance_id={instance_id}")
            return instance

    @staticmethod
    def mark_skipped(instance_id: int) -> HabitInstance | None:
        """Marca instância como pulada."""
        logger.debug(f"Marcando como pulada: instance_id={instance_id}")

        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                logger.warning(
                    f"Tentativa de pular instância inexistente: "
                    f"instance_id={instance_id}"
                )
                return None

            instance.status = "SKIPPED"
            session.add(instance)
            session.commit()
            session.refresh(instance)

            logger.info(f"Instância pulada: instance_id={instance_id}")
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
