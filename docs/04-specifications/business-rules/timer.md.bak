# Business Rules: Timer

- **Domínio:** Timer
- **Área:** Tracking de Tempo e Múltiplas Sessões
- **Última atualização:** 14 de Novembro de 2025

---

## Índice

- [BR-TIMER-001: Single Active Timer Constraint](#br-timer-001)
- [BR-TIMER-002: State Transitions](#br-timer-002)
- [BR-TIMER-003: Multiple Sessions Same Day](#br-timer-003)
- [BR-TIMER-004: Manual Log Validation](#br-timer-004)
- [BR-TIMER-005: Completion Percentage Calculation](#br-timer-005)
- [BR-TIMER-006: Pause Tracking](#br-timer-006)

---

## BR-TIMER-001: Single Active Timer Constraint

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)

### Descrição

Apenas UM timer pode estar ATIVO (RUNNING ou PAUSED) por vez. Timer STOPPED não bloqueia novo start.

### Diferença stop vs reset

**timer stop:**

- Fecha sessão atual e SALVA
- Marca instance como DONE
- Permite start novamente (nova sessão)

**timer reset:**

- Cancela timer atual SEM salvar
- Instance continua PENDING
- Usado quando iniciou habit errado

### Constraint

```python
# Constraint: max 1 timer ATIVO (RUNNING ou PAUSED)
active_timers = get_active_timers()  # status in [RUNNING, PAUSED]
assert len(active_timers) <= 1

# Timer STOPPED não conta como ativo!
stopped_timer = get_stopped_timer()
# Não bloqueia novo start
```

### Regra de Validação

```python
def start_timer(instance_id: int, session: Session) -> Timer:
    """Inicia timer, validando apenas 1 ativo."""

    # Verificar se existe timer ATIVO (RUNNING ou PAUSED)
    active = session.query(Timer)\
        .filter(Timer.status.in_([TimerStatus.RUNNING, TimerStatus.PAUSED]))\
        .first()

    if active is not None:
        raise TimerActiveError(
            f"Timer já ativo: {active.habit_instance.habit.title}\n"
            f"Opções:\n"
            f"  [1] Pausar timer atual\n"
            f"  [2] Cancelar timer atual (reset)\n"
            f"  [3] Continuar com timer atual"
        )

    # Timer STOPPED não bloqueia!
    # Pode iniciar novo timer (nova sessão)

    timer = Timer(
        habit_instance_id=instance_id,
        status=TimerStatus.RUNNING,
        started_at=datetime.now()
    )

    session.add(timer)
    session.commit()
    return timer
```

### Critérios de Aceitação

- [ ] Apenas 1 timer com status RUNNING ou PAUSED
- [ ] `timer start` falha se já existe timer ATIVO
- [ ] Timer após `stop` NÃO bloqueia novo start
- [ ] Múltiplas sessões permitidas (start → stop → start)
- [ ] CLI oferece opções (pausar/reset atual)

### Testes Relacionados

- `test_br_timer_001_only_one_active`
- `test_br_timer_001_error_if_already_running`
- `test_br_timer_001_stopped_not_blocking`
- `test_br_timer_001_multiple_sessions_allowed`

### Exemplos

#### Exemplo 1: Múltiplas Sessões (PERMITIDO)

```python
# Sessão 1
timer1 = start_timer(instance_id=42)  # Academia
timer1.stop()  # SALVA primeira sessão

# Sessão 2 (PERMITIDO - timer1 não está mais ativo)
timer2 = start_timer(instance_id=42)  # Mesma instance!
timer2.stop()  # SALVA segunda sessão

# Ambas sessões acumulam no total do dia
```

#### Exemplo 2: Tentar Start com Timer Ativo (BLOQUEADO)

```bash
$ timer start Academia
⏱  Timer iniciado: Academia (00:00 / 01:30)

$ timer start Meditação
[ERROR] Timer já ativo: Academia (15min decorridos)

Opções:
  [1] Pausar Academia e iniciar Meditação
  [2] Cancelar Academia (reset) e iniciar Meditação
  [3] Continuar com Academia

Escolha [1-3]: _
```

#### Exemplo 3: Reset (cancela sem salvar)

```python
# Iniciou habit errado
timer = start_timer(instance_id=42)  # Meditação (ERRADO)

# Ops! Cancelar sem salvar
timer.reset()
# Instance 42 continua PENDING (nada salvo)

# Iniciar correto
timer = start_timer(instance_id=50)  # Academia (CORRETO)
```

---

## BR-TIMER-002: State Transitions

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)

### Descrição

Timer possui apenas 2 estados ativos (RUNNING, PAUSED). Comandos stop e reset finalizam timer mas não mudam estado.

### Estados do Timer

```python
class TimerStatus(str, Enum):
    """Estados ativos do timer."""
    RUNNING = "running"    # Timer rodando
    PAUSED = "paused"      # Timer pausado
    # Não há STOPPED ou CANCELLED (timer é deletado/finalizado)
```

### Máquina de Estados

```terminal
[NO TIMER]
  │
  ├─> timer start
  │
  v
RUNNING
  ├─> timer pause → PAUSED
  │                    │
  │                    └─> timer resume → RUNNING
  │
  ├─> timer stop → [FINALIZA E SALVA] → [NO TIMER]
  │
  └─> timer reset → [CANCELA SEM SALVAR] → [NO TIMER]
```

### Comandos e Efeitos

| Comando | De             | Para     | Efeito             |
| ------- | -------------- | -------- | ------------------ |
| start   | NO TIMER       | RUNNING  | Cria timer         |
| pause   | RUNNING        | PAUSED   | Pausa contagem     |
| resume  | PAUSED         | RUNNING  | Retoma contagem    |
| stop    | RUNNING/PAUSED | NO TIMER | Salva e marca DONE |
| reset   | RUNNING/PAUSED | NO TIMER | Cancela sem salvar |

### Critérios de Aceitação

- [ ] Apenas 2 estados: RUNNING e PAUSED
- [ ] stop finaliza timer e salva sessão
- [ ] reset finaliza timer SEM salvar
- [ ] pause só de RUNNING
- [ ] resume só de PAUSED
- [ ] stop/reset de RUNNING ou PAUSED

### Testes Relacionados

- `test_br_timer_002_valid_transitions`
- `test_br_timer_002_stop_saves_session`
- `test_br_timer_002_reset_no_save`
- `test_br_timer_002_pause_from_running_only`

### Exemplos

#### Exemplo 1: Fluxo Normal (start → pause → resume → stop)

```python
# Iniciar
timer = start_timer(instance_id=42)
assert timer.status == TimerStatus.RUNNING

# Pausar
timer.pause()
assert timer.status == TimerStatus.PAUSED

# Retomar
timer.resume()
assert timer.status == TimerStatus.RUNNING

# Finalizar (salva)
timer.stop()
# Timer não existe mais (finalizado)
# Instance marcada como DONE
```

#### Exemplo 2: Reset (cancela sem salvar)

```python
# Iniciar timer errado
timer = start_timer(instance_id=42)  # Meditação
assert timer.status == TimerStatus.RUNNING

# Ops! Cancelar
timer.reset()
# Timer não existe mais (cancelado)
# Instance 42 continua PENDING (nada salvo)
```

---

## BR-TIMER-003: Multiple Sessions Same Day

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)

### Descrição

Usuário pode fazer múltiplas sessões do mesmo habit no mesmo dia via start → stop → start → stop. Duração acumulada determina substatus final.

### Lógica de Acumulação

```python
def accumulate_sessions(instance_id: int) -> dict:
    """Acumula tempo de múltiplas sessões."""

    sessions = get_completed_sessions(instance_id)

    total_duration = sum(s.duration for s in sessions)
    session_count = len(sessions)

    # Calcular completion baseado em total acumulado
    completion = (total_duration / instance.expected_duration) * 100

    # Determinar substatus
    if completion > 150:
        substatus = DoneSubstatus.EXCESSIVE
    elif completion > 110:
        substatus = DoneSubstatus.OVERDONE
    elif completion >= 90:
        substatus = DoneSubstatus.FULL
    else:
        substatus = DoneSubstatus.PARTIAL

    return {
        "sessions": session_count,
        "total_duration": total_duration,
        "completion": completion,
        "substatus": substatus
    }
```

### Workflow de Múltiplas Sessões

```python
# Sessão 1 (manhã)
timer1 = start_timer(instance_id=42)
# ... 60 minutos ...
timer1.stop()
# Sessão 1 salva: 60min

# Sessão 2 (tarde) - MESMO INSTANCE!
timer2 = start_timer(instance_id=42)  # ✓ PERMITIDO
# ... 35 minutos ...
timer2.stop()
# Sessão 2 salva: 35min

# Total acumulado: 95min
# Completion: 106% (OVERDONE)
```

### Critérios de Aceitação

- [ ] Permitir múltiplos start para mesma instance
- [ ] Cada stop salva uma sessão independente
- [ ] Acumular duração total de todas sessões
- [ ] Substatus baseado em total acumulado
- [ ] CLI mostra breakdown por sessão
- [ ] Instance marcada DONE após primeira sessão completa

### Testes Relacionados

- `test_br_timer_003_multiple_sessions_allowed`
- `test_br_timer_003_accumulate_duration`
- `test_br_timer_003_substatus_on_total`
- `test_br_timer_003_done_after_first_session`

### Exemplos

#### Exemplo 1: Duas Sessões (PARTIAL → OVERDONE)

```bash
# Sessão 1
$ timer start Academia
⏱  00:00 / 01:30

$ timer stop
✓ Sessão 1: 60min (67% da meta)
  Status: DONE (PARTIAL)

# Sessão 2 (mesmo habit!)
$ timer start Academia
⏱  Sessão 2: 00:00 / 01:30

$ timer stop
✓ Sessão 2: 35min

╔════════════════════════════════╗
║  TOTAL DO DIA: Academia        ║
╠════════════════════════════════╣
║  Sessões: 2                    ║
║  Tempo: 95min (106% da meta)   ║
║  Status: DONE (OVERDONE)       ║
╚════════════════════════════════╝
```

#### Exemplo 2: Três Sessões (EXCESSIVE)

```python
# Sessão 1: 60min
# Sessão 2: 40min
# Sessão 3: 70min
# Total: 170min (189% da meta de 90min)
# Status: DONE (EXCESSIVE)
```

---

## BR-TIMER-004: Manual Log Validation

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)

### Descrição

Comando `habit log` permite preenchimento manual retrospectivo com validações de horário e duração.

### Validações

```python
def validate_manual_log(
    instance_id: int,
    start: time | None,
    end: time | None,
    duration: int | None
) -> None:
    """Valida parâmetros de log manual."""

    # Validação 1: start < end
    if start and end and start >= end:
        raise ValueError("Horário de fim deve ser após horário de início")

    # Validação 2: duração positiva
    if duration is not None and duration <= 0:
        raise ValueError("Duração deve ser positiva")

    # Validação 3: apenas um método (start+end OU duration)
    if (start or end) and duration:
        raise ValueError("Use start+end OU duration, não ambos")

    # Validação 4: instance não pode ter timer ativo
    active_timer = get_active_timer_for_instance(instance_id)
    if active_timer:
        raise ValueError("Timer ativo para este habit. Stop timer primeiro.")

    # Validação 5: confirmar sobrescrever se já completo
    if instance.status == InstanceStatus.DONE:
        confirm = input("Habit já completo. Adicionar nova sessão? [y/N]: ")
        if confirm.lower() != 'y':
            raise ValueError("Operação cancelada")
```

### Critérios de Aceitação

- [ ] Aceita `--start` + `--end` OU `--duration`
- [ ] Valida start < end
- [ ] Valida duração > 0
- [ ] Bloqueia se timer ativo
- [ ] Permite adicionar nova sessão se já DONE
- [ ] Calcula completion % baseado em log

### Testes Relacionados

- `test_br_timer_004_start_end_validation`
- `test_br_timer_004_duration_positive`
- `test_br_timer_004_blocks_if_timer_active`
- `test_br_timer_004_allows_additional_session`

### Exemplos

#### Exemplo 1: Log Manual com Horários

```bash
$ habit log Academia --start 07:00 --end 08:30

✓ Tempo registrado manualmente

  Academia (14/11/2025)
  Programado: 07:00 → 08:30 (90min)
  Real: 07:00 → 08:30 (90min)
  Completion: 100%
  Status: DONE (FULL)
```

#### Exemplo 2: Adicionar Sessão Manual

```bash
# Habit já tem 1 sessão (timer)
$ habit log Academia --duration 30

Habit já completo (1 sessão: 60min).
Adicionar nova sessão? [y/N]: y

✓ Nova sessão adicionada: 30min

╔════════════════════════════════╗
║  TOTAL: Academia               ║
╠════════════════════════════════╣
║  Sessões: 2 (1 timer + 1 log)  ║
║  Tempo: 90min (100%)           ║
║  Status: DONE (FULL)           ║
╚════════════════════════════════╝
```

---

## BR-TIMER-005: Completion Percentage Calculation

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)

### Descrição

Completion percentage é calculado ao parar timer (ou log manual), baseado em duração acumulada de todas sessões.

### Fórmula

```python
# Total de TODAS as sessões (timer + log)
total_actual_duration = sum(session.duration for session in sessions)

# Completion %
completion_percentage = (total_actual_duration / expected_duration) * 100
```

### Lógica Completa

```python
def calculate_completion(instance: HabitInstance) -> dict:
    """Calcula completion % e determina substatus."""

    # 1. Buscar TODAS as sessões (timer + log manual)
    sessions = get_all_sessions(instance.id)

    # 2. Calcular duração total acumulada
    total_duration = sum(s.duration for s in sessions)

    # 3. Buscar duração esperada
    expected_duration = instance.expected_duration

    # 4. Calcular completion %
    completion = (total_duration / expected_duration) * 100

    # 5. Determinar substatus
    if completion > 150:
        substatus = DoneSubstatus.EXCESSIVE
        feedback = "[WARN] Ultrapassou meta"
    elif completion > 110:
        substatus = DoneSubstatus.OVERDONE
        feedback = "[INFO] Acima da meta"
    elif completion >= 90:
        substatus = DoneSubstatus.FULL
        feedback = "[OK] Perfeito!"
    else:
        substatus = DoneSubstatus.PARTIAL
        feedback = "Abaixo da meta"

    return {
        "total_duration": total_duration,
        "expected_duration": expected_duration,
        "completion_percentage": completion,
        "done_substatus": substatus,
        "session_count": len(sessions),
        "feedback": feedback
    }
```

### Critérios de Aceitação

- [ ] Fórmula: (total_actual / expected) \* 100
- [ ] Thresholds: 150%, 110%, 90%
- [ ] Substatus baseado em total acumulado
- [ ] Considera pausas (desconta do tempo)
- [ ] Arredondamento: 2 casas decimais

### Testes Relacionados

- `test_br_timer_005_completion_formula`
- `test_br_timer_005_multiple_sessions_accumulated`
- `test_br_timer_005_thresholds`
- `test_br_timer_005_with_pauses`

### Exemplos

#### Exemplo 1: Múltiplas Sessões Acumuladas

```python
# Sessão 1: 60min
# Sessão 2: 35min
# Total: 95min

expected = 90min
actual = 95min
completion = (95 / 90) * 100 = 105.56%
substatus = DoneSubstatus.OVERDONE  # Entre 110-150%... não, é < 110!
# Correção: 105.56% < 110%, então é FULL (90-110%)
substatus = DoneSubstatus.FULL
```

---

## BR-TIMER-006: Pause Tracking

- **Status:** Definida
- **Prioridade:** Baixa
- **Decisão relacionada:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)

