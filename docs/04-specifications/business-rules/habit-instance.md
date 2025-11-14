# Business Rules: Habit Instance

- **Domínio:** HabitInstance
- **Área:** Estados, Transições e Substatus
- **Última atualização:** 14 de Novembro de 2025

---

## Índice

- [BR-HABIT-INSTANCE-001: Status Transitions](#br-habit-instance-001)
- [BR-HABIT-INSTANCE-002: Substatus Assignment](#br-habit-instance-002)
- [BR-HABIT-INSTANCE-003: Completion Thresholds](#br-habit-instance-003)
- [BR-HABIT-INSTANCE-004: Streak Calculation with Substatus](#br-habit-instance-004)
- [BR-HABIT-INSTANCE-005: Ignored Auto-Assignment](#br-habit-instance-005)
- [BR-HABIT-INSTANCE-006: Impact Analysis on EXCESSIVE/OVERDONE](#br-habit-instance-006)

---

## BR-HABIT-INSTANCE-001: Status Transitions

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [habit-states-final.md](../../11-planning/decisions/habit-states-final.md)

### Descrição

HabitInstance possui 3 status principais (PENDING, DONE, NOT_DONE) com transições bem definidas.

### Enum InstanceStatus

```python
class InstanceStatus(str, Enum):
    """Status principal do HabitInstance."""
    PENDING = "pending"      # Agendado, não iniciado
    DONE = "done"            # Realizado
    NOT_DONE = "not_done"    # Não realizado
```

### Transições Permitidas

```terminal
PENDING
  ├─> DONE (via timer stop)
  └─> NOT_DONE (via skip ou timeout)

DONE
  └─> [FINAL] (não pode voltar)

NOT_DONE
  └─> [FINAL] (não pode voltar)
```

### Regras de Transição

**1. PENDING → DONE:**

- Gatilho: `timer stop`
- Requer: `actual_duration` > 0
- Define: `done_substatus` baseado em completion %

**2. PENDING → NOT_DONE:**

- Gatilho A: `habit skip` (comando explícito)
- Gatilho B: Timeout após 48h sem ação
- Define: `not_done_substatus` (SKIPPED\_\* ou IGNORED)

**3. Transições Proibidas:**

- DONE → PENDING ✗
- NOT_DONE → PENDING ✗
- DONE → NOT_DONE ✗
- NOT_DONE → DONE ✗

### Critérios de Aceitação

- [ ] Apenas 3 status possíveis
- [ ] Status inicial sempre PENDING
- [ ] Transições irreversíveis (DONE e NOT_DONE são finais)
- [ ] timer stop sempre leva a DONE (nunca NOT_DONE)
- [ ] skip sempre leva a NOT_DONE (nunca DONE)

### Testes Relacionados

- `test_br_habit_instance_001_initial_status_pending`
- `test_br_habit_instance_001_timer_stop_to_done`
- `test_br_habit_instance_001_skip_to_not_done`
- `test_br_habit_instance_001_no_reverse_transitions`

### Exemplos

#### Exemplo 1: Transição Normal (PENDING → DONE)

```python
# Estado inicial
instance = HabitInstance(
    status=InstanceStatus.PENDING,
    scheduled_start=time(7, 0),
    scheduled_end=time(8, 30)
)

# Após timer stop
instance.status = InstanceStatus.DONE
instance.done_substatus = DoneSubstatus.FULL
instance.actual_duration = 90
```

#### Exemplo 2: Skip (PENDING → NOT_DONE)

```python
# Estado inicial
instance = HabitInstance(status=InstanceStatus.PENDING)

# Após skip
instance.status = InstanceStatus.NOT_DONE
instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
instance.skip_reason = SkipReason.HEALTH
```

#### Exemplo 3: Transição Proibida

```python
# ✗ Não permitido
instance = HabitInstance(status=InstanceStatus.DONE)
instance.status = InstanceStatus.PENDING  # ValueError!
```

---

## BR-HABIT-INSTANCE-002: Substatus Assignment

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [habit-states-final.md](../../11-planning/decisions/habit-states-final.md)

### Descrição

Cada status principal possui substatus específico que detalha a natureza da conclusão ou não conclusão.

### Enums de Substatus

```python
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
    IGNORED = "ignored"                            # Não realizado sem ação
```

### Regras de Associação

```python
# Se status == DONE → done_substatus obrigatório
if instance.status == InstanceStatus.DONE:
    assert instance.done_substatus is not None
    assert instance.not_done_substatus is None

# Se status == NOT_DONE → not_done_substatus obrigatório
if instance.status == InstanceStatus.NOT_DONE:
    assert instance.not_done_substatus is not None
    assert instance.done_substatus is None

# Se status == PENDING → ambos NULL
if instance.status == InstanceStatus.PENDING:
    assert instance.done_substatus is None
    assert instance.not_done_substatus is None
```

### Critérios de Aceitação

- [ ] DONE sempre tem done_substatus (nunca NULL)
- [ ] NOT_DONE sempre tem not_done_substatus (nunca NULL)
- [ ] PENDING sempre tem ambos NULL
- [ ] Substatus mutuamente exclusivos (apenas 1 não-NULL)

### Testes Relacionados

- `test_br_habit_instance_002_done_requires_done_substatus`
- `test_br_habit_instance_002_not_done_requires_not_done_substatus`
- `test_br_habit_instance_002_pending_substatus_null`
- `test_br_habit_instance_002_substatus_mutual_exclusive`

### Exemplos

#### Exemplo 1: DONE com FULL

```python
instance = HabitInstance(
    status=InstanceStatus.DONE,
    done_substatus=DoneSubstatus.FULL,       # ✓ Obrigatório
    not_done_substatus=None                   # ✓ NULL
)
```

#### Exemplo 2: NOT_DONE com SKIPPED_JUSTIFIED

```python
instance = HabitInstance(
    status=InstanceStatus.NOT_DONE,
    done_substatus=None,                                        # ✓ NULL
    not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED      # ✓ Obrigatório
)
```

#### Exemplo 3: Validação (ambos preenchidos = erro)

```python
# ✗ Erro: não pode ter ambos
instance = HabitInstance(
    status=InstanceStatus.DONE,
    done_substatus=DoneSubstatus.FULL,
    not_done_substatus=NotDoneSubstatus.IGNORED  # ValueError!
)
```

---

## BR-HABIT-INSTANCE-003: Completion Thresholds

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [habit-states-final.md](../../11-planning/decisions/habit-states-final.md)

### Descrição

Substatus de DONE é determinado por thresholds de completion percentage baseados em expected_duration vs actual_duration.

### Fórmula de Completion

```python
completion_percentage = (actual_duration / expected_duration) * 100
```

### Thresholds Definidos

```python
if completion_percentage > 150:
    done_substatus = DoneSubstatus.EXCESSIVE
    # [WARN] Problema: desbalanceou rotina

elif completion_percentage > 110:
    done_substatus = DoneSubstatus.OVERDONE
    # [INFO] Atenção: acima do planejado

elif completion_percentage >= 90:
    done_substatus = DoneSubstatus.FULL
    # [OK] Ideal: dentro da faixa

else:  # completion_percentage < 90
    done_substatus = DoneSubstatus.PARTIAL
    # Abaixo da meta
```

### Tabela de Thresholds

| Completion % | Substatus | Significado         | Feedback |
| ------------ | --------- | ------------------- | -------- |
| > 150%       | EXCESSIVE | Desbalanceou rotina | [WARN]   |
| 110-150%     | OVERDONE  | Acima do ideal      | [INFO]   |
| 90-110%      | FULL      | Ideal               | [OK]     |
| < 90%        | PARTIAL   | Abaixo da meta      | -        |

### Critérios de Aceitação

- [ ] Thresholds exatos: 150%, 110%, 90%
- [ ] Cálculo usa expected_duration e actual_duration
- [ ] EXCESSIVE sempre gera warning
- [ ] OVERDONE gera info se recorrente
- [ ] FULL é o target ideal
- [ ] PARTIAL mantém streak mas alerta

### Testes Relacionados

- `test_br_habit_instance_003_excessive_above_150`
- `test_br_habit_instance_003_overdone_110_to_150`
- `test_br_habit_instance_003_full_90_to_110`
- `test_br_habit_instance_003_partial_below_90`
- `test_br_habit_instance_003_edge_cases`

### Exemplos

#### Exemplo 1: EXCESSIVE (200%)

```python
expected_duration = 90  # min
actual_duration = 180   # min
completion = 200%

# Resultado
done_substatus = DoneSubstatus.EXCESSIVE
# [WARN] Academia ultrapassou meta em 90min
```

#### Exemplo 2: OVERDONE (111%)

```python
expected_duration = 90  # min
actual_duration = 100   # min
completion = 111%

# Resultado
done_substatus = DoneSubstatus.OVERDONE
# [INFO] Acima da meta
```

#### Exemplo 3: FULL (100%)

```python
expected_duration = 90  # min
actual_duration = 90    # min
completion = 100%

# Resultado
done_substatus = DoneSubstatus.FULL
# [OK] Perfeito!
```

#### Exemplo 4: PARTIAL (67%)

```python
expected_duration = 90  # min
actual_duration = 60    # min
completion = 67%

# Resultado
done_substatus = DoneSubstatus.PARTIAL
# Abaixo da meta, mas mantém streak
```

#### Exemplo 5: Edge Cases (boundaries)

```python
# Exatamente 150% → EXCESSIVE
150.0% → EXCESSIVE

# 150.1% → EXCESSIVE
150.1% → EXCESSIVE

# 149.9% → OVERDONE
149.9% → OVERDONE

# Exatamente 110% → OVERDONE
110.0% → OVERDONE

# Exatamente 90% → FULL
90.0% → FULL

# 89.9% → PARTIAL
89.9% → PARTIAL
```

---

## BR-HABIT-INSTANCE-004: Streak Calculation with Substatus

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)

### Descrição

Streak é mantido por DONE (qualquer substatus) e quebrado por NOT_DONE (qualquer substatus).

### Regra Fundamental

```python
if instance.status == InstanceStatus.DONE:
    # Mantém streak (EXCESSIVE, OVERDONE, FULL, PARTIAL)
    maintain_streak()
elif instance.status == InstanceStatus.NOT_DONE:
    # Quebra streak (SKIPPED_*, IGNORED)
    break_streak()
```

### Detalhamento por Substatus

**DONE (mantém):**

- EXCESSIVE: Mantém ✓ MAS alerta sobre impacto
- OVERDONE: Mantém ✓ MAS monitora recorrência
- FULL: Mantém ✓ [OK] Ideal!
- PARTIAL: Mantém ✓ (warning se recorrente)

**NOT_DONE (quebra):**

- SKIPPED_JUSTIFIED: Quebra ✗ (impacto psicológico BAIXO)
- SKIPPED_UNJUSTIFIED: Quebra ✗ (impacto psicológico MÉDIO)
- IGNORED: Quebra ✗ (impacto psicológico ALTO)

### Critérios de Aceitação

- [ ] Qualquer DONE mantém streak
- [ ] Qualquer NOT_DONE quebra streak
- [ ] PENDING não afeta streak (ainda não passou)
- [ ] Feedback diferenciado por substatus
- [ ] Streak resetado para 0 ao quebrar

### Testes Relacionados

- `test_br_habit_instance_004_done_maintains_streak`
- `test_br_habit_instance_004_not_done_breaks_streak`
- `test_br_habit_instance_004_partial_maintains`
- `test_br_habit_instance_004_excessive_maintains_with_warning`

### Exemplos

#### Exemplo 1: Histórico com Streak

```python
# Histórico Academia (últimos 7 dias):
14/11 - DONE (FULL)          ✓ Dia 3
13/11 - DONE (PARTIAL)       ✓ Dia 2
12/11 - DONE (OVERDONE)      ✓ Dia 1
11/11 - NOT_DONE (SKIPPED_J) ✗ QUEBROU
10/11 - DONE (FULL)          ✓ (streak anterior: 4 dias)
09/11 - DONE (FULL)          ✓
08/11 - DONE (EXCESSIVE)     ✓ (mantém, mas com warning)
07/11 - DONE (PARTIAL)       ✓

# Streak atual: 3 dias
# Último break: 11/11 (SKIPPED_JUSTIFIED)
```

#### Exemplo 2: EXCESSIVE Mantém Streak

```python
instance = HabitInstance(
    status=InstanceStatus.DONE,
    done_substatus=DoneSubstatus.EXCESSIVE,
    actual_duration=180,  # 200% da meta
    expected_duration=90
)

# Streak: MANTÉM ✓
# Feedback: [WARN] Ultrapassou meta em 90min
#           Impacto: Trabalho PERDIDO, Inglês ATRASADO
```

---

## BR-HABIT-INSTANCE-005: Ignored Auto-Assignment

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [habit-states-final.md](../../11-planning/decisions/habit-states-final.md)

### Descrição

Instance PENDING por mais de 48h sem ação do usuário é automaticamente marcada como IGNORED (job background).

### Regra Temporal

```python
# Job executa a cada 1h
if instance.status == InstanceStatus.PENDING:
    elapsed = datetime.now() - instance.scheduled_date

    if elapsed > timedelta(hours=48):
        instance.status = InstanceStatus.NOT_DONE
        instance.not_done_substatus = NotDoneSubstatus.IGNORED
        instance.ignored_at = datetime.now()
```

### Critérios de Aceitação

- [ ] Threshold de 48h após scheduled_date
- [ ] Job background executa automaticamente
- [ ] Apenas instances PENDING são verificadas
- [ ] Marca como IGNORED (não SKIPPED)
- [ ] Registra ignored_at timestamp
- [ ] Quebra streak

### Testes Relacionados

- `test_br_habit_instance_005_ignored_after_48h`
- `test_br_habit_instance_005_not_ignored_before_48h`
- `test_br_habit_instance_005_only_pending_checked`

### Exemplos

#### Exemplo 1: Timeline do IGNORED

```python
# 14/11/2025 07:00 - Instance criada
instance = HabitInstance(
    scheduled_date=date(2025, 11, 14),
    scheduled_start=time(7, 0),
    status=InstanceStatus.PENDING
)

# 15/11/2025 07:00 - 24h depois (ainda PENDING)
# Job verifica: elapsed = 24h → não marca ainda

# 16/11/2025 07:00 - 48h depois (ainda PENDING)
# Job verifica: elapsed = 48h → ainda não marca (> 48h, não >= 48h)

# 16/11/2025 08:00 - 49h depois
# Job verifica: elapsed = 49h → MARCA COMO IGNORED

instance.status = InstanceStatus.NOT_DONE
instance.not_done_substatus = NotDoneSubstatus.IGNORED
instance.ignored_at = datetime(2025, 11, 16, 8, 0)
```

#### Exemplo 2: User Ação Antes de 48h (evita IGNORED)

```python
# 14/11 07:00 - Criada
instance = HabitInstance(status=InstanceStatus.PENDING)

# 15/11 20:00 - User faz skip (37h depois)
habit skip Academia --reason WORK

# Instance: NOT_DONE (SKIPPED_JUSTIFIED)
# Não será marcada como IGNORED pelo job
```

---

## BR-HABIT-INSTANCE-006: Impact Analysis on EXCESSIVE/OVERDONE

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [habit-states-final.md](../../11-planning/decisions/habit-states-final.md)

### Descrição

Quando instance é marcada como EXCESSIVE ou OVERDONE, sistema analisa impacto em outros habits agendados para o mesmo dia.

### Análise de Impacto

```python
def analyze_impact(instance: HabitInstance) -> ImpactAnalysis:
    """Analisa se overdone/excessive afetou outros hábitos."""

    if instance.done_substatus not in [DoneSubstatus.EXCESSIVE, DoneSubstatus.OVERDONE]:
        return None  # Não precisa analisar

    # Buscar hábitos posteriores no mesmo dia
    subsequent = get_subsequent_habits_same_day(
        date=instance.scheduled_date,
        after_time=instance.scheduled_end
    )

    affected = []
    for habit in subsequent:
        # Verificar se foi pulado por falta de tempo
        if habit.status == InstanceStatus.NOT_DONE:
            # Checar se horário real de término conflitou
            if instance.actual_end > habit.scheduled_start:
                affected.append(habit)

    return ImpactAnalysis(
        affected_count=len(affected),
        affected_habits=affected,
        overtime_minutes=instance.actual_duration - instance.expected_duration
    )
```

### Critérios de Aceitação

- [ ] Análise apenas para EXCESSIVE e OVERDONE
- [ ] Verifica habits posteriores no mesmo dia
- [ ] Detecta conflitos de horário real
- [ ] Conta quantos habits foram afetados
- [ ] CLI exibe impacto após timer stop
- [ ] Sugere ajuste de meta se recorrente

### Testes Relacionados

- `test_br_habit_instance_006_excessive_impact_detected`
- `test_br_habit_instance_006_no_impact_if_no_conflict`
- `test_br_habit_instance_006_multiple_habits_affected`

### Exemplos

#### Exemplo 1: EXCESSIVE com Impacto

```python
# Agenda planejada
07:00-08:30  Academia (90min)
09:00-12:00  Trabalho (180min)
13:00-14:00  Inglês (60min)

# Realidade (Academia EXCESSIVE)
07:00-10:00  Academia REAL (180min) → 200% da meta

# Impacto detectado
affected_habits = [
    "Trabalho focado",  # PERDIDO (conflito total)
    "Inglês"            # ATRASADO 30min
]

# CLI output
[WARN] Academia ultrapassou meta em 90min (200%)

Impacto na rotina:
  - Trabalho focado: PERDIDO (conflito horário)
  - Inglês: ATRASADO 30min

Sugestão: Ajustar meta de Academia para 2h?
```

#### Exemplo 2: OVERDONE sem Impacto

```python
# Agenda planejada
07:00-08:30  Academia (90min)
14:00-15:00  Inglês (60min)

# Realidade (Academia OVERDONE, mas sem impacto)
07:00-09:00  Academia REAL (120min) → 133% da meta

# Análise
affected_habits = []  # Nenhum afetado (gap de 5h até Inglês)

# CLI output
✓ Sessão completa!
  Tempo: 120min (133% da meta)
  Status: DONE (OVERDONE)

[INFO] Acima da meta. Frequente? Considere ajustar para 2h.
```

---

## Referências

- **Decisão:** [habit-states-final.md](../../11-planning/decisions/habit-states-final.md)
- **Decisão:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)
- **Modelo:** `src/timeblock/models/habit_instance.py`
- **Service:** `src/timeblock/services/habit_instance_service.py`
- **Service:** `src/timeblock/services/streak_service.py`

---

**Última revisão:** 14 de Novembro de 2025

**Status:** Documentação completa, ready para implementação
