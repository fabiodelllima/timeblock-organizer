"""Service para gerenciar timers de HabitInstance."""

from datetime import datetime

from sqlmodel import Session, select

from ..database.engine import get_engine_context
from ..models.enums import DoneSubstatus, Status
from ..models.habit_instance import HabitInstance
from ..models.time_log import TimeLog


class TimerService:
    """Service para operações de timer."""

    # Estado em memória para pause tracking (BR-TIMER-006 MVP)
    _active_pause_start: datetime | None = None

    @staticmethod
    def start_timer(habit_instance_id: int, session: Session | None = None) -> TimeLog:
        """Inicia timer para HabitInstance.

        Args:
            habit_instance_id: ID da instância
            session: Optional session (for tests/transactions)

        Returns:
            TimeLog criado

        Raises:
            ValueError: Se instance não existe ou timer já ativo
        """

        def _start(sess: Session) -> TimeLog:
            instance = sess.get(HabitInstance, habit_instance_id)
            if not instance:
                raise ValueError(f"HabitInstance {habit_instance_id} not found")

            # Verificar se já existe timer ativo
            statement = select(TimeLog).where(
                TimeLog.habit_instance_id == habit_instance_id, TimeLog.end_time is None
            )
            existing_timer = sess.exec(statement).first()
            if existing_timer:
                raise ValueError("Timer already active for this instance")

            timelog = TimeLog(
                habit_instance_id=habit_instance_id,
                start_time=datetime.now(),
                end_time=None,
            )
            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            return _start(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _start(sess)

    @staticmethod
    def stop_timer(timelog_id: int, session: Session | None = None) -> TimeLog:
        """Para timer e calcula substatus automaticamente (BR-TIMER-006).

        Args:
            timelog_id: ID of timer to stop
            session: Optional session (for tests/transactions)

        Returns:
            TimeLog atualizado com duração

        Raises:
            ValueError: Se timer não existe, já parado, ou dados inválidos

        Side effects:
            - Atualiza HabitInstance com status=DONE
            - Calcula e seta done_substatus (FULL/PARTIAL/OVERDONE/EXCESSIVE)
            - Calcula e persiste completion_percentage
        """

        def _stop(sess: Session) -> TimeLog:
            # 1. Buscar TimeLog
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError(f"TimeLog {timelog_id} not found")

            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            # 2. Parar timer
            timelog.end_time = datetime.now()
            total_duration = (timelog.end_time - timelog.start_time).total_seconds()
            paused_duration = timelog.paused_duration or 0
            timelog.duration_seconds = int(total_duration - paused_duration)

            # 3. Buscar HabitInstance (garantir não-None)
            if timelog.habit_instance_id is None:
                raise ValueError("TimeLog must have habit_instance_id")

            instance = sess.get(HabitInstance, timelog.habit_instance_id)
            if not instance:
                raise ValueError(f"HabitInstance {timelog.habit_instance_id} not found")

            # 4. Calcular completion percentage (BR-TIMER-006)
            # Target duration em segundos
            target_start = datetime.combine(instance.date, instance.scheduled_start)
            target_end = datetime.combine(instance.date, instance.scheduled_end)
            target_seconds = (target_end - target_start).total_seconds()

            if target_seconds <= 0:
                raise ValueError("Target duration must be positive")

            # Completion percentage
            actual_seconds = timelog.duration_seconds
            completion_percentage = int((actual_seconds / target_seconds) * 100)

            # 5. Determinar substatus baseado em completion (BR-TIMER-006)
            if completion_percentage < 90:
                done_substatus = DoneSubstatus.PARTIAL
            elif completion_percentage <= 110:
                done_substatus = DoneSubstatus.FULL
            elif completion_percentage <= 150:
                done_substatus = DoneSubstatus.OVERDONE
            else:
                done_substatus = DoneSubstatus.EXCESSIVE

            # 6. Atualizar HabitInstance
            instance.status = Status.DONE
            instance.done_substatus = done_substatus
            instance.completion_percentage = completion_percentage
            instance.not_done_substatus = None

            # 7. Validar consistência (BR-HABIT-INSTANCE-STATUS-001)
            instance.validate_status_consistency()

            # 8. Persistir tudo
            sess.add(timelog)
            sess.add(instance)
            sess.commit()
            sess.refresh(timelog)
            sess.refresh(instance)

            return timelog

        if session is not None:
            return _stop(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _stop(sess)

    @staticmethod
    def pause_timer(timelog_id: int, session: Session | None = None) -> TimeLog:
        """Marca início de pausa (não persiste ainda).

        BR-TIMER-006: Pause Tracking MVP

        Args:
            timelog_id: ID do TimeLog
            session: Optional session (for tests/transactions)

        Returns:
            TimeLog (pausa marcada em memória)

        Raises:
            ValueError: Se timer não existe, já stopped, ou já pausado
        """

        def _pause(sess: Session) -> TimeLog:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError(f"TimeLog {timelog_id} not found")

            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            if TimerService._active_pause_start is not None:
                raise ValueError("Timer already paused")

            TimerService._active_pause_start = datetime.now()
            return timelog

        if session is not None:
            return _pause(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _pause(sess)

    @staticmethod
    def get_active_timer(habit_instance_id: int, session: Session | None = None) -> TimeLog | None:
        """Busca timer ativo para HabitInstance.

        Args:
            habit_instance_id: ID da instância
            session: Optional session

        Returns:
            TimeLog ativo ou None se não houver
        """

        def _get(sess: Session) -> TimeLog | None:
            statement = select(TimeLog).where(
                TimeLog.habit_instance_id == habit_instance_id, TimeLog.end_time is None
            )
            return sess.exec(statement).first()

        if session is not None:
            return _get(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)