### Descrição

Sistema rastreia pausas durante timer (modelo TimeLog) para cálculo preciso de duração efetiva.

### Modelo TimeLog

```python
class TimeLog(SQLModel, table=True):
    """Registro de pausa durante timer."""

    id: int | None = Field(default=None, primary_key=True)
    timer_id: int = Field(foreign_key="timers.id")

    # Timing
    pause_start: datetime
    pause_end: datetime | None  # NULL se ainda pausado
    duration: int | None  # Calculado ao resume (minutos)

    # Opcional
    reason: str | None = Field(max_length=100)
```

### Lógica de Tracking

```python
def pause_timer(timer_id: int) -> TimeLog:
    """Pausa timer e registra pausa."""

    timer = get_timer(timer_id)
    timer.status = TimerStatus.PAUSED

    # Criar log de pausa
    time_log = TimeLog(
        timer_id=timer_id,
        pause_start=datetime.now(),
        pause_end=None,
        duration=None
    )

    session.add(time_log)
    session.commit()
    return time_log

def resume_timer(timer_id: int) -> None:
    """Retoma timer e finaliza log de pausa."""

    timer = get_timer(timer_id)
    timer.status = TimerStatus.RUNNING

    # Finalizar último log
    time_log = get_last_pause(timer_id)
    time_log.pause_end = datetime.now()
    time_log.duration = calculate_minutes(
        time_log.pause_start,
        time_log.pause_end
    )

    session.commit()
```

