# Decisão: Estados de HabitInstance (Status + Substatus)

- **Status:** Decidido
- **Data:** 14 de Novembro de 2025
- **Contexto:** Discussão sobre skip/justificativa e estados
- **Impacto:** HabitInstance model, CLI, reports

---

## Problema

Definir claramente os estados possíveis de um HabitInstance e suas transições, diferenciando:

1. Skip justificado vs não justificado
2. Completion em 4 níveis (EXCESSIVE, OVERDONE, FULL, PARTIAL)
3. Falha por inação (IGNORED) vs skip consciente
4. OVERDONE pode ser problema se desbalanceia rotina

---

## Decisão: Status + Substatus

### Estrutura Escolhida

```python
class InstanceStatus(str, Enum):
    """Status principal do HabitInstance."""
    PENDING = "pending"      # Agendado, não iniciado
    DONE = "done"            # Realizado (excessive, overdone, full ou partial)
    NOT_DONE = "not_done"    # Não realizado (skip ou ignored)

class DoneSubstatus(str, Enum):
    """Substatus quando DONE."""
    EXCESSIVE = "excessive"    # > 150% (PROBLEMA - desbalanceou rotina)
    OVERDONE = "overdone"      # 110-150% (ATENÇÃO - acima do ideal)
    FULL = "full"              # 90-110% (IDEAL - dentro da faixa)
    PARTIAL = "partial"        # < 90% (abaixo da meta)

class NotDoneSubstatus(str, Enum):
    """Substatus quando NOT_DONE."""
    SKIPPED_JUSTIFIED = "skipped_justified"       # Skip COM reason
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"   # Skip SEM reason
    IGNORED = "ignored"                            # Não realizado sem ação consciente
```

### Modelo Atualizado

```python
class HabitInstance(SQLModel, table=True):
    # ... campos existentes

    # Status principal
    status: InstanceStatus = Field(default=InstanceStatus.PENDING)

    # Substatus (opcional, depende do status)
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None

    # Campos auxiliares
    skip_reason: SkipReason | None = None  # Se NOT_DONE + SKIPPED_*
    skip_note: str | None = Field(None, max_length=200)
    actual_duration: int | None = None     # Minutos reais trackados
    expected_duration: int                  # Minutos da meta
    completion_percentage: float | None = None
```

---

## Justificativa

### Por que 4 Níveis de DONE?

#### **1. EXCESSIVE é PROBLEMA, não Celebração**

```terminal
Cenário Real:
07:00-08:30  Academia (90min esperado)
07:00-10:00  Academia REAL (180min = 200%)
             ↓
09:00-12:00  Trabalho focado (PERDIDO)
13:00-14:00  Inglês (ATRASADO ou SKIPPED)
```

**EXCESSIVE = Warning forte**: Um hábito "roubou tempo" de outros

#### **2. OVERDONE é Sinal de Alerta**

- 110-150%: Acima do planejado, mas não crítico
- Sistema monitora recorrência
- Sugere ajuste de meta se OVERDONE for frequente

#### **3. FULL é o Alvo Ideal**

- 90-110%: Faixa de tolerância saudável
- Não precisa ser exatamente 100%
- Permite flexibilidade natural

#### **4. PARTIAL não é Falha**

- < 90%: Abaixo da meta, mas ainda é DONE
- Mantém streak (importante!)
- Sistema monitora padrão (se recorrente → ajustar meta)

### Diferença IGNORED vs SKIPPED

- **SKIPPED:** Decisão consciente do usuário (comando `habit skip`)
- **IGNORED:** Inação - passou do prazo sem nenhuma ação

---

## Transições de Estado

### Diagrama de Estados

```terminal
PENDING
  ├─> DONE
  │    ├─> EXCESSIVE (timer stop > 150% meta) [WARN]
  │    ├─> OVERDONE (timer stop 110-150% meta) [INFO]
  │    ├─> FULL (timer stop 90-110% meta) [OK]
  │    └─> PARTIAL (timer stop < 90% meta)
  │
  └─> NOT_DONE
       ├─> SKIPPED_JUSTIFIED (habit skip + reason)
       ├─> SKIPPED_UNJUSTIFIED (habit skip, sem reason < 24h)
       └─> IGNORED (pending > 48h sem ação)
```

