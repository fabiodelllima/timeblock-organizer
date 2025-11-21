"""Serviço para detecção de conflitos de eventos."""

from datetime import date, datetime, timedelta

from sqlmodel import Session, or_, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Event, HabitInstance, Task

from .event_reordering_models import Conflict, ConflictType


class EventReorderingService:
    """Serviço para detecção de conflitos de eventos."""

    @staticmethod
    def detect_conflicts(
        triggered_event_id: int,
        event_type: str,
        session: Session | None = None,
    ) -> list[Conflict]:
        """
        Detecta conflitos com outros eventos causados pelo evento disparador.

        Este método apenas detecta e retorna informações de conflito.
        NÃO modifica nenhum dado no banco de dados.

        Args:
            triggered_event_id: ID do evento que disparou a verificação
            event_type: Tipo do evento disparador ("task", "habit_instance", "event")
            session: Optional session (for tests/transactions)

        Returns:
            Lista de conflitos encontrados. Lista vazia se não houver conflitos.
        """
        def _detect(sess: Session) -> list[Conflict]:
            triggered = EventReorderingService._get_event_by_type(
                sess, triggered_event_id, event_type
            )
            if not triggered:
                return []

            start, end = EventReorderingService._get_event_times(triggered, event_type)
            if not start or not end:
                return []

            conflicting_events = EventReorderingService._get_events_in_range(
                sess, start, end, triggered_event_id, event_type
            )

            conflicts = []
            for conf_event, conf_type in conflicting_events:
                conf_start, conf_end = EventReorderingService._get_event_times(
                    conf_event, conf_type
                )
                if not conf_start or not conf_end:
                    continue

                if EventReorderingService._has_overlap(start, end, conf_start, conf_end):
                    conflicts.append(
                        Conflict(
                            triggered_event_id=triggered_event_id,
                            triggered_event_type=event_type,
                            conflicting_event_id=conf_event.id,
                            conflicting_event_type=conf_type,
                            conflict_type=ConflictType.OVERLAP,
                            triggered_start=start,
                            triggered_end=end,
                            conflicting_start=conf_start,
                            conflicting_end=conf_end,
                        )
                    )

            return conflicts

        if session is not None:
            return _detect(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _detect(sess)

    @staticmethod
    def get_conflicts_for_day(
        target_date: date,
        session: Session | None = None,
    ) -> list[Conflict]:
        """
        Obtém todos os conflitos detectados em um dia específico.

        Útil para visualização geral dos conflitos da agenda do dia.

        Args:
            target_date: Data para verificar conflitos
            session: Optional session (for tests/transactions)

        Returns:
            Lista de todos os conflitos do dia
        """
        def _get_conflicts(sess: Session) -> list[Conflict]:
            all_conflicts = []

            # Busca todos os eventos do dia
            day_start = datetime.combine(target_date, datetime.min.time())
            day_end = datetime.combine(target_date, datetime.max.time())

            # Busca todas as tasks do dia
            task_stmt = select(Task).where(
                Task.scheduled_datetime.between(day_start, day_end)
            )
            tasks = list(sess.exec(task_stmt).all())

            # Busca todas as instâncias de hábitos do dia
            habit_stmt = select(HabitInstance).where(HabitInstance.date == target_date)
            habits = list(sess.exec(habit_stmt).all())

            # Busca todos os eventos do dia
            event_stmt = select(Event).where(
                or_(
                    Event.scheduled_start.between(day_start, day_end),
                    Event.scheduled_end.between(day_start, day_end),
                    (Event.scheduled_start <= day_start) & (Event.scheduled_end >= day_end),
                )
            )
            events = list(sess.exec(event_stmt).all())

            # Verifica cada task contra os outros
            for task in tasks:
                task_conflicts = EventReorderingService.detect_conflicts(
                    task.id, "task", session=sess
                )
                all_conflicts.extend(task_conflicts)

            # Verifica cada instância de hábito contra os outros
            for habit in habits:
                habit_conflicts = EventReorderingService.detect_conflicts(
                    habit.id, "habit_instance", session=sess
                )
                all_conflicts.extend(habit_conflicts)

            # Verifica cada evento contra os outros
            for event in events:
                event_conflicts = EventReorderingService.detect_conflicts(
                    event.id, "event", session=sess
                )
                all_conflicts.extend(event_conflicts)

            # Remove conflitos duplicados (A vs B e B vs A)
            unique_conflicts = []
            seen_pairs = set()

            for conflict in all_conflicts:
                pair = tuple(
                    sorted(
                        [
                            (conflict.triggered_event_id, conflict.triggered_event_type),
                            (conflict.conflicting_event_id, conflict.conflicting_event_type),
                        ]
                    )
                )
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_conflicts.append(conflict)

            return unique_conflicts

        if session is not None:
            return _get_conflicts(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _get_conflicts(sess)

    @staticmethod
    def _get_event_by_type(
        session: Session, event_id: int, event_type: str
    ) -> Task | HabitInstance | Event | None:
        """Busca evento por tipo."""
        if event_type == "task":
            return session.get(Task, event_id)
        elif event_type == "habit_instance":
            return session.get(HabitInstance, event_id)
        elif event_type == "event":
            return session.get(Event, event_id)
        return None

    @staticmethod
    def _get_event_times(
        event: Task | HabitInstance | Event, event_type: str
    ) -> tuple[datetime | None, datetime | None]:
        """Obtém horários de início e fim do evento."""
        if event_type == "task":
            if event.scheduled_datetime:
                # Assume duração de 1 hora para tasks
                return event.scheduled_datetime, event.scheduled_datetime + timedelta(hours=1)
        elif event_type == "habit_instance":
            if event.scheduled_start and event.scheduled_end:
                start = datetime.combine(event.date, event.scheduled_start)
                end = datetime.combine(event.date, event.scheduled_end)
                return start, end
        elif event_type == "event":
            if event.scheduled_start and event.scheduled_end:
                return event.scheduled_start, event.scheduled_end
        return None, None

    @staticmethod
    def _get_events_in_range(
        session: Session,
        start: datetime,
        end: datetime,
        exclude_id: int,
        exclude_type: str,
    ) -> list[tuple[Task | HabitInstance | Event, str]]:
        """Busca todos os eventos que podem conflitar no intervalo de tempo."""
        events = []

        # Busca tasks
        task_stmt = select(Task).where(
            Task.scheduled_datetime.between(start - timedelta(hours=1), end + timedelta(hours=1))
        )
        if exclude_type == "task":
            task_stmt = task_stmt.where(Task.id != exclude_id)
        for task in session.exec(task_stmt).all():
            events.append((task, "task"))

        # Busca instâncias de hábitos
        date = start.date()
        habit_stmt = select(HabitInstance).where(HabitInstance.date == date)
        if exclude_type == "habit_instance":
            habit_stmt = habit_stmt.where(HabitInstance.id != exclude_id)
        for habit in session.exec(habit_stmt).all():
            events.append((habit, "habit_instance"))

        # Busca eventos
        event_stmt = select(Event).where(
            or_(
                Event.scheduled_start.between(start, end),
                Event.scheduled_end.between(start, end),
                (Event.scheduled_start <= start) & (Event.scheduled_end >= end),
            )
        )
        if exclude_type == "event":
            event_stmt = event_stmt.where(Event.id != exclude_id)
        for evt in session.exec(event_stmt).all():
            events.append((evt, "event"))

        return events

    @staticmethod
    def _has_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """Verifica se dois intervalos de tempo se sobrepõem."""
        return start1 < end2 and start2 < end1
