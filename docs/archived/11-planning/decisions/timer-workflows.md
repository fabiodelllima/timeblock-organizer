# Decisão: Timer Workflows e Tracking de Tempo

- **Status:** Decidido
- **Data:** 14 de Novembro de 2025
- **Contexto:** Sistema de tracking de tempo para habits
- **Impacto:** Timer service, CLI, HabitInstance status

---

## Problema

Definir fluxos completos do timer para tracking de tempo de habits, incluindo:

1. Comandos disponíveis (start/pause/resume/stop/reset)
2. Diferença entre stop e reset
3. Múltiplas sessões do mesmo habit
4. Preenchimento manual (sem timer)
5. Estados intermediários (pausado, rodando)

---

## Decisão: Timer com 6 Comandos

### Comandos Disponíveis

```bash
timer start <instance_id>     # Inicia timer para habit instance
timer pause                   # Pausa timer atual
timer resume                  # Retoma timer pausado
timer stop                    # Fecha sessão e salva (DONE)
timer reset                   # Cancela timer atual sem salvar
timer status                  # Ver timer ativo
```

---

## Justificativa

### 1. **timer stop** ≠ Cancelar (é Completar)

```bash
timer start Academia
# ... 90 minutos depois ...
timer stop
# Sessão SALVA e FECHADA
# Status: DONE (substatus depende da % da meta)
```

**stop** = Fecha e salva a sessão como DONE.

### 2. **timer reset** = Cancelar Timer Errado

```bash
timer start Meditação
# Ops! Queria Academia!
timer reset
# Timer de Meditação CANCELADO (nada salvo)
# Instance continua PENDING

timer start Academia
# Agora sim, timer correto!
```

**reset** = Cancela timer sem salvar, permite restart correto.

### 3. **Múltiplas Sessões Permitidas**

```bash
# Sessão 1
timer start Academia
timer stop
# DONE: 60min (67% da meta de 90min) = PARTIAL

# User tem tempo livre, faz mais
timer start Academia  # MESMO habit, NOVA sessão
timer stop
# DONE: 40min adicional

# TOTAL DO DIA: 100min (111% da meta)
# Status final: DONE (OVERDONE)
```

**Permite:** User fazer múltiplas sessões do mesmo habit no dia.

### 4. **Preenchimento Manual** (habit log)

```bash
# User foi na academia sem celular
# Chega em casa e preenche manualmente

habit log Academia --start 07:00 --end 08:30

# Sistema calcula:
# Expected: 90min
# Actual: 90min
# Completion: 100%
# Status: DONE (FULL)
```

**habit log** = Alternativa ao timer para preenchimento retrospectivo.

---

## Estados do Timer

### Estado 1: IDLE (Sem Timer Ativo)

```bash
$ timer status
Nenhum timer ativo
```

**Comandos permitidos:**

- timer start <instance_id> ✓

**Comandos bloqueados:**

- timer pause ✗
- timer resume ✗
- timer stop ✗
- timer reset ✗

### Estado 2: RUNNING (Timer Rodando)

```bash
$ timer status
⏱  Timer ativo: Academia
   00:45:23 / 01:30:00 (50%)
   Iniciado: 07:15
```

**Comandos permitidos:**

- timer pause ✓
- timer stop ✓
- timer reset ✓
- timer status ✓

**Comandos bloqueados:**

- timer start <outro_id> ✗ (apenas 1 timer por vez)
- timer resume ✗ (já está rodando)

### Estado 3: PAUSED (Timer Pausado)

```bash
$ timer status
⏸  Timer pausado: Academia
   00:45:23 / 01:30:00 (50%)
   Pausado há: 5min
```

**Comandos permitidos:**

- timer resume ✓
- timer stop ✓
- timer reset ✓
- timer status ✓

**Comandos bloqueados:**

- timer start <outro_id> ✗
- timer pause ✗ (já está pausado)

---

## Fluxos Completos

### Fluxo 1: Timer Normal (Happy Path)

```bash
$ timer start Academia
⏱  Timer iniciado: Academia
   00:00 / 01:30 (meta: 90min)

# ... 90 minutos depois ...

$ timer stop
✓ Sessão completa!
  Tempo: 90min (100% da meta)
  Status: DONE (FULL)
  Streak: 13 dias consecutivos

# Instance status: DONE
# done_substatus: FULL
```

### Fluxo 2: Timer com Pausas

