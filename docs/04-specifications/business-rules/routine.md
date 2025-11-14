# Business Rules: Routine

- **Domínio:** Routine
- **Área:** Gerenciamento de Rotinas e Contexto
- **Última atualização:** 14 de Novembro de 2025

---

## Índice

- [BR-ROUTINE-001: Single Active Constraint](#br-routine-001)
- [BR-ROUTINE-002: Habit Belongs to Routine](#br-routine-002)
- [BR-ROUTINE-003: Task Independent of Routine](#br-routine-003)
- [BR-ROUTINE-004: Activation Cascade](#br-routine-004)

---

## BR-ROUTINE-001: Single Active Constraint

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [routine-scope-habits-only.md](../../11-planning/decisions/routine-scope-habits-only.md)

### Descrição

Apenas UMA rotina pode estar ativa por vez. Ativar uma rotina desativa automaticamente todas as outras.

### Constraint de Banco

```sql
-- Constraint de check (soft enforcement)
CREATE TABLE routines (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,

    -- Constraint garante apenas 1 ativa
    -- (implementado via trigger ou validação em código)
);

-- Trigger exemplo (SQLite)
CREATE TRIGGER enforce_single_active_routine
BEFORE UPDATE ON routines
WHEN NEW.is_active = 1
BEGIN
    UPDATE routines SET is_active = 0 WHERE id != NEW.id;
END;
```

### Lógica de Ativação

```python
def activate_routine(routine_id: int, session: Session) -> Routine:
    """Ativa rotina e desativa todas as outras."""

    # 1. Desativar TODAS as rotinas
    session.query(Routine).update({"is_active": False})

    # 2. Ativar apenas a escolhida
    routine = session.get(Routine, routine_id)
    if routine is None:
        raise ValueError(f"Routine {routine_id} não encontrada")

    routine.is_active = True
    session.commit()

    return routine
```

### Critérios de Aceitação

- [ ] Apenas 1 rotina com `is_active = True` por vez
- [ ] Ativar rotina A desativa automaticamente rotina B
- [ ] Campo `is_active` booleano (não NULL)
- [ ] Criar rotina não ativa automaticamente (requer `activate()`)
- [ ] Deletar rotina ativa não deixa nenhuma ativa

### Testes Relacionados

- `test_br_routine_001_only_one_active`
- `test_br_routine_001_activate_deactivates_others`
- `test_br_routine_001_create_not_auto_active`
- `test_br_routine_001_delete_active_no_orphan`

### Exemplos

#### Exemplo 1: Ativação Básica

```python
# Estado inicial
routines = [
    Routine(id=1, name="Rotina Matinal", is_active=True),   # Ativa
    Routine(id=2, name="Rotina Trabalho", is_active=False),
    Routine(id=3, name="Rotina Noite", is_active=False),
]

# Ativar Rotina Trabalho
activate_routine(routine_id=2)

# Estado final
routines = [
    Routine(id=1, name="Rotina Matinal", is_active=False),  # Desativada!
    Routine(id=2, name="Rotina Trabalho", is_active=True),  # Ativa
    Routine(id=3, name="Rotina Noite", is_active=False),
]
```

#### Exemplo 2: CLI Feedback

```bash
$ routine activate "Rotina Trabalho"

[INFO] Rotina "Rotina Matinal" desativada
[OK] Rotina "Rotina Trabalho" ativada

Agora a rotina ativa é: Rotina Trabalho (8 hábitos)
```

#### Exemplo 3: Criar Rotina (não ativa automaticamente)

```python
# Criar nova rotina
new_routine = Routine(name="Rotina Fim de Semana")
session.add(new_routine)
session.commit()

# is_active = False (padrão)
assert new_routine.is_active == False

# Para ativar, precisa chamar explicitamente
activate_routine(new_routine.id)
```

---

## BR-ROUTINE-002: Habit Belongs to Routine

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [routine-scope-habits-only.md](../../11-planning/decisions/routine-scope-habits-only.md)

### Descrição

Todo Habit DEVE pertencer a exatamente UMA rotina. Campo `routine_id` é obrigatório (NOT NULL).

### Modelo de Dados

```python
class Habit(SQLModel, table=True):
    """Hábito recorrente pertence a UMA rotina."""

    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routines.id")  # NOT NULL
    title: str = Field(min_length=1, max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: str

    # Relacionamento
    routine: Routine = Relationship(back_populates="habits")
```

### Relacionamento 1:N

```terminal
Routine (1) ----< Habits (N)

Rotina Matinal
  ├─ Academia
  ├─ Meditação
  └─ Café da manhã

Rotina Trabalho
  ├─ Daily standup
  ├─ Deep work
  └─ Code review
```

### Critérios de Aceitação

- [ ] `routine_id` obrigatório (NOT NULL)
- [ ] Foreign key válida (rotina deve existir)
- [ ] Habit não pode existir sem rotina
- [ ] Deletar rotina com habits: cascade ou block
- [ ] Criar habit sem `routine_id`: erro

### Testes Relacionados

- `test_br_routine_002_habit_requires_routine`
- `test_br_routine_002_foreign_key_valid`
- `test_br_routine_002_delete_cascade`

### Exemplos

#### Exemplo 1: Criar Habit em Rotina

```python
# Rotina existe
routine = Routine(id=1, name="Rotina Matinal", is_active=True)

# Criar habit vinculado
habit = Habit(
    routine_id=1,  # Obrigatório
    title="Academia",
    scheduled_start=time(7, 0),
    scheduled_end=time(8, 30),
    recurrence="WEEKDAYS"
)

session.add(habit)
session.commit()
```

#### Exemplo 2: Erro sem Routine

```python
# ✗ Erro: routine_id obrigatório
habit = Habit(
    routine_id=None,  # ValueError!
    title="Academia"
)

# ✗ Erro: rotina não existe
habit = Habit(
    routine_id=999,  # IntegrityError! (FK constraint)
    title="Academia"
)
```

#### Exemplo 3: CLI Context (rotina ativa)

```bash
# habit create usa rotina ativa automaticamente
$ routine activate "Rotina Matinal"
[OK] Rotina "Rotina Matinal" ativada

$ habit create --title "Leitura" --start 21:00 --end 22:00
✓ Hábito criado na rotina ativa: Rotina Matinal

# Hábito vinculado à rotina ativa (id=1)
```

---

## BR-ROUTINE-003: Task Independent of Routine

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [routine-scope-habits-only.md](../../11-planning/decisions/routine-scope-habits-only.md)

### Descrição

Tasks são independentes de rotinas. Task NÃO possui campo `routine_id`.

### Modelo de Dados

```python
class Task(SQLModel, table=True):
    """Task pontual NÃO pertence a rotina."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    scheduled_datetime: datetime
    status: TaskStatus

    # SEM relacionamento com Routine!
    # routine_id = None  ✗ Campo não existe
```

### Justificativa

**Routine = Padrão recorrente:**

- Rotina Matinal: Academia, Meditação (EVERYDAY)
- Rotina Trabalho: Standup, Deep work (WEEKDAYS)

**Task = Evento pontual único:**

- Dentista (25/11/2025 14:30) - não faz parte de rotina
- Reunião cliente (30/11/2025 10:00) - não faz parte de rotina

**Problema se Task pertencesse a Routine:**

- Task recorrente vs única?
- Task pertence a múltiplas rotinas?
- Complexidade desnecessária

### Critérios de Aceitação

- [ ] Task não possui campo `routine_id`
- [ ] Task independente de routine activation
- [ ] `task list` mostra todas tasks (não filtra por rotina)
- [ ] Deletar rotina NÃO afeta tasks

### Testes Relacionados

- `test_br_routine_003_task_no_routine_field`
- `test_br_routine_003_task_list_independent`
- `test_br_routine_003_delete_routine_keeps_tasks`

### Exemplos

#### Exemplo 1: Criar Task (sem routine)

```python
# Task não precisa de routine_id
task = Task(
    title="Dentista",
    scheduled_datetime=datetime(2025, 11, 25, 14, 30),
    status=TaskStatus.PENDING
    # routine_id não existe!
)

session.add(task)
session.commit()
```

#### Exemplo 2: CLI Independence

```bash
# Rotina ativa: Rotina Matinal
$ routine list
Rotinas:
1. Rotina Matinal [ATIVA]
2. Rotina Trabalho

# Tasks não dependem de rotina ativa
$ task list
Tasks Pendentes:
1. Dentista (25/11 14:30)
2. Reunião cliente (30/11 10:00)

# Mesmo se trocar rotina, tasks permanecem
$ routine activate "Rotina Trabalho"

$ task list
Tasks Pendentes:
1. Dentista (25/11 14:30)
2. Reunião cliente (30/11 10:00)
# ✓ Mesmas tasks
```

---

## BR-ROUTINE-004: Activation Cascade

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [routine-scope-habits-only.md](../../11-planning/decisions/routine-scope-habits-only.md)

### Descrição

Ativar rotina define contexto padrão para comandos `habit`. Habits de outras rotinas ficam inacessíveis via CLI sem flag explícita.

### Contexto de Rotina Ativa

```python
def get_active_routine(session: Session) -> Routine:
    """Retorna rotina ativa (usada como contexto padrão)."""
    routine = session.query(Routine).filter(Routine.is_active == True).first()

    if routine is None:
        raise ValueError("Nenhuma rotina ativa. Ative uma rotina primeiro.")

    return routine
```

### Comandos Afetados

**Comandos que usam contexto de rotina ativa:**

```bash
# habit list → lista apenas da rotina ativa
habit list  # Hábitos de "Rotina Matinal" (ativa)

# habit create → cria na rotina ativa
habit create --title "Leitura"  # Criado em "Rotina Matinal"

# habit details → busca na rotina ativa (por título)
habit details "Academia"  # Busca em "Rotina Matinal"
```

**Comandos independentes de rotina:**

```bash
# routine list → mostra TODAS rotinas
routine list

# task list → mostra TODAS tasks
task list

# report → aceita habit_id (não depende de rotina ativa)
report habit 42
```

### Flags para Escapar Contexto

```bash
# --all-routines: busca em todas rotinas
habit list --all-routines

# --routine <id>: especifica rotina diferente
habit create --routine 2 --title "Teste"
```

### Critérios de Aceitação

- [ ] `habit list` mostra apenas habits da rotina ativa
- [ ] `habit create` cria na rotina ativa (sem flag)
- [ ] Erro claro se nenhuma rotina ativa
- [ ] Flag `--all-routines` permite ver todos habits
- [ ] `task` commands não dependem de rotina ativa

### Testes Relacionados

- `test_br_routine_004_habit_list_active_context`
- `test_br_routine_004_habit_create_active_context`
- `test_br_routine_004_error_no_active_routine`
- `test_br_routine_004_all_routines_flag`

### Exemplos

#### Exemplo 1: Contexto Padrão

```bash
# Ativar rotina
$ routine activate "Rotina Matinal"
[OK] Rotina "Rotina Matinal" ativada

# habit list usa contexto
$ habit list
Hábitos da Rotina Ativa: Rotina Matinal
┌────┬───────────────┬─────────────────┐
│ ID │ Título        │ Horário         │
├────┼───────────────┼─────────────────┤
│ 42 │ Academia      │ 07:00 → 08:30   │
│ 43 │ Meditação     │ 20:00 → 20:15   │
└────┴───────────────┴─────────────────┘
# Apenas hábitos de "Rotina Matinal"
```

#### Exemplo 2: Trocar Rotina (contexto muda)

```bash
$ routine activate "Rotina Trabalho"
[OK] Rotina "Rotina Trabalho" ativada

$ habit list
Hábitos da Rotina Ativa: Rotina Trabalho
┌────┬───────────────┬─────────────────┐
│ ID │ Título        │ Horário         │
├────┼───────────────┼─────────────────┤
│ 50 │ Daily Standup │ 09:00 → 09:15   │
│ 51 │ Deep Work     │ 10:00 → 12:00   │
└────┴───────────────┴─────────────────┘
# Hábitos diferentes (outra rotina)
```

#### Exemplo 3: Erro Sem Rotina Ativa

```bash
# Desativar todas rotinas (cenário de erro)
$ routine deactivate --all

$ habit list
[ERROR] Nenhuma rotina ativa.

Para ativar uma rotina:
  routine list
  routine activate <id>
```

#### Exemplo 4: Flag All Routines

```bash
# Ver todos habits (todas rotinas)
$ habit list --all-routines

Todos os Hábitos:
┌────┬───────────────┬─────────────┬──────────────────┐
│ ID │ Título        │ Rotina      │ Horário          │
├────┼───────────────┼─────────────┼──────────────────┤
│ 42 │ Academia      │ Matinal     │ 07:00 → 08:30    │
│ 43 │ Meditação     │ Matinal     │ 20:00 → 20:15    │
│ 50 │ Daily Standup │ Trabalho    │ 09:00 → 09:15    │
│ 51 │ Deep Work     │ Trabalho    │ 10:00 → 12:00    │
└────┴───────────────┴─────────────┴──────────────────┘
```

---

## Referências

- **Decisão:** [routine-scope-habits-only.md](../../11-planning/decisions/routine-scope-habits-only.md)
- **Modelo:** `src/timeblock/models/routine.py`
- **Modelo:** `src/timeblock/models/habit.py`
- **Modelo:** `src/timeblock/models/task.py`
- **Service:** `src/timeblock/services/routine_service.py`
- **CLI:** `src/timeblock/commands/routine.py`

---

**Última revisão:** 14 de Novembro de 2025

**Status:** Documentação completa, ready para implementação
