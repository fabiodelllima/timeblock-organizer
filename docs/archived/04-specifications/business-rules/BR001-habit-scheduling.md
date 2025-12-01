# BR001: Habit Scheduling Rules

## Regra

Habits geram HabitInstances baseado em RRULE, respeitando constraints temporais.

## Comportamento

### Geração de Instâncias

```python
def generate_instances(
    habit: Habit,
    start_date: date,
    end_date: date
) -> List[HabitInstance]:
    """
    Gera instâncias no período baseado em recurrence_rule.
    """
    rrule = parse_rrule(habit.recurrence_rule)
    occurrences = rrule.between(start_date, end_date)

    return [
        HabitInstance(
            habit_id=habit.id,
            scheduled_date=dt,
            status=HabitStatus.PLANNED,
            duration=habit.default_duration
        )
        for dt in occurrences
    ]
```

### Constraints

**MUST:**

- Respeitar RRULE válido (RFC 5545)
- Não gerar instâncias no passado (> hoje)
- Verificar conflitos antes de persistir

**SHOULD:**

- Gerar no máximo 90 dias futuros
- Avisar se RRULE não gera ocorrências

**MUST NOT:**

- Duplicar instâncias (unique constraint: habit_id + scheduled_date)
- Gerar sem duration válido

## Exemplos

### Diário

```python
habit = Habit(
    name="Meditar",
    recurrence_rule="FREQ=DAILY",
    default_duration=15
)
# Gera 1 instância por dia
```

### Semanal Específico

```python
habit = Habit(
    name="Academia",
    recurrence_rule="FREQ=WEEKLY;BYDAY=MO,WE,FR",
    default_duration=60
)
# Gera 3 instâncias por semana (seg/qua/sex)
```

### Com Exceções

```python
habit = Habit(
    name="Reunião Semanal",
    recurrence_rule="FREQ=WEEKLY;BYDAY=TU;EXDATE=20250101"
)
# Pula 01/01/2025
```

## Estados

```terminal
PLANNED → IN_PROGRESS → COMPLETED
           ↓
        SKIPPED
           ↓
        OVERDUE (se past due)
```

## Validações

```python
def validate_habit_scheduling(habit: Habit) -> None:
    if not is_valid_rrule(habit.recurrence_rule):
        raise ValueError("RRULE inválido")

    if habit.default_duration <= 0:
        raise ValueError("Duração deve ser > 0")

    if habit.priority not in range(1, 6):
        raise ValueError("Prioridade deve ser 1-5")
```

## Edge Cases

**Horário de Verão:**

```python
# Usar timezone-aware datetimes
scheduled_date = datetime.now(tz=local_tz)
```

**Conflito na Geração:**

```python
# Marcar para reordering automático
if has_conflict(new_instance, existing_events):
    new_instance.needs_reordering = True
```

**RRULE sem occurrências:**

```python
if not occurrences:
    logger.warning(f"Habit {habit.id} não gera ocorrências no período")
```

## Performance

- Gerar 90 dias de instâncias: < 50ms
- Validar RRULE: < 5ms
- Batch insert: usar bulk_save_objects()

## Testes

```python
def test_daily_generation():
    habit = create_habit(recurrence="FREQ=DAILY")
    instances = generate_instances(habit, date.today(), date.today() + timedelta(7))
    assert len(instances) == 7

def test_no_duplicates():
    habit = create_habit()
    generate_instances(habit, today, today + timedelta(7))
    generate_instances(habit, today, today + timedelta(7))  # Rerun
    assert count_instances(habit) == 7  # Não duplica
```
