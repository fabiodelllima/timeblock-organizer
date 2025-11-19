# BR-HABIT-INSTANCE-STATUS-001: Cenários BDD

- **Referência:** BR-HABIT-INSTANCE-STATUS-001
- **Formato:** Gherkin (DADO/QUANDO/ENTÃO)
- **Total de Cenários:** 15

---

## FUNCIONALIDADE: Refatoração Status + Substatus

Como usuário do TimeBlock
Quero que o sistema rastreie detalhadamente completion e skip
Para analisar padrões comportamentais e impacto na rotina

---

## CENÁRIO 1: Timer stop com completion FULL (90-110%)

**ID:** SCENARIO-STATUS-001

```gherkin
DADO um HabitInstance com status PENDING
E meta de duração de 60 minutos
QUANDO usuário completa timer com 55 minutos (92%)
ENTÃO status deve ser DONE
E done_substatus deve ser FULL
E not_done_substatus deve ser None
E completion_percentage deve ser 92
```

---

## CENÁRIO 2: Timer stop com completion PARTIAL (<90%)

**ID:** SCENARIO-STATUS-002

```gherkin
DADO um HabitInstance com status PENDING
E meta de duração de 60 minutos
QUANDO usuário completa timer com 45 minutos (75%)
ENTÃO status deve ser DONE
E done_substatus deve ser PARTIAL
E not_done_substatus deve ser None
E completion_percentage deve ser 75
```

---

## CENÁRIO 3: Timer stop com completion OVERDONE (110-150%)

**ID:** SCENARIO-STATUS-003

```gherkin
DADO um HabitInstance com status PENDING
E meta de duração de 60 minutos
QUANDO usuário completa timer com 75 minutos (125%)
ENTÃO status deve ser DONE
E done_substatus deve ser OVERDONE
E not_done_substatus deve ser None
E completion_percentage deve ser 125
```

---

## CENÁRIO 4: Timer stop com completion EXCESSIVE (>150%)

**ID:** SCENARIO-STATUS-004

```gherkin
DADO um HabitInstance com status PENDING
E meta de duração de 60 minutos
QUANDO usuário completa timer com 100 minutos (167%)
ENTÃO status deve ser DONE
E done_substatus deve ser EXCESSIVE
E not_done_substatus deve ser None
E completion_percentage deve ser 167
```

---

## CENÁRIO 5: Skip com categoria (SKIPPED_JUSTIFIED)

**ID:** SCENARIO-STATUS-005

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa `habit skip 42 --category HEALTH`
ENTÃO status deve ser NOT_DONE
E not_done_substatus deve ser SKIPPED_JUSTIFIED
E skip_reason deve ser HEALTH
E done_substatus deve ser None
E completion_percentage deve ser None
```

---

## CENÁRIO 6: Skip com categoria e nota

**ID:** SCENARIO-STATUS-006

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa `habit skip 42 --category HEALTH --note "Gripe"`
ENTÃO status deve ser NOT_DONE
E not_done_substatus deve ser SKIPPED_JUSTIFIED
E skip_reason deve ser HEALTH
E skip_note deve ser "Gripe"
E done_substatus deve ser None
```

---

## CENÁRIO 7: Skip sem categoria (ERRO)

**ID:** SCENARIO-STATUS-007

```gherkin
DADO um HabitInstance com status PENDING
QUANDO usuário executa `habit skip 42` (sem --category)
ENTÃO sistema deve rejeitar com erro
E mensagem deve ser "Categoria obrigatória. Use --category"
E status deve permanecer PENDING
```

---

## CENÁRIO 8: Validação - DONE sem done_substatus (ERRO)

**ID:** SCENARIO-STATUS-008

```gherkin
DADO tentativa de criar HabitInstance
COM status = DONE
E done_substatus = None
QUANDO validar modelo
ENTÃO sistema deve lançar ValueError
COM mensagem "done_substatus obrigatório quando status=DONE"
```

---

## CENÁRIO 9: Validação - NOT_DONE sem not_done_substatus (ERRO)

**ID:** SCENARIO-STATUS-009

```gherkin
DADO tentativa de criar HabitInstance
COM status = NOT_DONE
E not_done_substatus = None
QUANDO validar modelo
ENTÃO sistema deve lançar ValueError
COM mensagem "not_done_substatus obrigatório quando status=NOT_DONE"
```

---

## CENÁRIO 10: Validação - Substatus mutuamente exclusivos (ERRO)

**ID:** SCENARIO-STATUS-010

```gherkin
DADO tentativa de criar HabitInstance
COM status = DONE
E done_substatus = FULL
E not_done_substatus = IGNORED
QUANDO validar modelo
ENTÃO sistema deve lançar ValueError
COM mensagem "not_done_substatus deve ser None quando status=DONE"
```

---

## CENÁRIO 11: Validação - Skip reason sem JUSTIFIED (ERRO)

