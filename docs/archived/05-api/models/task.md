# Task Model

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = Field(default=3, ge=1, le=5)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    estimated_duration: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```
