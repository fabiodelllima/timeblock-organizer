# Conflict Detection - Especificação

## Objetivo

Identificar sobreposições temporais entre eventos de forma eficiente.

## Entrada/Saída

```python
def detect_conflicts(events: List[Event]) -> List[Conflict]:
    """Retorna pares de eventos que se sobrepõem."""
```

## Algoritmo Base (O(n²))

```python
def detect_conflicts(events: List[Event]) -> List[Conflict]:
    conflicts = []
    n = len(events)

    for i in range(n):
        for j in range(i + 1, n):
            if events_overlap(events[i], events[j]):
                conflicts.append(Conflict(
                    event1=events[i],
                    event2=events[j],
                    overlap_start=max(events[i].start, events[j].start),
                    overlap_end=min(events[i].end, events[j].end)
                ))

    return conflicts

def events_overlap(e1: Event, e2: Event) -> bool:
    """Verifica se dois eventos se sobrepõem."""
    return (e1.start < e2.end) and (e2.start < e1.end)
```

## Otimização: Sweep Line (O(n log n))

Para grandes volumes (>100 eventos):

```python
def detect_conflicts_optimized(events: List[Event]) -> List[Conflict]:
    """Sweep line algorithm para detecção eficiente."""

    # Criar pontos de início e fim
    points = []
    for event in events:
        points.append((event.start, 'start', event))
        points.append((event.end, 'end', event))

    # Ordenar por tempo
    points.sort(key=lambda p: (p[0], p[1] == 'end'))

    active = set()
    conflicts = []

    for time, event_type, event in points:
        if event_type == 'start':
            # Checar conflitos com eventos ativos
            for active_event in active:
                conflicts.append(Conflict(event, active_event))
            active.add(event)
        else:
            active.remove(event)

    return conflicts
```

## Tipos de Conflito

### Hard Conflict

Sobreposição impossível de resolver sem mover evento.

```python
if e1.priority == 5 and e2.priority == 5:
    conflict.type = ConflictType.HARD
```

### Soft Conflict

Pelo menos um evento pode ser movido.

```python
if e1.priority < 5 or e2.priority < 5:
    conflict.type = ConflictType.SOFT
```

### Partial Overlap

```python
overlap_duration = min(e1.end, e2.end) - max(e1.start, e2.start)
if overlap_duration < min(e1.duration, e2.duration):
    conflict.type = ConflictType.PARTIAL
```

## Casos Especiais

### Eventos Adjacentes (Sem Conflito)

```python
# 09:00-10:00 e 10:00-11:00 = SEM conflito
assert not events_overlap(
    Event(start="09:00", end="10:00"),
    Event(start="10:00", end="11:00")
)
```

### Buffer Time

```python
def events_overlap_with_buffer(
    e1: Event,
    e2: Event,
    buffer_minutes: int = 5
) -> bool:
    """Considera buffer entre eventos."""
    buffer = timedelta(minutes=buffer_minutes)
    return (e1.start < e2.end + buffer) and (e2.start < e1.end + buffer)
```

## Métricas

```python
@dataclass
class ConflictStats:
    total_conflicts: int
    hard_conflicts: int
    soft_conflicts: int
    total_overlap_minutes: int

    @property
    def avg_overlap(self) -> float:
        return self.total_overlap_minutes / self.total_conflicts
```

## Performance

| Eventos | Algoritmo Base | Sweep Line |
| ------- | -------------- | ---------- |
| 10      | 0.1ms          | 0.2ms      |
| 50      | 2ms            | 1ms        |
| 100     | 10ms           | 2ms        |
| 500     | 250ms          | 12ms       |

**Threshold:** Usar sweep line se `n > 50`.

## Testes

```python
def test_basic_overlap():
    e1 = Event(start="09:00", end="10:00")
    e2 = Event(start="09:30", end="10:30")
    assert events_overlap(e1, e2)

def test_no_overlap():
    e1 = Event(start="09:00", end="10:00")
    e2 = Event(start="10:00", end="11:00")
    assert not events_overlap(e1, e2)

def test_contained():
    e1 = Event(start="09:00", end="12:00")
    e2 = Event(start="10:00", end="11:00")
    assert events_overlap(e1, e2)
```
