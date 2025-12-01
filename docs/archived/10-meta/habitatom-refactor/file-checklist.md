# Checklist de Arquivos - Refatoração HabitAtom

**Total:** 26 arquivos | **Refs Código:** 56 | **Refs Testes:** 85

## FASE 1: Database e Modelos

### Migration

- [ ] `database/migrations.py` - Criar nova migration
- [ ] Testar migration em banco dev
- [ ] Validar rollback

### Modelo Base

- [ ] `models/habit_instance.py` → `models/habit_atom.py`
  - [ ] Renomear classe HabitInstance → HabitAtom
  - [ ] Renomear enum HabitInstanceStatus → HabitAtomStatus
  - [ ] Atualizar **tablename** = "habitatom"
  - [ ] Atualizar docstrings

### Modelos Relacionados

- [ ] `models/__init__.py`
  - [ ] Atualizar import: from .habit_atom import HabitAtom
  - [ ] Atualizar **all**
- [ ] `models/habit.py`
  - [ ] Atualizar import
  - [ ] Atualizar type hint em Relationship

## FASE 2: Services

### Service Principal

- [ ] `services/habit_instance_service.py` → `services/habit_atom_service.py`
  - [ ] Renomear classe HabitInstanceService → HabitAtomService
  - [ ] Atualizar imports de HabitInstance
  - [ ] Atualizar type hints em retornos
  - [ ] Atualizar docstrings

### Service de Reordenamento

- [ ] `services/event_reordering_service.py`
  - [ ] Atualizar import: from ...models import HabitAtom
  - [ ] Atualizar type hints: Task | HabitAtom | Event
  - [ ] Atualizar queries: select(HabitAtom)
  - [ ] Verificar 13 referências

### Exports

- [ ] `services/__init__.py`
  - [ ] Atualizar import: from ...habit_atom_service import HabitAtomService
  - [ ] Atualizar **all**

## FASE 3: Comandos CLI

- [ ] `commands/habit.py` (4 refs)

  - [ ] Atualizar import HabitAtomService
  - [ ] Atualizar calls: HabitAtomService.generate_atoms()
  - [ ] Atualizar calls: HabitAtomService.adjust_atom_time()

- [ ] `commands/schedule.py` (6 refs)

  - [ ] Atualizar import
  - [ ] Atualizar 3 calls generate/list/get

- [ ] `commands/report.py` (6 refs)

  - [ ] Atualizar import
  - [ ] Atualizar calls list_atoms()

- [ ] `commands/timer.py` (5 refs)
  - [ ] Atualizar import
  - [ ] Atualizar calls get_atom()

## FASE 4: Testes Unitários (7 arquivos)

### Testes de Modelo

- [ ] `test_models/test_habit_instance.py` → `test_habit_atom.py`
  - [ ] Renomear arquivo
  - [ ] Atualizar imports
  - [ ] Atualizar docstrings
- [ ] `test_models/test_habit_instance_overdue.py` → `test_habit_atom_overdue.py`
  - [ ] Renomear arquivo
  - [ ] Atualizar classe TestHabitInstanceOverdue
  - [ ] Atualizar 14 referências
- [ ] `test_models/test_habit_instance_user_override.py` → `test_habit_atom_user_override.py`
  - [ ] Renomear arquivo
  - [ ] Atualizar imports

### Testes de Service

- [ ] `test_services/test_habit_instance_service.py` → `test_habit_atom_service.py`
  - [ ] Renomear arquivo
  - [ ] Atualizar classe de teste
  - [ ] Atualizar 16 referências
- [ ] `test_services/test_event_reordering_apply.py`
  - [ ] Atualizar imports HabitAtom
  - [ ] Atualizar fixtures
- [ ] `test_services/test_event_reordering_service.py`
  - [ ] Atualizar imports
  - [ ] Atualizar type hints
- [ ] `test_services/test_timer_service.py`
  - [ ] Atualizar import

### Testes de Commands

- [ ] `test_commands/test_habit_adjust.py`
  - [ ] Atualizar imports (6 refs)
  - [ ] Atualizar calls HabitAtomService

## FASE 5: Testes de Integração (5 arquivos)

- [ ] `integration/services/test_habit_instance_integration.py` → `test_habit_atom_integration.py`
  - [ ] Renomear arquivo
  - [ ] Atualizar classe TestHabitInstanceReorderingIntegration
  - [ ] Atualizar 15 referências
- [ ] `integration/services/test_task_integration.py`
  - [ ] Atualizar imports (2 refs)
- [ ] `integration/services/test_timer_integration.py`
  - [ ] Atualizar imports (2 refs)
- [ ] `integration/database/test_migrations.py`
  - [ ] Atualizar test de tabela
  - [ ] Atualizar 3 referências
- [ ] `integration/workflows/conftest.py`
  - [ ] Atualizar fixtures (2 refs)

## FASE 6: Fixtures

- [ ] `tests/conftest.py`
  - [ ] Atualizar import HabitAtom
- [ ] `tests/integration/conftest.py`
  - [ ] Atualizar import

## VALIDAÇÃO FINAL

### Testes

- [ ] `pytest tests/unit/test_models/test_habit_atom*.py -v`
- [ ] `pytest tests/unit/test_services/test_habit_atom*.py -v`
- [ ] `pytest tests/unit/test_services/test_event_reordering*.py -v`
- [ ] `pytest tests/integration/ -v`
- [ ] `pytest tests/ --tb=short` (todos os testes)

### Qualidade

- [ ] `mypy cli/src/timeblock/` (sem erros de tipo)
- [ ] `ruff check cli/src/` (sem erros de lint)
- [ ] Busca: `grep -r "HabitInstance" cli/src/ cli/tests/` (deve retornar 0)
- [ ] Busca: `grep -r "habit_instance" cli/src/ cli/tests/` (deve retornar 0 ou apenas comentários)

### Migration

- [ ] Migration testada em banco limpo
- [ ] Migration testada em banco com dados
- [ ] Rollback testado
- [ ] Queries funcionando

### Documentação

- [ ] Atualizar docs/01-architecture/
- [ ] Atualizar docs/04-specifications/
- [ ] Atualizar CHANGELOG.md
- [ ] Criar guia de migração

---

**Status:** 0/26 arquivos completos

**Última Atualização:** Sprint 1.1 (02 Nov 2025)
