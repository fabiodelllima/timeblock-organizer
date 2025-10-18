"""Task model for one-time events."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Evento único e pontual."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    scheduled_datetime: datetime = Field(index=True)
    completed_datetime: datetime | None = None
    description: str | None = Field(default=None, max_length=1000)
    started_at: datetime | None = None
    color: str | None = Field(default=None, max_length=7)
    tag_id: int | None = Field(default=None, foreign_key="tag.id")
