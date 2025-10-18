"""Service para gerenciamento de timers."""

from datetime import datetime

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import PauseLog, TimeLog


class TimerService:
    """Serviço de gerenciamento de timers."""

    @staticmethod
    def start_timer(
        event_id: int | None = None,
        task_id: int | None = None,
        habit_instance_id: int | None = None,
    ) -> TimeLog:
        """Inicia timer."""
        ids_provided = sum(
            [
                event_id is not None,
                task_id is not None,
                habit_instance_id is not None,
            ]
        )
        if ids_provided != 1:
            raise ValueError("Exactly one ID must be provided")

        active = TimerService.get_active_timer()
        if active:
            raise ValueError("Another timer is already active")

        timelog = TimeLog(
            event_id=event_id,
            task_id=task_id,
            habit_instance_id=habit_instance_id,
            start_time=datetime.now(),
        )

        with get_engine_context() as engine, Session(engine) as session:
            session.add(timelog)
            session.commit()
            session.refresh(timelog)
            return timelog

    @staticmethod
    def stop_timer(timelog_id: int) -> TimeLog | None:
        """Para timer e salva duração."""
        with get_engine_context() as engine, Session(engine) as session:
            timelog = session.get(TimeLog, timelog_id)
            if not timelog:
                return None
            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            timelog.end_time = datetime.now()
            total_duration = (timelog.end_time - timelog.start_time).total_seconds()
            paused_duration = timelog.paused_duration or 0
            timelog.duration_seconds = int(total_duration - paused_duration)

            session.add(timelog)
            session.commit()
            session.refresh(timelog)
            return timelog

    @staticmethod
    def cancel_timer(timelog_id: int) -> bool:
        """Cancela timer sem salvar."""
        with get_engine_context() as engine, Session(engine) as session:
            timelog = session.get(TimeLog, timelog_id)
            if not timelog:
                return False
            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            # Deletar pausas associadas
            pauses = session.exec(select(PauseLog).where(PauseLog.timelog_id == timelog_id)).all()
            for pause in pauses:
                session.delete(pause)

            session.delete(timelog)
            session.commit()
            return True

    @staticmethod
    def pause_timer(timelog_id: int) -> PauseLog:
        """Pausa timer ativo."""
        with get_engine_context() as engine, Session(engine) as session:
            timelog = session.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError("TimeLog not found")
            if timelog.end_time is not None:
                raise ValueError("Timer already stopped")

            pause = PauseLog(
                timelog_id=timelog_id,
                pause_start=datetime.now(),
            )
            session.add(pause)
            session.commit()
            session.refresh(pause)
            return pause

    @staticmethod
    def resume_timer(timelog_id: int) -> None:
        """Retoma timer pausado."""
        with get_engine_context() as engine, Session(engine) as session:
            timelog = session.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError("TimeLog not found")

            pauses = session.exec(
                select(PauseLog)
                .where(PauseLog.timelog_id == timelog_id)
                .where(PauseLog.pause_end == None) # noqa: E711
            ).all()

            if not pauses:
                raise ValueError("No active pause found")

            for pause in pauses:
                pause.pause_end = datetime.now()
                pause_duration = (pause.pause_end - pause.pause_start).total_seconds()
                timelog.paused_duration = (timelog.paused_duration or 0) + int(pause_duration)
                session.add(pause)

            session.add(timelog)
            session.commit()

    @staticmethod
    def get_active_timer() -> TimeLog | None:
        """Busca timer ativo."""
        with get_engine_context() as engine, Session(engine) as session:
            return session.exec(select(TimeLog).where(TimeLog.end_time == None)).first() # noqa: E711
