"""Database query utilities."""

from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from ..models import Event


def build_events_query(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    ascending: bool = True,
):
    """Build a query for events with optional date range filter.

    Args:
        start: Filter events starting from this datetime (inclusive).
        end: Filter events up to this datetime (inclusive).
        ascending: Sort by start time ascending (True) or descending (False).

    Returns:
        SQLModel Select statement ready to execute.

    Examples:
        >>> # Query all events, newest first
        >>> query = build_events_query(ascending=False)

        >>> # Query events in a specific range
        >>> from datetime import datetime, timezone
        >>> start = datetime(2025, 10, 1, tzinfo=timezone.utc)
        >>> end = datetime(2025, 10, 31, tzinfo=timezone.utc)
        >>> query = build_events_query(start, end)
    """
    statement = select(Event)

    # Apply date range filters
    if start is not None and end is not None:
        statement = statement.where(
            Event.scheduled_start >= start,
            Event.scheduled_start <= end,
        )  # type: ignore
    elif start is not None:
        statement = statement.where(Event.scheduled_start >= start)  # type: ignore
    elif end is not None:
        statement = statement.where(Event.scheduled_start <= end)  # type: ignore

    # Apply ordering
    if ascending:
        statement = statement.order_by(Event.scheduled_start)  # type: ignore
    else:
        # Pylint false positive: SQLModel dynamic attributes
        statement = statement.order_by(
            Event.scheduled_start.desc()  # pylint: disable=no-member
        )

    return statement


def fetch_events(session: Session, statement) -> list[Event]:
    """Execute query and return list of events.

    Args:
        session: Active SQLModel session.
        statement: Query statement to execute.

    Returns:
        List of Event objects.

    Examples:
        >>> with Session(engine) as session:
        ...     query = build_events_query()
        ...     events = fetch_events(session, query)
    """
    return list(session.exec(statement))


def fetch_events_in_range(
    session: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    ascending: bool = True,
) -> list[Event]:
    """Fetch events in a date range (convenience function).

    Combines build_events_query() and fetch_events() in one call.

    Args:
        session: Active SQLModel session.
        start: Filter events starting from this datetime (inclusive).
        end: Filter events up to this datetime (inclusive).
        ascending: Sort by start time ascending (True) or descending (False).

    Returns:
        List of Event objects matching the criteria.

    Examples:
        >>> # Fetch all events, newest first
        >>> with Session(engine) as session:
        ...     events = fetch_events_in_range(session, ascending=False)

        >>> # Fetch events in October 2025
        >>> from datetime import datetime, timezone
        >>> start = datetime(2025, 10, 1, tzinfo=timezone.utc)
        >>> end = datetime(2025, 10, 31, tzinfo=timezone.utc)
        >>> with Session(engine) as session:
        ...     events = fetch_events_in_range(session, start, end)
    """
    query = build_events_query(start, end, ascending)
    return fetch_events(session, query)
