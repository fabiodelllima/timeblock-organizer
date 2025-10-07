"""Database connection and operations."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine

# Allow database path override for tests
DB_PATH = os.getenv("TIMEBLOCK_DB_PATH")
if DB_PATH is None:
    DATA_DIR = Path(__file__).parent.parent.parent / "data"
    DATA_DIR.mkdir(exist_ok=True)
    DB_PATH = str(DATA_DIR / "timeblock.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"


def get_engine():
    """Get database engine."""
    return create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Create database and tables."""
    from .models import ChangeLog, Event, TimeLog

    engine = get_engine()
    SQLModel.metadata.create_all(engine)


# ========== CRUD Operations ==========


def create_event(
    title: str,
    scheduled_start: datetime,
    scheduled_end: datetime,
    description: str = "",
    color: str = "",
) -> Optional[int]:
    """Create a new event in the database.

    Args:
        title: Event title
        scheduled_start: Start datetime
        scheduled_end: End datetime
        description: Event description (optional)
        color: Display color (optional)

    Returns:
        Event ID if successful, None otherwise
    """
    from .models import Event, EventStatus

    try:
        engine = get_engine()
        with Session(engine) as session:
            event = Event(
                title=title,
                description=description,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                color=color,
                status=EventStatus.PLANNED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            return event.id
    except Exception as e:
        print(f"Error creating event: {e}")
        return None
