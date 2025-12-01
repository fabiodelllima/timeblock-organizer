# Arquitetura TimeBlock Organizer

**Versão:** 2.0.0

**Data:** 28 de Novembro de 2025

**Status:** Consolidado (SSOT)

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Filosofia de Controle do Usuário](#2-filosofia-de-controle-do-usuário)
3. [Stack Tecnológica](#3-stack-tecnológica)
4. [Camadas da Aplicação](#4-camadas-da-aplicação)
5. [Modelos de Dados](#5-modelos-de-dados)
6. [Fluxos Principais](#6-fluxos-principais)
7. [Decisões Arquiteturais](#7-decisões-arquiteturais)
8. [Padrões e Convenções](#8-padrões-e-convenções)
9. [Evolução Futura](#9-evolução-futura)

---

## 1. Visão Geral

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada nos princípios de "Atomic Habits" de James Clear.

### 1.1. Princípios Arquiteturais

1. **Simplicidade** - Arquitetura direta sem over-engineering
2. **Separação de Responsabilidades** - Service pattern claro
3. **Testabilidade** - Design orientado a testes
4. **Stateless** - Operações sem estado persistente em memória
5. **Database-First** - SQLite como fonte de verdade
6. **User Control** - Sistema informa, usuário decide

### 1.2. Características Principais

- **CLI-First**: Interface de linha de comando como cidadão de primeira classe
- **Embedded Database**: SQLite sem servidor externo
- **Offline-First**: Funciona perfeitamente sem conexão
- **Sync-Ready**: Arquitetura preparada para sincronização futura
- **Logging Estruturado**: Observabilidade desde o início

### 1.3. Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                      Usuário (CLI)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                   Commands Layer                            │
│              (Typer/Click, parsing, output)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                   Services Layer                            │
│           (Business logic, orchestration)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                    Models Layer                             │
│              (SQLModel, relationships)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                            │
│              (SQLite, engine management)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Filosofia de Controle do Usuário

### 2.1. Princípio Fundamental

O TimeBlock é construído sobre o princípio de que sua função é **informar, sugerir e facilitar, mas NUNCA decidir**. Cada alteração na agenda do usuário requer aprovação explícita.

### 2.2. O Problema que Evitamos

Muitos sistemas de produtividade tentam ser "inteligentes" tomando decisões automáticas. Eles reordenam tarefas, ajustam prioridades e movem eventos baseados em algoritmos que presumem entender o contexto completo da vida do usuário.

**Exemplo do problema:**

- Sistema detecta que usuário executa "Academia" às 18h em vez do horário planejado às 7h
- Sistema "inteligente" move automaticamente futuras instâncias para 18h
- **Problema:** Usuário está temporariamente ajustando devido a projeto com deadline, mas seu objetivo real continua sendo ir a academia de manhã
- Sistema reforçou comportamento não desejado

### 2.3. Nossa Solução: Informação sem Imposição

**Detecção de Conflitos:**

- Sistema detecta sobreposição temporal
- Apresenta informações claras
- NÃO propõe solução automaticamente

**Ajuste de Horários:**

- Ajuste em um dia afeta apenas aquele dia
- Plano ideal (Routine) permanece intocado
- Cada dia é nova oportunidade de seguir a Routine

**Priorização:**

- Sistema NÃO aplica regras de priorização automática
- Apresenta eventos e permite usuário escolher

### 2.4. Routine como Norte Verdadeiro

```
┌─────────────────────────────────────────────────────┐
│                    ROUTINE                          │
│              (Plano Ideal - Imutável)               │
│                                                     │
│   Academia: 07:00-08:00 WEEKDAYS                    │
│   Meditação: 06:30-07:00 EVERYDAY                   │
└─────────────────────────────────────────────────────┘
                          │
                          │ Gera instancias
                          v
┌─────────────────────────────────────────────────────┐
│               HABIT INSTANCES                       │
│            (Realidade - Flexível)                   │
│                                                     │
│   Seg 25/11: Academia 07:00 [DONE]                  │
│   Ter 26/11: Academia 18:00 [DONE] (ajustado)       │
│   Qua 27/11: Academia 07:00 [PENDING]               │
└─────────────────────────────────────────────────────┘
```

**Separação:**

- **Routine:** Intenções e objetivos (o que usuário aspira)
- **HabitInstance:** O que realmente acontece (ajustes, atrasos)

### 2.5. Implicações no Código

#### **Princípio 1: Detecção sem Ação**

```python
# CORRETO: Detecta e retorna informações
def detect_conflicts(event_id: int) -> list[Conflict]:
    conflicts = query_overlapping_events(event_id)
    return conflicts  # Apenas retorna, NAO modifica

# CORRETO: Ação separada que requer confirmação
def apply_user_resolution(conflict_id: int, user_choice: Resolution):
    if user_choice.confirmed:
        apply_changes(user_choice.changes)
```

```python
# INCORRETO: Detecção e ação misturadas
def detect_and_resolve_conflicts(event_id: int):
    conflicts = query_overlapping_events(event_id)
    for conflict in conflicts:
        auto_resolve(conflict)  # NUNCA fazer isso
```

#### **Princípio 2: Preservação de Template**

```python
# CORRETO: Ajuste afeta apenas instancia
def adjust_instance(instance_id: int, new_start: time):
    instance = get_instance(instance_id)
    instance.scheduled_start = new_start
    # Habit (template) permanece inalterado
    save(instance)
```

#### **Princípio 3: Confirmação Explicita**

```python
# CORRETO: Requer confirmação
if conflicts_detected:
    print("Conflitos encontrados:")
    for c in conflicts:
        print(f"  - {c.description}")

    if typer.confirm("Continuar mesmo assim?"):
        proceed()
```

---

## 3. Stack Tecnológica

### 3.1. Core

| Componente | Tecnologia | Versão | Razão                     |
| ---------- | ---------- | ------ | ------------------------- |
| Linguagem  | Python     | 3.13+  | Produtividade, ecosystem  |
| CLI        | Typer      | 0.x    | Type hints, auto-complete |
| ORM        | SQLModel   | 0.0.x  | Pydantic + SQLAlchemy     |
| Database   | SQLite     | 3.x    | Zero-config, portável     |
| Output     | Rich       | 13.x   | Terminal formatting       |

### 3.2. Desenvolvimento

| Componente | Tecnologia | Razão                  |
| ---------- | ---------- | ---------------------- |
| Testes     | pytest     | Padrão de facto Python |
| Coverage   | pytest-cov | Métricas de cobertura  |
| Linting    | ruff       | Rápido, moderno        |
| Type Check | mypy       | Segurança de tipos     |
| VCS        | Git        | Gitflow workflow       |

### 3.3. Dependências Principais

```
sqlmodel>=0.0.14
typer>=0.9.0
rich>=13.0.0
python-dateutil>=2.8.0
```

**Filosofia:** Mínimas dependências, máxima estabilidade.

---

## 4. Camadas da Aplicação

### 4.1. CLI Commands Layer

**Localização:** `cli/src/timeblock/commands/`

**Responsabilidade:** Interface com usuário, parsing de argumentos.

**Estrutura:**

```
commands/
├── habit.py       # Comandos de hábitos
├── task.py        # Comandos de tarefas
├── routine.py     # Comandos de rotinas
├── timer.py       # Comandos de timer
├── report.py      # Relatórios
└── ...
```

**Princípios:**

- Commands são thin wrappers
- Validação básica de input
- Delegam para Services
- Formatam output para usuário

**Exemplo:**

```python
@app.command()
def create(
    title: str = typer.Argument(...),
    start: str = typer.Option(..., "--start"),
):
    """Cria novo hábito."""
    # 1. Valida input básico
    if not title:
        console.print("[ERROR] Titulo obrigatório")
        raise typer.Exit(1)

    # 2. Delega para service
    habit = HabitService.create_habit(
        title=title,
        scheduled_start=parse_time(start)
    )

    # 3. Formata output
    console.print(f"[OK] Hábito criado: {habit.title}")
```

### 4.2. Services Layer

**Localização:** `cli/src/timeblock/services/`

**Responsabilidade:** Lógica de negócio, orquestração.

**Estrutura:**

```
services/
├── habit_service.py             # CRUD hábitos
├── habit_instance_service.py    # Gestão de instancias
├── event_reordering_service.py  # Detecção de conflitos
├── task_service.py              # Gestão de tarefas
├── routine_service.py           # Gestão de rotinas
├── timer_service.py             # Timer tracking
└── ...
```

**Princípios:**

- Stateless (sem estado interno)
- Métodos estáticos ou de classe
- Transações DB isoladas
- Business rules centralizadas

**Exemplo:**

```python
class HabitInstanceService:
    """Service para gestão de instancias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date
    ) -> list[HabitInstance]:
        """Gera instancias baseadas em recorrência.

        Args:
            habit_id: ID do hábito template
            start_date: Data inicial
            end_date: Data final

        Returns:
            Lista de instancias criadas
        """
        with get_session() as session:
            habit = session.get(Habit, habit_id)
            instances = []

            for day in date_range(start_date, end_date):
                if matches_recurrence(day, habit.recurrence):
                    instance = HabitInstance(
                        habit_id=habit_id,
                        date=day,
                        scheduled_start=habit.scheduled_start,
                        scheduled_end=habit.scheduled_end
                    )
                    session.add(instance)
                    instances.append(instance)

            session.commit()
            return instances
```

**Por que Stateless:**

- Testabilidade (sem setup/teardown complexo)
- Concorrência (sem race conditions)
- Simplicidade (fácil entender fluxo)

### 4.3. Models Layer

**Localização:** `cli/src/timeblock/models/`

**Responsabilidade:** Estrutura de dados, relacionamentos.

**Estrutura:**

```
models/
├── __init__.py           # Exports
├── enums.py              # Status, Recurrence, etc
├── routine.py            # Modelo Routine
├── habit.py              # Modelo Habit
├── habit_instance.py     # Modelo HabitInstance
├── task.py               # Modelo Task
├── tag.py                # Modelo Tag
├── time_log.py           # Modelo TimeLog
└── event.py              # Union type Event
```

**Princípios:**

- SQLModel (Pydantic + SQLAlchemy)
- Type hints completos
- Validação automática
- Relationships explícitos

**Exemplo:**

```python
class HabitInstance(SQLModel, table=True):
    """Instancia de habito em data específica."""

    __tablename__ = "habit_instances"

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    status: Status = Field(default=Status.PENDING)
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None

    # Relationships
    habit: "Habit" = Relationship(back_populates="instances")

    @property
    def is_overdue(self) -> bool:
        """Verifica se instância está atrasada."""
        if self.status != Status.PENDING:
            return False
        now = datetime.now()
        scheduled = datetime.combine(self.date, self.scheduled_start)
        return now > scheduled
```

### 4.4. Database Layer

**Localização:** `cli/src/timeblock/database/`

**Responsabilidade:** Gerenciamento de conexões, migrations.

**Estrutura:**

```
database/
├── __init__.py     # Exports
├── engine.py       # Engine management
└── migrations/     # Schema migrations
```

**Engine Management:**

```python
from contextlib import contextmanager
from sqlmodel import create_engine, Session

DB_PATH = Path.home() / ".timeblock" / "timeblock.db"

@contextmanager
def get_session():
    """Context manager para sessão SQLite.

    Garante:
    - Conexão única por operação
    - Cleanup automático
    - Thread-safety
    """
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
```

### 4.5. Utils Layer

**Localização:** `cli/src/timeblock/utils/`

**Responsabilidade:** Funcionalidades transversais.

**Estrutura:**

```
utils/
├── logger.py               # Logging estruturado
├── formatters.py           # Output formatters
├── date_helpers.py         # Date utilities
├── validators.py           # Input validation
├── queries.py              # Query helpers
└── event_date_filters.py   # Filtros de eventos
```

**Princípios:**

- Pure functions quando possível
- Sem side effects
- Altamente testáveis
- Reutilizáveis

---

## 5. Modelos de Dados

### 5.1. Diagrama ER

```
┌─────────────┐
│   Routine   │
│─────────────│
│ id          │
│ name        │
│ is_active   │
└──────┬──────┘
       │ 1:N
       v
┌─────────────┐      1:N     ┌──────────────────┐
│    Habit    │─────────────→│  HabitInstance   │
│─────────────│              │──────────────────│
│ id          │              │ id               │
│ routine_id  │              │ habit_id         │
│ title       │              │ date             │
│ start/end   │              │ start/end        │
│ recurrence  │              │ status           │
└─────────────┘              │ substatus        │
                             └──────────────────┘

┌─────────────┐
│    Task     │
│─────────────│
│ id          │
│ title       │
│ datetime    │
│ completed   │
└─────────────┘

┌─────────────┐
│     Tag     │
│─────────────│
│ id          │
│ name        │
│ color       │
└─────────────┘

┌─────────────┐
│   TimeLog   │
│─────────────│
│ id          │
│ event_id    │
│ task_id     │
│ instance_id │
│ start_time  │
│ end_time    │
│ duration    │
└─────────────┘
```

### 5.2. Entidades Core

**Routine (Agrupamento):**

```python
class Routine(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    is_active: bool = Field(default=False)

    habits: list["Habit"] = Relationship(back_populates="routine")
```

**Habit (Template):**

```python
class Habit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routines.id")
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence
    color: str | None = None
    tag_id: int | None = Field(foreign_key="tags.id")

    routine: "Routine" = Relationship(back_populates="habits")
    instances: list["HabitInstance"] = Relationship(back_populates="habit")

```

**HabitInstance (Ocorrência):**

```python
class HabitInstance(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date
    scheduled_start: time
    scheduled_end: time
    status: Status = Field(default=Status.PENDING)
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None
    skip_reason: SkipReason | None = None
    skip_note: str | None = None
    completion_percentage: int | None = None

    habit: "Habit" = Relationship(back_populates="instances")
```

**Task (Evento Único):**

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    scheduled_datetime: datetime
    completed_datetime: datetime | None = None
    description: str | None = None
    color: str | None = None
    tag_id: int | None = Field(foreign_key="tags.id")
```

**TimeLog (Rastreamento de Tempo):**

```python
class TimeLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int | None = Field(foreign_key="event.id")
    task_id: int | None = Field(foreign_key="tasks.id")
    habit_instance_id: int | None = Field(foreign_key="habitinstance.id")
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: int | None = None
    paused_duration: int | None = Field(default=0)
    notes: str | None = Field(max_length=500)

```

### 5.3. Enums

```python
class Status(str, Enum):
    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"

class DoneSubstatus(str, Enum):
    FULL = "full"           # 90-110%
    PARTIAL = "partial"     # <90%
    OVERDONE = "overdone"   # 110-150%
    EXCESSIVE = "excessive" # >150%

class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"

class Recurrence(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    WEEKDAYS = "WEEKDAYS"
    WEEKENDS = "WEEKENDS"
    EVERYDAY = "EVERYDAY"

class SkipReason(str, Enum):
    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    TRAVEL = "viagem"
    WEATHER = "clima"
    LACK_RESOURCES = "falta_recursos"
    EMERGENCY = "emergencia"
    OTHER = "outro"
```

---

## 6. Fluxos Principais

### 6.1. Criação e Geração de Instâncias

```
Usuário CLI
    │
    │ timeblock habit create "Academia" --start 07:00 --generate 3
    v
┌──────────────────┐
│  habit.py (CLI)  │  1. Parse argumentos
└────────┬─────────┘  2. Valida input
         │
         v
┌──────────────────────┐
│    HabitService      │  3. Cria Habit
└────────┬─────────────┘  4. Persiste
         │
         v
┌──────────────────────────┐
│ HabitInstanceService     │  5. Gera instancias
└────────┬─────────────────┘  6. Para próximos 3 meses
         │
         v
┌──────────────────────┐
│     Database         │  7. Persiste instancias
└──────────────────────┘
```

### 6.2. Detecção de Conflitos

```
Usuário ajusta horário
    │
    │ timeblock habit edit <id> --start 09:00
    v
┌────────────────────────────┐
│ HabitInstanceService       │  1. Atualiza horário
└──────────┬─────────────────┘
           │
           v
┌────────────────────────────┐
│ EventReorderingService     │  2. Detecta conflitos
└──────────┬─────────────────┘  3. Lista sobreposições
           │
           v
      Conflitos?
       /      \
    Sim       Não
     │         │
     v         └──→ [OK] Atualizado
┌──────────────────────┐
│ Apresenta conflitos  │  4. Mostra ao usuário
└──────────┬───────────┘  5. Pede confirmação
           │
           v
    Usuário confirma?
       /      \
    Sim       Não
     │         │
     v         └──→ Cancelado
   Salva
```

### 6.3. Timer Workflow

```
┌──────────┐     start     ┌─────────┐
│ NO TIMER │──────────────→│ RUNNING │
└──────────┘               └────┬────┘
     ^                          │
     │                     ┌────┴────┐
     │                     │         │
     │                   pause     stop
     │                     │         │
     │                     v         v
     │               ┌─────────┐  ┌──────┐
     │               │ PAUSED  │  │ DONE │
     │               └────┬────┘  └──────┘
     │                    │
     │                 resume
     │                    │
     │                    v
     │               ┌─────────┐
     └───────────────│ RUNNING │
          reset      └─────────┘
```

---

## 7. Decisões Arquiteturais

### ADR-001: SQLModel como ORM

**Decisão:** Usar SQLModel ao invés de SQLAlchemy puro.

**Razão:**

- Pydantic integrado (validação grátis)
- Type hints nativos
- API mais simples
- Serialização JSON automática

**Trade-offs:**

- [-] Comunidade menor
- [-] Alguns features avançados não disponíveis

### ADR-002: Stateless Services

**Decisão:** Services sem estado interno, métodos estáticos.

**Razão:**

- Testabilidade superior
- Sem race conditions
- Fluxo fácil de entender

### ADR-003: SQLite Embedded

**Decisão:** SQLite local sem servidor.

**Razão:**

- Zero configuração
- Portabilidade total
- Suficiente para single-user

**Trade-offs:**

- [-] Sem concorrência multi-processo

### ADR-004: Typer para CLI

**Decisão:** Usar Typer ao invés de Click puro.

**Razão:**

- Type hints nativos
- Auto-complete automático
- Baseado em Click (compatível)

### ADR-005: Offline-First

**Decisão:** Sistema funciona 100% offline.

**Razão:**

- Independência de conexão
- Performance garantida
- Privacidade total

### ADR-006: User Control Philosophy

**Decisão:** Sistema informa mas NAO decide.

**Razão:**

- Usuário conhece contexto completo
- Evita automações indesejadas
- Preserva intenção original

---

## 8. Padrões e Convenções

### 8.1. Estrutura de Diretórios

```
cli/
├── src/
│   └── timeblock/
│       ├── commands/      # CLI commands
│       ├── services/      # Business logic
│       ├── models/        # Data models
│       ├── database/      # DB management
│       └── utils/         # Helpers
├── tests/
│   ├── unit/              # Testes unitários
│   ├── integration/       # Testes integração
│   └── e2e/               # Testes end-to-end
└── docs/                  # Documentação
```

### 8.2. Naming Conventions

**Arquivos:**

- `snake_case.py` para módulos
- `test_<module>.py` para testes

**Classes:**

- `PascalCase` para classes
- `Test<Feature>` para classes de teste

**Funções/Métodos:**

- `snake_case` para funções
- `test_<behavior>` para métodos de teste

**Constantes:**

- `UPPER_SNAKE_CASE`

### 8.3. Imports

```python
# 1. Standard library
from datetime import date, time, datetime
from pathlib import Path

# 2. Third-party
from sqlmodel import SQLModel, Field, Session

# 3. Local
from timeblock.services import HabitService
from timeblock.models import Habit, HabitInstance
```

### 8.4. Type Hints

```python
def generate_instances(
    habit_id: int,
    start_date: date,
    end_date: date
) -> list[HabitInstance]:
    """Sempre type hints completos."""
    pass
```

### 8.5. Docstrings

```python
def calculate_streak(habit_id: int) -> int:
    """Calcula streak atual do hábito.

    Conta dias consecutivos com status DONE,
    do mais recente para trás.

    Args:
        habit_id: ID do hábito

    Returns:
        Número de dias consecutivos

    Raises:
        ValueError: Se habit_id inválido
    """
    pass
```

### 8.6. Padrões de Teste

**Estrutura:**

```
tests/
├── unit/
│   ├── test_models/
│   ├── test_services/
│   ├── test_business_rules/
│   └── test_utils/
├── integration/
│   └── test_flows/
└── e2e/
    └── test_cli/
```

**Naming:**

- Classes: `TestBR<Domain><Number>`
- Métodos: `test_br_<domain>_<number>_<scenario>`

**Padrão BDD:**

```python
def test_br_streak_001_counts_done(self):
    """Streak conta dias consecutivos DONE.

    DADO: Hábito com 5 instancias DONE consecutivas
    QUANDO: Calcular streak
    ENTÃO: Deve retornar 5

    BR: BR-STREAK-001
    """
    # Arrange
    # Act
    # Assert
```

### 8.7. Git Workflow

**Branches:**

- `main` - produção
- `develop` - desenvolvimento
- `feat/*` - features
- `fix/*` - bugfixes
- `refactor/*` - refatorações

**Commits:**

```
type(scope): Descrição em Português

Corpo opcional

Footer opcional
```

**Types:** feat, fix, refactor, test, docs, chore

---

## 9. Evolução Futura

### v1.4.0 - Consolidação

- Documentação consolidada
- Testes reorganizados
- CI/CD pipeline

### v2.0.0 - Sincronização

- Sync Linux <-> Android (Termux)
- UUID como primary keys
- Conflict resolution
- Queue-based sync

### v3.0.0 - Analytics

- Dashboard de métricas
- Streak tracking avançado
- Reports automáticos

---

## Referências

- **SQLModel:** <https://sqlmodel.tiangolo.com/>
- **Typer:** <https://typer.tiangolo.com/>
- **Rich:** <https://rich.readthedocs.io/>
- **Atomic Habits:** James Clear
- **Business Rules:** `docs/core/business-rules.md`

---

**Documento consolidado em:** 28 de Novembro de 2025
