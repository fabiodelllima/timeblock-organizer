# HabitService

## API

```python
class HabitService:
    def __init__(self, session: Session):
        self.session = session

    def create_habit(self, name: str, recurrence: str, duration: int, priority: int = 3) -> Habit:
        """Cria habit com validação."""

    def generate_instances(self, habit: Habit, start: date, end: date) -> List[HabitInstance]:
        """Gera instâncias baseado em RRULE."""

    def get_instances_by_date(self, date: date) -> List[HabitInstance]:
        """Lista instâncias de uma data."""

    def mark_complete(self, instance_id: int, actual_duration: Optional[int] = None) -> HabitInstance:
        """Marca instância como completa."""

    def skip_instance(self, instance_id: int, reason: Optional[str] = None) -> HabitInstance:
        """Pula instância conscientemente."""

    def calculate_completion_rate(self, habit: Habit, period: timedelta) -> float:
        """Taxa de conclusão no período."""
```

## Exemplo

```python
service = HabitService(session)

# Criar
habit = service.create_habit("Meditar", "FREQ=DAILY", 15)

# Gerar instâncias
instances = service.generate_instances(habit, date.today(), date.today() + timedelta(30))

# Completar
service.mark_complete(instances[0].id, actual_duration=18)

# Taxa
rate = service.calculate_completion_rate(habit, timedelta(days=7))
```

## Validações

- RRULE válido (RFC 5545)
- Duration > 0
- Priority em 1-5
- Unique (habit_id, scheduled_date)
