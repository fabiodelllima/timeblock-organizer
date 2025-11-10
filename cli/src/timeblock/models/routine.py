"""Routine model for weekly habit templates."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .habit import Habit


class Routine(SQLModel, table=True):
    """Template semanal de habits."""

    __tablename__ = "routines"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    habits: list["Habit"] = Relationship(back_populates="routine")
