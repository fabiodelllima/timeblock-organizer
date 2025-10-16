"""Data models for TimeBlock application."""

from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class EventStatus(str, Enum):
    """Event lifecycle status."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Event(SQLModel, table=True):
    """Time-blocked event with scheduling information."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: str | None = Field(default=None, max_length=1000)
    # Optional color for visual organization (hex format: #RRGGBB)
    color: str | None = Field(default=None, max_length=7)
    status: EventStatus = Field(default=EventStatus.PLANNED)
    # Scheduled time window
    scheduled_start: datetime = Field(index=True)
    scheduled_end: datetime
    # Audit timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TimeLog(SQLModel, table=True):
    """Actual execution time record for an event."""

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    # Actual execution timeframe
    actual_start: datetime
    actual_end: datetime | None = Field(default=None)
    # Accumulated pause time in seconds
    paused_duration: int = Field(default=0)
    # Audit timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PauseLog(SQLModel, table=True):
    """Individual pause intervals for time tracking."""

    id: int | None = Field(default=None, primary_key=True)
    timelog_id: int = Field(foreign_key="timelog.id", index=True)
    # Pause interval
    pause_start: datetime
    pause_end: datetime | None = Field(default=None)
    # Audit timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChangeType(str, Enum):
    """Types of changes for audit logging."""

    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    RESCHEDULED = "rescheduled"
    DELETED = "deleted"


class ChangeLog(SQLModel, table=True):
    """Audit trail for event modifications."""

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    change_type: ChangeType
    field_name: str | None = Field(default=None, max_length=50)
    old_value: str | None = Field(default=None, max_length=500)
    new_value: str | None = Field(default=None, max_length=500)
    # Audit timestamp (indexed for chronological queries)
    changed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
