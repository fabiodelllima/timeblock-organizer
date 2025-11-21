"""Task model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tag import Tag


class Task(SQLModel, table=True):
    """Tarefa pontual agendada."""

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    scheduled_datetime: datetime = Field(index=True)
    completed_datetime: datetime | None = Field(default=None)
    description: str | None = Field(default=None)
    color: str | None = Field(default=None)
    tag_id: int | None = Field(default=None, foreign_key="tags.id")

    # Relationships
    tag: Optional["Tag"] = Relationship(back_populates="tasks")
