# Habit Model

```python
class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    default_duration: int  # minutos
    recurrence_rule: str  # RRULE (RFC 5545)
    priority: int = Field(default=3, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    instances: List["HabitInstance"] = Relationship(back_populates="habit")
```

## Campos

- **name**: Título do hábito
- **default_duration**: Duração padrão em minutos
- **recurrence_rule**: RRULE para geração de instâncias
- **priority**: 1 (baixa) a 5 (alta)

## Validações

- name não vazio
- duration > 0
- recurrence_rule válido
- priority 1-5
