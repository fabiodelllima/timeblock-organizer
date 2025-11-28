# Requirements Traceability Matrix (RTM)

- **Versão:** 1.0
- **Data:** 2025-11-10
- **Status:** Em Construção (Sprint 1 - Habits)

---

## Propósito

Este documento mapeia bidirecionalmente:

- **Business Rules** → **Tests** → **Code**
- Garante que toda BR tem teste e implementação
- Facilita manutenção e impacto de mudanças
- Serve como índice navegável do sistema

---

## Legenda

| Símbolo   | Significado                      |
| --------- | -------------------------------- |
| [OK]      | Implementado e testado           |
| [PARTIAL] | Implementado mas sem teste BR-\* |
| [TODO]    | Não implementado                 |
| [WIP]     | Em refactoring (Sprint atual)    |

---

## Habits Domain (8 BRs)

### BR-HABIT-001: Criação de Hábitos em Rotinas

**Status:** [WIP] Em refactoring (Sprint 1)

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-001`
- Descrição: Usuário cria Habits especificando dias da semana e horários

**Tests:**

- Unit: `tests/unit/test_services/test_habit_service_crud.py`
  - `TestCreateHabit::test_create_habit_success` [PARTIAL] (renomear para `test_br_habit_001_creates_successfully`)
  - `TestCreateHabit::test_create_habit_with_color` [PARTIAL]
  - `TestCreateHabit::test_create_habit_strips_whitespace` [PARTIAL]
- Integration: `tests/integration/commands/test_habit_commands.py`
  - `test_habit_create_success` [PARTIAL] (renomear para `test_br_habit_001_cli_creates`)
- E2E: `tests/e2e/test_habit_lifecycle.py`
  - `test_habit_full_lifecycle` [PARTIAL] (parcial, renomear)

**Code:**

- Service: `src/timeblock/services/habit_service.py::HabitService.create_habit` (linhas 14-45)
- Model: `src/timeblock/models/habit.py::Habit`
- Command: `src/timeblock/commands/habit.py::habit_create`

**Cenários Cobertos:**

- [x] Criação com dados válidos
- [x] Criação com cor opcional
- [x] Remoção de whitespace do título
- [x] Validação via CLI

**Cenários Faltando:**

- [ ] Teste E2E específico para BR-HABIT-001

---

### BR-HABIT-002: Validação de Dados Inválidos

**Status:** [WIP] Em refactoring (Sprint 1)

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-001` (mesma seção)
- Descrição: Sistema rejeita título vazio, longo, ou horários inválidos

**Tests:**

- Unit: `tests/unit/test_services/test_habit_service_crud.py`
  - `TestCreateHabit::test_create_habit_with_empty_title` [PARTIAL]
  - `TestCreateHabit::test_create_habit_with_title_too_long` [PARTIAL]
  - `TestCreateHabit::test_create_habit_with_invalid_times` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/habit_service.py::HabitService.create_habit` (linhas 24-35, validações)

**Cenários Cobertos:**

- [x] Rejeita título vazio
- [x] Rejeita título > 200 chars
- [x] Rejeita horário fim antes de início

---

### BR-HABIT-003: Geração de Instâncias

**Status:** [PARTIAL] Implementado sem padrão BR-\*

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-002`
- Descrição: Sistema gera HabitInstances para período especificado

**Tests:**

- Unit: `tests/unit/test_services/test_habit_instance_service_extended.py`
  - `TestGenerateInstances::test_generate_everyday_habit` [PARTIAL]
  - `TestGenerateInstances::test_generate_weekdays_only` [PARTIAL]
  - `TestGenerateInstances::test_generate_single_day` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/habit_instance_service.py::HabitInstanceService.generate_instances`

**Cenários Cobertos:**

- [x] Geração para hábito EVERYDAY
- [x] Geração para WEEKDAYS
- [x] Geração para dia específico

---

### BR-HABIT-004: Ajuste de Horário de Instância

**Status:** [PARTIAL] Implementado sem padrão BR-\*

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-004`
- Descrição: Usuário ajusta horário de instância específica via ID

**Tests:**

- Unit: `tests/unit/test_services/test_habit_instance_service.py`
  - `TestAdjustInstanceTimeBasic::test_adjust_time_successfully` [PARTIAL]
  - `TestAdjustInstanceTimeBasic::test_adjust_time_invalid` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/habit_instance_service.py::HabitInstanceService.adjust_instance_time`

---

### BR-HABIT-005: Marcação de Complete

**Status:** [PARTIAL] Implementado sem padrão BR-\*

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-005`
- Descrição: Usuário marca instância como concluída

**Tests:**

- Unit: `tests/unit/test_services/test_habit_instance_service_extended.py`
  - `TestMarkCompleted::test_mark_completed_success` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/habit_instance_service.py::HabitInstanceService.mark_completed`

---

### BR-HABIT-006: Skip de Instância

**Status:** [PARTIAL] Implementado sem padrão BR-\*

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-006`
- Descrição: Usuário pula instância sem marcar como complete

