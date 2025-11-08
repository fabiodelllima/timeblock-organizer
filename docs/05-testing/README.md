# Estrutura de Testes

## Visão Geral

Todos os testes validam Regras de Negócio documentadas em `docs/04-specifications/business-rules/`.

## Mapeamento Docs → Testes

### Event Reordering

**Documento:** `docs/04-specifications/business-rules/event-reordering-rules.md`

**Testes:** `cli/tests/unit/test_services/test_event_reordering_service.py`

| Regra        | Classes de Teste                           |
| ------------ | ------------------------------------------ |
| RN-EVENT-001 | `TestRNEvent001DeteccaoConflitosTemporais` |
| RN-EVENT-002 | `TestRNEvent002ApresentacaoConflitos`      |
| RN-EVENT-007 | `TestRNEvent007InteracaoTimerComplete`     |

### Habit Instance

**Documento:** `docs/04-specifications/business-rules/habit-instance-rules.md`

**Testes:** `cli/tests/unit/test_services/test_habit_instance_service.py`

| Regra        | Classes de Teste                       |
| ------------ | -------------------------------------- |
| RN-HABIT-001 | `TestRNHabit001GeracaoInstancias`      |
| RN-HABIT-004 | `TestRNHabit004AjusteHorarioInstancia` |

### Task

**Documento:** `docs/04-specifications/business-rules/task-rules.md`

**Testes:** `cli/tests/unit/test_services/test_task_service.py`

| Regra       | Classes de Teste                       |
| ----------- | -------------------------------------- |
| RN-TASK-001 | `TestRNTask001AtualizacaoComConflitos` |

## Executando Testes

```bash
# Todos os testes
pytest cli/tests/

# Por módulo
pytest cli/tests/unit/test_services/test_event_reordering_service.py -v

# Por regra específica
pytest cli/tests/unit/test_services/test_event_reordering_service.py::TestRNEvent001DeteccaoConflitosTemporais -v

# Com cobertura
pytest --cov=src/timeblock --cov-report=html
```

## Ver também

- [Filosofia de Testes](testing-philosophy.md)
- [Regras de Negócio](../04-specifications/business-rules/)
