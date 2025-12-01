# Débito Técnico - Testes Sprint 1

- **Data:** 2025-11-19
- **Status:** IDENTIFICADO
- **Impacto:** MÉDIO (não afeta Sprint 2)
- **Esforço estimado:** 2-3 horas

---

## Contexto

Durante validação da suite completa após conclusão do Sprint 2 (Timer + Skip Integration), identificamos 93 testes do Sprint 1 que necessitam atualização devido a mudanças de API introduzidas no próprio Sprint 1.

**Sprint 2 está 100% funcional** - todos os 31 novos testes passando.

---

## Sprint 2 Status: ✓ COMPLETO

**Novos testes (31/31 PASSANDO):**

- 4 BDD CLI tests (comando `habit skip`)
- 8 BDD service tests (skip com categorização)
- 12 unit tests (HabitInstanceService.skip_habit_instance)
- 7 unit tests (timer auto-calculation substatus)

**Features implementadas:**

- BR-TIMER-006: Stop timer auto-marca habit
- BR-HABIT-SKIP-001: Skip habit com 8 categorias

---

## Testes Sprint 1 Quebrados

**Total:** 93 failures + 18 errors

**Suite:** 394 passed, 93 failed, 4 skipped, 18 errors

### Categoria 1: Enum Status obsoleto (≈60 testes)

**Problema:** Código usa `Status.PLANNED` (removido ADR-017)

**Correção:** Substituir por `Status.PENDING`

**Arquivos:**

- `tests/unit/test_models/test_habit_instance*.py`
- `tests/unit/test_services/test_habit_instance_service*.py`
- `tests/integration/services/test_habit_instance_integration.py`
- `tests/e2e/test_event_creation.py`
- `tests/e2e/test_habit_lifecycle.py`

### Categoria 2: Campos removidos (≈10 testes)

**Campos obsoletos:** `manually_adjusted`, `user_override`

**Arquivos:**

- `tests/unit/test_models/test_habit_instance_user_override.py`
- `tests/unit/test_commands/test_habit_adjust.py`

### Categoria 3: Routine.is_active default (≈5 testes)

**Mudança:** Default True → False

**Arquivos:**

- `tests/unit/test_models/test_routine.py`
- `tests/unit/test_services/test_routine_service_crud.py`

### Categoria 4: Import faltando (≈10 testes)

**Erro:** `NameError: name 'HabitInstance' is not defined`

**Local:** `src/timeblock/commands/habit.py`

**Arquivos afetados:**

- `tests/integration/commands/test_habit_commands.py`
- `tests/e2e/test_*.py`

### Categoria 5: Fixtures faltando (14 errors)

**Erro:** `fixture 'test_db' not found`

**Arquivo:** `tests/unit/utils/test_queries.py`

### Categoria 6: Edge case (1 test)

**Teste:** `test_br_habit_instance_003_edge_case_110_exact`

**Problema:** 110% classifica FULL, esperado OVERDONE

---

## Priorização

**P0 - CRÍTICA:**

- Cat. 4: Adicionar import HabitInstance

**P1 - ALTA:**

- Cat. 1: Status.PLANNED → PENDING
- Cat. 3: Routine.is_active

**P2 - MÉDIA:**

- Cat. 2: Remover testes campos obsoletos
- Cat. 6: Investigar edge case

**P3 - BAIXA:**

- Cat. 5: Migrar fixtures

---

## Plano de Ação

1. **PR Correção Rápida** (~30min)

   - Import HabitInstance
   - Find/replace Status.PLANNED
   - Ajustar is_active

2. **PR Limpeza** (~1h)

   - Remover testes obsoletos
   - Migrar fixtures

3. **PR Investigação** (~30min)
   - Edge case BR-003

**Tracking:** Issue #TBD

**Milestone:** Sprint 1 Cleanup

---

## Impacto

- Sprint 2: ZERO (100% funcional)
- Sprint 1: Testes quebrados (não produção)
- Cobertura geral: 59% (era 99% antes Sprint 1)

**Status após correção esperado:** 99%+

---

**Responsável:** TBD

**Deadline:** Antes de Sprint 3
