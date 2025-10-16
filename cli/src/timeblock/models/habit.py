"""Habit model for recurring events."""
from datetime import time
from enum import Enum

from sqlmodel import Field, SQLModel


class Recurrence(str, Enum):
    """Padrões de recorrência."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    WEEKDAYS = "WEEKDAYS"
    WEEKENDS = "WEEKENDS"
    EVERYDAY = "EVERYDAY"


class Habit(SQLModel, table=True):
    """Evento recorrente da rotina."""

    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routine.id")
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence
    color: str | None = Field(default=None, max_length=7)
