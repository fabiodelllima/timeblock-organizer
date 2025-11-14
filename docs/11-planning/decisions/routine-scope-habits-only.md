# Decisão: Routine Contém Apenas Habits

- **Status:** Decidido
- **Data:** 14 de Novembro de 2025
- **Contexto:** Definição de escopo e responsabilidades
- **Impacto:** Modelo de dados, CLI, relatórios

---

## Problema

Definir claramente o que uma Routine agrupa:

1. Apenas Habits?
2. Habits + Tasks?
3. Habits + Tasks + Events?

---

## Decisão: Routine = Container de Habits

### Regra Fundamental

```python
class Routine:
    """
    Rotina agrupa APENAS Habits recorrentes.
    Tasks são independentes (não pertencem a rotinas).
    """
    habits: list[Habit]  # ✓ Sim
    tasks: list[Task]    # ✗ Não
```

---

## Justificativa

### 1. Semântica Clara

#### **Routine = Padrão recorrente**

- Rotina Matinal: Academia, Meditação, Café da manhã (EVERYDAY)
- Rotina Trabalho: Reunião diária, Deep work, Revisão (WEEKDAYS)
- Rotina Fim de Semana: Leitura, Família, Hobbies (WEEKENDS)

#### **Task = Evento pontual único**

- Dentista (25/11/2025 14:30) - não faz parte de rotina
- Reunião cliente X (30/11/2025 10:00) - não faz parte de rotina
- Compras mercado (26/11/2025 18:00) - não faz parte de rotina

### 2. Simplicidade Arquitetural

```python
# SIMPLES (decisão atual)
Routine → Habits (recorrentes)
Tasks (independentes, pontuais)

# COMPLEXO (alternativa rejeitada)
Routine → Habits + Tasks
  - Como diferenciar task recorrente de única?
  - Task pertence a múltiplas rotinas?
  - Task pontual "herda" rotina?
```

### 3. UX Intuitivo

```bash
# Criar rotina (apenas habits)
routine create "Rotina Matinal"
habit create --title "Academia" --start 07:00 --end 08:30

# Criar task (independente)
task create --title "Dentista" --datetime "2025-11-25 14:30"

# Listar rotina (apenas habits)
routine list
# Rotinas:
# 1. Rotina Matinal (5 habits) [ATIVA]

# Listar tasks (separado)
task list
# Tasks Pendentes:
# 1. Dentista (25/11 14:30)
```

### 4. Routine Activation (Apenas UMA Ativa)

**Apenas UMA rotina ativa por vez:**

- Rotina ativa define contexto padrão para `habit` commands
- Tasks não dependem de rotina ativa
- Switching entre rotinas é simples e previsível

```bash
routine activate "Rotina Trabalho"
# [INFO] Rotina "Rotina Matinal" desativada
# [OK] Rotina "Rotina Trabalho" ativada

habit list
# Lista apenas habits de "Rotina Trabalho"

task list
# Tasks continuam visíveis (independentes de rotina)
```

---

## Modelo de Dados

### Routine (Container de Habits)

```python
class Routine(SQLModel, table=True):
    """Rotina agrupa habits recorrentes."""

    __tablename__ = "routines"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=200)
    is_active: bool = Field(default=False)  # Apenas UMA ativa
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Soft delete
    deleted_at: datetime | None = Field(default=None)

    # Relacionamento
    habits: list["Habit"] = Relationship(back_populates="routine")
```

### Habit (Pertence a Routine)

```python
class Habit(SQLModel, table=True):
    """Hábito recorrente pertence a UMA rotina."""

    __tablename__ = "habits"

    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routines.id")
    title: str = Field(min_length=1, max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: str  # EVERYDAY, WEEKDAYS, WEEKENDS, etc

    # Soft delete
    is_active: bool = Field(default=True)
    deleted_at: datetime | None = Field(default=None)

    # Relacionamento
    routine: Routine = Relationship(back_populates="habits")
    instances: list["HabitInstance"] = Relationship(back_populates="habit")
```

### Task (Independente)

```python
class Task(SQLModel, table=True):
    """Task pontual NÃO pertence a rotina."""

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    scheduled_datetime: datetime
    status: TaskStatus

    # SEM relacionamento com Routine!
    # routine_id = None  ✗ Não existe
```

---

## Constraint: Apenas UMA Rotina Ativa

### Lógica de Ativação

```python
def activate_routine(routine_id: int, session: Session) -> Routine:
    """Ativa rotina e desativa todas as outras."""

    # Desativar todas
    session.query(Routine).update({"is_active": False})

    # Ativar escolhida
    routine = session.get(Routine, routine_id)
    routine.is_active = True

    session.commit()
    return routine
```

### Validação no Create

```python
def create_routine(name: str, session: Session, activate: bool = True) -> Routine:
    """Cria rotina. Por padrão, ativa automaticamente."""

    routine = Routine(name=name)
    session.add(routine)

    if activate:
        # Desativa outras
        session.query(Routine).update({"is_active": False})
        routine.is_active = True

    session.commit()
    return routine
```

---

## CLI Outputs

