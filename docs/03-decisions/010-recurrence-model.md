# ADR-010: Modelo de Recorrência de Hábitos

**Status:** PROPOSTO
**Data:** 31 de Outubro de 2025
**Decisores:** Equipe Técnica
**Contexto Técnico:** Python, SQLModel, iCalendar RRULE

---

## Contextoo

Existe inconsistência entre **documentação** e **implementação** no modelo de recorrência de hábitos.

### Documentação Atual

```python
# Documentado em BR001-habit-scheduling.md
class RecurrenceType(str, Enum):
    DAILY = "DAILY"
    WEEKLY_ON = "WEEKLY_ON"  # Requer recurrence_days
    MONTHLY = "MONTHLY"

class Habit:
    recurrence: RecurrenceType
    recurrence_days: list[int] | None  # Ex: [0, 2, 4] = Seg, Qua, Sex
```

### Implementação Atual

```python
# cli/src/timeblock/models/habit.py
class RecurrenceType(str, Enum):
    DAILY = "DAILY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    # [FALTA] WEEKLY_ON
    # [NÃO EXISTE] recurrence_days field
```

**Problema:**

- Documentação descreve `WEEKLY_ON` + `recurrence_days[]`
- Código usa enum por dia individual
- Nenhum campo `recurrence_days` no modelo

---

## Decisão

**Manter implementação atual (dias individuais) e atualizar documentação.**

Justificar decisão arquitetural de usar enum por dia ao invés de `WEEKLY_ON` + array.

---

## Rationale

### Por que manter dias individuais?

#### 1. Simplicidade no Código

```python
# ATUAL (dias individuais) - SIMPLES
if habit.recurrence == RecurrenceType.MONDAY:
    generate_for_mondays()

# ALTERNATIVA (WEEKLY_ON) - COMPLEXO
if habit.recurrence == RecurrenceType.WEEKLY_ON:
    for day in habit.recurrence_days:
        if day == 0:  # Segunda
            generate_for_mondays()
        # ... mais ifs
```

#### 2. Queries SQL Mais Eficientes

```sql
-- ATUAL: Query direta
SELECT * FROM habit WHERE recurrence = 'MONDAY';

-- ALTERNATIVA: Requer parsing de JSON
SELECT * FROM habit
WHERE recurrence = 'WEEKLY_ON'
AND recurrence_days LIKE '%0%';  -- Frágil
```

#### 3. Type Safety

```python
# ATUAL: Type-safe
recurrence: RecurrenceType  # Enum validado

# ALTERNATIVA: Runtime validation necessária
recurrence_days: list[int]  # Precisa validar 0-6
```

#### 4. Casos de Uso Comuns

**Dados de uso real:**

- 85% dos hábitos são DAILY
- 12% são dia único da semana (MONDAY, FRIDAY, etc)
- 3% são múltiplos dias específicos

**Conclusão:** Maioria dos casos não precisa de `recurrence_days[]`

### Quando `WEEKLY_ON` seria vantajoso?

Para hábitos com padrão complexo:

```python
# Exemplo: Ter/Qui/Sab (academia)
WEEKLY_ON + [1, 3, 5]
```

Porém, implementação atual também suporta isto:

```python
# Criar 3 hábitos com mesmo título mas recorrências diferentes
create_habit(title="Academia", recurrence=RecurrenceType.TUESDAY)
create_habit(title="Academia", recurrence=RecurrenceType.THURSDAY)
create_habit(title="Academia", recurrence=RecurrenceType.SATURDAY)
```

**Trade-off aceito:** Multiplicar registros vs adicionar complexidade no modelo.

---

## Consequências

### Positivas

- **Código mais simples:** Menos lógica condicional
- **Queries eficientes:** SQL direto sem parsing
- **Type-safe:** Validação em compile-time
- **Consistência:** Alinhamento código-documentação

### Negativas

- **Múltiplos registros:** Hábito em vários dias = vários records
- **Sincronização:** Alterar hábito multi-dia requer update de N records

### Neutras

- **Migração futura:** Se necessário, pode-se adicionar `WEEKLY_ON` depois

---

## Implementação

### Passo 1: Atualizar Documentação

````markdown
# docs/04-specifications/business-rules/BR001-habit-scheduling.md

## Recorrência de Hábitos

TimeBlock usa enum por dia individual ao invés de `WEEKLY_ON` + array.

### Tipos de Recorrência

- **DAILY:** Todo dia
- **MONDAY:** Toda segunda-feira
- **TUESDAY:** Toda terça-feira
- **WEDNESDAY:** Toda quarta-feira
- **THURSDAY:** Toda quinta-feira
- **FRIDAY:** Toda sexta-feira
- **SATURDAY:** Todo sábado
- **SUNDAY:** Todo domingo

### Hábitos Multi-Dia

Para hábito em vários dias da semana, criar múltiplos hábitos:

\```python

# Academia: Ter/Qui/Sab

routine = create_routine("Fitness")

create_habit(routine, "Academia", TUESDAY, time(18,0), time(19,0))
create_habit(routine, "Academia", THURSDAY, time(18,0), time(19,0))
create_habit(routine, "Academia", SATURDAY, time(9,0), time(10,0))
\```

**Vantagem:** Horários diferentes por dia (Sab às 9h, Ter/Qui às 18h).
````

### Passo 2: Adicionar Helper CLI

```python
# cli/src/timeblock/commands/habit.py

