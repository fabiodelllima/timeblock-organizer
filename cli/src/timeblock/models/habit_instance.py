"""HabitInstance model."""
from datetime import date as date_type
from datetime import datetime, time
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .habit import Habit


class HabitInstanceStatus(str, Enum):
    """Status de instância de hábito."""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    SKIPPED = "SKIPPED"


class HabitInstance(SQLModel, table=True):
    """Instância específica de hábito em data específica."""

    __tablename__ = "habitinstance"

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date_type = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    status: HabitInstanceStatus = Field(default=HabitInstanceStatus.PLANNED)

    # Relationships
    habit: Optional["Habit"] = Relationship(back_populates="instances")

    @property
    def is_overdue(self) -> bool:
        """Verifica se instância está atrasada."""
        if self.status != HabitInstanceStatus.PLANNED:
            return False

        now = datetime.now()
        scheduled = datetime.combine(self.date, self.scheduled_start)
        return now > scheduled
