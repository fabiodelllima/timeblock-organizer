# API: Event Models

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025

---

## HabitInstance

Instância de hábito para data específica.

### Schema
```python
class HabitInstance(SQLModel, table=True):
    __tablename__ = "habit_instance"
    
    # Primary Key
    id: int | None = Field(default=None, primary_key=True)
    
    # Foreign Keys
    habit_id: int = Field(foreign_key="habit.id")
    
    # Temporal
    date: date = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    
    # Estado
    status: HabitInstanceStatus = Field(default=HabitInstanceStatus.PLANNED)
    
    # Controle
    user_override: bool = Field(default=False)
    
    # Relationships
    habit: "Habit" = Relationship(back_populates="instances")
    time_logs: list["TimeLog"] = Relationship(back_populates="habit_instance")
```

### Estados
```python
class HabitInstanceStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
```

### Properties
```python
@property
def duration_minutes(self) -> int:
    """Duração planejada em minutos."""
    start = datetime.combine(date.min, self.scheduled_start)
    end = datetime.combine(date.min, self.scheduled_end)
    return int((end - start).total_seconds() / 60)

@property
def is_overdue(self) -> bool:
    """True se passou do horário e ainda não iniciou."""
    if self.status != HabitInstanceStatus.PLANNED:
        return False
    
    now = datetime.now()
    scheduled = datetime.combine(self.date, self.scheduled_start)
    return now > scheduled
```

### Validações

- scheduled_end > scheduled_start
- date não pode ser no passado (para criação manual)
- Transições de estado válidas

---

## Task

Evento único (não-recorrente).

### Schema
```python
class Task(SQLModel, table=True):
    __tablename__ = "task"
    
    id: int | None = Field(default=None, primary_key=True)
    
    # Dados básicos
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    
    # Temporal
    scheduled_date: date = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    
    # Metadata
    priority: int = Field(default=3, ge=1, le=5)
    completed: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
```

### Properties
```python
@property
def duration_minutes(self) -> int:
    start = datetime.combine(date.min, self.scheduled_start)
    end = datetime.combine(date.min, self.scheduled_end)
    return int((end - start).total_seconds() / 60)

@property
def is_today(self) -> bool:
    return self.scheduled_date == date.today()

@property
def is_overdue(self) -> bool:
    return self.scheduled_date < date.today() and not self.completed
```

---

## ReorderingProposal

Proposta de reorganização de eventos.

### Schema
```python
class ReorderingProposal(SQLModel, table=False):
    """Proposta de reorganização (não persistida)."""
    
    triggered_by: str  # "task:123" ou "habit_instance:456"
    changes: list[ProposedChange]
    warnings: list[str] = Field(default_factory=list)
    
    @property
    def has_conflicts(self) -> bool:
        return len(self.changes) > 0
```

### ProposedChange
```python
class ProposedChange(SQLModel, table=False):
    event_id: int
    event_type: str  # "habit_instance" ou "task"
    event_title: str
    
    current_start: time
    current_end: time
    proposed_start: time
    proposed_end: time
    
    @property
    def delay_minutes(self) -> int:
        curr = datetime.combine(date.min, self.current_start)
        prop = datetime.combine(date.min, self.proposed_start)
        return int((prop - curr).total_seconds() / 60)
```

---

## TimeLog

Registro histórico de execução.

### Schema
```python
class TimeLog(SQLModel, table=True):
    __tablename__ = "time_log"
    
    id: int | None = Field(default=None, primary_key=True)
    
    # Foreign Key
    habit_instance_id: int | None = Field(
        default=None, 
        foreign_key="habit_instance.id"
    )
    
    # Temporal
    started_at: datetime
    ended_at: datetime
    duration_minutes: int
    
    # Pausas
    pauses: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Relationships
    habit_instance: "HabitInstance" = Relationship(back_populates="time_logs")
```

---

## Exemplos de Uso

### Criar HabitInstance
```python
instance = HabitInstance(
    habit_id=1,
    date=date(2025, 11, 1),
    scheduled_start=time(7, 0),
    scheduled_end=time(8, 0),
    status=HabitInstanceStatus.PLANNED
)
session.add(instance)
session.commit()
```

### Query Instâncias do Dia
```python
today_instances = session.exec(
    select(HabitInstance)
    .where(HabitInstance.date == date.today())
    .order_by(HabitInstance.scheduled_start)
).all()
```

### Completar Instância
```python
instance.status = HabitInstanceStatus.COMPLETED
instance.actual_end = datetime.now()

time_log = TimeLog(
    habit_instance_id=instance.id,
    started_at=instance.actual_start,
    ended_at=instance.actual_end,
    duration_minutes=instance.duration_minutes
)
session.add(time_log)
session.commit()
```

---

## Referências

**Services:**
- [HabitInstanceService](../services/habit-service.md)
- [TaskService](../services/task-service.md)
- [EventReorderingService](../services/event-reordering.md)

**Business Rules:**
- [BR002: Event Conflicts](../../04-specifications/business-rules/BR002-event-conflicts.md)

**Diagramas:**
- [Event States](../../02-diagrams/states/event-states.md)

---

**Localização:** `docs/05-api/models/event-models.md`
