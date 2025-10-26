"""Service for event reordering and conflict detection."""

from datetime import datetime, timedelta

from sqlmodel import Session, or_, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Event, EventStatus, HabitInstance, Task

from .event_reordering_models import (
    Conflict,
    ConflictType,
    EventPriority,
    ProposedChange,
    ReorderingProposal,
)


class EventReorderingService:
    """Service for detecting and resolving event conflicts."""

    @staticmethod
    def detect_conflicts(
        triggered_event_id: int,
        event_type: str,
    ) -> list[Conflict]:
        """
        Detect conflicts with other events caused by triggered event.

        Args:
            triggered_event_id: ID of event that triggered reordering
            event_type: Type of triggered event ("task", "habit_instance", "event")

        Returns:
            List of conflicts found
        """
        with get_engine_context() as engine, Session(engine) as session:
            triggered = EventReorderingService._get_event_by_type(
                session, triggered_event_id, event_type
            )
            if not triggered:
                return []

            start, end = EventReorderingService._get_event_times(triggered, event_type)
            if not start or not end:
                return []

            conflicting_events = EventReorderingService._get_events_in_range(
                session, start, end, triggered_event_id, event_type
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

    @staticmethod
    def calculate_priorities(conflicts: list[Conflict]) -> dict[tuple[int, str], EventPriority]:
        """
        Calculate priority for each event involved in conflicts.

        Args:
            conflicts: List of detected conflicts

        Returns:
            Dictionary mapping (event_id, event_type) to EventPriority
        """
        with get_engine_context() as engine, Session(engine) as session:
            priorities = {}
            now = datetime.now()

            # Collect all unique events
            events_to_check = set()
            for conflict in conflicts:
                events_to_check.add((conflict.triggered_event_id, conflict.triggered_event_type))
                events_to_check.add(
                    (conflict.conflicting_event_id, conflict.conflicting_event_type)
                )

            # Calculate priority for each event
            for event_id, event_type in events_to_check:
                event = EventReorderingService._get_event_by_type(session, event_id, event_type)
                if not event:
                    continue

                priority = EventReorderingService._calculate_event_priority(event, event_type, now)
                priorities[(event_id, event_type)] = priority

            return priorities

    @staticmethod
    def _calculate_event_priority(
        event: Task | HabitInstance | Event,
        event_type: str,
        now: datetime,
    ) -> EventPriority:
        """Calculate priority for a single event."""
        # CRITICAL: IN_PROGRESS events
        if hasattr(event, "status"):
            if event.status == EventStatus.IN_PROGRESS:
                return EventPriority.CRITICAL

        # CRITICAL: Task with deadline < 24h
        if event_type == "task" and hasattr(event, "completed_datetime"):
            if event.completed_datetime:
                deadline = event.completed_datetime
                if deadline < now + timedelta(hours=24):
                    return EventPriority.CRITICAL

        # HIGH: PAUSED events
        if hasattr(event, "status"):
            if event.status == EventStatus.PAUSED:
                return EventPriority.HIGH

        # Get event start time
        start, _ = EventReorderingService._get_event_times(event, event_type)
        if not start:
            return EventPriority.LOW

        # NORMAL: PLANNED with start < 1h
        if hasattr(event, "status"):
            if event.status == EventStatus.PLANNED:
                if start < now + timedelta(hours=1):
                    return EventPriority.NORMAL

        # LOW: Everything else
        return EventPriority.LOW

    @staticmethod
    def _get_event_by_type(
        session: Session, event_id: int, event_type: str
    ) -> Task | HabitInstance | Event | None:
        """Get event by type."""
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
        """Get start and end times for event."""
        if event_type == "task":
            if event.scheduled_datetime:
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
        """Get all events that may conflict in time range."""
        events = []

        # Get tasks
        task_stmt = select(Task).where(
            Task.scheduled_datetime.between(start - timedelta(hours=1), end + timedelta(hours=1))
        )
        if exclude_type == "task":
            task_stmt = task_stmt.where(Task.id != exclude_id)
        for task in session.exec(task_stmt).all():
            events.append((task, "task"))

        # Get habit instances
        date = start.date()
        habit_stmt = select(HabitInstance).where(HabitInstance.date == date)
        if exclude_type == "habit_instance":
            habit_stmt = habit_stmt.where(HabitInstance.id != exclude_id)
        for habit in session.exec(habit_stmt).all():
            events.append((habit, "habit_instance"))

        # Get events
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
        """Check if two time ranges overlap."""
        return start1 < end2 and start2 < end1

    @staticmethod
    def propose_reordering(conflicts: list[Conflict]) -> ReorderingProposal:
        """
        Propose reordering solution for conflicts.

        Args:
            conflicts: List of detected conflicts

        Returns:
            ReorderingProposal with suggested changes
        """
        if not conflicts:
            return ReorderingProposal(
                conflicts=[],
                proposed_changes=[],
                estimated_duration_shift=0,
            )

        with get_engine_context() as engine, Session(engine) as session:
            # Calculate priorities
            priorities = EventReorderingService.calculate_priorities(conflicts)

            # Collect all events to reorder
            events_data = []
            for (event_id, event_type), priority in priorities.items():
                event = EventReorderingService._get_event_by_type(session, event_id, event_type)
                if not event:
                    continue
                start, end = EventReorderingService._get_event_times(event, event_type)
                if not start or not end:
                    continue

                # Get event title
                if event_type == "habit_instance":
                    event_title = event.habit.title if event.habit else f"Habit Instance {event_id}"
                else:  # task or event
                    event_title = event.title if hasattr(event, "title") else f"Event {event_id}"

                events_data.append(
                    {
                        "event_id": event_id,
                        "event_type": event_type,
                        "event": event,
                        "event_title": event_title,
                        "priority": priority,
                        "current_start": start,
                        "current_end": end,
                        "duration": (end - start).total_seconds() / 60,  # minutes
                    }
                )

            # Sort by priority (CRITICAL first), then by start time
            events_data.sort(key=lambda x: (x["priority"].value, x["current_start"]))

            # Calculate new times sequentially
            proposed_changes = []
            current_time = None

            for event_data in events_data:
                # HIGH and CRITICAL priorities don't move
                if event_data["priority"] in (EventPriority.CRITICAL, EventPriority.HIGH):
                    current_time = event_data["current_end"]
                    continue

                # NORMAL and LOW priorities get reordered after CRITICAL/HIGH
                if current_time is None:
                    # First event after critical/high - use its original time
                    current_time = event_data["current_start"]

                new_start = current_time
                new_end = current_time + timedelta(minutes=event_data["duration"])

                # Only add change if times actually changed
                if new_start != event_data["current_start"] or new_end != event_data["current_end"]:
                    # Calculate time shift for reason
                    shift_minutes = int(
                        (new_start - event_data["current_start"]).total_seconds() / 60
                    )
                    reason = f"Reordered due to {event_data['priority'].name} priority (shifted {shift_minutes:+d} min)"

                    proposed_changes.append(
                        ProposedChange(
                            event_id=event_data["event_id"],
                            event_type=event_data["event_type"],
                            event_title=event_data["event_title"],
                            current_start=event_data["current_start"],
                            current_end=event_data["current_end"],
                            proposed_start=new_start,
                            proposed_end=new_end,
                            priority=event_data["priority"],
                            reason=reason,
                        )
                    )

                current_time = new_end

            # Calculate total duration shift
            total_shift = sum(
                (change.proposed_end - change.current_end).total_seconds() / 60
                for change in proposed_changes
            )

            return ReorderingProposal(
                conflicts=conflicts,
                proposed_changes=proposed_changes,
                estimated_duration_shift=int(total_shift),
            )

    @staticmethod
    def apply_reordering(proposal: ReorderingProposal) -> bool:
        """
        Aplica mudanças propostas ao banco.
        
        Args:
            proposal: Proposta com mudanças
            
        Returns:
            bool: True se aplicado com sucesso
        """
        if not proposal.proposed_changes:
            return False
            
        with get_engine_context() as engine, Session(engine) as session:
            for change in proposal.proposed_changes:
                event = EventReorderingService._get_event_by_type(
                    session, change.event_id, change.event_type
                )
                
                if not event:
                    continue
                
                # Atualizar horários
                EventReorderingService._set_event_times(
                    event, change.event_type, change.proposed_start, change.proposed_end
                )
                
                # Marcar como reordenado automaticamente
                if hasattr(event, 'user_override'):
                    event.user_override = False
                
                session.add(event)
            
            session.commit()
            return True

    @staticmethod
    def _set_event_times(
        event: Task | HabitInstance | Event,
        event_type: str,
        new_start: datetime,
        new_end: datetime,
    ) -> None:
        """Set new start and end times for event."""
        if event_type == "task":
            event.scheduled_datetime = new_start
        elif event_type == "habit_instance":
            event.scheduled_start = new_start.time()
            event.scheduled_end = new_end.time()
        elif event_type == "event":
            event.scheduled_start = new_start
            event.scheduled_end = new_end
