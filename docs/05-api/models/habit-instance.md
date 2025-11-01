# HabitInstance Model

```python
class HabitInstance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id")
    scheduled_date: datetime
    actual_start_date: Optional[datetime] = None
    status: HabitStatus = Field(default=HabitStatus.PLANNED)
    duration: Optional[int] = None  # Override
    user_override: bool = Field(default=False)

    # Reordering
    was_reordered: bool = Field(default=False)
    original_start: Optional[datetime] = None
    reorder_reason: Optional[str] = None

    # Relationships
    habit: Habit = Relationship(back_populates="instances")

class HabitStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
```

## Properties

```python
@property
def is_overdue(self) -> bool:
    return (
        self.status == HabitStatus.PLANNED
        and self.scheduled_date < datetime.now()
    )
```
