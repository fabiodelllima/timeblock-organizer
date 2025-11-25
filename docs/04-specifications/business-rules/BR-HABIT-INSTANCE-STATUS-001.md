# BR-HABIT-INSTANCE-STATUS-001: Sistema Status e Substatus

- **Data Criação:** 2025-11-21 (Retroativo)
- **Status:** IMPLEMENTADO
- **Commit:** afea231 (2025-11-19)
- **ADR:** [ADR-021] Status+Substatus Refactoring

---

## Contexto

Refatoração do sistema de status do HabitInstance para suportar rastreamento detalhado de completude e skip categorizado.

**BREAKING CHANGE:** Migração de sistema 4-estados para sistema 3-estados com substatus.

---

## Sistema Anterior (DEPRECATED)

```python
# 4 estados independentes (v1.0-v1.3)
PLANNED       # Aguardando execução
IN_PROGRESS   # Timer ativo
COMPLETED     # Concluído
SKIPPED       # Pulado
```

**Problemas:**

- Não rastreia % completude (parcial vs completo)
- Skip sem categorização (justificado vs injustificado)
- Timer não calcula automaticamente status final

---

## Sistema Atual (v1.4+)

### Status Principal (3 estados)

```python
class Status(str, Enum):
    PENDING = "pending"      # Aguardando execução
    DONE = "done"            # Concluído (qualquer %)
    NOT_DONE = "not_done"    # Não concluído (skip/timeout)
```

### Substatus Done (4 níveis)

```python
class DoneSubstatus(str, Enum):
    FULL = "full"            # 90-110% (ideal)
    OVERDONE = "overdone"    # 110-150% (excesso moderado)
    EXCESSIVE = "excessive"  # >150% (burnout warning)
    PARTIAL = "partial"      # <90% (insuficiente)
```

### Substatus NotDone (3 categorias)

```python
class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"        # Com razão válida
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"    # Sem razão
    IGNORED = "ignored"                            # Timeout (>48h)
```

### Skip Reason (8 categorias)

```python
class SkipReason(str, Enum):
    HEALTH = "saude"          # Doença, mal-estar
    WORK = "trabalho"         # Demandas profissionais
    FAMILY = "familia"        # Obrigações familiares
    WEATHER = "clima"         # Condições climáticas
    LACK_TIME = "falta_tempo" # Agenda sobrecarregada
    LACK_ENERGY = "falta_energia"  # Cansaço físico/mental
    TRAVEL = "viagem"         # Deslocamento
    OTHER = "outro"           # Outras razões
```

---

## Regras de Negócio

### BR-HABIT-INSTANCE-STATUS-001.1: Estados Válidos

**DADO** uma instância de hábito
**QUANDO** o status é definido
**ENTÃO** deve ser PENDING, DONE ou NOT_DONE

**Validação:** Enum Status garante valores válidos.

### BR-HABIT-INSTANCE-STATUS-001.2: Substatus Obrigatório

**DADO** uma instância com status DONE
**QUANDO** finalizada
**ENTÃO** deve ter done_substatus definido

**DADO** uma instância com status NOT_DONE
**QUANDO** finalizada
**ENTÃO** deve ter not_done_substatus definido

**DADO** uma instância com status PENDING
**QUANDO** ainda não iniciada
**ENTÃO** ambos substatus devem ser None

**Validação:** método `validate_status_consistency()`

### BR-HABIT-INSTANCE-STATUS-001.3: Substatus Mutuamente Exclusivos

**DADO** uma instância finalizada
**QUANDO** substatus é definido
**ENTÃO** apenas UM substatus pode existir (done_substatus XOR not_done_substatus)

**Exemplo Inválido:**

```python
instance.done_substatus = DoneSubstatus.FULL
instance.not_done_substatus = NotDoneSubstatus.IGNORED
# ValueError: Cannot have both done and not_done substatus
```

### BR-HABIT-INSTANCE-STATUS-001.4: Cálculo Automático (Timer)

**DADO** timer parado
**QUANDO** duração efetiva vs esperada calculada
**ENTÃO** substatus definido automaticamente:

| % Completude | Substatus | Fórmula                    |
| ------------ | --------- | -------------------------- |
| < 90%        | PARTIAL   | duration < 0.9 \* expected |
| 90-110%      | FULL      | 0.9 <= ratio <= 1.1        |
| 110-150%     | OVERDONE  | 1.1 < ratio <= 1.5         |
| > 150%       | EXCESSIVE | ratio > 1.5                |

