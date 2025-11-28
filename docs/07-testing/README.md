# Estrutura de Testes

## Visão Geral

Todos os testes validam Regras de Negócio documentadas em `docs/04-specifications/business-rules/`.

## Mapeamento Docs → Testes

### Event Reordering

**Documento:** `docs/04-specifications/business-rules/event-reordering-rules.md`

**Testes:** `cli/tests/unit/test_services/test_event_reordering_service.py`

| Regra        | Classes de Teste                           |
| ------------ | ------------------------------------------ |
| BR-EVENT-001 | `TestBREvent001DeteccaoConflitosTemporais` |
| BR-EVENT-002 | `TestBREvent002ApresentacaoConflitos`      |
| BR-EVENT-007 | `TestBREvent007InteracaoTimerComplete`     |

### Habit Instance

**Documento:** `docs/04-specifications/business-rules/habit-instance-rules.md`

**Testes:** `cli/tests/unit/test_services/test_habit_instance_service.py`

| Regra        | Classes de Teste                       |
| ------------ | -------------------------------------- |
| BR-HABIT-001 | `TestBRHabit001GeracaoInstancias`      |
| BR-HABIT-004 | `TestBRHabit004AjusteHorarioInstancia` |

### Task

**Documento:** `docs/04-specifications/business-rules/task-rules.md`

**Testes:** `cli/tests/unit/test_services/test_task_service.py`

| Regra       | Classes de Teste                       |
| ----------- | -------------------------------------- |
| BR-TASK-001 | `TestBRTask001AtualizacaoComConflitos` |

## Executando Testes

```bash
# Todos os testes
pytest cli/tests/

# Por módulo
pytest cli/tests/unit/test_services/test_event_reordering_service.py -v

# Por regra específica
pytest cli/tests/unit/test_services/test_event_reordering_service.py::TestBREvent001DeteccaoConflitosTemporais -v

# Com cobertura
pytest --cov=src/timeblock --cov-report=html
```

## Ver também

- [Filosofia de Testes](testing-philosophy.md)
- [Regras de Negócio](../04-specifications/business-rules/)