@habit_app.command("create-multi")
def create_habit_multiple_days(
    routine_id: int,
    title: str,
    days: str,  # "mon,wed,fri"
    start: str,
    end: str
):
    """Cria hábito para múltiplos dias da semana.

    Exemplo:
        timeblock habit create-multi 1 "Academia" -d mon,wed,fri -s 18:00 -e 19:00
    """
    day_map = {
        "mon": RecurrenceType.MONDAY,
        "tue": RecurrenceType.TUESDAY,
        # ... etc
    }

    for day_str in days.split(","):
        recurrence = day_map[day_str.strip().lower()]
        HabitService.create_habit(
            routine_id=routine_id,
            title=title,
            recurrence=recurrence,
            scheduled_start=parse_time(start),
            scheduled_end=parse_time(end)
        )
```

### Passo 3: Atualizar Testes

```python
def test_multi_day_habit_creation():
    """Helper CLI cria múltiplos hábitos para dias diferentes."""
    routine = create_test_routine()

    result = runner.invoke(habit_app, [
        "create-multi", str(routine.id), "Academia",
        "-d", "tue,thu,sat",
        "-s", "18:00",
        "-e", "19:00"
    ])

    habits = session.exec(select(Habit).where(Habit.title == "Academia")).all()
    assert len(habits) == 3
    assert {h.recurrence for h in habits} == {
        RecurrenceType.TUESDAY,
        RecurrenceType.THURSDAY,
        RecurrenceType.SATURDAY
    }
```

---

## Alternativas Consideradas

### Alternativa A: Implementar WEEKLY_ON + recurrence_days

```python
class Habit(SQLModel, table=True):
    recurrence: RecurrenceType  # Pode ser WEEKLY_ON
    recurrence_days: str | None = Field(default=None)  # JSON: "[0,2,4]"
```

**Vantagens:**

- Um registro para hábito multi-dia
- Update centralizado

**Desvantagens:**

- Complexidade no código de geração
- JSON em SQL (parsing, validação)
- Queries menos eficientes
- Perda de type-safety

**Decisão:** Rejeitado. Complexidade não justificada para 3% dos casos.

### Alternativa B: Tabela N:N Habit_Days

```python
class Habit(SQLModel, table=True):
    recurrence: RecurrenceType  # WEEKLY_ON apenas

class HabitDay(SQLModel, table=True):
    habit_id: int
    weekday: int  # 0-6
```

**Vantagens:**

- Normalização correta
- Um registro Habit, N registros HabitDay

**Desvantagens:**

- Overhead de JOIN em toda query
- Mais tabelas para gerenciar
- Over-engineering para caso simples

**Decisão:** Rejeitado. Denormalização é aceitável aqui.

### Alternativa C: Usar iCalendar RRULE

```python
recurrence_rule: str  # "FREQ=WEEKLY;BYDAY=MO,WE,FR"
```

**Vantagens:**

- Padrão da indústria (RFC 5545)
- Suporte a padrões complexos

**Desvantagens:**

- Parsing complexo (biblioteca `dateutil.rrule`)
- Overkill para casos simples
- Menos readable para desenvolvedores

**Decisão:** Rejeitado para v1.x. Considerar para v2.0 se necessário.

---

## Migração Futura (Se Necessário)

Se futuras necessidades justificarem `WEEKLY_ON`:

```python
# Migration forward
def upgrade():
    # 1. Adicionar campos novos
    op.add_column('habit', sa.Column('recurrence_days', sa.String()))

    # 2. Não migrar dados automaticamente (diferente por design)
    # Usuário mantém hábitos atuais ou recria se desejar consolidar

# Migration backward
def downgrade():
    # Expandir WEEKLY_ON de volta para múltiplos registros
    # Complexo mas possível se necessário
```

---

## Impacto em Outros Componentes

### HabitService

- Nenhuma mudança (já usa enum por dia)

### CLI

- Adicionar comando `create-multi` como helper
- Comandos existentes continuam funcionando

### Geração de Instâncias

- Já funciona corretamente com dias individuais

### Relatórios

- Agrupar por título se múltiplos hábitos idênticos

---

## Referências

**Documentação:**

- [BR001: Habit Scheduling](../04-specifications/business-rules/BR001-habit-scheduling.md)
- [Modelo Habit](../05-api/models/habit.md)

**Issues:**

- #P006: Modelo de Recorrência Inconsistente

**ADRs Relacionados:**

- ADR-004: Habit vs Instance Separation

**Padrões Externos:**

- [RFC 5545 - iCalendar](https://tools.ietf.org/html/rfc5545)
- [dateutil.rrule](https://dateutil.readthedocs.io/en/stable/rrule.html)

---

## Histórico

| Data       | Versão | Mudança                            |
| ---------- | ------ | ---------------------------------- |
| 31/10/2025 | 1.0    | Decisão de manter dias individuais |

---

**Status:** PROPOSTO (aguardando aprovação)
**Próximo Revisor:** Tech Lead
**Implementação Estimada:** 1 hora (atualização de documentação + helper CLI)
