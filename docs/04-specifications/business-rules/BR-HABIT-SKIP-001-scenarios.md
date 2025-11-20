# BR-HABIT-SKIP-001: Cenários BDD

- **Referência:** BR-HABIT-SKIP-001
- **Formato:** Gherkin (DADO/QUANDO/ENTÃO)
- **Total de Cenários:** 10

---

## FUNCIONALIDADE: Skip de Habit com Categorização

Como usuário do TimeBlock

Quero marcar hábitos como skipped com categoria

Para rastrear razões de interrupção e identificar padrões

---

## CENÁRIO 1: Skip com categoria HEALTH

**ID:** SCENARIO-HABIT-SKIP-001-001

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa skip com categoria HEALTH
E nota "Gripe, febre 38°C"
ENTÃO status deve ser NOT_DONE
E not_done_substatus deve ser SKIPPED_JUSTIFIED
E skip_reason deve ser HEALTH
E skip_note deve ser "Gripe, febre 38°C"
E done_substatus deve ser None
E completion_percentage deve ser None
```

---

## CENÁRIO 2: Skip com categoria WORK sem nota

**ID:** SCENARIO-HABIT-SKIP-001-002

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa skip com categoria WORK
E sem nota (None)
ENTÃO status deve ser NOT_DONE
E not_done_substatus deve ser SKIPPED_JUSTIFIED
E skip_reason deve ser WORK
E skip_note deve ser None
```

---

## CENÁRIO 3: Skip com categoria FAMILY

**ID:** SCENARIO-HABIT-SKIP-001-003

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa skip com categoria FAMILY
E nota "Aniversário do filho"
ENTÃO status deve ser NOT_DONE
E not_done_substatus deve ser SKIPPED_JUSTIFIED
E skip_reason deve ser FAMILY
E skip_note deve ser "Aniversário do filho"
```

---

## CENÁRIO 4: Skip com categoria WEATHER

**ID:** SCENARIO-HABIT-SKIP-001-004

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa skip com categoria WEATHER
E nota "Chuva forte"
ENTÃO status deve ser NOT_DONE
E not_done_substatus deve ser SKIPPED_JUSTIFIED
E skip_reason deve ser WEATHER
E skip_note deve ser "Chuva forte"
```

---

## CENÁRIO 5: Re-skip muda categoria

**ID:** SCENARIO-HABIT-SKIP-001-005

```gherkin
DADO um HabitInstance já skipped com categoria WORK
QUANDO usuário executa skip novamente com categoria HEALTH
E nota "Descobri que estava doente"
ENTÃO skip_reason deve ser HEALTH (atualizado)
E skip_note deve ser "Descobri que estava doente"
E status continua NOT_DONE
E not_done_substatus continua SKIPPED_JUSTIFIED
```

---

## CENÁRIO 6: Validação de consistência após skip

**ID:** SCENARIO-HABIT-SKIP-001-006

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa skip com categoria EMERGENCY
ENTÃO sistema deve invocar validate_status_consistency()
E validação deve passar sem exceções
E campos devem estar consistentes:
  - status = NOT_DONE
  - not_done_substatus = SKIPPED_JUSTIFIED
  - skip_reason preenchido
  - done_substatus = None
```

---

## CENÁRIO 7: Erro - HabitInstance não existe

**ID:** SCENARIO-HABIT-SKIP-001-007

```gherkin
DADO ID de HabitInstance inexistente (99999)
QUANDO usuário tenta skip com categoria HEALTH
ENTÃO sistema deve lançar ValueError
COM mensagem "HabitInstance 99999 not found"
```

---

## CENÁRIO 8: Erro - Nota muito longa (>500 chars)

**ID:** SCENARIO-HABIT-SKIP-001-008

```gherkin
DADO um HabitInstance com status PENDING
E nota com 501 caracteres
QUANDO usuário tenta skip com categoria HEALTH
ENTÃO sistema deve lançar ValueError
COM mensagem "Skip note must be <= 500 characters"
```

---

## CENÁRIO 9: Erro - Timer ativo

**ID:** SCENARIO-HABIT-SKIP-001-009

```gherkin
DADO um HabitInstance com timer ativo (TimeLog sem end_time)
QUANDO usuário tenta skip com categoria HEALTH
ENTÃO sistema deve lançar ValueError
COM mensagem "Cannot skip with active timer"
```

---

## CENÁRIO 10: Erro - Instância já completada (DONE)

**ID:** SCENARIO-HABIT-SKIP-001-010

```gherkin
DADO um HabitInstance com status DONE
E done_substatus FULL
QUANDO usuário tenta skip com categoria HEALTH
ENTÃO sistema deve lançar ValueError
COM mensagem "Cannot skip completed instance"
```

---

## CENÁRIO 11: Skip limpa campos de completion

**ID:** SCENARIO-HABIT-SKIP-001-011

```gherkin
DADO um HabitInstance previamente DONE
E done_substatus = FULL
E completion_percentage = 95
QUANDO usuário re-marca como skip (após desfazer completion)
E categoria HEALTH
ENTÃO done_substatus deve ser None
E completion_percentage deve ser None
E status deve ser NOT_DONE
E skip_reason deve ser HEALTH
```

---

## CENÁRIO 12: Skip com todas as 8 categorias

**ID:** SCENARIO-HABIT-SKIP-001-012

```gherkin
DADO 8 HabitInstances diferentes
QUANDO usuário executa skip em cada uma com categoria diferente:
  - Instance 1: HEALTH
  - Instance 2: WORK
  - Instance 3: FAMILY
  - Instance 4: TRAVEL
  - Instance 5: WEATHER
  - Instance 6: LACK_RESOURCES
  - Instance 7: EMERGENCY
  - Instance 8: OTHER
ENTÃO todas devem ter status NOT_DONE
E not_done_substatus SKIPPED_JUSTIFIED
E skip_reason correspondente à categoria
```

---

## MAPEAMENTO SCENARIOS → TESTES

### Testes Unitários (test_services/test_habit_instance_skip.py)

| Cenário | Método de Teste                                    |
| ------- | -------------------------------------------------- |
| 1       | `test_br_habit_skip_001_skip_with_health_and_note` |
| 2       | `test_br_habit_skip_001_skip_work_without_note`    |
| 3       | `test_br_habit_skip_001_skip_family`               |
| 4       | `test_br_habit_skip_001_skip_weather`              |
| 5       | `test_br_habit_skip_001_reskip_changes_category`   |
| 6       | `test_br_habit_skip_001_validates_consistency`     |
| 7       | `test_br_habit_skip_001_error_instance_not_found`  |
| 8       | `test_br_habit_skip_001_error_note_too_long`       |
| 9       | `test_br_habit_skip_001_error_timer_active`        |
| 10      | `test_br_habit_skip_001_error_already_completed`   |
| 11      | `test_br_habit_skip_001_clears_completion_fields`  |
| 12      | `test_br_habit_skip_001_all_categories`            |

### Testes de Integração (test_integration/test_habit_skip_integration.py)

| Cenário | Método de Teste                                      |
| ------- | ---------------------------------------------------- |
| 1-5     | `test_br_habit_skip_001_end_to_end_skip`             |
| 6       | `test_br_habit_skip_001_integration_with_validation` |

---

## CRITÉRIOS DE ACEITAÇÃO

**TODOS os 12 cenários devem passar para considerar BR implementada.**

**Cobertura de código esperada:** 90%+ (habit_instance_service.py)

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - PRONTO PARA TDD]