**Tests:**

- Unit: `tests/unit/test_services/test_habit_instance_service_extended.py`
  - `TestMarkSkipped::test_mark_skipped_success` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/habit_instance_service.py::HabitInstanceService.mark_skipped`

---

### BR-HABIT-007: Reset de Instância

**Status:** [TODO] Não implementado

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-007`
- Descrição: Usuário reseta instância para estado PLANNED

**Tests:**

- [TODO] Nenhum teste encontrado

**Code:**

- [TODO] Não implementado

**Ação:** Implementar em Sprint 1

---

### BR-HABIT-008: Vínculo com Routine

**Status:** [OK] Implementado

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/habit-instances.md#br-habit-008`
- Descrição: Habits pertencem a Routines

**Tests:**

- Unit: Coberto implicitamente em todos testes de habits (fixture test_routine)

**Code:**

- Model: `src/timeblock/models/habit.py::Habit.routine_id`
- Service: Todos métodos HabitService validam routine_id

---

## Tasks Domain (9 BRs)

### BR-TASK-001: Criação de Task

**Status:** [PARTIAL] Implementado sem padrão BR-\*

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/tasks.md#br-task-001`

**Tests:**

- Unit: `tests/unit/test_services/test_task_service.py`
  - `TestCreateTask::test_create_task_success` [PARTIAL]
  - `TestCreateTask::test_create_task_with_description` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/task_service.py::TaskService.create_task`

---

### BR-TASK-002 a BR-TASK-009

**Status:** [PARTIAL] Implementados mas não mapeados

**Ação:** Mapear durante Sprint 2 (Tasks)

---

## Event Reordering Domain (7 BRs)

### BR-EVENT-001: Detecção de Conflitos

**Status:** [PARTIAL] Implementado sem padrão BR-\*

**Business Rule:**

- Documento: `docs/04-specifications/business-rules/event-reordering.md#br-event-001`

**Tests:**

- Unit: `tests/unit/test_services/test_event_reordering_service.py`
  - `TestDetectConflicts::test_no_conflicts` [PARTIAL]
  - `TestDetectConflicts::test_task_overlaps_with_task` [PARTIAL]

**Code:**

- Service: `src/timeblock/services/event_reordering_service.py::EventReorderingService.detect_conflicts`

---

### BR-EVENT-002 a BR-EVENT-007

**Status:** [PARTIAL] Implementados mas não mapeados

**Ação:** Mapear durante Sprint 3 (Events)

---

## Resumo Executivo

### Estatísticas Globais

| Métrica               | Valor    | Progresso                    |
| --------------------- | -------- | ---------------------------- |
| BRs Documentadas      | 24       | 100%                         |
| BRs Implementadas     | 22       | 92%                          |
| BRs com Testes        | 22       | 92%                          |
| Testes seguindo BR-\* | 0        | 0% -> 100% (meta Sprint 1-4) |
| RTM Completo          | Sprint 1 | 12% -> 100% (meta Sprint 4)  |

### Por Domínio

| Domínio | BRs | Implementadas | Testadas   | Padrão BR-\*   |
| ------- | --- | ------------- | ---------- | -------------- |
| Habits  | 8   | 7/8 (88%)     | 7/8 (88%)  | 0/8 (0%) [WIP] |
| Tasks   | 9   | 9/9 (100%)    | 9/9 (100%) | 0/9 (0%)       |
| Events  | 7   | 6/7 (86%)     | 6/7 (86%)  | 0/7 (0%)       |

---

## Cronograma de Atualização

- **Sprint 1 (Atual):** Habits - RTM detalhado + renomear testes
- **Sprint 2:** Tasks - RTM detalhado + renomear testes
- **Sprint 3:** Events - RTM detalhado + renomear testes
- **Sprint 4:** Timer, Routines - RTM completo

---

## Notas

### Testes Órfãos Identificados

Testes que NÃO correspondem a BRs documentadas:

1. `test_habit_instance_manually_adjusted` - Campo `manually_adjusted` não existe
2. `test_user_override_default_false` - Campo `user_override` não existe
3. `test_propose_reordering` - Método não existe

**Ação:** Revisar e criar BRs ou remover testes (Sprint 1).

### Scripts de Validação

```bash
# Verificar rastreabilidade de uma BR
grep -r "BR-HABIT-001" tests/ docs/ src/

# Listar testes sem padrão BR-*
grep -r "class Test" tests/ | grep -v "TestBR"

# Gerar relatório de cobertura de BRs
python scripts/generate-br-coverage-report.py
```

---

## Referências

- ADR-019: Test Naming Convention
- ADR-021: Requirements Traceability Matrix (este documento)
- IEEE 830-1998: Software Requirements Specification
- Microsoft Azure DevOps: Requirements Traceability