### Routine List (Indica Qual Está Ativa)

```bash
timeblock routine list

Rotinas:
┌────┬──────────────────┬────────┬──────────┐
│ ID │ Nome             │ Hábitos│ Status   │
├────┼──────────────────┼────────┼──────────┤
│ 1  │ Rotina Matinal   │ 5      │ [ATIVA]  │
│ 2  │ Rotina Trabalho  │ 8      │ Inativa  │
│ 3  │ Rotina Fim Sem.  │ 3      │ Inativa  │
└────┴──────────────────┴────────┴──────────┘
```

### Habit List (Contexto: Rotina Ativa)

```bash
timeblock habit list

Hábitos da Rotina Ativa: Rotina Matinal
┌────┬───────────────┬─────────────────┬──────────────┐
│ ID │ Título        │ Horário         │ Recorrência  │
├────┼───────────────┼─────────────────┼──────────────┤
│ 42 │ Academia      │ 07:00 → 08:30   │ WEEKDAYS     │
│ 43 │ Meditação     │ 20:00 → 20:15   │ EVERYDAY     │
│ 44 │ Leitura       │ 21:00 → 22:00   │ EVERYDAY     │
└────┴───────────────┴─────────────────┴──────────────┘

# Flags
timeblock habit list --all          # Todos (ativos + inativos)
timeblock habit list --inactive     # Apenas inativos
```

### Routine Activate (Muda Contexto)

```bash
timeblock routine activate 2

[INFO] Rotina "Rotina Matinal" desativada
[OK] Rotina "Rotina Trabalho" ativada

Agora a rotina ativa é: Rotina Trabalho (8 hábitos)

# habit list agora mostra hábitos de "Rotina Trabalho"
timeblock habit list

Hábitos da Rotina Ativa: Rotina Trabalho
┌────┬───────────────┬─────────────────┬──────────────┐
│ ID │ Título        │ Horário         │ Recorrência  │
├────┼───────────────┼─────────────────┼──────────────┤
│ 50 │ Daily Standup │ 09:00 → 09:15   │ WEEKDAYS     │
│ 51 │ Deep Work     │ 10:00 → 12:00   │ WEEKDAYS     │
│ 52 │ Code Review   │ 16:00 → 17:00   │ WEEKDAYS     │
└────┴───────────────┴─────────────────┴──────────────┘
```

### Task List (Independente de Routine)

```bash
# Tasks NÃO mudam com routine activate
timeblock task list

Tasks Pendentes:
┌────┬────────────────┬─────────────────┬──────────┐
│ ID │ Título         │ Data/Hora       │ Status   │
├────┼────────────────┼─────────────────┼──────────┤
│ 20 │ Dentista       │ 25/11 14:30     │ Pendente │
│ 21 │ Reunião X      │ 26/11 10:00     │ Pendente │
└────┴────────────────┴─────────────────┴──────────┘

# Não importa qual rotina está ativa, tasks são as mesmas
```

---

## Alternativas Consideradas e Rejeitadas

### Alternativa A: Routine Contém Tasks

**Problemas:**

- Task pontual não se repete, não faz sentido em "rotina"
- Confusion semântica (rotina = padrão, task = único)
- Complexidade: task pertence a qual rotina?

### Alternativa B: Task Como Habit de 1 Dia

**Problemas:**

- Abuso de conceito (Habit = recorrente)
- Modelo complexo: `recurrence = "ONCE"`?
- Queries confusas: filtrar habits verdadeiros vs tasks

### Alternativa C: Routine Hierárquica

**Exemplo:**

```terminal
Routine Semana
  ├─ Routine Matinal (sub-rotina)
  ├─ Routine Trabalho (sub-rotina)
  └─ Routine Noite (sub-rotina)
```

**Problemas:**

- Over-engineering para MVP
- Complexidade na ativação (ativar pai? filho?)
- UX confusa para criar/editar

**Decisão:** KISS (Keep It Simple) - Routine flat, apenas habits.

---

## Implementação MVP

### Fase 1 (Imediato)

- [x] Routine contém apenas Habits
- [x] Task independente (sem routine_id)
- [x] Constraint: apenas UMA routine ativa
- [x] routine activate desativa outras

### Fase 2 (Pós-MVP)

- [ ] Routine templates (pré-configuradas)
- [ ] Routine clone (duplicar com habits)
- [ ] Routine archive (soft delete em massa)
- [ ] Routine stats (agregação de todos habits)

---

## Business Rules Relacionadas

**A criar:**

- BR-ROUTINE-001: Single Active Constraint
- BR-ROUTINE-002: Habit Belongs to Routine
- BR-ROUTINE-003: Task Independent of Routine
- BR-ROUTINE-004: Activation Cascade (desativa outras)

---

## Referências

- Modelo: `src/timeblock/models/routine.py`
- Modelo: `src/timeblock/models/habit.py`
- Modelo: `src/timeblock/models/task.py`
- Service: `src/timeblock/services/routine_service.py`
- CLI: `src/timeblock/commands/routine.py`

---

**Próxima Revisão:** Após implementação MVP

**Status:** DECIDIDO