### Cálculo de Duração Efetiva

```python
# Tempo total - pausas = tempo efetivo
elapsed_time = stop_time - start_time  # 100min
total_pauses = sum(p.duration for p in pauses)  # 15min
effective_duration = elapsed_time - total_pauses  # 85min
```

### Critérios de Aceitação

- [ ] TimeLog criado ao pausar
- [ ] TimeLog finalizado ao resumir
- [ ] Duração calculada automaticamente
- [ ] Pausas descontadas do tempo total
- [ ] CLI mostra pausas no output final

### Testes Relacionados

- `test_br_timer_006_create_log_on_pause`
- `test_br_timer_006_finalize_on_resume`
- `test_br_timer_006_effective_duration`

### Exemplos

#### Exemplo 1: CLI Output com Pausas

```bash
$ timer stop

✓ SESSÃO COMPLETA!
╔════════════════════════════════════════╗
║ Academia (14/11/2025)                  ║
╠════════════════════════════════════════╣
║ Programado: 07:00 → 08:30 (90min)      ║
║ Real: 07:00 → 08:45 (105min total)     ║
╠════════════════════════════════════════╣
║ Pausas: 2x (15min total)               ║
║   1. 07:30-07:40 (10min)               ║
║   2. 08:10-08:15 (5min)                ║
╠════════════════════════════════════════╣
║ Tempo efetivo: 90min                   ║
║ Completion: 100%                       ║
║ Status: DONE (FULL)                    ║
╚════════════════════════════════════════╝
```

---

## Referências

- **Decisão:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)
- **Modelo:** `src/timeblock/models/timer.py`
- **Modelo:** `src/timeblock/models/time_log.py`
- **Service:** `src/timeblock/services/timer_service.py`
- **CLI:** `src/timeblock/commands/timer.py`

---

**Última revisão:** 14 de Novembro de 2025

**Status:** Documentação completa, ready para implementação
