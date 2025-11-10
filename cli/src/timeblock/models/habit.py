"""Habit model."""
from datetime import time
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .habit_instance import HabitInstance
from .routine import Routine

if TYPE_CHECKING:
    from .tag import Tag


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

    __tablename__ = "habits"

    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routines.id")
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence
    color: str | None = Field(default=None, max_length=7)
    tag_id: int | None = Field(default=None, foreign_key="tags.id")

    # Relationships
    routine: Routine | None = Relationship(back_populates="habits")
    instances: list[HabitInstance] = Relationship(
        back_populates="habit", cascade_delete=True
    )
    tag: Optional["Tag"] = Relationship(back_populates="habits")
