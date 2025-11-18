"""Service para gerenciamento de timers."""

from datetime import datetime

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import PauseLog, TimeLog

from .event_reordering_models import Conflict
from .event_reordering_service import EventReorderingService


class TimerService:
    """Serviço de gerenciamento de timers."""

    @staticmethod
    def start_timer(
        event_id: int | None = None,
        task_id: int | None = None,
        habit_instance_id: int | None = None,
        session: Session | None = None,
    ) -> tuple[TimeLog, list[Conflict] | None]:
        """
        Inicia timer e detecta conflitos.

        Detecta conflitos no horário atual mas não bloqueia o início do timer.
        O usuário é informado dos conflitos mas pode prosseguir.

        Args:
            event_id: ID do evento (opcional)
            task_id: ID da task (opcional)
            habit_instance_id: ID da instância de hábito (opcional)
            session: Optional session (for tests/transactions)

        Returns:
            Tupla (timelog criado, lista de conflitos detectados ou None)

        Raises:
            ValueError: Se não exatamente 1 ID fornecido ou timer já ativo
        """
        ids_provided = sum(
            [
                event_id is not None,
                task_id is not None,
                habit_instance_id is not None,
            ]
        )
        if ids_provided != 1:
            raise ValueError("Exactly one ID must be provided")

        active = TimerService.get_active_timer(session=session)
        if active:
            raise ValueError("Another timer is already active")

        def _start(sess: Session) -> TimeLog:
            timelog = TimeLog(
                event_id=event_id,
                task_id=task_id,
                habit_instance_id=habit_instance_id,
                start_time=datetime.now(),
            )
            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            timelog = _start(session)
        else:
            with get_engine_context() as engine, Session(engine) as sess:
                timelog = _start(sess)

        # Detectar conflitos após criar timelog, mas não bloqueia
        conflicts = None
        if task_id:
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=task_id,
                event_type="task"
            ,
                session=session,
            )
        elif habit_instance_id:
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=habit_instance_id,
                event_type="habit_instance"
            ,
                session=session,
            )
        elif event_id:
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=event_id,
                event_type="event"
            ,
                session=session,
            )

        # Retorna None se não houver conflitos
        return timelog, conflicts if conflicts else None

    @staticmethod
    def stop_timer(timelog_id: int, session: Session | None = None) -> TimeLog | None:
        """Para timer e salva duração.
        
        Args:
            timelog_id: ID of timer to stop
            session: Optional session (for tests/transactions)
        """
        def _stop(sess: Session) -> TimeLog | None:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                return None
            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            timelog.end_time = datetime.now()
            total_duration = (timelog.end_time - timelog.start_time).total_seconds()
            paused_duration = timelog.paused_duration or 0
            timelog.duration_seconds = int(total_duration - paused_duration)

            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            return _stop(session)
        
        with get_engine_context() as engine, Session(engine) as sess:
            return _stop(sess)

    @staticmethod
    def cancel_timer(timelog_id: int, session: Session | None = None) -> bool:
        """Cancela timer sem salvar.
        
        Args:
            timelog_id: ID of timer to cancel
            session: Optional session (for tests/transactions)
        """
        def _cancel(sess: Session) -> bool:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                return False
            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            pauses = sess.exec(select(PauseLog).where(PauseLog.timelog_id == timelog_id)).all()
            for pause in pauses:
                sess.delete(pause)

            sess.delete(timelog)
            sess.commit()
            return True

        if session is not None:
            return _cancel(session)
        
        with get_engine_context() as engine, Session(engine) as sess:
            return _cancel(sess)

    @staticmethod
    def pause_timer(timelog_id: int, session: Session | None = None) -> PauseLog:
        """Pausa timer ativo.
        
        Args:
            timelog_id: ID of timer to pause
            session: Optional session (for tests/transactions)
        """
        def _pause(sess: Session) -> PauseLog:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError("TimeLog not found")
            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            pause = PauseLog(
                timelog_id=timelog_id,
                pause_start=datetime.now(),
            )
            sess.add(pause)
            sess.commit()
            sess.refresh(pause)
            return pause

        if session is not None:
            return _pause(session)
        
        with get_engine_context() as engine, Session(engine) as sess:
            return _pause(sess)

    @staticmethod
    def resume_timer(timelog_id: int, session: Session | None = None) -> None:
        """Retoma timer pausado.
        
        Args:
            timelog_id: ID of timer to resume
            session: Optional session (for tests/transactions)
        """
        def _resume(sess: Session) -> None:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError("TimeLog not found")

            pauses = sess.exec(
                select(PauseLog)
                .where(PauseLog.timelog_id == timelog_id)
                .where(PauseLog.pause_end == None)  # noqa: E711
            ).all()

            if not pauses:
                raise ValueError("No active pause found")

            for pause in pauses:
                pause.pause_end = datetime.now()
                pause_duration = (pause.pause_end - pause.pause_start).total_seconds()
                timelog.paused_duration = (timelog.paused_duration or 0) + int(pause_duration)
                sess.add(pause)

            sess.add(timelog)
            sess.commit()

        if session is not None:
            _resume(session)
        else:
            with get_engine_context() as engine, Session(engine) as sess:
                _resume(sess)

    @staticmethod
    def get_active_timer(session: Session | None = None) -> TimeLog | None:
        """Busca timer ativo.
        
        Args:
            session: Optional session (for tests/transactions)
        """
        def _get(sess: Session) -> TimeLog | None:
            return sess.exec(select(TimeLog).where(TimeLog.end_time == None)).first()  # noqa: E711

        if session is not None:
            return _get(session)
        
        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)
