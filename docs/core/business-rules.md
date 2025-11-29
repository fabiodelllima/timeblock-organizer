# Business Rules - TimeBlock Organizer

**Versão:** 3.0.0

**Data:** 28 de Novembro de 2025

**Status:** Consolidado (SSOT)

---

## Índice

1. [Introdução e Fundamentos](#1-introdução-e-fundamentos)
2. [Conceitos do Domínio](#2-conceitos-do-domínio)
3. [Routine](#3-routine)
4. [Habit](#4-habit)
5. [HabitInstance](#5-habitinstance)
6. [Skip](#6-skip)
7. [Streak](#7-streak)
8. [Task](#8-task)
9. [Timer](#9-timer)
10. [Event Reordering](#10-event-reordering)
11. [Validações Globais](#11-validações-globais)

---

## 1. Introdução e Fundamentos

### 1.1. O Que São Regras de Negócio?

Regras de negócio são políticas, restrições e lógicas que definem comportamento do sistema:

- **O que é permitido:** Operações válidas
- **O que é obrigatório:** Campos e operações mandatórios
- **Como o sistema reage:** Comportamento automático
- **O que é calculado:** Derivações automáticas
- **Como conflitos são resolvidos:** Lógica de resolução

### 1.2. Hierarquia de Regras

**Nível 1 - Estruturais (Sempre Aplicadas):**

- Garantem integridade estrutural
- Viola-las torna sistema inconsistente
- Ex: "Todo HabitInstance deve ter um Habit pai"

**Nível 2 - Domínio (Operações Normais):**

- Implementam lógica de time blocking
- Podem ser sobrescritas com justificativa
- Ex: "Eventos não devem conflitar"

**Nível 3 - Preferência (Sugestões):**

- Guiam comportamento padrão
- Facilmente ignoradas
- Ex: "Sugerir cor padrão baseada em categoria"

### 1.3. Princípios Fundamentais

**Adaptabilidade:** Sistema se adapta a realidade do usuário. Quando algo atrasa, informa e permite reorganização.

**Preservação de Intenção:** Mudanças manuais preservam intenção original. Se planejou 30min de meditação, duração é mantida mesmo que horário mude.

**Transparência:** Toda mudança é explicável e reversível. Usuário sempre tem controle final.

**Simplicidade Progressiva:** Funcionalidade básica simples, sofisticação quando necessário.

**Controle do Usuário:** Sistema NUNCA altera agenda automaticamente. Apenas detecta, informa e sugere.

### 1.4. Filosofia: Atomic Habits

**Base teórica:** "Atomic Habits" de James Clear (2018)

#### O Que São Hábitos Atômicos

**Definição:** Uma prática ou rotina regular que é:

1. **Pequena** - Fácil de fazer
2. **Específica** - Claramente definida
3. **Parte de um sistema maior** - Compõe com outros hábitos

**A Matemática dos Hábitos:**

- Melhora de 1% ao dia: 1.01^365 = 37.78x melhor em um ano
- Piora de 1% ao dia: 0.99^365 = 0.03x (quase zero)

TimeBlock torna essa matemática visível e acionável.

**Por que "Atômico":**

- Átomo = Menor unidade que mantém propriedades do sistema
- HabitInstance = Menor unidade que mantém propriedades do hábito

#### As Quatro Leis

| Lei                   | Princípio       | Implementação TimeBlock       |
| --------------------- | --------------- | ----------------------------- |
| 1. Torne Óbvio        | Notar o hábito  | Agenda visual, horários fixos |
| 2. Torne Atraente     | Querer fazer    | Streaks, progresso visível    |
| 3. Torne Fácil        | Reduzir fricção | Recorrência automática        |
| 4. Torne Satisfatório | Recompensa      | Feedback imediato, relatórios |

#### Lei 1: Torne Óbvio (Cue)

**Princípio:** Você precisa notar o hábito antes de fazê-lo.

**Implementação:**

```
┌──────────────────────────────────┐
│  HOJE - 03 Nov 2025              │
├──────────────────────────────────┤
│ 07:00-08:00  Exercício Matinal   │ ← ÓBVIO
│ 09:00-10:00  Deep Work           │
│ 15:00-15:30  Leitura             │
└──────────────────────────────────┘
```

**Técnicas:**

- Agenda visual: Hábitos aparecem no seu dia
- Implementation Intention: "Quando for [HORA], eu vou [HÁBITO]"
- Rotina diária: Consistência cria pistas ambientais

#### Lei 2: Torne Atraente (Craving)

**Princípio:** Você precisa querer fazer o hábito.

**Implementação:**

**1. Progresso Visível:**

```
Exercício Matinal:
████████████████░░░░  15/20 dias este mês (75%)
```

**2. Streak Tracking:**

```
Sequência atual: 7 dias
Melhor sequência: 23 dias
```

Cada dia completado reforça a identidade: "Sou uma pessoa que se exercita".

#### Lei 3: Torne Fácil (Response)

**Princípio:** Reduza fricção para começar.

**Implementação:**

**1. Regra dos Dois Minutos:**

```python
habit = Habit(
    title="Escrever",
    scheduled_start=time(9, 0),
    scheduled_end=time(9, 2)  # Apenas 2 minutos!
)
```

**2. Recorrência Automática:**

```python
habit = Habit(
    title="Meditação",
    recurrence=Recurrence.EVERYDAY
)
# TimeBlock gera instâncias automaticamente
# Você só marca: feito ou não feito
```

**3. Event Reordering:**

Quando conflito surge, sistema detecta e informa:

```
CONFLITO DETECTADO:
┌─────────────────────────────────────┐
│ 09:00  Reunião inesperada (nova)    │
│ 09:00  Leitura (planejada)          │ ← Conflito!
└─────────────────────────────────────┘
```

Sistema remove fricção: você decide, não precisa repensar toda agenda.

#### Lei 4: Torne Satisfatório (Reward)

**Princípio:** Recompensa imediata reforça hábito.

**Implementação:**

**1. Gratificação Visual Instantânea:**

```
[ ] Exercício 7:00-8:00

 ↓ (ao completar)

[✓] Exercício 7:00-8:00  ← Dopamina!
```

**2. Relatórios de Progresso:**

```
SEMANA 1: ███████ 7/7 dias (100%)
SEMANA 2: ██████░ 6/7 dias (86%)
SEMANA 3: ███████ 7/7 dias (100%)
```

**3. Identity Reinforcement:**

Cada instância completada reforça: "Sou o tipo de pessoa que [FAZ ISSO]"

#### Arquitetura Conceitual

```
┌──────────────────────────────────────────────┐
│              ATOMIC HABITS                   │
│                                              │
│  Cue → Craving → Response → Reward           │
│   ↓       ↓         ↓         ↓              │
│  Óbvio  Atraente  Fácil   Satisfatório       │
└──────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────┐
│             TIMEBLOCK SYSTEM                 │
│                                              │
│  Habit → HabitInstance → Completion →        │
│           (scheduled)      (tracked)         │
│                ↓                             │
│        EventReordering                       │
│       (remove friction)                      │
└──────────────────────────────────────────────┘
```

#### Componentes e Princípios

**1. Habit (Template) - Identity-based habits:**

```python
class Habit:
    """Não é apenas uma tarefa, é quem você é."""
    title: str  # "Exercício" não "Preciso me exercitar"
    recurrence: Recurrence  # Sistema, não objetivo
    routine_id: int  # Parte de identidade maior
```

Identidade > Objetivos:

- "Exercício" → identidade: "Sou atleta"
- "Preciso me exercitar" → objetivo: "Quero estar em forma"

**2. HabitInstance (Átomo) - Smallest actionable unit:**

```python
class HabitInstance:
    """Um átomo: menor unidade do sistema."""
    date: date  # Hoje, específico
    scheduled_start: time  # Hora exata
    scheduled_end: time  # Duração definida
    status: Status  # Rastreável
```

Você não "cria um hábito" (abstrato), você "faz hoje às 7h" (concreto).

**3. TimeLog (Feedback) - Measurement = visibility = improvement:**

```python
class TimeLog:
    """Track para feedback."""
    start_time: datetime
    end_time: datetime
    habit_instance_id: int
```

"O que é medido é gerenciado"

#### Exemplo Prático: Construir Hábito de Leitura

**Objetivo:** Ler 30min/dia

**1. Torne Óbvio:**

```bash
timeblock habit create "Leitura" \
  --start 21:00 \
  --duration 30 \
  --recurrence EVERYDAY
```

Aparece na agenda todo dia, mesmo horário.

**2. Torne Atraente:**

- Lista de livros interessantes preparada
- Local confortável (sofá favorito)
- Chá quente como ritual

**3. Torne Fácil:**

- Apenas 30min (pequeno)
- Horário fixo (sem decisão)
- Livro já na mesinha (sem fricção)

**4. Torne Satisfatório:**

```bash
timeblock habit complete <instance_id>
```

Marca concluído, vê progresso visual.

**Resultado após 30 dias:**

```
Leitura Diária:
███████████████████████████░░░ 27/30 dias (90%)
Sequência atual: 12 dias
Livros completados: 2
```

#### Referências

- **Livro:** "Atomic Habits" - James Clear (2018), ISBN 978-0735211292
- **Site:** <https://jamesclear.com/atomic-habits>
- **Conceitos:** Aggregation of marginal gains, Identity-based habits, Two-Minute Rule, Habit stacking

---

## 2. Conceitos do Domínio

### 2.1. Entidades Principais

| Entidade          | Descrição                                              |
| ----------------- | ------------------------------------------------------ |
| **Routine**       | Template semanal que agrupa hábitos relacionados       |
| **Habit**         | Evento recorrente, template do "ideal"                 |
| **HabitInstance** | Ocorrência real em data específica, o "real"           |
| **Task**          | Evento pontual não-recorrente (checkbox com data/hora) |
| **Timer**         | Rastreador de tempo ativo                              |
| **TimeLog**       | Registro de tempo efetivamente gasto                   |
| **Tag**           | Categoria para organizar habits e tasks                |

### 2.2. Diagrama Conceitual

```
Routine (Morning Routine)
├── Habit (Meditation 7:00-7:30 Daily)
│   ├── HabitInstance (21/10 - DONE)
│   │   └── TimeLog (7:15-7:40)
│   └── HabitInstance (22/10 - PENDING)
│
└── Habit (Workout 7:30-8:30 Weekdays)
    ├── HabitInstance (21/10 - DONE)
    │   └── TimeLog (8:00-9:00)
    └── HabitInstance (22/10 - PENDING)

Task (Dentista 14:30 - independente de routine)
```

### 2.3. Glossário

| Termo                | Definição                                               |
| -------------------- | ------------------------------------------------------- |
| **Conflito**         | Dois eventos ocupam mesmo intervalo de tempo            |
| **Event Reordering** | Processo de reorganizar eventos quando um atrasa        |
| **Streak**           | Dias consecutivos com habito DONE                       |
| **Skip**             | Pular habito conscientemente (com ou sem justificativa) |
| **Substatus**        | Qualificação adicional de DONE ou NOT_DONE              |
| **Completion %**     | Percentual de tempo realizado vs planejado              |

---

## 3. Routine

### BR-ROUTINE-001: Single Active Constraint

**Descrição:** Apenas UMA rotina pode estar ativa por vez. Ativar uma rotina desativa automaticamente todas as outras.

**Regras:**

1. Campo `is_active` é booleano (não NULL)
2. Apenas 1 rotina com `is_active = True` por vez
3. Ativar rotina A desativa automaticamente rotina B
4. Criar rotina NÃO ativa automaticamente (requer `activate()`)
5. Primeira rotina criada e ativada automaticamente
6. Deletar rotina ativa não deixa nenhuma ativa

**Implementação:**

```python
def activate_routine(routine_id: int, session: Session) -> Routine:
    # 1. Desativar TODAS as rotinas
    session.query(Routine).update({"is_active": False})

    # 2. Ativar apenas a escolhida
    routine = session.get(Routine, routine_id)
    routine.is_active = True
    session.commit()
    return routine
```

**CLI:**

```bash
$ routine activate "Rotina Trabalho"
[INFO] Rotina "Rotina Matinal" desativada
[OK] Rotina "Rotina Trabalho" ativada
```

**Testes:**

- `test_br_routine_001_only_one_active`
- `test_br_routine_001_activate_deactivates_others`
- `test_br_routine_001_create_not_auto_active`
- `test_br_routine_001_first_routine_auto_active`

---

### BR-ROUTINE-002: Habit Belongs to Routine

**Descrição:** Todo Habit DEVE pertencer a exatamente UMA rotina. Campo `routine_id` é obrigatório (NOT NULL).

**Modelo:**

```python
class Habit(SQLModel, table=True):
    routine_id: int = Field(
        foreign_key="routines.id",
        ondelete="RESTRICT"  # Bloqueia delete com habits
    )
```

**Relacionamento:**

```
Routine (1) ----< Habits (N)
```

**Regras:**

1. `routine_id` obrigatório (NOT NULL)
2. Foreign key válida (rotina deve existir)
3. Habit não pode existir sem rotina
4. Deletar rotina com habits é bloqueado (RESTRICT)

**Testes:**

- `test_br_routine_002_habit_requires_routine`
- `test_br_routine_002_foreign_key_valid`
- `test_br_routine_002_delete_routine_with_habits_blocked`

---

### BR-ROUTINE-003: Task Independent of Routine

**Descrição:** Task NÃO pertence a rotina. É entidade independente.

**Regras:**

1. Task NÃO possui campo `routine_id`
2. Task visível independente de rotina ativa
3. `task list` mostra todas tasks (não filtra por rotina)
4. Deletar rotina NÃO afeta tasks

**Justificativa:** Tasks são eventos pontuais que não fazem parte de rotinas recorrentes.

**Testes:**

- `test_br_routine_003_task_no_routine_field`
- `test_br_routine_003_task_list_independent`
- `test_br_routine_003_delete_routine_keeps_tasks`

---

### BR-ROUTINE-004: Activation Cascade

**Descrição:** Ativar rotina define contexto padrão para comandos `habit`.

**Regras:**

1. `habit list` mostra apenas habits da rotina ativa
2. `habit create` cria na rotina ativa por default
3. Erro claro se nenhuma rotina ativa
4. Flag `--all` permite ver habits de todas rotinas

**First Routine Flow:**

```bash
$ habit create --title "Academia"
[ERROR] Nenhuma rotina existe

Deseja criar uma rotina agora? (S/n): s
Nome da rotina: Rotina Matinal
[OK] Rotina "Rotina Matinal" criada e ativada

Continuar criando habito "Academia"? (S/n): s
[OK] Habito "Academia" criado na rotina "Rotina Matinal"
```

**Comandos Afetados por Contexto:**

```bash
habit list         # Lista apenas da rotina ativa
habit create       # Cria na rotina ativa
habit list --all   # Lista de TODAS rotinas
```

**Comandos Independentes:**

```bash
routine list       # Mostra TODAS rotinas
task list          # Mostra TODAS tasks
```

**Testes:**

- `test_br_routine_004_habit_list_active_context`
- `test_br_routine_004_habit_create_active_context`
- `test_br_routine_004_error_no_active_routine`
- `test_br_routine_004_all_flag`
- `test_br_routine_004_first_routine_flow`

---

### BR-ROUTINE-005: Validação de Nome

**Descrição:** Nome da rotina deve atender requisitos de validação.

**Regras:**

1. Nome não pode ser vazio (após trim)
2. Nome deve ter 1-200 caracteres
3. Nome deve ser único (case-insensitive)

**Validação:**

```python
name = name.strip()
if not name:
    raise ValueError("Nome da rotina não pode ser vazio")
if len(name) > 200:
    raise ValueError("Nome não pode ter mais de 200 caracteres")
```

**Testes:**

- `test_br_routine_005_empty_name_error`
- `test_br_routine_005_max_length`
- `test_br_routine_005_unique_name`

---

### BR-ROUTINE-006: Soft Delete e Purge

**Descrição:** Rotinas podem ser desativadas (soft delete) ou removidas permanentemente (purge).

**Soft Delete (padrão):**

```bash
$ routine delete 1
[WARN] Desativar rotina "Rotina Matinal"?
       - 8 hábitos permanecem vinculados
       - Rotina pode ser reativada depois
Confirmar? (s/N): s
[OK] Rotina "Rotina Matinal" desativada
```

**Hard Delete (--purge):**

```bash
# Sem habits - funciona
$ routine delete 1 --purge
[OK] Rotina deletada permanentemente

# Com habits - bloqueado
$ routine delete 1 --purge
[ERROR] Não é possível deletar rotina com hábitos
```

**Testes:**

- `test_br_routine_006_soft_delete_default`
- `test_br_routine_006_purge_empty_routine`
- `test_br_routine_006_purge_with_habits_blocked`

---

## 4. Habit

### BR-HABIT-001: Estrutura de Habito

**Descrição:** Habit é template de evento recorrente vinculado a Routine.

**Campos:**

```python
class Habit(SQLModel, table=True):
    id: int | None
    routine_id: int                    # FK obrigatório
    title: str                         # 1-200 chars
    scheduled_start: time              # Horário inicio
    scheduled_end: time                # Horário fim
    recurrence: Recurrence             # Padrão recorrência
    color: str | None                  # Cor hexadecimal
    tag_id: int | None                 # FK opcional para Tag
```

**Validações:**

- Title vazio após trim → ValueError
- Title > 200 chars → ValueError
- start >= end → ValueError

**Testes:**

- `test_br_habit_001_title_required`
- `test_br_habit_001_title_max_length`
- `test_br_habit_001_start_before_end`

---

### BR-HABIT-002: Padrões de Recorrência

**Descrição:** Habit define quando se repete usando enum Recurrence.

**Enum Recurrence:**

```python
class Recurrence(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    WEEKDAYS = "WEEKDAYS"      # Seg-Sex
    WEEKENDS = "WEEKENDS"      # Sab-Dom
    EVERYDAY = "EVERYDAY"      # Todos os dias
```

**Exemplos:**

```bash
habit create --title "Academia" --repeat WEEKDAYS
habit create --title "Meditação" --repeat EVERYDAY
habit create --title "Revisão" --repeat FRIDAY
```

**Testes:**

- `test_br_habit_002_recurrence_weekdays`
- `test_br_habit_002_recurrence_everyday`
- `test_br_habit_002_invalid_recurrence`

---

### BR-HABIT-003: Geração de Instâncias

**Descrição:** Sistema gera HabitInstances durante criação do habito com `--generate N`.

**Comando:**

```bash
habit create --title "Academia" --start 07:00 --end 08:30 \
  --repeat WEEKDAYS --generate 3
```

**Parâmetros:**

- `--generate N`: Gerar instâncias para próximos N meses
- Se omitido: não gera instâncias automaticamente

**Comportamento:**

- Data inicio: hoje (`date.today()`)
- Data fim: hoje + N meses (`relativedelta`)
- Respeita padrão de recorrência
- Não duplica instâncias existentes

**Validações:**

- N deve ser inteiro positivo
- Recomendado: 1-12 meses

**Testes:**

- `test_br_habit_003_generate_on_create`
- `test_br_habit_003_generate_respects_recurrence`
- `test_br_habit_003_no_duplicate_instances`
- `test_br_habit_003_create_without_generate`

---

### BR-HABIT-004: Modificação de Habito

**Descrição:** Modificar Habit afeta apenas instâncias futuras (PENDING).

**Comando:**

```bash
habit update ID --start 08:00 --end 09:30
```

**Comportamento:**

1. Usuário modifica Habit (ex: muda horário)
2. Sistema identifica instâncias PENDING com date >= hoje
3. Atualiza essas instâncias
4. Instâncias DONE/NOT_DONE não mudam

**Testes:**

- `test_br_habit_004_update_affects_future_only`
- `test_br_habit_004_preserves_completed`

---

### BR-HABIT-005: Deleção de Habito

**Descrição:** Deletar Habit deleta instâncias futuras mas preserva histórico.

**Comportamento:**

1. Instâncias PENDING são deletadas
2. Instâncias DONE/NOT_DONE são preservadas (para reports)
3. Habit é removido

**Cascade:**

```python
instances: list[HabitInstance] = Relationship(
    back_populates="habit",
    cascade_delete=True  # Deleta instâncias automaticamente
)
```

**Testes:**

- `test_br_habit_005_delete_removes_future`
- `test_br_habit_005_preserves_history`

---

## 5. HabitInstance

### BR-HABITINSTANCE-001: Status Principal

**Descrição:** HabitInstance possui 3 status principais.

**Enum Status:**

```python
class Status(str, Enum):
    PENDING = "pending"      # Agendado, não iniciado
    DONE = "done"            # Realizado
    NOT_DONE = "not_done"    # Não realizado
```

**Transições:**

```plaintext
PENDING
  ├─> DONE (via timer stop ou log manual)
  └─> NOT_DONE (via skip ou timeout)

DONE → [FINAL]
NOT_DONE → [FINAL]
```

**Testes:**

- `test_br_habitinstance_001_valid_status`
- `test_br_habitinstance_001_transitions`

---

### BR-HABITINSTANCE-002: Substatus Obrigatório

**Descrição:** Status finais requerem substatus correspondente.

**DoneSubstatus (quando DONE):**

```python
class DoneSubstatus(str, Enum):
    FULL = "full"            # 90-110% da meta
    PARTIAL = "partial"      # <90% da meta
    OVERDONE = "overdone"    # 110-150% da meta
    EXCESSIVE = "excessive"  # >150% da meta
```

**NotDoneSubstatus (quando NOT_DONE):**

```python
class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"      # Timeout sem ação
```

**Regras de Consistência:**

1. DONE requer done_substatus preenchido
2. NOT_DONE requer not_done_substatus preenchido
3. PENDING não pode ter substatus
4. Substatus são mutuamente exclusivos

**Validação:**

```python
def validate_status_consistency(self) -> None:
    if self.status == Status.DONE:
        if self.done_substatus is None:
            raise ValueError("done_substatus obrigatório quando status=DONE")
        if self.not_done_substatus is not None:
            raise ValueError("not_done_substatus deve ser None quando status=DONE")
    # ... similar para NOT_DONE e PENDING
```

**Testes:**

- `test_br_habitinstance_002_done_requires_substatus`
- `test_br_habitinstance_002_not_done_requires_substatus`
- `test_br_habitinstance_002_pending_no_substatus`
- `test_br_habitinstance_002_mutually_exclusive`

---

### BR-HABITINSTANCE-003: Completion Thresholds

**Descrição:** DoneSubstatus é calculado baseado em completion percentage.

**Thresholds:**

| Completion | Substatus | Feedback                |
| ---------- | --------- | ----------------------- |
| > 150%     | EXCESSIVE | [WARN] Ultrapassou meta |
| 110-150%   | OVERDONE  | [INFO] Acima da meta    |
| 90-110%    | FULL      | [OK] Perfeito           |
| < 90%      | PARTIAL   | Abaixo da meta          |

**Formula:**

```python
completion = (actual_duration / expected_duration) * 100
```

**Testes:**

- `test_br_habitinstance_003_threshold_full`
- `test_br_habitinstance_003_threshold_partial`
- `test_br_habitinstance_003_threshold_overdone`
- `test_br_habitinstance_003_threshold_excessive`

---

### BR-HABITINSTANCE-004: Timeout Automático

**Descrição:** Instancia PENDING sem ação após prazo é marcada como IGNORED.

**Regra:**

- Instancia PENDING > 48h após scheduled_start
- Automaticamente: NOT_DONE + IGNORED

**Property:**

```python
@property
def is_overdue(self) -> bool:
    if self.status != Status.PENDING:
        return False
    now = datetime.now()
    scheduled = datetime.combine(self.date, self.scheduled_start)
    return now > scheduled
```

**Nota:** Timeout automático está documentado mas ainda não implementado no MVP. Property `is_overdue` apenas verifica atraso.

**Testes:**

- `test_br_habitinstance_004_is_overdue_pending`
- `test_br_habitinstance_004_not_overdue_done`

---

### BR-HABITINSTANCE-005: Edição de Instancia

**Descrição:** Usuário pode editar horário de uma HabitInstance específica.

**Comando:**

```bash
habit edit INSTANCE_ID --start 08:00 --end 09:30
```

**Comportamento:**

- Novo horário aplicado apenas àquela instância
- Outras instâncias mantêm horário do template
- Não afeta Habit (template)

**Testes:**

- `test_br_habitinstance_005_edit_single`
- `test_br_habitinstance_005_preserves_template`

---

## 6. Skip

### BR-SKIP-001: Categorização de Skip

**Descrição:** Skip de habit deve ser categorizado usando enum SkipReason.

**Enum SkipReason:**

```python
class SkipReason(str, Enum):
    HEALTH = "saude"                   # Saude (doenca, consulta)
    WORK = "trabalho"                  # Trabalho (reuniao, deadline)
    FAMILY = "familia"                 # Familia (evento, emergencia)
    TRAVEL = "viagem"                  # Viagem/Deslocamento
    WEATHER = "clima"                  # Clima (chuva, frio)
    LACK_RESOURCES = "falta_recursos"  # Falta de recursos
    EMERGENCY = "emergencia"           # Emergencias
    OTHER = "outro"                    # Outros
```

**Comando:**

```bash
habit skip INSTANCE_ID --reason HEALTH --note "Consulta medica"
```

**Testes:**

- `test_br_skip_001_valid_reasons`
- `test_br_skip_001_with_note`

---

### BR-SKIP-002: Campos de Skip

**Descrição:** HabitInstance possui campos para rastrear skip.

**Campos:**

```python
skip_reason: SkipReason | None    # Categoria (obrigatório se justified)
skip_note: str | None             # Nota opcional (max 500 chars)
```

**Regras:**

1. SKIPPED_JUSTIFIED requer skip_reason
2. SKIPPED_UNJUSTIFIED não tem skip_reason
3. skip_note é sempre opcional

**Validação:**

```python
if self.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED:
    if self.skip_reason is None:
        raise ValueError("skip_reason obrigatório para SKIPPED_JUSTIFIED")
else:
    if self.skip_reason is not None:
        raise ValueError("skip_reason só permitido com SKIPPED_JUSTIFIED")
```

**Testes:**

- `test_br_skip_002_justified_requires_reason`
- `test_br_skip_002_unjustified_no_reason`
- `test_br_skip_002_note_optional`

---

### BR-SKIP-003: Prazo para Justificar

**Descrição:** Usuário tem 48h após horário planejado para justificar skip.

**Comportamento:**

- Dentro de 48h: pode adicionar/editar justificativa
- Apos 48h: instância marcada como IGNORED automaticamente
- IGNORED não pode receber justificativa retroativa

**Nota:** Timeout automático documentado, implementação pendente.

**Testes:**

- `test_br_skip_003_within_deadline`
- `test_br_skip_003_after_deadline_ignored`

---

### BR-SKIP-004: CLI Prompt Interativo

**Descrição:** Ao dar skip, CLI oferece prompt interativo para categorizar.

**Fluxo:**

```bash
$ habit skip 42

Por que você esta pulando Academia hoje?

[1] Saúde
[2] Trabalho
[3] Família
[4] Viagem
[5] Clima
[6] Falta de recursos
[7] Emergência
[8] Outro
[9] Sem justificativa

Escolha [1-9]: _
```

**Comportamento:**

- Opções 1-8: SKIPPED_JUSTIFIED + skip_reason
- Opção 9: SKIPPED_UNJUSTIFIED + skip_reason=None

**Testes:**

- `test_br_skip_004_interactive_justified`
- `test_br_skip_004_interactive_unjustified`

---

## 7. Streak

### BR-STREAK-001: Algoritmo de Cálculo

**Descrição:** Streak conta dias consecutivos com `status = DONE`, do mais recente para trás.

**Algoritmo:**

```python
def calculate_streak(habit_id: int) -> int:
    instances = get_instances_by_date(habit_id)  # Ordem cronológica
    streak = 0

    for instance in reversed(instances):  # Mais recente primeiro
        if instance.status == Status.DONE:
            streak += 1
        elif instance.status == Status.NOT_DONE:
            break  # Para no primeiro NOT_DONE
        # PENDING não conta nem quebra

    return streak
```

**Regras:**

1. Direção: presente → passado
2. Conta: apenas DONE (qualquer substatus)
3. Para: no primeiro NOT_DONE
4. Ignora: PENDING (futuro)

**Testes:**

- `test_br_streak_001_counts_done`
- `test_br_streak_001_stops_at_not_done`
- `test_br_streak_001_ignores_pending`

---

### BR-STREAK-002: Condições de Quebra

**Descrição:** Streak SEMPRE quebra quando `status = NOT_DONE`, independente do substatus.

**Todos quebram:**

| Substatus           | Quebra? | Impacto Psicológico |
| ------------------- | ------- | ------------------- |
| SKIPPED_JUSTIFIED   | Sim     | Baixo               |
| SKIPPED_UNJUSTIFIED | Sim     | Medio               |
| IGNORED             | Sim     | Alto                |

**Filosofia (Atomic Habits - James Clear):**

- Consistência > Perfeição
- "Nunca pule dois dias seguidos"
- Skip consciente ainda é quebra
- Diferenciamos impacto psicológico, não o fato da quebra

**Testes:**

- `test_br_streak_002_breaks_on_skipped_justified`
- `test_br_streak_002_breaks_on_skipped_unjustified`
- `test_br_streak_002_breaks_on_ignored`

---

### BR-STREAK-003: Condições de Manutenção

**Descrição:** Streak SEMPRE mantêm quando `status = DONE`, independente do substatus.

**Todos mantêm:**

| Substatus | Mantém? | Feedback      |
| --------- | ------- | ------------- |
| FULL      | Sim     | [OK] Perfeito |
| PARTIAL   | Sim     | Encorajador   |
| OVERDONE  | Sim     | Info          |
| EXCESSIVE | Sim     | Warning       |

**Filosofia:** "Melhor feito que perfeito"

**Testes:**

- `test_br_streak_003_maintains_on_full`
- `test_br_streak_003_maintains_on_partial`
- `test_br_streak_003_maintains_on_overdone`

---

### BR-STREAK-004: Dias Sem Instancia

**Descrição:** Dias sem instância não quebram streak.

**Exemplo:**

- Habit é WEEKDAYS (seg-sex)
- Hoje é sábado (sem instância)
- Streak continua válido

**Regra:** Apenas instâncias NOT_DONE quebram streak. Ausência de instância é neutra.

**Testes:**

- `test_br_streak_004_weekend_no_break`
- `test_br_streak_004_gap_no_break`

---

## 8. Task

### BR-TASK-001: Estrutura de Task

**Descrição:** Task é evento pontual não-recorrente. Funciona como checkbox com data/hora.

**Campos:**

```python
class Task(SQLModel, table=True):
    id: int | None
    title: str                           # 1-200 chars
    scheduled_datetime: datetime         # Quando executar
    completed_datetime: datetime | None  # Quando foi concluido
    description: str | None              # Texto opcional
    color: str | None                    # Cor hexadecimal
    tag_id: int | None                   # FK opcional para Tag
```

**Características:**

- NÃO tem status enum (usa completed_datetime)
- NÃO tem priority
- NÃO tem timer
- NÃO tem deadline separado
- NÃO pertence a routine

**Testes:**

- `test_br_task_001_create_basic`
- `test_br_task_001_title_required`

---

### BR-TASK-002: Conclusão de Task

**Descrição:** Task é marcada como concluída via `completed_datetime`.

**Estados:**

- `completed_datetime = None` → Pendente
- `completed_datetime = datetime` → Concluida

**Comando:**

```bash
$ task complete 42
[OK] Task "Dentista" marcada como concluída
```

**Comportamento:**

- Sistema registra timestamp atual
- Task sai da lista de pendentes
- Aparece em histórico

**Testes:**

- `test_br_task_002_complete_sets_datetime`
- `test_br_task_002_pending_no_datetime`

---

### BR-TASK-003: Independência de Routine

**Descrição:** Tasks são independentes de routines.

**Regras:**

1. Task não tem campo routine_id
2. `task list` mostra todas tasks
3. Mudar rotina ativa não afeta tasks
4. Deletar rotina não afeta tasks

**Testes:**

- `test_br_task_003_no_routine_field`
- `test_br_task_003_list_all_tasks`
- `test_br_task_003_routine_change_no_effect`

---

### BR-TASK-004: Visualização e Listagem

**Descrição:** Tasks podem ser listadas com filtros.

**Filtros:**

- Por status (pendentes, concluídas)
- Por data (hoje, semana, mes)
- Por tag

**Ordenação:** Cronológica por scheduled_datetime

**Comandos:**

```bash
task list              # Pendentes
task list --today      # Hoje
task list --completed  # Concluidas
task list --all        # Todas
```

**Testes:**

- `test_br_task_004_list_pending`
- `test_br_task_004_filter_today`
- `test_br_task_004_filter_completed`

---

### BR-TASK-005: Atualização de Task

**Descrição:** Task pendente pode ser atualizada.

**Campos Atualizáveis:**

- title
- description
- scheduled_datetime
- color
- tag_id

**Restrição:** Task concluída não pode ser editada.

**Testes:**

- `test_br_task_005_update_pending`
- `test_br_task_005_update_completed_error`

---

### BR-TASK-006: Simplicidade Mantida

**Descrição:** Tasks são intencionalmente simples no MVP.

**NÃO implementado:**

- Timer tracking
- Subtasks
- Dependencias entre tasks
- Priorização explícita
- Checklist interno

**Justificativa:** Foco do TimeBlock está em hábitos e rotinas. Tasks são complemento para atividades pontuais.

---

## 9. Timer

### BR-TIMER-001: Single Active Timer

**Descrição:** Apenas UM timer pode estar ATIVO (RUNNING ou PAUSED) por vez.

**Constraint:**

```python
active_timers = get_active_timers()  # status in [RUNNING, PAUSED]
assert len(active_timers) <= 1
```

**Comportamento:**

- Timer finalizado não bloqueia novo start
- Múltiplas sessões permitidas (start → stop → start)

**Erro:**

```bash
$ timer start Academia
[OK] Timer iniciado: Academia (00:00 / 01:30)

$ timer start Meditação
[ERROR] Timer já ativo: Academia (15min decorridos)

Opções:
  [1] Pausar Academia e iniciar Meditação
  [2] Cancelar Academia (reset) e iniciar Meditação
  [3] Continuar com Academia
```

**Testes:**

- `test_br_timer_001_only_one_active`
- `test_br_timer_001_error_if_already_running`
- `test_br_timer_001_stopped_not_blocking`

---

### BR-TIMER-002: Estados e Transições

**Descrição:** Timer possui estados RUNNING e PAUSED.

**Maquina de Estados:**

```
[NO TIMER]
  │
  └─> start → RUNNING
              ├─> pause → PAUSED
              │            └─> resume → RUNNING
              ├─> stop → [SALVA] → [NO TIMER]
              └─> reset → [CANCELA] → [NO TIMER]
```

**Comandos:**

| Comando | De             | Para     | Efeito             |
| ------- | -------------- | -------- | ------------------ |
| start   | NO TIMER       | RUNNING  | Cria timer         |
| pause   | RUNNING        | PAUSED   | Pausa contagem     |
| resume  | PAUSED         | RUNNING  | Retoma contagem    |
| stop    | RUNNING/PAUSED | NO TIMER | Salva e marca DONE |
| reset   | RUNNING/PAUSED | NO TIMER | Cancela sem salvar |

**Testes:**

- `test_br_timer_002_start_creates_running`
- `test_br_timer_002_pause_from_running`
- `test_br_timer_002_resume_from_paused`
- `test_br_timer_002_stop_saves`
- `test_br_timer_002_reset_cancels`

---

### BR-TIMER-003: Stop vs Reset

**Descrição:** `stop` e `reset` finalizam timer com comportamentos diferentes.

**stop:**

- Fecha sessão atual e SALVA no banco
- Marca instance como DONE
- Calcula completion percentage
- Permite start novamente (nova sessão)

**reset:**

- Cancela timer atual SEM salvar
- Instance continua PENDING
- Usado quando iniciou habit errado

**Testes:**

- `test_br_timer_003_stop_saves_session`
- `test_br_timer_003_reset_no_save`
- `test_br_timer_003_reset_keeps_pending`

---

### BR-TIMER-004: Múltiplas Sessóes

**Descrição:** Usuário pode fazer múltiplas sessões do mesmo habit no mesmo dia.

**Workflow:**

```python
# Sessão 1 (manhá)
timer1 = start_timer(instance_id=42)
timer1.stop()  # SALVA (60min)

# Sessão 2 (tarde)
timer2 = start_timer(instance_id=42)
timer2.stop()  # SALVA (30min)

# Total: 90min (acumulado)
```

**Substatus:** Calculado sobre tempo acumulado de todas sessões.

**Testes:**

- `test_br_timer_004_multiple_sessions`
- `test_br_timer_004_accumulates_duration`

---

### BR-TIMER-005: Cálculo de Completion

**Descrição:** Completion percentage calculado ao parar timer.

**Formula:**

```python
total_actual = sum(session.duration for session in sessions)
completion = (total_actual / expected_duration) * 100
```

**Testes:**

- `test_br_timer_005_completion_formula`
- `test_br_timer_005_multiple_sessions_accumulated`

---

### BR-TIMER-006: Pause Tracking

**Descrição:** Sistema rastreia pausas via campo acumulado `paused_duration`.

**Fluxo:**

```
10:00 - start_timer()
10:30 - pause_timer()
10:45 - resume_timer()  # paused_duration = 15min
11:00 - stop_timer()    # duration = 60min - 15min = 45min
```

**Cálculo:**

```python
effective_duration = total_duration - paused_duration
```

**Testes:**

- `test_br_timer_006_pause_tracking`
- `test_br_timer_006_multiple_pauses`
- `test_br_timer_006_effective_duration`

---

### BR-TIMER-007: Log Manual

**Descrição:** Usuário pode registrar tempo manualmente sem usar timer.

**Comando:**

```bash
habit log INSTANCE_ID --start 07:00 --end 08:30
# ou
habit log INSTANCE_ID --duration 90
```

**Validações:**

- start < end
- duration > 0

**Testes:**

- `test_br_timer_007_manual_log_times`
- `test_br_timer_007_manual_log_duration`
- `test_br_timer_007_validates_times`

---

## 10. Event Reordering

### BR-REORDER-001: Definição de Conflito

**Descrição:** Conflito ocorre quando dois eventos tem sobreposição temporal no mesmo dia.

**Detecção:**

```
Evento A: [T1, T2]
Evento B: [T3, T4]
Conflito se: (T1 < T4) AND (T3 < T2)
```

**Eventos Monitorados:**

- HabitInstances
- Tasks

**Testes:**

- `test_br_reorder_001_detects_overlap`
- `test_br_reorder_001_no_conflict_adjacent`

---

### BR-REORDER-002: Escopo Temporal

**Descrição:** Detecção de conflitos ocorre dentro do mesmo dia (00:00-23:59).

**Regra:** Eventos de dias diferentes NÃO podem conflitar, mesmo que horários se sobreponham numericamente.

**Testes:**

- `test_br_reorder_002_same_day_only`
- `test_br_reorder_002_different_days_no_conflict`

---

### BR-REORDER-003: Apresentação de Conflitos

**Descrição:** Sistema apresenta conflitos de forma clara ao usuário.

**Quando Apresentar:**

1. Apos criar/ajustar evento que resulta em conflito
2. Quando usuário solicita visualização de conflitos
3. Antes de iniciar timer, se houver conflitos

**Formato:**

```
Conflito detectado:
  - Academia: 07:00-08:00
  - Reuniao: 07:30-08:30
  Sobreposição: 30 minutos
```

**Testes:**

- `test_br_reorder_003_presents_conflicts`
- `test_br_reorder_003_shows_overlap_duration`

---

### BR-REORDER-004: Conflitos Não Bloqueiam

**Descrição:** Conflitos são informativos, NÃO impeditivos.

**Comportamento:**

- Timer start com conflito: apenas avisa, pergunta confirmação
- Criar evento com conflito: apenas avisa, permite criar

```bash
$ timer start Academia
[WARN] Conflito detectado:
  - Academia: 07:00-08:00
  - Reuniao: 07:00-08:30

Iniciar timer mesmo assim? [Y/n]: y
[OK] Timer iniciado
```

**Testes:**

- `test_br_reorder_004_conflict_warning_only`
- `test_br_reorder_004_allows_with_confirmation`

---

### BR-REORDER-005: Persistencia de Conflitos

**Descrição:** Conflitos NÃO são persistidos no banco. São calculados dinamicamente.

**Justificativa:** Conflitos são resultado de relação temporal entre eventos. Como eventos podem mudar, conflitos devem ser recalculados.

**Testes:**

- `test_br_reorder_005_calculated_dynamically`
- `test_br_reorder_005_no_conflict_table`

---

### BR-REORDER-006: Algoritmo de Reordenamento

**Descrição:** Algoritmo de sugestão de reordenamento NÃO está no MVP.

**Status Atual:**

- Sistema detecta conflitos
- Sistema apresenta conflitos
- Sistema NÃO sugere novos horários automaticamente

**Futuro:** Algoritmo Simple Cascade planejado para v2.0.

---

## 11. Validações Globais

### BR-VAL-001: Validação de Horários

**Regras:**

- `start_time < end_time`
- `duration_minutes > 0`
- Horários dentro do dia (00:00 - 23:59)

**Testes:**

- `test_br_val_001_start_before_end`
- `test_br_val_001_positive_duration`

---

### BR-VAL-002: Validação de Datas

**Regras:**

- Data não anterior a 2025-01-01
- Sem limite de data futura
- Formato ISO 8601

**Testes:**

- `test_br_val_002_min_date`
- `test_br_val_002_iso_format`

---

### BR-VAL-003: Validação de Strings

| Campo       | Limite       |
| ----------- | ------------ |
| title       | 1-200 chars  |
| description | 0-2000 chars |
| name        | 1-200 chars  |
| note        | 0-500 chars  |

**Comportamento:** Trim de espaços antes da validação.

**Testes:**

- `test_br_val_003_title_limits`
- `test_br_val_003_trim_whitespace`

---

## Referências

- **ADRs:** `docs/decisions/`
- **Livro:** "Atomic Habits" - James Clear
- **Service Layer:** `cli/src/timeblock/services/`
- **Models:** `cli/src/timeblock/models/`
- **Enums:** `cli/src/timeblock/models/enums.py`

---

- **Documento consolidado em:** 28 de Novembro de 2025
- **Total de regras:** 45 BRs
- **Este é o SSOT para regras de negócio**
