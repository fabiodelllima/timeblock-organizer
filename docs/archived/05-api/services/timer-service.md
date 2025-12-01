# TimerService

## API

```python
class TimerService:
    def __init__(self, session: Session):
        self.session = session

    def start_timer(self, event_id: int) -> Timer:
        """Inicia timer para evento."""

    def pause_timer(self, timer_id: int) -> Timer:
        """Pausa timer ativo."""

    def resume_timer(self, timer_id: int) -> Timer:
        """Retoma timer pausado."""

    def stop_timer(self, timer_id: int) -> TimeLog:
        """Finaliza e registra tempo."""

    def get_active_timer(self) -> Optional[Timer]:
        """Timer ativo no momento."""

    def get_time_logs(self, event_id: int) -> List[TimeLog]:
        """Histórico de execuções."""
```

## Exemplo

```python
service = TimerService(session)

# Iniciar
timer = service.start_timer(event.id)

# Pausar/Retomar
service.pause_timer(timer.id)
service.resume_timer(timer.id)

# Finalizar
log = service.stop_timer(timer.id)
print(f"Duração: {log.duration} min")

# Histórico
logs = service.get_time_logs(event.id)
```

## Validações

- Máximo 1 timer ativo
- Transições válidas de estado
- Event_id deve existir
