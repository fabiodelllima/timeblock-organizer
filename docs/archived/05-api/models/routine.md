# Routine Model

```python
class Routine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    habits: List[Habit] = Relationship()
    order: List[int]  # IDs dos habits em ordem
```

## Exemplo

```python
morning = Routine(
    name="Rotina Matinal",
    habits=[wake_up, meditate, exercise, breakfast],
    order=[1, 2, 3, 4]
)
```