```bash
$ timer start Academia
⏱  00:15:00 / 01:30:00

$ timer pause
⏸  Timer pausado
   Tempo decorrido: 15min

# ... 10min depois (pausa para água) ...

$ timer resume
▶  Timer retomado

# ... continua ...

$ timer stop
✓ Completo!
  Tempo efetivo: 90min
  Pausas: 1x (10min)
  Tempo total: 100min
  Status: DONE (FULL)
```

### Fluxo 3: Timer Errado (Reset)

```bash
$ timer start Meditação
⏱  00:15:00 / 00:20:00

# Ops! Queria Academia!

$ timer reset
[!] Timer será cancelado sem salvar. Confirma? [y/N]: y
✓ Timer cancelado (Meditação)

# Meditação continua PENDING (nada salvo)

$ timer start Academia
⏱  Timer correto iniciado
   00:00 / 01:30:00
```

### Fluxo 4: Múltiplas Sessões (OVERDONE)

```bash
# Sessão 1 (manhã)
$ timer start Academia
⏱  00:00 / 01:30:00

$ timer stop
✓ Sessão 1: 60min (67%)
  Status: DONE (PARTIAL)

# Sessão 2 (tarde - tempo livre)
$ timer start Academia
⏱  Sessão 2 iniciada
   00:00 / 01:30:00

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

### Fluxo 5: Preenchimento Manual

```bash
# User esqueceu celular, fez academia sem timer
# Chega em casa e preenche

$ habit log Academia --start 07:00 --end 08:30
✓ Tempo registrado manualmente

  Academia (14/11/2025)
  Programado: 07:00 → 08:30 (90min)
  Real: 07:00 → 08:30 (90min)
  Completion: 100%
  Status: DONE (FULL)

# Alternativa: especificar duração direta
$ habit log Academia --duration 90
✓ Tempo registrado: 90min (100% da meta)
  Status: DONE (FULL)
```

### Fluxo 6: Timer EXCESSIVE (Desbalancea Rotina)

```bash
$ timer start Academia
⏱  00:00 / 01:30:00

# User perdeu noção do tempo...
# ... 3 horas depois ...

$ timer stop
✓ Sessão completa!
  Tempo: 180min (200% da meta)
  Status: DONE (EXCESSIVE)

[WARN] Academia ultrapassou meta em 90min

Impacto na rotina de hoje:
  - Trabalho focado: PERDIDO (conflito horário)
  - Inglês: ATRASADO 1h

Sugestão: Ajustar meta de Academia para 2h?
          [Y] Sim, ajustar permanentemente
          [N] Não, foi exceção hoje
```

---

## Cálculo de Completion %

### Fórmula

```python
completion_percentage = (actual_duration / expected_duration) * 100

# Determinar substatus
if completion_percentage > 150:
    done_substatus = DoneSubstatus.EXCESSIVE
elif completion_percentage > 110:
    done_substatus = DoneSubstatus.OVERDONE
elif completion_percentage >= 90:
    done_substatus = DoneSubstatus.FULL
else:
    done_substatus = DoneSubstatus.PARTIAL
```

### Exemplos

```python
# EXCESSIVE (> 150%)
actual: 180min, expected: 90min
completion: 200%
substatus: EXCESSIVE

# OVERDONE (110-150%)
actual: 100min, expected: 90min
completion: 111%
substatus: OVERDONE

# FULL (90-110%)
actual: 90min, expected: 90min
completion: 100%
substatus: FULL

# PARTIAL (< 90%)
actual: 60min, expected: 90min
completion: 67%
substatus: PARTIAL
```

---

## Persistência de Dados

### HabitInstance após timer stop

```python
class HabitInstance(SQLModel, table=True):
    # ... campos existentes

    # Status
    status: InstanceStatus = InstanceStatus.DONE
    done_substatus: DoneSubstatus = DoneSubstatus.FULL

    # Timing
    scheduled_start: time  # 07:00 (planejado)
    scheduled_end: time    # 08:30 (planejado)
    actual_start: time     # 07:15 (real)
    actual_end: time       # 08:35 (real)

    # Duração
    expected_duration: int  # 90min
    actual_duration: int    # 80min
    completion_percentage: float  # 88.89%

    # Pausas
    pause_count: int = 2
    pause_total_duration: int = 10  # min
```

### TimeLog (Pausas)

```python
class TimeLog(SQLModel, table=True):
    """Registro de pausa durante timer."""
    id: int | None = Field(default=None, primary_key=True)
    habit_instance_id: int = Field(foreign_key="habit_instances.id")

    # Timing
    pause_start: datetime
    pause_end: datetime | None
    duration: int | None  # Calculado ao resume

    # Opcional
    reason: str | None  # "Café", "Banheiro", etc
