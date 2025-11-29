# Arquitetura TimeBlock Organizer

**Versao:** 2.0.0

**Data:** 28 de Novembro de 2025

**Status:** Consolidado (SSOT)

---

## Indice

1. [Visao Geral](#1-visao-geral)
2. [Filosofia de Controle do Usuario](#2-filosofia-de-controle-do-usuario)
3. [Stack Tecnologica](#3-stack-tecnologica)
4. [Camadas da Aplicacao](#4-camadas-da-aplicacao)
5. [Modelos de Dados](#5-modelos-de-dados)
6. [Fluxos Principais](#6-fluxos-principais)
7. [Decisoes Arquiteturais](#7-decisoes-arquiteturais)
8. [Padroes e Convencoes](#8-padroes-e-convencoes)
9. [Evolucao Futura](#9-evolucao-futura)

---

## 1. Visao Geral

TimeBlock Organizer e uma aplicacao CLI para gerenciamento de tempo baseada nos principios de "Atomic Habits" de James Clear.

### 1.1. Principios Arquiteturais

1. **Simplicidade** - Arquitetura direta sem over-engineering
2. **Separacao de Responsabilidades** - Service pattern claro
3. **Testabilidade** - Design orientado a testes
4. **Stateless** - Operacoes sem estado persistente em memoria
5. **Database-First** - SQLite como fonte de verdade
6. **User Control** - Sistema informa, usuario decide

### 1.2. Caracteristicas Principais

- **CLI-First**: Interface de linha de comando como cidadao de primeira classe
- **Embedded Database**: SQLite sem servidor externo
- **Offline-First**: Funciona perfeitamente sem conexao
- **Sync-Ready**: Arquitetura preparada para sincronizacao futura
- **Logging Estruturado**: Observabilidade desde o inicio

### 1.3. Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                      Usuario (CLI)                          │
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

## 2. Filosofia de Controle do Usuario

### 2.1. Principio Fundamental

O TimeBlock e construido sobre o principio de que sua funcao e **informar, sugerir e facilitar, mas NUNCA decidir**. Cada alteracao na agenda do usuario requer aprovacao explicita.

### 2.2. O Problema que Evitamos

Muitos sistemas de produtividade tentam ser "inteligentes" tomando decisoes automaticas. Eles reordenam tarefas, ajustam prioridades e movem eventos baseados em algoritmos que presumem entender o contexto completo da vida do usuario.

**Exemplo do problema:**

- Sistema detecta que usuario executa "Academia" as 18h em vez das 7h planejadas
- Sistema "inteligente" move automaticamente futuras instancias para 18h
- **Problema:** Usuario esta temporariamente ajustando devido a projeto com deadline, mas seu objetivo real continua sendo ir a academia de manha
- Sistema reforcou comportamento nao desejado

### 2.3. Nossa Solucao: Informacao sem Imposicao

**Deteccao de Conflitos:**

- Sistema detecta sobreposicao temporal
- Apresenta informacoes claras
- NAO propoe solucao automaticamente

**Ajuste de Horarios:**

- Ajuste em um dia afeta apenas aquele dia
- Plano ideal (Routine) permanece intocado
- Cada dia e nova oportunidade de seguir a Routine

**Priorizacao:**

- Sistema NAO aplica regras de priorizacao automatica
- Apresenta eventos e permite usuario escolher

### 2.4. Routine como Norte Verdadeiro

```
┌─────────────────────────────────────────────────────┐
│                    ROUTINE                          │
│              (Plano Ideal - Imutavel)               │
│                                                     │
│   Academia: 07:00-08:00 WEEKDAYS                    │
│   Meditacao: 06:30-07:00 EVERYDAY                   │
└─────────────────────────────────────────────────────┘
                          │
                          │ Gera instancias
                          v
┌─────────────────────────────────────────────────────┐
│               HABIT INSTANCES                       │
│            (Realidade - Flexivel)                   │
│                                                     │
│   Seg 25/11: Academia 07:00 [DONE]                  │
│   Ter 26/11: Academia 18:00 [DONE] (ajustado)       │
│   Qua 27/11: Academia 07:00 [PENDING]               │
└─────────────────────────────────────────────────────┘
```

**Separacao:**

- **Routine:** Intencoes e objetivos (o que usuario aspira)
- **HabitInstance:** O que realmente acontece (ajustes, atrasos)

### 2.5. Implicacoes no Codigo

#### **Principio 1: Deteccao sem Acao**

```python
# CORRETO: Detecta e retorna informacoes
def detect_conflicts(event_id: int) -> list[Conflict]:
    conflicts = query_overlapping_events(event_id)
    return conflicts  # Apenas retorna, NAO modifica

# CORRETO: Acao separada que requer confirmacao
def apply_user_resolution(conflict_id: int, user_choice: Resolution):
    if user_choice.confirmed:
        apply_changes(user_choice.changes)
```

```python
# INCORRETO: Deteccao e acao misturadas
def detect_and_resolve_conflicts(event_id: int):
    conflicts = query_overlapping_events(event_id)
    for conflict in conflicts:
        auto_resolve(conflict)  # NUNCA fazer isso
```

#### **Principio 2: Preservacao de Template**

```python
# CORRETO: Ajuste afeta apenas instancia
def adjust_instance(instance_id: int, new_start: time):
    instance = get_instance(instance_id)
    instance.scheduled_start = new_start
    # Habit (template) permanece inalterado
    save(instance)
```

#### **Principio 3: Confirmacao Explicita**

```python
# CORRETO: Requer confirmacao
if conflicts_detected:
    print("Conflitos encontrados:")
    for c in conflicts:
        print(f"  - {c.description}")

    if click.confirm("Continuar mesmo assim?"):
        proceed()
```

---

## 3. Stack Tecnologica

### 3.1. Core

| Componente | Tecnologia | Versao | Razao                     |
| ---------- | ---------- | ------ | ------------------------- |
| Linguagem  | Python     | 3.13+  | Produtividade, ecosystem  |
| CLI        | Typer      | 0.x    | Type hints, auto-complete |
| ORM        | SQLModel   | 0.0.x  | Pydantic + SQLAlchemy     |
| Database   | SQLite     | 3.x    | Zero-config, portavel     |
| Output     | Rich       | 13.x   | Terminal formatting       |

### 3.2. Desenvolvimento

| Componente | Tecnologia | Razao                  |
| ---------- | ---------- | ---------------------- |
| Testes     | pytest     | Padrao de facto Python |
| Coverage   | pytest-cov | Metricas de cobertura  |
| Linting    | ruff       | Rapido, moderno        |
| Type Check | mypy       | Seguranca de tipos     |
| VCS        | Git        | Gitflow workflow       |

### 3.3. Dependencias Principais

```
sqlmodel>=0.0.14
typer>=0.9.0
rich>=13.0.0
python-dateutil>=2.8.0
```

**Filosofia:** Minimas dependencias, maxima estabilidade.

---

## 4. Camadas da Aplicacao

### 4.1. CLI Commands Layer

**Localizacao:** `cli/src/timeblock/commands/`

**Responsabilidade:** Interface com usuario, parsing de argumentos.

**Estrutura:**

```
commands/
├── habit.py       # Comandos de habitos
├── task.py        # Comandos de tarefas
├── routine.py     # Comandos de rotinas
├── timer.py       # Comandos de timer
├── report.py      # Relatorios
└── ...
```

**Principios:**

- Commands sao thin wrappers
- Validacao basica de input
- Delegam para Services
- Formatam output para usuario

**Exemplo:**

```python
@app.command()
def create(
    title: str = typer.Argument(...),
    start: str = typer.Option(..., "--start"),
):
    """Cria novo habito."""
    # 1. Valida input basico
    if not title:
        console.print("[ERROR] Titulo obrigatorio")
        raise typer.Exit(1)

    # 2. Delega para service
    habit = HabitService.create_habit(
        title=title,
        scheduled_start=parse_time(start)
    )

    # 3. Formata output
    console.print(f"[OK] Habito criado: {habit.title}")
```

### 4.2. Services Layer

**Localizacao:** `cli/src/timeblock/services/`

**Responsabilidade:** Logica de negocio, orquestracao.

**Estrutura:**

```
services/
├── habit_service.py             # CRUD habitos
├── habit_instance_service.py    # Gestao de instancias
├── event_reordering_service.py  # Deteccao de conflitos
├── task_service.py              # Gestao de tarefas
├── routine_service.py           # Gestao de rotinas
├── timer_service.py             # Timer tracking
└── ...
```

**Principios:**

- Stateless (sem estado interno)
- Metodos estaticos ou de classe
- Transacoes DB isoladas
- Business rules centralizadas

**Exemplo:**

```python
class HabitInstanceService:
    """Service para gestao de instancias de habitos."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date
    ) -> list[HabitInstance]:
        """Gera instancias baseadas em recorrencia.

        Args:
            habit_id: ID do habito template
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
- Concorrencia (sem race conditions)
- Simplicidade (facil entender fluxo)

### 4.3. Models Layer

**Localizacao:** `cli/src/timeblock/models/`

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

**Principios:**

- SQLModel (Pydantic + SQLAlchemy)
- Type hints completos
- Validacao automatica
- Relationships explicitos

**Exemplo:**

```python
class HabitInstance(SQLModel, table=True):
    """Instancia de habito em data especifica."""

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
        """Verifica se instancia esta atrasada."""
        if self.status != Status.PENDING:
            return False
        now = datetime.now()
        scheduled = datetime.combine(self.date, self.scheduled_start)
        return now > scheduled
```

### 4.4. Database Layer

**Localizacao:** `cli/src/timeblock/database/`

**Responsabilidade:** Gerenciamento de conexoes, migrations.

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
    """Context manager para sessao SQLite.

    Garante:
    - Conexao unica por operacao
    - Cleanup automatico
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

**Localizacao:** `cli/src/timeblock/utils/`

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

**Principios:**

- Pure functions quando possivel
- Sem side effects
- Altamente testaveis
- Reutilizaveis

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

**HabitInstance (Ocorrencia):**

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

**Task (Evento Unico):**

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

### 6.1. Criacao e Geracao de Instancias

```
Usuario CLI
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
└────────┬─────────────────┘  6. Para proximos 3 meses
         │
         v
┌──────────────────────┐
│     Database         │  7. Persiste instancias
└──────────────────────┘
```

### 6.2. Deteccao de Conflitos

```
Usuario ajusta horario
    │
    │ timeblock habit edit <id> --start 09:00
    v
┌────────────────────────────┐
│ HabitInstanceService       │  1. Atualiza horario
└──────────┬─────────────────┘
           │
           v
┌────────────────────────────┐
│ EventReorderingService     │  2. Detecta conflitos
└──────────┬─────────────────┘  3. Lista sobreposicoes
           │
           v
      Conflitos?
       /      \
    Sim       Nao
     │         │
     v         └──→ [OK] Atualizado
┌──────────────────────┐
│ Apresenta conflitos  │  4. Mostra ao usuario
└──────────┬───────────┘  5. Pede confirmacao
           │
           v
    Usuario confirma?
       /      \
    Sim       Nao
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

## 7. Decisoes Arquiteturais

### ADR-001: SQLModel como ORM

**Decisao:** Usar SQLModel ao inves de SQLAlchemy puro.

**Razao:**

- Pydantic integrado (validacao gratis)
- Type hints nativos
- API mais simples
- Serializacao JSON automatica

**Trade-offs:**

- [-] Comunidade menor
- [-] Alguns features avancados nao disponiveis

### ADR-002: Stateless Services

**Decisao:** Services sem estado interno, metodos estaticos.

**Razao:**

- Testabilidade superior
- Sem race conditions
- Fluxo facil de entender

### ADR-003: SQLite Embedded

**Decisao:** SQLite local sem servidor.

**Razao:**

- Zero configuracao
- Portabilidade total
- Suficiente para single-user

**Trade-offs:**

- [-] Sem concorrencia multi-processo

### ADR-004: Typer para CLI

**Decisao:** Usar Typer ao inves de Click puro.

**Razao:**

- Type hints nativos
- Auto-complete automatico
- Baseado em Click (compativel)

### ADR-005: Offline-First

**Decisao:** Sistema funciona 100% offline.

**Razao:**

- Independencia de conexao
- Performance garantida
- Privacidade total

### ADR-006: User Control Philosophy

**Decisao:** Sistema informa mas NAO decide.

**Razao:**

- Usuario conhece contexto completo
- Evita automacoes indesejadas
- Preserva intencao original

---

## 8. Padroes e Convencoes

### 8.1. Estrutura de Diretorios

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
│   ├── unit/              # Testes unitarios
│   ├── integration/       # Testes integracao
│   └── e2e/               # Testes end-to-end
└── docs/                  # Documentacao
```

### 8.2. Naming Conventions

**Arquivos:**

- `snake_case.py` para modulos
- `test_<module>.py` para testes

**Classes:**

- `PascalCase` para classes
- `Test<Feature>` para classes de teste

**Funcoes/Metodos:**

- `snake_case` para funcoes
- `test_<behavior>` para metodos de teste

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
    """Calcula streak atual do habito.

    Conta dias consecutivos com status DONE,
    do mais recente para tras.

    Args:
        habit_id: ID do habito

    Returns:
        Numero de dias consecutivos

    Raises:
        ValueError: Se habit_id invalido
    """
    pass
```

### 8.6. Padroes de Teste

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
- Metodos: `test_br_<domain>_<number>_<scenario>`

**Padrao BDD:**

```python
def test_br_streak_001_counts_done(self):
    """Streak conta dias consecutivos DONE.

    DADO: Habito com 5 instancias DONE consecutivas
    QUANDO: Calcular streak
    ENTAO: Deve retornar 5

    BR: BR-STREAK-001
    """
    # Arrange
    # Act
    # Assert
```

### 8.7. Git Workflow

**Branches:**

- `main` - producao
- `develop` - desenvolvimento
- `feat/*` - features
- `fix/*` - bugfixes
- `refactor/*` - refatoracoes

**Commits:**

```
type(scope): Descricao em Portugues

Corpo opcional

Footer opcional
```

**Types:** feat, fix, refactor, test, docs, chore

---

## 9. Evolucao Futura

### v1.4.0 - Consolidacao

- Documentacao consolidada
- Testes reorganizados
- CI/CD pipeline

### v2.0.0 - Sincronizacao

- Sync Linux <-> Android (Termux)
- UUID como primary keys
- Conflict resolution
- Queue-based sync

### v3.0.0 - Analytics

- Dashboard de metricas
- Streak tracking avancado
- Reports automaticos

---

## Referencias

- **SQLModel:** <https://sqlmodel.tiangolo.com/>
- **Typer:** <https://typer.tiangolo.com/>
- **Rich:** <https://rich.readthedocs.io/>
- **Atomic Habits:** James Clear
- **Business Rules:** `docs/core/business-rules.md`

---

- **Documento consolidado em:** 28 de Novembro de 2025
- **Este e o SSOT para arquitetura do sistema**
