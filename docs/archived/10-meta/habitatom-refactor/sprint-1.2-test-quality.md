# Sprint 1.2 - Qualidade de Testes

**Duração:** 6h

**Objetivo:** Base sólida antes de avançar

## Fase 1: Corrigir Bugs Existentes (2h)

### Bug 1: test_habit_instance_creation

```python
# PROBLEMA:
assert instance.status == "planned"
# Atual: HabitInstanceStatus.PLANNED (enum)
# Esperado: "planned" (string)

# FIX:
assert instance.status == HabitInstanceStatus.PLANNED
# ou
assert instance.status.value == "planned"
```

### Bug 2: test_habit_instance_with_actuals

```python
# PROBLEMA:
assert instance.actual_start == datetime(...)
# AttributeError: 'HabitInstance' object has no attribute 'actual_start'

# ANÁLISE NECESSÁRIA:
# 1. Campo existe no modelo?
# 2. Foi removido em refatoração anterior?
# 3. Teste está obsoleto?
```

### ResourceWarnings

```python
# PROBLEMA: 112+ warnings de conexões não fechadas
# INVESTIGAR:
# - Fixtures sem close()
# - Context managers faltando
# - Session management incorreto
```

## Fase 2: Aumentar Cobertura (4h)

### Target: HabitInstanceService 69% → 90%

**Linhas não cobertas:** 30 (de 98 statements)

**Adicionar testes para:**

1. Error paths (validações)
2. Edge cases (datas extremas, conflitos)
3. Integration paths (EventReordering)

**Estimativa:** ~8 testes novos (30min cada)

## Validação

```bash
# ANTES de prosseguir:
pytest cli/tests/unit/test_models/test_habit_instance*.py -v
pytest cli/tests/unit/test_services/test_habit_instance_service.py -v
pytest cli/tests/integration/services/test_habit_instance_integration.py -v

# Todos PASSANDO
# Cobertura: 90%+
```

## Deliverables

- [ ] 2 testes corrigidos
- [ ] ResourceWarnings investigados/resolvidos
- [ ] HabitInstanceService: 90%+ cobertura
- [ ] Documentação: quais testes adicionados e por quê

---

**Próximo:** Sprint 1.3 - Logging Básico
