"""Tag model for categorizing tasks and habits."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .habit import Habit
    from .task import Task


class Tag(SQLModel, table=True):
    """Tag for categorization."""

    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=1, max_length=50)
    color: str = Field(default="#808080", max_length=7)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="tag")
    habits: list["Habit"] = Relationship(back_populates="tag")
