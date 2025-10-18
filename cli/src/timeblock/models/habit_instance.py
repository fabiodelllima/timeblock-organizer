"""HabitInstance model for concrete habit occurrences."""

from datetime import date as date_type
from datetime import datetime, time

from sqlmodel import Field, SQLModel


class HabitInstance(SQLModel, table=True):
    """Instância concreta de habit em dia específico."""

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id")
    date: date_type = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    status: str = Field(default="planned")
    manually_adjusted: bool = Field(default=False)