### Regras de Transição

**PENDING → DONE:**

```python
# Timer stop
completion = (actual_duration / expected_duration) * 100

if completion > 150:
    status = InstanceStatus.DONE
    done_substatus = DoneSubstatus.EXCESSIVE
    # Sistema checa impacto em outros hábitos do dia
elif completion > 110:
    status = InstanceStatus.DONE
    done_substatus = DoneSubstatus.OVERDONE
    # Sistema monitora recorrência
elif completion >= 90:
    status = InstanceStatus.DONE
    done_substatus = DoneSubstatus.FULL
else:  # completion < 90
    status = InstanceStatus.DONE
    done_substatus = DoneSubstatus.PARTIAL
```

**PENDING → NOT_DONE (skip):**

```python
# Comando: habit skip
if skip_reason is not None:
    status = InstanceStatus.NOT_DONE
    not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
else:
    status = InstanceStatus.NOT_DONE
    not_done_substatus = NotDoneSubstatus.SKIPPED_UNJUSTIFIED
```

**SKIPPED_UNJUSTIFIED → SKIPPED_JUSTIFIED:**

```python
# Usuário adiciona justificativa dentro de 24h
if skip_reason is added:
    not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
```

**PENDING → NOT_DONE (ignored):**

```python
# Automático: pending > 48h sem ação (Job background - Fase 2)
if elapsed_time > 48h and no_action_taken:
    status = InstanceStatus.NOT_DONE
    not_done_substatus = NotDoneSubstatus.IGNORED
```

---

## Impacto em Streak

**Regras:**

1. DONE (qualquer substatus) → **mantém streak**
2. NOT_DONE (qualquer substatus) → **quebra streak**

**Detalhamento:**

- EXCESSIVE: mantém streak MAS sistema alerta sobre impacto
- OVERDONE: mantém streak MAS monitora recorrência
- FULL: mantém streak [OK] Ideal!
- PARTIAL: mantém streak (warning se recorrente)
- SKIPPED_JUSTIFIED: quebra streak (mas é "aceitável")
- SKIPPED_UNJUSTIFIED: quebra streak (warning forte)
- IGNORED: quebra streak (problema crítico)

**Justificativa:**

- Qualquer DONE conta para streak (incentiva execução)
- Mas EXCESSIVE/OVERDONE recebem feedback corretivo
- Sistema balanceia incentivo com ajuste comportamental

---

## Análise de Impacto (EXCESSIVE/OVERDONE)

### Sistema Inteligente

Quando EXCESSIVE ou OVERDONE ocorre, sistema analisa:

```python
def analyze_impact(instance: HabitInstance) -> ImpactAnalysis:
    """Analisa se overdone/excessive afetou outros hábitos."""

    # Buscar hábitos posteriores no mesmo dia
    subsequent = get_subsequent_habits_same_day(instance.scheduled_date)

    affected = []
    for habit in subsequent:
        if habit.status == InstanceStatus.NOT_DONE:
            # Verificar se foi por falta de tempo
            if habit.scheduled_start < instance.actual_end:
                affected.append(habit)

    return ImpactAnalysis(
        affected_count=len(affected),
        affected_habits=affected,
        overtime_minutes=instance.actual_duration - instance.expected_duration
    )
```

### CLI Output com Impacto

```bash
# Após timer stop com EXCESSIVE
timeblock timer stop

[WARN] Academia ultrapassou meta em 90min (200%)

Impacto na rotina:
  - Trabalho focado: PERDIDO (conflito horário)
  - Inglês: ATRASADO 30min
  - Leitura: SKIPPED

Sugestão: Ajustar meta de Academia para 2h?
          [Y] Sim, ajustar permanentemente
          [N] Não, foi exceção de hoje
```

---

## CLI Outputs

### Status Display

