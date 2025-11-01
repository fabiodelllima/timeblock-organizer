# Cenário de Teste: Criação de Eventos

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025

---

## Cenário 1: Criar Task Sem Conflitos
```python
def test_create_task_no_conflicts(session):
    """Task em horário livre é criada normalmente."""
    task, proposal = TaskService.create_task(
        title="Meeting",
        date=date(2025, 11, 1),
        start=time(14, 0),
        end=time(15, 0)
    )
    
    assert task.id is not None
    assert task.title == "Meeting"
    assert proposal is None  # Sem conflitos
```

## Cenário 2: Criar Task Com Conflito
```python
def test_create_task_with_conflict(session, instance_factory):
    """Task conflitante retorna proposta."""
    # Instância existente: 14h-15h
    instance_factory(
        date_=date(2025, 11, 1),
        start=time(14, 0),
        end=time(15, 0)
    )
    
    # Task nova: 14h30-15h30
    task, proposal = TaskService.create_task(
        title="Urgent Meeting",
        date=date(2025, 11, 1),
        start=time(14, 30),
        end=time(15, 30)
    )
    
    assert task.id is not None  # SEMPRE cria
    assert proposal is not None
    assert proposal.has_conflicts
    assert len(proposal.changes) == 1
```

## Cenário 3: Geração de Instâncias
```python
def test_generate_daily_instances(session, habit_factory, frozen_time):
    """DAILY gera para todo dia."""
    habit = habit_factory(recurrence=RecurrenceType.DAILY)
    
    count = HabitInstanceService.generate(date(2025, 11, 1))
    
    assert count == 1
    instance = session.exec(
        select(HabitInstance)
        .where(HabitInstance.habit_id == habit.id)
        .where(HabitInstance.date == date(2025, 11, 1))
    ).first()
    
    assert instance is not None
    assert instance.status == HabitInstanceStatus.PLANNED
```

## Cenário 4: Idempotência de Geração
```python
def test_generate_idempotent(session, habit_factory):
    """Gerar 2x não duplica."""
    habit = habit_factory(recurrence=RecurrenceType.DAILY)
    target = date(2025, 11, 1)
    
    count1 = HabitInstanceService.generate(target)
    count2 = HabitInstanceService.generate(target)
    
    assert count1 == 1
    assert count2 == 0
    
    instances = session.exec(
        select(HabitInstance)
        .where(HabitInstance.habit_id == habit.id)
        .where(HabitInstance.date == target)
    ).all()
    
    assert len(instances) == 1
```

---

**Localização:** `docs/07-testing/scenarios/event-creation.md`
