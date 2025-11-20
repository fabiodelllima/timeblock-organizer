# BR-TIMER-006: Cenários BDD

- **Referência:** BR-TIMER-006
- **Formato:** Gherkin (DADO/QUANDO/ENTÃO)
- **Total de Cenários:** 8

---

## FUNCIONALIDADE: Cálculo Automático de Substatus ao Parar Timer

Como usuário do TimeBlock

Quero que o sistema calcule automaticamente substatus ao parar timer

Para receber feedback imediato de performance sem entrada manual

---

## CENÁRIO 1: Timer stop com completion PARTIAL (<90%)

**ID:** SCENARIO-TIMER-006-001

```gherkin
DADO um HabitInstance com meta de 60 minutos (08:00-09:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 08:45 (45 minutos = 75%)
ENTÃO status deve ser DONE
E done_substatus deve ser PARTIAL
E completion_percentage deve ser 75
E not_done_substatus deve ser None
E TimeLog.duration_seconds deve ser 2700 (45min)
```

---

## CENÁRIO 2: Timer stop com completion FULL (90-110%) - Limite inferior

**ID:** SCENARIO-TIMER-006-002

```gherkin
DADO um HabitInstance com meta de 60 minutos (08:00-09:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 08:54 (54 minutos = 90%)
ENTÃO status deve ser DONE
E done_substatus deve ser FULL
E completion_percentage deve ser 90
E not_done_substatus deve ser None
```

---

## CENÁRIO 3: Timer stop com completion FULL (90-110%) - Centro

**ID:** SCENARIO-TIMER-006-003

```gherkin
DADO um HabitInstance com meta de 60 minutos (08:00-09:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 09:00 (60 minutos = 100%)
ENTÃO status deve ser DONE
E done_substatus deve ser FULL
E completion_percentage deve ser 100
E not_done_substatus deve ser None
```

---

## CENÁRIO 4: Timer stop com completion FULL (90-110%) - Limite superior

**ID:** SCENARIO-TIMER-006-004

```gherkin
DADO um HabitInstance com meta de 60 minutos (08:00-09:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 09:06 (66 minutos = 110%)
ENTÃO status deve ser DONE
E done_substatus deve ser FULL
E completion_percentage deve ser 110
E not_done_substatus deve ser None
```

---

## CENÁRIO 5: Timer stop com completion OVERDONE (110-150%)

**ID:** SCENARIO-TIMER-006-005

```gherkin
DADO um HabitInstance com meta de 60 minutos (08:00-09:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 09:18 (78 minutos = 130%)
ENTÃO status deve ser DONE
E done_substatus deve ser OVERDONE
E completion_percentage deve ser 130
E not_done_substatus deve ser None
```

---

## CENÁRIO 6: Timer stop com completion EXCESSIVE (>150%)

**ID:** SCENARIO-TIMER-006-006

```gherkin
DADO um HabitInstance com meta de 60 minutos (08:00-09:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 10:00 (120 minutos = 200%)
ENTÃO status deve ser DONE
E done_substatus deve ser EXCESSIVE
E completion_percentage deve ser 200
E not_done_substatus deve ser None
```

---

## CENÁRIO 7: Validação de consistência após stop

**ID:** SCENARIO-TIMER-006-007

```gherkin
DADO um HabitInstance com timer ativo
QUANDO usuário para timer
ENTÃO sistema deve invocar validate_status_consistency()
E validação deve passar sem exceções
E campos devem estar consistentes:
  - status = DONE
  - done_substatus preenchido
  - not_done_substatus = None
  - skip_reason = None
```

---

## CENÁRIO 8: Timer stop sem timer ativo (ERRO)

**ID:** SCENARIO-TIMER-006-008

```gherkin
DADO um HabitInstance sem timer ativo
QUANDO usuário tenta parar timer
ENTÃO sistema deve lançar ValueError
COM mensagem "Timer não está ativo para HabitInstance {id}"
E status do HabitInstance não deve mudar
```

---

## CENÁRIO 9: Timer stop com meta muito curta (edge case)

**ID:** SCENARIO-TIMER-006-009

```gherkin
DADO um HabitInstance com meta de 5 minutos (08:00-08:05)
E timer iniciado às 08:00
QUANDO usuário para timer às 08:03 (3 minutos = 60%)
ENTÃO status deve ser DONE
E done_substatus deve ser PARTIAL
E completion_percentage deve ser 60
E cálculo deve ser preciso mesmo com duração curta
```

---

## CENÁRIO 10: Timer stop com meta muito longa (edge case)

**ID:** SCENARIO-TIMER-006-010

```gherkin
DADO um HabitInstance com meta de 180 minutos (08:00-11:00)
E timer iniciado às 08:00
QUANDO usuário para timer às 10:45 (165 minutos = 92%)
ENTÃO status deve ser DONE
E done_substatus deve ser FULL
E completion_percentage deve ser 92
E cálculo deve ser preciso mesmo com duração longa
```

---

## MAPEAMENTO SCENARIOS → TESTES

### Testes Unitários (test_services/test_timer_service_substatus.py)

| Cenário | Método de Teste                                |
| ------- | ---------------------------------------------- |
| 1       | `test_br_timer_006_stop_calculates_partial`    |
| 2-4     | `test_br_timer_006_stop_calculates_full_range` |
| 5       | `test_br_timer_006_stop_calculates_overdone`   |
| 6       | `test_br_timer_006_stop_calculates_excessive`  |
| 7       | `test_br_timer_006_validates_consistency`      |
| 8       | `test_br_timer_006_error_no_active_timer`      |
| 9-10    | `test_br_timer_006_edge_cases_duration`        |

### Testes de Integração (test_integration/test_timer_substatus_integration.py)

| Cenário | Método de Teste                                      |
| ------- | ---------------------------------------------------- |
| 1-6     | `test_br_timer_006_end_to_end_substatus_calculation` |
| 7       | `test_br_timer_006_integration_with_habit_instance`  |

---

## CRITÉRIOS DE ACEITAÇÃO

**TODOS os 10 cenários devem passar para considerar BR implementada.**

**Cobertura de código esperada:** 95%+ (timer_service.py)

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - PRONTO PARA TDD]
