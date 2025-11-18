# GAP ANALYSIS - MVP RELEASE

Data: 2025-11-17

MVP Target: 17 BRs essenciais

## RESUMO EXECUTIVO

| Domínio        | BRs MVP   | Status                     | % Completo |
| -------------- | --------- | -------------------------- | ---------- |
| ROUTINE        | 4/4       | [OK] COMPLETO              | 100%       |
| TIMER          | 4/4       | [OK] COMPLETO              | 100%       |
| HABIT-INSTANCE | 4/4       | [BLOCKER] INCOMPLETO       | 25%        |
| STREAK         | 3/3       | [BLOCKER] NÃO IMPLEMENTADO | 0%         |
| HABIT-SKIP     | 2/2       | [BLOCKER] INCOMPLETO       | 50%        |
| **TOTAL**      | **17/17** | **PARCIAL**                | **55%**    |

---

## DETALHAMENTO

### [OK] ROUTINE (4/4 BRs) - 100%

- [OK] BR-ROUTINE-001: Single active routine
- [OK] BR-ROUTINE-002: Habit belongs to routine
- [OK] BR-ROUTINE-003: Task independent
- [OK] BR-ROUTINE-004: Activation cascade

**Status:** Implementado e testado

**Arquivos:** routine.py, routine_service.py, commands/routine.py

---

### [OK] TIMER (4/4 BRs) - 100%

- [OK] BR-TIMER-001: Single active timer
- [OK] BR-TIMER-002: State transitions
- [OK] BR-TIMER-004: Manual log
- [OK] BR-TIMER-005: Completion percentage

**Status:** Implementado e testado (6 testes passando)

**Arquivos:** time_log.py, timer_service.py, commands/timer.py

---

### [BLOCKER] HABIT-INSTANCE (4/4 BRs) - 25%

**Implementado:**

- [OK] Enum HabitInstanceStatus (PLANNED, IN_PROGRESS, COMPLETED, PAUSED, SKIPPED)

**FALTA IMPLEMENTAR:**

- [ ] BR-HABIT-INSTANCE-001: Status transitions (validação)
- [ ] BR-HABIT-INSTANCE-002: **Substatus field** (CAMPO FALTANDO)
- [ ] BR-HABIT-INSTANCE-003: Completion thresholds
- [ ] BR-HABIT-INSTANCE-004: Streak calculation

**Problema crítico:**

- Modelo HabitInstance NÃO TEM campo `substatus`
- Precisa adicionar: `substatus: str | None = None`
- Precisa adicionar enums de substatus por status

**Arquivos:** habit_instance.py (precisa refatoração)

---

### [BLOCKER] STREAK (3/3 BRs) - 0%

**FALTA IMPLEMENTAR:**

- [ ] BR-STREAK-001: Calculation algorithm
- [ ] BR-STREAK-002: Break conditions
- [ ] BR-STREAK-003: Maintain conditions

**Problema crítico:**

- NÃO EXISTE modelo Streak
- NÃO EXISTE StreakService
- Lógica deve estar em HabitInstanceService

**Ação:** Implementar streak tracking dentro de Habit/HabitInstance

---

### [BLOCKER] HABIT-SKIP (2/2 BRs) - 50%

**Implementado:**

- [OK] Enum SKIPPED em HabitInstanceStatus

**FALTA IMPLEMENTAR:**

- [ ] BR-HABIT-SKIP-001: Enum skip_category (NONE definido)
- [ ] BR-HABIT-SKIP-002: Skip fields (skip_reason, skip_notes)

**Problema:**

- Modelo tem SKIPPED mas sem campos de categoria/razão
- Precisa adicionar campos ao HabitInstance

**Arquivos:** habit_instance.py (precisa campos adicionais)

---

## TRABALHO RESTANTE PARA MVP

### Sprint 1: HabitInstance Refatoração

**Estimativa:** 2-3 dias

**Prioridade:** CRÍTICA

1. Adicionar campo `substatus` ao HabitInstance
2. Criar enums de substatus:
   - CompletedSubstatus (DONE, PARTIAL, EXCEEDED, OVERDONE)
   - SkippedSubstatus (ILLNESS, EMERGENCY, TRAVEL, WEATHER, PERSONAL, PLANNED_REST)
3. Adicionar campos skip:
   - skip_category: SkippedSubstatus | None
   - skip_reason: str | None
   - skip_notes: str | None
4. Implementar BR-HABIT-INSTANCE-001: Validar transições
5. Implementar BR-HABIT-INSTANCE-003: Thresholds

### Sprint 2: Streak Implementation

**Estimativa:** 2-3 dias

**Prioridade:** CRÍTICA

1. Adicionar campos ao Habit:
   - current_streak: int = 0
   - best_streak: int = 0
   - last_completed: date | None
2. Implementar StreakService ou lógica em HabitInstanceService
3. Implementar BR-STREAK-001: Algorithm
4. Implementar BR-STREAK-002: Break conditions
5. Implementar BR-STREAK-003: Maintain conditions

### Sprint 3: Testes E2E

**Estimativa:** 1-2 dias

**Prioridade:** ALTA

1. Testes de status transitions
2. Testes de streak calculation
3. Testes de skip workflow
4. Validação completa MVP

---

## ESTIMATIVA TOTAL

**Tempo estimado:** 5-8 dias de desenvolvimento

**BRs faltantes:** 9/17 (53%)

**Bloqueadores críticos:** 2 (HabitInstance refatoração, Streak implementation)

---

## PRÓXIMOS PASSOS IMEDIATOS

1. [ ] Criar branch: feature/mvp-habit-instance-substatus
2. [ ] Implementar campos substatus em HabitInstance
3. [ ] Migração de banco (adicionar colunas)
4. [ ] Testes unitários para novas BRs
5. [ ] Documentar em CHANGELOG

---

## RISCOS

- **Alto:** Mudanças no modelo HabitInstance podem quebrar testes existentes
- **Médio:** Streak calculation precisa considerar timezone/gaps
- **Baixo:** Skip categories podem precisar ajuste após uso real

---

**Conclusão:** MVP está ~55% completo. Faltam 2 sprints críticas antes de release.
