"""Routine model for weekly habit templates."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class Routine(SQLModel, table=True):
    """Template semanal de habits."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
