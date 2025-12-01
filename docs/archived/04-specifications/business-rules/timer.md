# Business Rules: Timer

- **Domínio:** Timer
- **Área:** Tracking de Tempo e Múltiplas Sessões
- **Última atualização:** 23 de Novembro de 2025

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

### Escopo

Timer aplica **APENAS em HabitInstance**. Tasks e Events não possuem funcionalidade de timer.

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
# 105.56% está entre 90-110%
substatus = DoneSubstatus.FULL
```

---

## BR-TIMER-006: Pause Tracking

- **Status:** Definida (MVP Simplificado)
- **Prioridade:** Alta
- **Decisão relacionada:** [ADR-021: Pause Tracking Simplification](../../03-decisions/ADR-021-pause-tracking-simplification.md)

### Descrição

Sistema rastreia pausas durante timer usando campo acumulado `paused_duration` (abordagem MVP). Histórico detalhado de pausas será implementado em v2.0 com tabela `PauseLog`.

### Modelo TimeLog (MVP)

```python
class TimeLog(SQLModel, table=True):
    """Registro de sessão de trabalho."""
    id: int | None = Field(default=None, primary_key=True)
    habit_instance_id: int = Field(foreign_key="habitinstance.id")

    # Timestamps
    start_time: datetime
    end_time: datetime | None = None

    # Durations
    duration_seconds: int | None = None
    paused_duration: int | None = Field(default=0)  # Total pausado (segundos)
```

### Lógica de Tracking (MVP)

**Estado interno (em memória):**

```python
# TimerService mantém estado durante sessão ativa
_active_pause_start: datetime | None = None
```

**pause_timer:**

```python
def pause_timer(timelog_id: int) -> TimeLog:
    """Marca início de pausa (não persiste ainda)."""
    timelog = get_timelog(timelog_id)

    # Validações
    if timelog.end_time is not None:
        raise ValueError("Timer already stopped")
    if _active_pause_start is not None:
        raise ValueError("Timer already paused")

    # Marca início (em memória)
    _active_pause_start = datetime.now()
    return timelog
```

**resume_timer:**

```python
def resume_timer(timelog_id: int) -> TimeLog:
    """Calcula duração da pausa e acumula em paused_duration."""
    timelog = get_timelog(timelog_id)

    # Validações
    if _active_pause_start is None:
        raise ValueError("Timer not paused")

    # Calcula e acumula
    pause_duration = (datetime.now() - _active_pause_start).total_seconds()
    timelog.paused_duration = (timelog.paused_duration or 0) + int(pause_duration)

    # Limpa estado
    _active_pause_start = None

    session.add(timelog)
    session.commit()
    return timelog
```

### Cálculo de Duração Efetiva

```python
def stop_timer(timelog_id: int) -> TimeLog:
    """Finaliza timer calculando tempo efetivo."""
    timelog = get_timelog(timelog_id)

    # Se estava pausado, acumula última pausa
    if _active_pause_start is not None:
        pause_duration = (datetime.now() - _active_pause_start).total_seconds()
        timelog.paused_duration = (timelog.paused_duration or 0) + int(pause_duration)

    # Calcula tempo total e efetivo
    total_duration = (datetime.now() - timelog.start_time).total_seconds()
    paused = timelog.paused_duration or 0
    effective_duration = total_duration - paused

    timelog.end_time = datetime.now()
    timelog.duration_seconds = int(effective_duration)

    session.add(timelog)
    session.commit()
    return timelog
```

### Exemplos

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

### Validações

1. **Pause apenas timer ativo:** Timer já stopped = erro
2. **Sem pause duplo:** Já pausado = erro
3. **Resume apenas pausado:** Não pausado = erro
4. **Stop acumula pausa ativa:** Se pausado, acumula antes de finalizar

### Migração v2.0

Em v2.0, adicionar `PauseLog` table sem remover `paused_duration`:

- `paused_duration`: total acumulado (compatibilidade)
- `PauseLog`: histórico detalhado (analytics)

### Testes

- `test_pause_timer_success`: Marca início de pausa
- `test_resume_timer_success`: Acumula duração
- `test_multiple_pauses`: Soma múltiplas pausas
- `test_stop_while_paused`: Acumula pausa ativa
- `test_pause_already_paused`: Erro esperado
- `test_resume_not_paused`: Erro esperado

---

## Referências

- **Decisão:** [timer-workflows.md](../../11-planning/decisions/timer-workflows.md)
- **Decisão:** [ADR-021: Pause Tracking Simplification](../../03-decisions/ADR-021-pause-tracking-simplification.md)
- **Modelo:** `cli/src/timeblock/models/time_log.py`
- **Service:** `cli/src/timeblock/services/timer_service.py`
- **CLI:** `cli/src/timeblock/commands/timer.py`

---

**Última revisão:** 23 de Novembro de 2025

**Status:** Documentação completa, ready para implementação MVP