**ID:** SCENARIO-STATUS-011

```gherkin
DADO tentativa de criar HabitInstance
COM status = NOT_DONE
E not_done_substatus = IGNORED
E skip_reason = HEALTH
QUANDO validar modelo
ENTÃO sistema deve lançar ValueError
COM mensagem "skip_reason só permitido com SKIPPED_JUSTIFIED"
```

---

## CENÁRIO 12: Validação - JUSTIFIED sem skip_reason (ERRO)

**ID:** SCENARIO-STATUS-012

```gherkin
DADO tentativa de criar HabitInstance
COM status = NOT_DONE
E not_done_substatus = SKIPPED_JUSTIFIED
E skip_reason = None
QUANDO validar modelo
ENTÃO sistema deve lançar ValueError
COM mensagem "skip_reason obrigatório para SKIPPED_JUSTIFIED"
```

---

## CENÁRIO 13: Property is_overdue - Evento PENDING atrasado

**ID:** SCENARIO-STATUS-013

```gherkin
DADO um HabitInstance com status PENDING
E scheduled_start = 08:00
E horário atual = 09:00 (1h atrasado)
QUANDO acessar property is_overdue
ENTÃO deve retornar True
```

---

## CENÁRIO 14: Property is_overdue - Evento PENDING no prazo

**ID:** SCENARIO-STATUS-014

```gherkin
DADO um HabitInstance com status PENDING
E scheduled_start = 10:00
E horário atual = 09:00 (1h antes)
QUANDO acessar property is_overdue
ENTÃO deve retornar False
```

---

## CENÁRIO 15: Property is_overdue - Evento DONE não é overdue

**ID:** SCENARIO-STATUS-015

```gherkin
DADO um HabitInstance com status DONE
E scheduled_start = 08:00
E horário atual = 09:00 (1h depois)
QUANDO acessar property is_overdue
ENTÃO deve retornar False
```

---

## CENÁRIO 16: Migração de dados - planned -> pending

**ID:** SCENARIO-STATUS-016

```gherkin
DADO banco de dados v1.3.0
COM HabitInstance status = "planned" (string)
QUANDO executar migração
ENTÃO status deve ser PENDING (enum)
E done_substatus deve ser None
E not_done_substatus deve ser None
```

---

## CENÁRIO 17: Migração de dados - completed -> done + FULL

**ID:** SCENARIO-STATUS-017

```gherkin
DADO banco de dados v1.3.0
COM HabitInstance status = "completed" (string)
QUANDO executar migração
ENTÃO status deve ser DONE (enum)
E done_substatus deve ser FULL (assumido)
E not_done_substatus deve ser None
```

---

## CENÁRIO 18: Migração de dados - skipped -> not_done + UNJUSTIFIED

**ID:** SCENARIO-STATUS-018

```gherkin
DADO banco de dados v1.3.0
COM HabitInstance status = "skipped" (string)
QUANDO executar migração
ENTÃO status deve ser NOT_DONE (enum)
E not_done_substatus deve ser SKIPPED_UNJUSTIFIED (assumido)
E done_substatus deve ser None
E skip_reason deve ser None
```

---

## MAPEAMENTO SCENARIOS → TESTES

### Testes Unitários (test_models/test_habit_instance_status.py)

| Cenário | Método de Teste                                              |
| ------- | ------------------------------------------------------------ |
| 1-4     | `test_br_status_001_timer_stop_calculates_substatus`         |
| 5-6     | `test_br_status_001_skip_with_category_sets_justified`       |
| 7       | `test_br_status_001_skip_without_category_rejected`          |
| 8       | `test_br_status_001_validation_done_requires_substatus`      |
| 9       | `test_br_status_001_validation_not_done_requires_substatus`  |
| 10      | `test_br_status_001_validation_substatus_mutually_exclusive` |
| 11-12   | `test_br_status_001_validation_skip_reason_consistency`      |
| 13-15   | `test_br_status_001_property_is_overdue`                     |

### Testes de Integração (test_integration/test_habit_instance_status_integration.py)

| Cenário | Método de Teste                                           |
| ------- | --------------------------------------------------------- |
| 1-4     | `test_br_status_001_timer_service_sets_correct_substatus` |
| 5-6     | `test_br_status_001_skip_service_creates_justified`       |
| 16-18   | `test_br_status_001_migration_preserves_data`             |

### Testes E2E (test_e2e/test_habit_instance_status_workflow.py)

| Cenário | Método de Teste                               |
| ------- | --------------------------------------------- |
| 1-7     | `test_br_status_001_complete_habit_lifecycle` |

---

## CRITÉRIOS DE ACEITAÇÃO

**TODOS os 18 cenários devem passar para considerar BR implementada.**

**Cobertura de código esperada:** 99%+

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - PRONTO PARA TDD]
