# ADR-021: Simplificação de Pause Tracking para MVP

- **Status:** Aceita
- **Data:** 2025-11-23
- **Contexto:** Sprint 3.4 Fase 3 - Correção de débito técnico

## Contexto

O sistema de timer precisa rastrear pausas durante sessões de trabalho. Duas abordagens foram consideradas para implementação.

### Escopo de Timer

Timer aplica **APENAS em HabitInstance**:

| Entidade      | Timer | Rastreamento                   | Justificativa                                       |
| ------------- | ----- | ------------------------------ | --------------------------------------------------- |
| HabitInstance | ✓ SIM | start/stop/pause/resume/cancel | Hábitos são rotineiros, precisam tracking detalhado |
| Task          | ✗ NÃO | Checkbox (done/pending)        | Tasks são pontuais, não precisam timer              |
| Event         | ✗ NÃO | Agendamento                    | Events são planejados, não executados com timer     |

**Implicação:** Testes com `task_id` ou `event_id` são obsoletos e devem ser removidos.

### Abordagens Consideradas

1. **PauseLog table:** Tabela separada com histórico detalhado de cada pausa
2. **paused_duration field:** Campo simples com total acumulado

## Decisão

- **MVP (v1.x):** Implementar `paused_duration: int` (campo simples)
- **v2.0+:** Migrar para `PauseLog` table (analytics avançado)

### Justificativa MVP

**Simplicidade:**

- Um campo, uma query
- Sem relacionamento 1:N
- Performance melhor

**Suficiente para 90% dos casos:**

- Usuário precisa: "tempo efetivo = tempo total - pausas"
- Não precisa: "pausei às 10h, 12h, 14h"

### Justificativa v2.0

**Analytics avançado:**

- Histórico detalhado: quando pausou
- Padrões temporais: quantas pausas, duração média
- Auditoria: motivo da pausa (opcional)

## Implementação MVP

### Modelo TimeLog

```python
class TimeLog(SQLModel, table=True):
    """Registro de sessão de trabalho."""
    habit_instance_id: int = Field(foreign_key="habitinstance.id")
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: int | None = None
    paused_duration: int | None = Field(default=0)  # Total pausado (segundos)
```

### Service API

```python
def pause_timer(timelog_id: int) -> TimeLog:
    """Marca timestamp de pausa (não persiste ainda)."""

def resume_timer(timelog_id: int) -> TimeLog:
    """Calcula duração da pausa e acumula em paused_duration."""

def stop_timer(timelog_id: int) -> TimeLog:
    """Finaliza: duration_seconds = tempo_total - paused_duration."""
```

### Lógica de Tracking

```python
# Estado interno (em memória durante sessão ativa)
_active_pause_start: datetime | None = None

def pause_timer(timelog_id: int):
    """Marca início de pausa."""
    _active_pause_start = datetime.now()

def resume_timer(timelog_id: int):
    """Calcula duração e acumula."""
    pause_duration = (datetime.now() - _active_pause_start).total_seconds()
    timelog.paused_duration += int(pause_duration)
    _active_pause_start = None
    session.commit()

def stop_timer(timelog_id: int):
    """Finaliza timer."""
    # Se estava pausado, acumula última pausa
    if _active_pause_start is not None:
        pause_duration = (datetime.now() - _active_pause_start).total_seconds()
        timelog.paused_duration += int(pause_duration)

    # Calcula tempo efetivo
    total_duration = (datetime.now() - timelog.start_time).total_seconds()
    effective_duration = total_duration - (timelog.paused_duration or 0)

    timelog.end_time = datetime.now()
    timelog.duration_seconds = int(effective_duration)
    session.commit()
```

### Exemplos de Uso

#### **Cenário 1: Pausa única**

```terminal
10:00 - start_timer()
10:30 - pause_timer()  # _active_pause_start = 10:30
10:45 - resume_timer() # paused_duration = 15min
11:00 - stop_timer()   # duration = 60min - 15min = 45min
```

#### **Cenário 2: Múltiplas pausas**

```terminal
10:00 - start_timer()
10:20 - pause_timer()  # _active_pause_start = 10:20
10:30 - resume_timer() # paused_duration = 10min
10:50 - pause_timer()  # _active_pause_start = 10:50
11:00 - resume_timer() # paused_duration = 20min (10 + 10)
11:30 - stop_timer()   # duration = 90min - 20min = 70min
```

## Implementação v2.0 (Futuro)

### Modelo PauseLog

```python
class PauseLog(SQLModel, table=True):
    """Histórico detalhado de pausas."""
    id: int | None = Field(default=None, primary_key=True)
    timelog_id: int = Field(foreign_key="time_log.id")
    pause_start: datetime
    pause_end: datetime | None
    duration_seconds: int | None
    reason: str | None = Field(max_length=100)
```

### Migration Path

```python
# v2.0 migration: preservar paused_duration
# Criar PauseLog retroativo se necessário
# Manter ambos durante período de transição
```

## Consequências

**Positivas:**

- MVP mais rápido
- Código mais simples
- Performance melhor
- Escalabilidade: migração v2.0 não quebra dados

**Negativas:**

- Sem histórico detalhado no MVP
- Análise limitada de padrões

**Mitigação:**

- v2.0 adiciona PauseLog sem remover paused_duration
- Dados MVP permanecem válidos

## Referências

- [BR-TIMER-006: Pause Tracking](../core/business-rules.md#br-timer-006)
- [TimeLog Model](../../cli/src/timeblock/models/time_log.py)
- [TimerService](../../cli/src/timeblock/services/timer_service.py)
