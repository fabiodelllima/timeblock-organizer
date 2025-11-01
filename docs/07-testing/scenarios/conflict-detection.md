# Cenário de Teste: Detecção de Conflitos

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025

---

## Cenário 1: Conflito Parcial
```python
def test_partial_overlap(session, instance_factory):
    """Sobreposição de 30min detectada."""
    # Existente: 14h-15h
    instance_factory(
        date_=date(2025, 11, 1),
        start=time(14, 0),
        end=time(15, 0)
    )
    
    # Nova: 14h30-15h30
    task, proposal = TaskService.create_task(
        title="Meeting",
        date=date(2025, 11, 1),
        start=time(14, 30),
        end=time(15, 30)
    )
    
    assert proposal.has_conflicts
    change = proposal.changes[0]
    assert change.delay_minutes == 30
```

## Cenário 2: Conflito Total
```python
def test_complete_overlap(session, instance_factory):
    """Evento dentro de outro detectado."""
    # Existente: 14h-16h
    instance_factory(
        date_=date(2025, 11, 1),
        start=time(14, 0),
        end=time(16, 0)
    )
    
    # Nova: 14h30-15h (dentro)
    task, proposal = TaskService.create_task(
        title="Quick call",
        date=date(2025, 11, 1),
        start=time(14, 30),
        end=time(15, 0)
    )
    
    assert proposal.has_conflicts
```

## Cenário 3: Múltiplos Conflitos
```python
def test_multiple_conflicts(session, instance_factory):
    """Cascata de conflitos detectada."""
    # 14h-15h
    instance_factory(date_=date(2025, 11, 1), start=time(14, 0), end=time(15, 0))
    # 15h-16h
    instance_factory(date_=date(2025, 11, 1), start=time(15, 0), end=time(16, 0))
    # 16h-17h
    instance_factory(date_=date(2025, 11, 1), start=time(16, 0), end=time(17, 0))
    
    # Nova: 14h30-15h30 (atrasa tudo)
    task, proposal = TaskService.create_task(
        title="Emergency",
        date=date(2025, 11, 1),
        start=time(14, 30),
        end=time(15, 30)
    )
    
    assert len(proposal.changes) == 3  # Todos shiftam
```

## Cenário 4: Sem Conflito (Adjacente)
```python
def test_adjacent_no_conflict(session, instance_factory):
    """Eventos adjacentes não conflitam."""
    # 14h-15h
    instance_factory(date_=date(2025, 11, 1), start=time(14, 0), end=time(15, 0))
    
    # 15h-16h (imediatamente após)
    task, proposal = TaskService.create_task(
        title="Next meeting",
        date=date(2025, 11, 1),
        start=time(15, 0),
        end=time(16, 0)
    )
    
    assert proposal is None  # Sem conflito
```

## Cenário 5: Tolerância de 1 Minuto
```python
def test_one_minute_tolerance(session, instance_factory):
    """Sobreposição < 1min ignorada."""
    # 14h-15h
    instance_factory(date_=date(2025, 11, 1), start=time(14, 0), end=time(15, 0))
    
    # 14h59m30s-16h (30s de overlap)
    task, proposal = TaskService.create_task(
        title="Close call",
        date=date(2025, 11, 1),
        start=time(14, 59),  # Arredondado para minuto
        end=time(16, 0)
    )
    
    assert proposal is None  # Tolerância
```

---

**Localização:** `docs/07-testing/scenarios/conflict-detection.md`
