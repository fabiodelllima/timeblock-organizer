# API: Habit Models

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025

---

## Habit

Template de hábito recorrente.

### Schema
```python
class Habit(SQLModel, table=True):
    __tablename__ = "habit"
    
    # Primary Key
    id: int | None = Field(default=None, primary_key=True)
    
    # Foreign Key
    routine_id: int = Field(foreign_key="routine.id")
    
    # Dados básicos
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    
    # Temporal
    scheduled_start: time
    scheduled_end: time
    recurrence: RecurrenceType
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    routine: "Routine" = Relationship(back_populates="habits")
    instances: list["HabitInstance"] = Relationship(
        back_populates="habit",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### RecurrenceType
```python
class RecurrenceType(str, Enum):
    DAILY = "DAILY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
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
def is_daily(self) -> bool:
    return self.recurrence == RecurrenceType.DAILY

@property
def is_weekday_specific(self) -> bool:
    return self.recurrence in {
        RecurrenceType.MONDAY,
        RecurrenceType.TUESDAY,
        RecurrenceType.WEDNESDAY,
        RecurrenceType.THURSDAY,
        RecurrenceType.FRIDAY,
        RecurrenceType.SATURDAY,
        RecurrenceType.SUNDAY
    }
```

### Methods
```python
def should_generate(self, target_date: date) -> bool:
    """Verifica se deve gerar instância para data."""
    if self.recurrence == RecurrenceType.DAILY:
        return True
    
    weekday = target_date.weekday()
    recurrence_map = {
        RecurrenceType.MONDAY: 0,
        RecurrenceType.TUESDAY: 1,
        RecurrenceType.WEDNESDAY: 2,
        RecurrenceType.THURSDAY: 3,
        RecurrenceType.FRIDAY: 4,
        RecurrenceType.SATURDAY: 5,
        RecurrenceType.SUNDAY: 6
    }
    
    return recurrence_map.get(self.recurrence) == weekday
```

---

## Routine

Agrupamento de hábitos relacionados.

### Schema
```python
class Routine(SQLModel, table=True):
    __tablename__ = "routine"
    
    id: int | None = Field(default=None, primary_key=True)
    
    # Dados básicos
    name: str = Field(min_length=1, max_length=100, unique=True)
    description: str | None = None
    
    # Controle
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    habits: list["Habit"] = Relationship(
        back_populates="routine",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### Properties
```python
@property
def habit_count(self) -> int:
    return len(self.habits)

@property
def active_habit_count(self) -> int:
    """Conta hábitos de rotina ativa."""
    return len(self.habits) if self.is_active else 0
```

---

## Exemplos de Uso

### Criar Rotina com Hábitos
```python
# Rotina
routine = Routine(
    name="Rotina Matinal",
    description="Hábitos da manhã"
)
session.add(routine)
session.flush()  # Para obter ID

# Hábitos
meditation = Habit(
    routine_id=routine.id,
    title="Meditação",
    scheduled_start=time(6, 0),
    scheduled_end=time(6, 20),
    recurrence=RecurrenceType.DAILY
)

exercise = Habit(
    routine_id=routine.id,
    title="Exercício",
    scheduled_start=time(7, 0),
    scheduled_end=time(8, 0),
    recurrence=RecurrenceType.MONDAY  # Apenas segundas
)

session.add_all([meditation, exercise])
session.commit()
```

### Query Hábitos Ativos
```python
active_habits = session.exec(
    select(Habit)
    .join(Routine)
    .where(Routine.is_active == True)
    .order_by(Habit.scheduled_start)
).all()
```

### Desativar Rotina
```python
routine = session.get(Routine, routine_id)
routine.is_active = False

# Cancelar instâncias futuras
for habit in routine.habits:
    future_instances = session.exec(
        select(HabitInstance)
        .where(HabitInstance.habit_id == habit.id)
        .where(HabitInstance.date >= date.today())
        .where(HabitInstance.status == HabitInstanceStatus.PLANNED)
    ).all()
    
    for instance in future_instances:
        instance.status = HabitInstanceStatus.CANCELLED

session.commit()
```

### Verificar Geração
```python
habit = session.get(Habit, habit_id)

# Segunda-feira
if habit.should_generate(date(2025, 11, 3)):
    print("Gera instância para 03/11/2025 (segunda)")

# Terça-feira
if not habit.should_generate(date(2025, 11, 4)):
    print("NÃO gera para 04/11/2025 (terça)")
```

---

## Validações

### Habit
```python
@validator("scheduled_end")
def end_after_start(cls, v, values):
    if "scheduled_start" in values and v <= values["scheduled_start"]:
        raise ValueError("scheduled_end must be after scheduled_start")
    return v

@validator("title")
def title_not_empty(cls, v):
    if not v.strip():
        raise ValueError("title cannot be empty")
    return v.strip()
```

### Routine
```python
@validator("name")
def name_not_empty(cls, v):
    if not v.strip():
        raise ValueError("name cannot be empty")
    return v.strip()
```

---

## Cascade Deletes
```python
# Deletar rotina remove hábitos e instâncias
routine = session.get(Routine, routine_id)
session.delete(routine)
session.commit()
# SQL: DELETE FROM habit WHERE routine_id = X
# SQL: DELETE FROM habit_instance WHERE habit_id IN (...)

# Deletar hábito remove instâncias
habit = session.get(Habit, habit_id)
session.delete(habit)
session.commit()
# SQL: DELETE FROM habit_instance WHERE habit_id = X
```

---

## Referências

**Services:**
- [HabitService](../services/habit-service.md)
- [RoutineService](../services/habit-service.md)

**Business Rules:**
- [BR001: Habit Scheduling](../../04-specifications/business-rules/BR001-habit-scheduling.md)

**Diagramas:**
- [ER Diagram](../../02-diagrams/data/er-diagram.md)

---

**Localização:** `docs/05-api/models/habit-models.md`