```

---

## CLI Outputs Detalhados

### timer status (Rodando)

```bash
$ timer status

⏱  TIMER ATIVO
╔════════════════════════════════════════╗
║ Academia                               ║
║ 00:45:23 / 01:30:00 (50%)              ║
╠════════════════════════════════════════╣
║ Iniciado: 07:15                        ║
║ Meta: 08:45                            ║
║ Tempo restante: 44min                  ║
╠════════════════════════════════════════╣
║ Comandos:                              ║
║   [P] pause | [S] stop | [R] reset     ║
╚════════════════════════════════════════╝
```

### timer status (Pausado)

```bash
$ timer status

⏸  TIMER PAUSADO
╔════════════════════════════════════════╗
║ Academia                               ║
║ 00:45:23 / 01:30:00 (50%)              ║
╠════════════════════════════════════════╣
║ Pausado há: 5min                       ║
║ Pausas nesta sessão: 2                 ║
╠════════════════════════════════════════╣
║ Comandos:                              ║
║   [R] resume | [S] stop | [X] reset    ║
╚════════════════════════════════════════╝
```

### timer stop (Com Análise)

```bash
$ timer stop

✓ SESSÃO COMPLETA!
╔════════════════════════════════════════╗
║ Academia (14/11/2025)                  ║
╠════════════════════════════════════════╣
║ Programado: 07:00 → 08:30 (90min)      ║
║ Real: 07:15 → 09:05 (110min)           ║
╠════════════════════════════════════════╣
║ Pausas: 2x (total 15min)               ║
║   1. 07:45-07:50 (5min) - Água         ║
║   2. 08:30-08:40 (10min) - Banheiro    ║
╠════════════════════════════════════════╣
║ Tempo efetivo: 95min                   ║
║ Completion: 106%                       ║
║ Status: DONE (OVERDONE)                ║
╠════════════════════════════════════════╣
║ Streak: 14 dias consecutivos ✓         ║
╚════════════════════════════════════════╝

[INFO] Acima da meta. Frequente? Considere ajustar para 2h.
```

---

## Validações e Restrições

### Apenas 1 Timer Ativo

```bash
$ timer start Academia
⏱  Timer iniciado: Academia

$ timer start Meditação
[ERROR] Timer já ativo: Academia (45min decorridos)

Opções:
  [1] Pausar Academia e iniciar Meditação
  [2] Cancelar Academia e iniciar Meditação
  [3] Continuar com Academia

Escolha [1-3]: _
```

### Timer Apenas Para PENDING

```bash
$ timer start Academia
[ERROR] Academia já está completa (DONE)

Para refazer:
  1. Faça: habit reset Academia
  2. Depois: timer start Academia
```

### habit log Validações

```bash
$ habit log Academia --start 07:00 --end 06:00
[ERROR] Horário de fim (06:00) antes do início (07:00)

$ habit log Academia --duration -10
[ERROR] Duração deve ser positiva

$ habit log Academia --start 07:00 --end 08:30
[WARN] Habit já tem timer registrado (90min)
       Sobrescrever? [y/N]: _
```

---

## Implementação MVP

### Fase 1 (Imediato)

- [x] timer start/pause/resume/stop/reset/status
- [x] Estado: IDLE/RUNNING/PAUSED
- [x] Apenas 1 timer ativo
- [x] Cálculo de completion %
- [x] Múltiplas sessões permitidas

### Fase 2 (Pós-MVP)

- [ ] habit log (preenchimento manual)
- [ ] TimeLog (rastreamento de pausas)
- [ ] Análise de impacto (EXCESSIVE)
- [ ] Sugestão de ajuste de meta
- [ ] Timer em background com notificação

---

## Business Rules Relacionadas

**A criar:**

- BR-TIMER-001: Single Active Timer Constraint
- BR-TIMER-002: State Transitions (IDLE/RUNNING/PAUSED)
- BR-TIMER-003: Multiple Sessions Same Day
- BR-TIMER-004: Manual Log Validation
- BR-TIMER-005: Completion Percentage Calculation
- BR-TIMER-006: Pause Tracking

---

## Referências

- Service: `src/timeblock/services/timer_service.py`
- Model: `src/timeblock/models/time_log.py`
- CLI: `src/timeblock/commands/timer.py`
- Decisão relacionada: `habit-states-final.md`

---

**Próxima Revisão:** Após implementação MVP

**Status:** DECIDIDO
