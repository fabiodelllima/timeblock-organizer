"""Habit model."""
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from .habit_instance import HabitInstance
from .routine import Routine
from .shared import RecurrenceBase, SharedBase

if TYPE_CHECKING:
    from .tag import Tag


class Habit(SharedBase, RecurrenceBase, table=True):
    """Hábito recorrente vinculado a uma rotina."""

    __tablename__ = "habits"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    routine_id: int = Field(foreign_key="routines.id")
    tag_id: int | None = Field(default=None, foreign_key="tags.id")

    # Relationships
    routine: Routine | None = Relationship(back_populates="habits")
    instances: list[HabitInstance] = Relationship(
        back_populates="habit", cascade_delete=True
    )
    tag: Optional["Tag"] = Relationship(back_populates="habits")
