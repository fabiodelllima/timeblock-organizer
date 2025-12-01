# MVP Scope Validation

**Gerado em:** 2025-11-15

## CRITERIO: BR ESSENCIAL PARA MVP?

Uma BR e essencial para MVP se:
1. Bloqueia funcionalidade core do sistema
2. Garante integridade de dados criticos
3. Implementa regra de negocio fundamental

---

## HABIT-SKIP (4 BRs)

| BR | Essencial? | Justificativa |
|----|------------|---------------|
| BR-HABIT-SKIP-001 | [MVP] | Categorias estruturam skip - core |
| BR-HABIT-SKIP-002 | [MVP] | Campos necessarios para persistir skip |
| BR-HABIT-SKIP-003 | [NICE] | Prazo 24h pode ser fase 2 |
| BR-HABIT-SKIP-004 | [NICE] | CLI interativo pode ser simplificado |

**MVP:** 2/4 (50%)
**Nice-to-Have:** 2/4

---

## HABIT-INSTANCE (6 BRs)

| BR | Essencial? | Justificativa |
|----|------------|---------------|
| BR-HABIT-INSTANCE-001 | [MVP] | Transicoes de status - CORE |
| BR-HABIT-INSTANCE-002 | [MVP] | Substatus estrutura dados - CORE |
| BR-HABIT-INSTANCE-003 | [MVP] | Thresholds definem DONE/PARTIAL |
| BR-HABIT-INSTANCE-004 | [MVP] | Streak calculation - feature core |
| BR-HABIT-INSTANCE-005 | [NICE] | Auto-IGNORED pode ser manual MVP |
| BR-HABIT-INSTANCE-006 | [NICE] | Analise impacto e fase 2 |

**MVP:** 4/6 (67%)
**Nice-to-Have:** 2/6

---

## STREAK (4 BRs)

| BR | Essencial? | Justificativa |
|----|------------|---------------|
| BR-STREAK-001 | [MVP] | Algoritmo calculo - CORE |
| BR-STREAK-002 | [MVP] | Condicoes break - CORE |
| BR-STREAK-003 | [MVP] | Condicoes maintain - CORE |
| BR-STREAK-004 | [NICE] | Feedback diferenciado fase 2 |

**MVP:** 3/4 (75%)
**Nice-to-Have:** 1/4

---

## ROUTINE (4 BRs)

| BR | Essencial? | Justificativa |
|----|------------|---------------|
| BR-ROUTINE-001 | [MVP] | Single active - integridade dados |
| BR-ROUTINE-002 | [MVP] | Habit belongs routine - FK |
| BR-ROUTINE-003 | [MVP] | Task independent - diferenciacao |
| BR-ROUTINE-004 | [MVP] | Activation cascade - UX core |

**MVP:** 4/4 (100%)
**Nice-to-Have:** 0/4

---

## TIMER (6 BRs)

| BR | Essencial? | Justificativa |
|----|------------|---------------|
| BR-TIMER-001 | [MVP] | Single active timer - integridade |
| BR-TIMER-002 | [MVP] | State transitions - CORE |
| BR-TIMER-003 | [NICE] | Multiple sessions pode ser fase 2 |
| BR-TIMER-004 | [MVP] | Manual log - fallback essencial |
| BR-TIMER-005 | [MVP] | Completion calc - feature core |
| BR-TIMER-006 | [NICE] | Pause tracking fase 2 |

**MVP:** 4/6 (67%)
**Nice-to-Have:** 2/6

---

## RESUMO MVP

| Dominio | Total | MVP | Nice | % MVP |
|---------|-------|-----|------|-------|
| HABIT-SKIP | 4 | 2 | 2 | 50% |
| HABIT-INSTANCE | 6 | 4 | 2 | 67% |
| STREAK | 4 | 3 | 1 | 75% |
| ROUTINE | 4 | 4 | 0 | 100% |
| TIMER | 6 | 4 | 2 | 67% |
| **TOTAL** | **24** | **17** | **7** | **71%** |

---

## DECISAO: ESCOPO MVP

### BRs ESSENCIAIS MVP (17):
```
HABIT-SKIP:
- BR-HABIT-SKIP-001 (Enum categorias)
- BR-HABIT-SKIP-002 (Campos)

HABIT-INSTANCE:
- BR-HABIT-INSTANCE-001 (Status transitions)
- BR-HABIT-INSTANCE-002 (Substatus)
- BR-HABIT-INSTANCE-003 (Thresholds)
- BR-HABIT-INSTANCE-004 (Streak calculation)

STREAK:
- BR-STREAK-001 (Algorithm)
- BR-STREAK-002 (Break conditions)
- BR-STREAK-003 (Maintain conditions)

ROUTINE:
- BR-ROUTINE-001 (Single active)
- BR-ROUTINE-002 (Habit belongs)
- BR-ROUTINE-003 (Task independent)
- BR-ROUTINE-004 (Activation cascade)

TIMER:
- BR-TIMER-001 (Single active)
- BR-TIMER-002 (State transitions)
- BR-TIMER-004 (Manual log)
- BR-TIMER-005 (Completion calc)
```

### BRs FASE 2 (7):
```
HABIT-SKIP:
- BR-HABIT-SKIP-003 (Prazo 24h)
- BR-HABIT-SKIP-004 (CLI interativo)

HABIT-INSTANCE:
- BR-HABIT-INSTANCE-005 (Auto-ignored 48h)
- BR-HABIT-INSTANCE-006 (Impact analysis)

STREAK:
- BR-STREAK-004 (Feedback diferenciado)

TIMER:
- BR-TIMER-003 (Multiple sessions)
- BR-TIMER-006 (Pause tracking)
```

---

## RECOMENDACAO

**[APROVADO]** Implementar 17 BRs MVP primeiro.

**Ordem sugerida:**
1. ROUTINE (4 BRs) - base estrutural
2. TIMER (4 BRs) - tracking basico
3. HABIT-INSTANCE (4 BRs) - estados core
4. STREAK (3 BRs) - motivacao
5. HABIT-SKIP (2 BRs) - flexibilidade

**Fase 2:** Adicionar 7 BRs nice-to-have apos MVP estavel.
