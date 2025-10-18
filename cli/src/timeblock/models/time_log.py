"""Unified TimeLog model for time tracking."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TimeLog(SQLModel, table=True):
    """Registro unificado de tempo rastreado."""

    __tablename__ = "time_log"

    id: int | None = Field(default=None, primary_key=True)

    # Foreign keys opcionais (apenas um preenchido por registro)
    event_id: int | None = Field(foreign_key="event.id", default=None, index=True)
    task_id: int | None = Field(foreign_key="task.id", default=None, index=True)
    habit_instance_id: int | None = Field(foreign_key="habitinstance.id", default=None, index=True)

    # Timestamps
    start_time: datetime
    end_time: datetime | None = None

    # Durations
    duration_seconds: int | None = None
    paused_duration: int | None = Field(default=0)  # compatibilidade v1.0

    # Notes
    notes: str | None = Field(default=None, max_length=500)
