"""Service para gerenciamento de instâncias de hábitos."""

from datetime import date, time, timedelta

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Habit, HabitInstance, Recurrence
from src.timeblock.models.enums import NotDoneSubstatus, SkipReason, Status
from src.timeblock.models.time_log import TimeLog
from src.timeblock.utils.logger import get_logger

from .event_reordering_models import Conflict
from .event_reordering_service import EventReorderingService

logger = get_logger(__name__)


class HabitInstanceService:
    """Serviço de gerenciamento de instâncias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date,
        session: Session | None = None,
    ) -> list[HabitInstance]:
        """Gera instâncias de hábito para período."""
        logger.info(
            f"Gerando instâncias para habit_id={habit_id}, período={start_date} até {end_date}"
        )

        def _generate(sess: Session) -> list[HabitInstance]:
            habit = sess.get(Habit, habit_id)
            if not habit:
                logger.error(f"Hábito não encontrado: habit_id={habit_id}")
                raise ValueError(f"Habit {habit_id} not found")

            instances = []
            current = start_date
            while current <= end_date:
                if HabitInstanceService._should_create_for_date(habit.recurrence, current):
                    instance = HabitInstance(
                        habit_id=habit_id,
                        date=current,
                        scheduled_start=habit.scheduled_start,
                        scheduled_end=habit.scheduled_end,
                        status="PLANNED",
                    )
                    sess.add(instance)
                    instances.append(instance)

                current += timedelta(days=1)

            sess.commit()
            for instance in instances:
                sess.refresh(instance)

            logger.info(f"Criadas {len(instances)} instâncias para habit_id={habit_id}")
            return instances

        if session is not None:
            return _generate(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _generate(sess)

    @staticmethod
    def adjust_instance_time(
        instance_id: int,
        new_start: time | None = None,
        new_end: time | None = None,
        session: Session | None = None,
    ) -> tuple[HabitInstance | None, list[Conflict] | None]:
        """
        Ajusta horário de instância específica.

        Apenas esta instância é modificada. O Habit na Routine permanece inalterado.
        Retorna conflitos detectados mas não aplica nenhuma resolução automática.

        Args:
            instance_id: ID da instância a ajustar
            new_start: Novo horário de início (opcional)
            new_end: Novo horário de fim (opcional)
            session: Optional session (for tests/transactions)

        Returns:
            Tupla (instância atualizada, lista de conflitos detectados ou None)
        """
        logger.debug(
            f"Ajustando horário instance_id={instance_id}, new_start={new_start}, new_end={new_end}"
        )

        # Validação
        if new_start is not None and new_end is not None and new_start >= new_end:
            logger.warning(
                f"Horário inválido para instance_id={instance_id}: "
                f"start={new_start} >= end={new_end}"
            )
            raise ValueError("Start time must be before end time")

        def _adjust(sess: Session) -> tuple[HabitInstance, bool]:
            instance = sess.get(HabitInstance, instance_id)
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

            sess.add(instance)
            sess.commit()
            sess.refresh(instance)
            return instance, time_changed

        if session is not None:
            instance, time_changed = _adjust(session)
        else:
            with get_engine_context() as engine, Session(engine) as sess:
                instance, time_changed = _adjust(sess)

        # Detecta conflitos mas não propõe resolução automática
        conflicts = None
        if time_changed:
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=instance_id,
                event_type="habit_instance",
                session=session,
            )

            if conflicts:
                logger.warning(
                    f"Conflitos detectados para instance_id={instance_id}: "
                    f"{len(conflicts)} conflito(s)"
                )

        return instance, conflicts

    @staticmethod
    def skip_habit_instance(
        habit_instance_id: int,
        skip_reason: SkipReason,
        skip_note: str | None = None,
        session: Session | None = None,
    ) -> HabitInstance:
        """Marca HabitInstance como skipped com categorização (BR-HABIT-SKIP-001).

        Args:
            habit_instance_id: ID da instância
            skip_reason: Categoria do skip (SkipReason enum)
            skip_note: Nota opcional (max 500 chars)
            session: Optional session (for tests/transactions)

        Returns:
            HabitInstance atualizada

        Raises:
            ValueError: Se instance não existe, nota muito longa, timer ativo, ou já completada

        Side effects:
            - status → NOT_DONE
            - not_done_substatus → SKIPPED_JUSTIFIED
            - skip_reason → valor fornecido
            - skip_note → texto fornecido ou None
            - done_substatus → None
            - completion_percentage → None
        """
        logger.debug(
            f"Skip habit_instance_id={habit_instance_id}, "
            f"reason={skip_reason.value}, note={skip_note}"
        )

        def _skip(sess: Session) -> HabitInstance:
            # 1. Validação: nota <= 500 chars
            if skip_note and len(skip_note) > 500:
                logger.warning(
                    f"Skip note muito longa para instance_id={habit_instance_id}: "
                    f"{len(skip_note)} chars"
                )
                raise ValueError("Skip note must be <= 500 characters")

            # 2. Buscar HabitInstance
            instance = sess.get(HabitInstance, habit_instance_id)
            if not instance:
                logger.error(f"HabitInstance não encontrada: {habit_instance_id}")
                raise ValueError(f"HabitInstance {habit_instance_id} not found")

            # 3. Validação: não pode ter timer ativo
            statement = select(TimeLog).where(
                TimeLog.habit_instance_id == habit_instance_id,
                TimeLog.end_time.is_(None),  # type: ignore
            )
            active_timer = sess.exec(statement).first()
            if active_timer:
                logger.warning(
                    f"Tentativa de skip com timer ativo: instance_id={habit_instance_id}"
                )
                raise ValueError("Cannot skip with active timer. Stop timer first.")

            # 4. Validação: não pode skip se já completada
            if instance.status == Status.DONE:
                logger.warning(
                    f"Tentativa de skip de instance completada: instance_id={habit_instance_id}"
                )
                raise ValueError("Cannot skip completed instance")

            # 5. Atualizar campos (BR-HABIT-SKIP-001)
            instance.status = Status.NOT_DONE
            instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
            instance.skip_reason = skip_reason
            instance.skip_note = skip_note

            # Limpar campos de completion
            instance.done_substatus = None
            instance.completion_percentage = None

            # 6. Validar consistência (BR-HABIT-INSTANCE-STATUS-001)
            instance.validate_status_consistency()

            # 7. Persistir
            sess.add(instance)
            sess.commit()
            sess.refresh(instance)

            logger.info(
                f"Instance skipped: instance_id={habit_instance_id}, reason={skip_reason.value}"
            )
            return instance

        if session is not None:
            return _skip(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _skip(sess)

    @staticmethod
    def mark_completed(
        instance_id: int,
        session: Session | None = None,
    ) -> HabitInstance | None:
        """Marca instância como completa."""
        logger.debug(f"Marcando como completa: instance_id={instance_id}")

        def _mark(sess: Session) -> HabitInstance | None:
            instance = sess.get(HabitInstance, instance_id)
            if not instance:
                logger.warning(
                    f"Tentativa de completar instância inexistente: instance_id={instance_id}"
                )
                return None

            instance.status = "COMPLETED"
            sess.add(instance)
            sess.commit()
            sess.refresh(instance)

            logger.info(f"Instância completada: instance_id={instance_id}")
            return instance

        if session is not None:
            return _mark(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _mark(sess)

    @staticmethod
    def mark_skipped(
        instance_id: int,
        session: Session | None = None,
    ) -> HabitInstance | None:
        """Marca instância como pulada.

        DEPRECATED: Use skip_habit_instance() com categoria para BR-HABIT-SKIP-001.
        """
        logger.debug(f"Marcando como pulada: instance_id={instance_id}")

        def _mark(sess: Session) -> HabitInstance | None:
            instance = sess.get(HabitInstance, instance_id)
            if not instance:
                logger.warning(
                    f"Tentativa de pular instância inexistente: instance_id={instance_id}"
                )
                return None

            instance.status = "SKIPPED"
            sess.add(instance)
            sess.commit()
            sess.refresh(instance)

            logger.info(f"Instância pulada: instance_id={instance_id}")
            return instance

        if session is not None:
            return _mark(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _mark(sess)

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
