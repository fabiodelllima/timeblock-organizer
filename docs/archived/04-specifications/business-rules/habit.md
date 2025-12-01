# Business Rules: HABIT

## Visão Geral

Habits são templates de eventos recorrentes vinculados a uma Routine. Definem horários fixos e padrões de recorrência para atividades regulares.

---

## BR-HABIT-001: Title Validation

**Descrição:** Título do habit deve ser válido e dentro dos limites.

**Regras:**

1. Title não pode ser vazio (após trim)
2. Title não pode exceder 200 caracteres
3. Title deve ter whitespace removido (trim automático)

**Validação:**

- Empty string após trim → ValueError
- Comprimento > 200 → ValueError
- Trim aplicado automaticamente

**Implementação:**

- `habit_service.py::create_habit()`
- `habit_service.py::update_habit()`

**Testes:**

- `test_br_habit_001_empty_title_rejected`
- `test_br_habit_001_long_title_rejected`
- `test_br_habit_001_whitespace_trimmed`

---

## BR-HABIT-002: Time Range Validation

**Descrição:** Horário de início deve ser antes do horário de término.

**Regras:**

1. scheduled_start DEVE ser estritamente menor que scheduled_end
2. Horários iguais são inválidos (sem eventos de duração zero)

**Validação:**

- start >= end → ValueError

**Implementação:**

- `habit_service.py::create_habit()`
- `habit_service.py::update_habit()`

**Testes:**

- `test_br_habit_002_start_before_end_required`
- `test_br_habit_002_equal_times_rejected`
- `test_br_habit_002_end_before_start_rejected`

---

## BR-HABIT-003: Routine Association

**Descrição:** Habit DEVE estar vinculado a uma Routine existente.

**Regras:**

1. routine_id é obrigatório (campo não-nullable)
2. Routine referenciada DEVE existir (FK constraint)
3. Delete de Routine com Habits é bloqueado (RESTRICT)

**Validação:**

- routine_id null → Database constraint error
- routine_id inexistente → Foreign key error

**Implementação:**

- `habit.py::routine_id` Field (FK com RESTRICT)
- Database constraint enforcement

**Testes:**

- `test_br_habit_003_requires_routine_id`
- `test_br_habit_003_invalid_routine_rejected`
- `test_br_habit_003_routine_delete_blocked`

---

## BR-HABIT-004: Recurrence Pattern

**Descrição:** Habit deve ter padrão de recorrência válido.

**Regras:**

1. Recurrence DEVE ser um dos valores do enum Recurrence
2. Padrões suportados:
   - Dias individuais: MONDAY-SUNDAY
   - Grupos: WEEKDAYS (seg-sex), WEEKENDS (sáb-dom), EVERYDAY

**Validação:**

- Valor inválido → Pydantic validation error

**Implementação:**

- `habit.py::Recurrence` enum
- Pydantic model validation

**Testes:**

- `test_br_habit_004_valid_recurrence_accepted`
- `test_br_habit_004_invalid_recurrence_rejected`

---

## BR-HABIT-005: Optional Color

**Descrição:** Habit pode ter cor opcional para visualização.

**Regras:**

1. Color é opcional (pode ser None)
2. Se presente, deve ser string válida (max 7 chars para hex #RRGGBB)

**Validação:**

- Color > 7 chars → Database constraint error

**Implementação:**

- `habit.py::color` Field (opcional, max_length=7)

**Testes:**

- `test_br_habit_005_color_optional`
- `test_br_habit_005_valid_hex_color`

---

## Resumo de Validações

| BR  | Validação        | Momento       | Handler     |
| --- | ---------------- | ------------- | ----------- |
| 001 | Title não vazio  | Create/Update | Service     |
| 001 | Title max 200    | Create/Update | Service     |
| 002 | Start < End      | Create/Update | Service     |
| 003 | Routine exists   | Create        | Database FK |
| 004 | Valid Recurrence | Create/Update | Pydantic    |
| 005 | Color max 7      | Create/Update | Database    |

---

**Última atualização:** 2025-11-16

**Status:** Mapeado do código existente - Aguardando testes