```bash
timeblock habit list

Agenda - 14/11/2025
┌────┬───────────────┬─────────────────┬──────────────────┐
│ ID │ Habit         │ Horário         │ Status           │
├────┼───────────────┼─────────────────┼──────────────────┤
│ 42 │ Academia      │ 07:00 → 08:30   │ Done (Excessive) │
│ 43 │ Meditação     │ 20:00 → 20:15   │ Done (Partial)   │
│ 44 │ Leitura       │ 21:00 → 22:00   │ Skipped (Just.)  │
│ 45 │ Inglês        │ 19:00 → 20:00   │ Done (Full)      │
│ 46 │ Journaling    │ 06:00 → 06:15   │ Ignored          │
└────┴───────────────┴─────────────────┴──────────────────┘

[WARN] Academia (EXCESSIVE) afetou 2 outros hábitos hoje
```

### Report Detalhado

```bash
timeblock report habit 42 --period 30

Academia - Últimos 30 dias
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DONE: 27/30 (90%)
  ├─ Excessive: 2 (7%)    ██░░░░░░░░░░░░░░  [WARN]
  ├─ Overdone: 3 (10%)    ███░░░░░░░░░░░░░  [INFO]
  ├─ Full: 19 (63%)       ████████████░░░░  [OK]
  └─ Partial: 3 (10%)     ██░░░░░░░░░░░░░░

NOT DONE: 3/30 (10%)
  ├─ Skipped (just.): 2 (7%)    █░░░░░░░░░░░░░░░
  ├─ Skipped (unjust.): 0 (0%)  ░░░░░░░░░░░░░░░░
  └─ Ignored: 1 (3%)             ░░░░░░░░░░░░░░░░  [WARN]

STREAK: 12 dias (quebrado 1x este mês)

[WARN] EXCESSIVE causou 4 skips em outros hábitos este mês
       Considere ajustar meta de 90min para 120min?
```

### Análise de Correlação

```bash
timeblock report analyze

Padrões Identificados:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[WARN] Academia EXCESSIVE → Inglês SKIPPED (4 ocorrências)
       Academia em média ultrapassa 45min além da meta

Sugestão: Aumentar meta Academia para 2h
          Ou mover Inglês para após 20h
```

---

## Implementação MVP

### Fase 1 (MVP - Imediato)

- [x] InstanceStatus enum (PENDING, DONE, NOT_DONE)
- [x] DoneSubstatus enum (EXCESSIVE, OVERDONE, FULL, PARTIAL)
- [x] NotDoneSubstatus enum (SKIPPED_JUSTIFIED, SKIPPED_UNJUSTIFIED, IGNORED)
- [x] Campos status + substatus no modelo
- [x] Transições PENDING → DONE (via timer)
- [x] Transições PENDING → NOT_DONE (via skip)
- [x] Lógica thresholds: 150%, 110%, 90%

### Fase 2 (Análise de Impacto)

- [ ] Função `analyze_impact()` após timer stop
- [ ] Alertas CLI quando EXCESSIVE afeta outros
- [ ] Sugestão de ajuste de meta se recorrente
- [ ] Report de correlações (habit X → habit Y)

### Fase 3 (Pós-MVP)

- [ ] Job automático para IGNORED (após 48h)
- [ ] Reversão de estados (desfazer skip/complete)
- [ ] Políticas customizáveis (thresholds configuráveis)
- [ ] Machine learning para sugerir ajustes de rotina

---

## Business Rules Relacionadas

**A criar:**

- BR-HABIT-INSTANCE-001: Status Transitions
- BR-HABIT-INSTANCE-002: Substatus Assignment
- BR-HABIT-INSTANCE-003: Completion Thresholds (excessive > 150%, overdone > 110%, full 90-110%)
- BR-HABIT-INSTANCE-004: Streak Calculation with Substatus
- BR-HABIT-INSTANCE-005: Ignored Auto-Assignment (48h)
- BR-HABIT-INSTANCE-006: Impact Analysis on EXCESSIVE/OVERDONE

---

## Referências

- Modelo: `src/timeblock/models/habit_instance.py`
- Service: `src/timeblock/services/habit_instance_service.py`
- Decisão relacionada: `skip-categorization-final.md`
- Discussão: `sessions/2025-11-14-skip-states-cli-discussion.md`

---

**Próxima Revisão:** Após implementação MVP

**Status:** DECIDIDO
