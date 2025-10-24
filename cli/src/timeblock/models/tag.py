"""Tag model para categorização visual."""
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Tag(SQLModel, table=True):
    """Tag para categorização de hábitos e tarefas."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, index=True)
    color: str = Field(default="#fbd75b")
    gcal_color_id: int = Field(default=5)
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tag")
    habits: List["Habit"] = Relationship(back_populates="tag")