**Implementação:** `TimerService.stop()` + `HabitInstance.completion_percentage`

### BR-HABIT-INSTANCE-STATUS-001.5: Skip com Categorização

**DADO** usuário pula hábito
**QUANDO** escolhe categoria (1-8)
**ENTÃO** cria NOT_DONE + SKIPPED_JUSTIFIED + skip_reason

**QUANDO** escolhe "Sem razão" (opção 9)
**ENTÃO** cria NOT_DONE + SKIPPED_UNJUSTIFIED + skip_reason=None

**Validação:** skip_reason obrigatório se SKIPPED_JUSTIFIED

### BR-HABIT-INSTANCE-STATUS-001.6: Timeout (>48h)

**DADO** instância PENDING
**QUANDO** >48h após scheduled_start
**ENTÃO** automaticamente: NOT_DONE + IGNORED

**Implementação:** `HabitInstance.is_overdue` property

---

## Migração de Dados

### SQL Migration

```sql
-- Adicionar novos campos
ALTER TABLE habitinstance ADD COLUMN done_substatus TEXT;
ALTER TABLE habitinstance ADD COLUMN not_done_substatus TEXT;
ALTER TABLE habitinstance ADD COLUMN skip_reason TEXT;
ALTER TABLE habitinstance ADD COLUMN skip_note TEXT;
ALTER TABLE habitinstance ADD COLUMN completion_percentage REAL;

-- Mapear status antigo -> novo
UPDATE habitinstance
SET status = 'pending' WHERE status = 'PLANNED';

UPDATE habitinstance
SET status = 'done', done_substatus = 'full'
WHERE status = 'COMPLETED';

UPDATE habitinstance
SET status = 'not_done', not_done_substatus = 'skipped_unjustified'
WHERE status = 'SKIPPED';
```

**Script:** `migration_001_status_substatus.py`

---

## Testes

### Cobertura

```terminal
[18 scenarios BDD] - docs/06-bdd/scenarios/habit-instance.feature
[14 unit tests]    - tests/unit/test_models/test_habit_instance_status.py
[12 skip tests]    - tests/unit/test_services/test_habit_instance_skip.py
[7 timer tests]    - tests/unit/test_services/test_timer_service_substatus.py
```

### Exemplos Críticos

```python
# Teste: Timer calcula FULL (90-110%)
def test_scenario_001_completion_full():
    instance = create_instance(expected_duration=60)
    timer.start(); sleep(58); timer.stop()
    assert instance.status == Status.DONE
    assert instance.done_substatus == DoneSubstatus.FULL
    assert 90 <= instance.completion_percentage <= 110

# Teste: Skip com saúde
def test_scenario_skip_health():
    result = service.skip_instance(
        instance_id=1,
        skip_reason=SkipReason.HEALTH,
        skip_note="Gripe"
    )
    assert instance.status == Status.NOT_DONE
    assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
    assert instance.skip_reason == SkipReason.HEALTH

# Teste: Validação consistência
def test_scenario_both_substatus_error():
    instance.done_substatus = DoneSubstatus.FULL
    instance.not_done_substatus = NotDoneSubstatus.IGNORED
    with pytest.raises(ValueError, match="Cannot have both"):
        instance.validate_status_consistency()
```

---

## Impacto

### Arquivos Modificados

```terminal
src/timeblock/models/enums.py
src/timeblock/models/habit_instance.py
src/timeblock/services/timer_service.py
src/timeblock/services/habit_instance_service.py
src/timeblock/database/migrations/migration_001_*.py [NOVO]
```

### Retrocompatibilidade

```python
# DEPRECATED (manter por 1 release)
class HabitInstanceStatus(str, Enum):
    PLANNED = "PLANNED"  # Mapeia para Status.PENDING
    # Warning: Use Status enum instead
```

---

## Referências

- **Commit:** afea231 - feat(models): Implementa refatoração Status+Substatus
- **ADR:** ADR-021 Status+Substatus Refactoring (prometido, não criado)
- **Sprint:** Sprint 1 - Routine + HabitInstance Status (Nov 2025)
- **Atomic Habits:** Cap. 15 - Tracking Progress

---

## Notas Retroativas

[ ! ] Esta BR foi criada RETROATIVAMENTE em 2025-11-21 para documentar mudança implementada em 2025-11-19.

**Razão:** Débito técnico - implementação precedeu documentação formal.

**Correção:** Sprint 3.4 - Alinhamento DOCS > BDD > TDD > CODE.
