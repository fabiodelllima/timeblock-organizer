# BR004: Timer Behavior Rules

## Regra

Timer rastreia tempo real de execução de eventos, permitindo comparação com estimativas.

## Estados

```terminal
idle → running → completed
         ↓
       paused → running
```

## Transições

```python
class TimerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

def start_timer(event: Event) -> Timer:
    if timer_exists(event):
        raise TimerAlreadyRunningError()

    return Timer(
        event_id=event.id,
        state=TimerState.RUNNING,
        start_time=now(),
        elapsed=0
    )

def pause_timer(timer: Timer) -> None:
    if timer.state != TimerState.RUNNING:
        raise InvalidStateError()

    timer.elapsed += now() - timer.start_time
    timer.state = TimerState.PAUSED

def resume_timer(timer: Timer) -> None:
    if timer.state != TimerState.PAUSED:
        raise InvalidStateError()

    timer.start_time = now()
    timer.state = TimerState.RUNNING

def stop_timer(timer: Timer) -> TimeLog:
    if timer.state not in [TimerState.RUNNING, TimerState.PAUSED]:
        raise InvalidStateError()

    if timer.state == TimerState.RUNNING:
        timer.elapsed += now() - timer.start_time

    timer.state = TimerState.COMPLETED

    return TimeLog(
        event_id=timer.event_id,
        duration=timer.elapsed,
        timestamp=now()
    )
```

## Constraints

**MUST:**

- Máximo 1 timer ativo por vez
- Persistir estado a cada 30s (recovery)
- Validar transições de estado

**SHOULD:**

- Notificar ao atingir tempo estimado
- Sugerir ajuste de estimativa se divergência > 30%

**MUST NOT:**

- Perder tempo acumulado em crash
- Permitir timer negativo

## Cálculos

```python
def calculate_elapsed(timer: Timer) -> timedelta:
    if timer.state == TimerState.RUNNING:
        return timer.elapsed + (now() - timer.start_time)
    return timer.elapsed

def calculate_variance(actual: int, estimated: int) -> float:
    return ((actual - estimated) / estimated) * 100
```

## TimeLog

```python
@dataclass
class TimeLog:
    event_id: int
    start_time: datetime
    end_time: datetime
    duration: int  # minutos
    was_paused: bool
    pause_count: int
```

## Validações

```python
def validate_timer_operation(timer: Timer, operation: str) -> None:
    valid_transitions = {
        'start': [TimerState.IDLE],
        'pause': [TimerState.RUNNING],
        'resume': [TimerState.PAUSED],
        'stop': [TimerState.RUNNING, TimerState.PAUSED]
    }

    if timer.state not in valid_transitions[operation]:
        raise InvalidTransitionError()
```

## Métricas

- Acurácia estimativa: média |actual - estimated| / estimated
- Taxa uso timer: eventos com timer / total eventos
- Pausa média por sessão

## Testes

```python
def test_timer_lifecycle():
    timer = start_timer(event)
    assert timer.state == TimerState.RUNNING

    pause_timer(timer)
    assert timer.state == TimerState.PAUSED
    assert timer.elapsed > 0

    resume_timer(timer)
    assert timer.state == TimerState.RUNNING

    log = stop_timer(timer)
    assert timer.state == TimerState.COMPLETED
    assert log.duration == timer.elapsed

def test_only_one_active():
    timer1 = start_timer(event1)
    with pytest.raises(TimerAlreadyRunningError):
        start_timer(event2)
```
