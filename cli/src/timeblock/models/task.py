"""Task model com campos para event reordering."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Task(SQLModel, table=True):
    """Evento único e pontual."""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    scheduled_datetime: datetime = Field(index=True)
    completed_datetime: Optional[datetime] = None
    description: Optional[str] = None
    
    # Campos para CLI refinements
    started_at: Optional[datetime] = None
    color: Optional[str] = None
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    
    # Relationships
    tag: Optional["Tag"] = Relationship(back_populates="tasks")
