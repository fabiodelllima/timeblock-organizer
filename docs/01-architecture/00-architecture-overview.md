# Arquitetura TimeBlock Organizer

- **Versão:** 1.2.0
- **Data:** 03 de Novembro de 2025
- **Status:** PRODUÇÃO

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Stack](#stack)
3. [Camadas da Aplicação](#camadas-da-aplicação)
4. [Modelos de Dados](#modelos-de-dados)
5. [Fluxos Principais](#fluxos-principais)
6. [Decisões Arquiteturais](#decisões-arquiteturais)
7. [Padrões e Convenções](#padrões-e-convenções)

---

## Visão Geral

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo.

### Princípios Arquiteturais

1. **Simplicidade** - Arquitetura direta sem over-engineering
2. **Separação de Responsabilidades** - Service pattern claro
3. **Testabilidade** - Design orientado a testes
4. **Stateless** - Operações sem estado persistente em memória
5. **Database-First** - SQLite como fonte de verdade

### Características Principais

- **CLI-First**: Interface de linha de comando como cidadão de primeira classe
- **Embedded Database**: SQLite sem servidor externo
- **Sync-Ready**: Arquitetura preparada para sincronização futura
- **Logging Estruturado**: Observabilidade desde o início

---

## Stack

### Core

| Componente    | Tecnologia     | Versão | Razão                            |
| ------------- | -------------- | ------ | -------------------------------- |
| Linguagem     | Python         | 3.13+  | Produtividade, rich ecosystem    |
| CLI Framework | Click          | 8.x    | Melhor DX para CLIs Python       |
| ORM           | SQLModel       | 0.0.x  | Pydantic + SQLAlchemy integrados |
| Database      | SQLite         | 3.x    | Zero-config, portável, confiável |
| Logging       | stdlib logging | 3.13   | Padrão, sem deps extras          |

### Desenvolvimento

| Componente    | Tecnologia | Razão                  |
| ------------- | ---------- | ---------------------- |
| Testes        | pytest     | Padrão de facto Python |
| Coverage      | pytest-cov | Métricas de cobertura  |
| Linting       | ruff       | Rápido, moderno        |
| Type Checking | mypy       | Segurança de tipos     |
| Versionamento | Git        | Gitflow workflow       |

### Dependências Principais

```terminal
sqlmodel>=0.0.14
click>=8.1.0
python-dateutil>=2.8.0
```

**Filosofia:** Mínimas dependências, máxima estabilidade.

---

## Camadas da Aplicação

### Arquitetura em Camadas

```terminal
┌─────────────────────────────────────┐
│         CLI Commands Layer          │  User Interface
│   (click, command parsing)          │
├─────────────────────────────────────┤
│         Services Layer              │  Business Logic
│   (domain logic, orchestration)     │
├─────────────────────────────────────┤
│         Models Layer                │  Data Structure
│   (SQLModel, relationships)         │
├─────────────────────────────────────┤
│         Database Layer              │  Persistence
│   (SQLite, engine management)       │
└─────────────────────────────────────┘
│         Utils Layer                 │  Cross-cutting
│   (logging, formatters, helpers)    │
└─────────────────────────────────────┘
```

### 1. CLI Commands Layer

**Localização:** `cli/src/timeblock/commands/`

**Responsabilidade:** Interface com usuário, parsing de argumentos.

**Estrutura:**

```terminal
commands/
├── habit.py       # Comandos de hábitos
├── task.py        # Comandos de tarefas
├── routine.py     # Comandos de rotinas
├── timer.py       # Comandos de timer
└── ...
```

**Princípios:**

- Commands são thin wrappers
- Validação básica de input
- Delegam para Services
- Formatam output para usuário

**Exemplo:**

```python
@click.command()
@click.argument('title')
@click.option('--start', type=click.DateTime())
def habit_create(title: str, start: datetime):
    """Cria novo hábito."""
    # 1. Valida input básico
    if not title:
        click.echo("Título obrigatório")
        return

    # 2. Delega para service
    habit = HabitService.create_habit(
        title=title,
        scheduled_start=start.time()
    )

    # 3. Formata output
    click.echo(f"Hábito criado: {habit.title}")
```

### 2. Services Layer

**Localização:** `cli/src/timeblock/services/`

**Responsabilidade:** Lógica de negócio, orquestração.

**Estrutura:**

```terminal
services/
├── habit_instance_service.py     # Gestão de instâncias
├── event_reordering_service.py   # Detecção de conflitos
├── task_service.py                # Gestão de tarefas
└── ...
```

**Princípios:**

- Stateless (sem estado interno)
- Métodos estáticos
- Database transactions isoladas
- Business rules centralizadas

**Exemplo:**

```python
class HabitInstanceService:
    """Service para gestão de instâncias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date
    ) -> list[HabitInstance]:
        """Gera instâncias baseadas em recorrência."""
        # Business logic aqui
        # Logging estruturado
        # Transação DB isolada
        pass
```

**Por que Stateless:**

- Testabilidade (sem setup/teardown complexo)
- Concorrência (sem race conditions)
- Simplicidade (fácil entender fluxo)

### 3. Models Layer

**Localização:** `cli/src/timeblock/models/`

**Responsabilidade:** Estrutura de dados, relacionamentos.

**Estrutura:**

```
models/
├── habit.py              # Modelo Habit
├── habit_instance.py     # Modelo HabitInstance
├── task.py               # Modelo Task
├── routine.py            # Modelo Routine
└── ...
```

**Princípios:**

- SQLModel (Pydantic + SQLAlchemy)
- Type hints completos
- Validação automática
- Relationships explícitos

**Exemplo:**

```python
class HabitInstance(SQLModel, table=True):
    """Instância de hábito em data específica."""

    __tablename__ = "habitinstance"

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date = Field(index=True)
    status: HabitInstanceStatus = Field(default=HabitInstanceStatus.PLANNED)

    # Relationship
    habit: Optional["Habit"] = Relationship(back_populates="instances")

    @property
    def is_overdue(self) -> bool:
        """Business logic no modelo quando apropriado."""
        if self.status != HabitInstanceStatus.PLANNED:
            return False
        return datetime.now() > datetime.combine(self.date, self.scheduled_start)
```

**SQLModel Benefits:**

- Validação Pydantic automática
- Type safety
- Serialização JSON grátis
- SQLAlchemy power quando necessário

### 4. Database Layer

**Localização:** `cli/src/timeblock/database/`

**Responsabilidade:** Gerenciamento de conexões, migrations.

**Estrutura:**

```
database/
├── engine.py       # Engine management
└── migrations.py   # Schema migrations (simples)
```

**Engine Management:**

```python
@contextmanager
def get_engine_context():
    """Context manager para engine SQLite.

    Garante:
    - Conexão única por operação
    - Cleanup automático
    - Thread-safety
    """
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )
    try:
        yield engine
    finally:
        engine.dispose()
```

**Por que Context Manager:**

- Cleanup garantido
- Resource management automático
- Previne connection leaks

### 5. Utils Layer

**Localização:** `cli/src/timeblock/utils/`

**Responsabilidade:** Funcionalidades transversais.

**Estrutura:**

```
utils/
├── logger.py             # Logging estruturado
├── formatters.py         # Output formatters
├── date_helpers.py       # Date utilities
└── validators.py         # Input validation
```

**Princípios:**

- Pure functions quando possível
- Sem side effects
- Altamente testáveis
- Reutilizáveis

---

## Modelos de Dados

### Diagrama ER Simplificado

```
┌─────────────┐
│   Routine   │
└──────┬──────┘
       │ 1:N
       ↓
┌─────────────┐      1:N     ┌──────────────────┐
│    Habit    │─────────────→│  HabitInstance   │
└─────────────┘              └──────────────────┘
                                      │
                                    1:1
                                      ↓
                              ┌──────────────┐
                              │   TimeLog    │
                              └──────────────┘

┌─────────────┐
│    Task     │
└──────┬──────┘
       │ N:M
       ↓
┌─────────────┐
│     Tag     │
└─────────────┘

┌─────────────┐
│    Event    │  (Union: Task | HabitInstance)
└─────────────┘
```

### Modelos Core

#### Habit (Template)

```python
class Habit(SQLModel, table=True):
    """Template de hábito recorrente."""
    id: int
    routine_id: int
    title: str
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence  # EVERYDAY, WEEKDAYS, etc

    # Relationships
    routine: Routine
    instances: list[HabitInstance]
```

**Conceito:** Habit é o molde, HabitInstance é a ocorrência.

#### HabitInstance (Occurrence)

```python
class HabitInstance(SQLModel, table=True):
    """Ocorrência específica de hábito."""
    id: int
    habit_id: int
    date: date
    scheduled_start: time
    scheduled_end: time
    status: HabitInstanceStatus  # PLANNED, COMPLETED, SKIPPED
    manually_adjusted: bool
    user_override: bool

    # Relationship
    habit: Habit
```

**Conceito:** Átomo do sistema. Menor unidade acionável.

#### Task (One-time Action)

```python
class Task(SQLModel, table=True):
    """Tarefa única (não recorrente)."""
    id: int
    title: str
    scheduled_start: datetime
    duration: int  # minutos
    status: str

    # Relationships
    tags: list[Tag]
```

**Diferença Habit vs Task:**

- Habit: Recorrente, parte de identidade
- Task: Única, objetivo específico

#### Routine (Grouping)

```python
class Routine(SQLModel, table=True):
    """Agrupamento de hábitos relacionados."""
    id: int
    name: str

    # Relationship
    habits: list[Habit]
```

**Conceito:** "Rotina Matinal" agrupa múltiplos hábitos.

---

## Fluxos Principais

### Fluxo 1: Criação e Geração de Instâncias

```
Usuario CLI
    │
    │ timeblock habit create "Exercício" --start 07:00
    ↓
┌──────────────────┐
│  habit.py (CLI)  │
└────────┬─────────┘
         │ HabitService.create()
         ↓
┌──────────────────────┐
│   HabitService       │  1. Valida dados
└────────┬─────────────┘  2. Cria Habit
         │                3. Persiste DB
         ↓
┌──────────────────────┐
│      Database        │
└──────────────────────┘

... tempo passa ...

timeblock habit generate --days 7
    │
    ↓
┌────────────────────────────┐
│ HabitInstanceService       │  1. Lista Habits
└──────────┬─────────────────┘  2. Para cada Habit:
           │                    3. Calcula datas (recurrence)
           │                    4. Cria HabitInstances
           ↓
┌──────────────────────┐
│  [HabitInstance]     │  7 instâncias criadas
└──────────────────────┘
```

**Código:**

```python
# 1. Criar Habit (template)
habit = HabitService.create_habit(
    title="Exercício",
    start=time(7, 0),
    duration=60,
    recurrence=Recurrence.EVERYDAY
)

# 2. Gerar instâncias (7 dias)
instances = HabitInstanceService.generate_instances(
    habit_id=habit.id,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=6)
)
# Resultado: 7 HabitInstances criadas
```

### Fluxo 2: Detecção de Conflitos e Reordenamento

```
Usuario ajusta horário de HabitInstance
    │
    │ timeblock habit adjust <id> --start 09:00
    ↓
┌────────────────────────────┐
│ HabitInstanceService       │  1. Atualiza horário
└──────────┬─────────────────┘  2. Detecta conflitos
           │
           ↓
┌────────────────────────────┐
│ EventReorderingService     │  3. Lista eventos no período
└──────────┬─────────────────┘  4. Identifica overlaps
           │
           ↓
      Conflitos?
       /      \
    Sim       Não
     │         │
     ↓         └──→ Retorna instância atualizada
┌──────────────────────┐
│ propose_reordering() │  5. Cria proposta
└──────────┬───────────┘  6. Sugere novos horários
           │
           ↓
┌──────────────────────┐
│  ReorderingProposal  │  Usuario decide aceitar/rejeitar
└──────────────────────┘
```

**Código:**

```python
# 1. Usuario ajusta
updated, proposal = HabitInstanceService.adjust_instance_time(
    instance_id=123,
    new_start=time(9, 0),
    new_end=time(10, 0)
)

# 2. Se conflito detectado
if proposal:
    print("Conflitos detectados:")
    for conflict in proposal.conflicts:
        print(f"  - {conflict.event_type} at {conflict.time_range}")

    print("\nProposta de reorganização:")
    for item in proposal.reordered_events:
        print(f"  - {item.title}: {item.new_start} - {item.new_end}")

    # Usuario decide
    if click.confirm("Aceitar proposta?"):
        proposal.accept()
```

### Fluxo 3: Logging de Operações

```
Qualquer operação de Service
    │
    ↓
┌──────────────────────┐
│  get_logger()        │  Logger configurado
└──────────┬───────────┘
           │
           ↓
┌─────────────────────────────-─┐
│  [timestamp] [level] [msg]    │
│  [2025-11-03 18:45:12] [INFO] │  Log estruturado
│  [HabitInstanceService]       │
│  Criadas 7 instâncias         │
└──────────┬──────────────────-─┘
           │
           ├──→ Console (dev)
           │
           └──→ File (prod)
                 ↓
            timeblock.log
            (com rotação 10MB)
```

**Benefícios:**

- Debugging facilitado
- Auditoria de operações
- Monitoramento de produção

---

## Decisões Arquiteturais

### ADR-001: SQLModel como ORM

**Decisão:** Usar SQLModel ao invés de SQLAlchemy puro.

**Contexto:**

- Projeto novo sem legado
- Type safety importante
- Validação automática desejável

**Razão:**

- Pydantic integrado (validação grátis)
- Type hints nativos
- API mais simples que SQLAlchemy
- Serialização JSON automática

**Trade-offs:**

- Comunidade menor que SQLAlchemy
- Alguns features avançados não disponíveis
- Documentação ainda em crescimento

**Decisão Final:** ACEITO
**Resultado:** Produtividade aumentada, menos boilerplate.

### ADR-002: Service Pattern Stateless

**Decisão:** Services são classes com métodos estáticos.

**Contexto:**

- CLI não tem sessão persistente
- Cada comando é invocação isolada

**Razão:**

- Testabilidade (sem setup complexo)
- Simplicidade (sem lifecycle management)
- Concorrência (sem race conditions)

**Alternativas Consideradas:**

- Services com instâncias (rejeitado - overhead desnecessário)
- Funções soltas (rejeitado - sem organização)

**Decisão Final:** ACEITO
**Resultado:** Código mais limpo e testável.

### ADR-003: SQLite como Database

**Decisão:** SQLite sem servidor externo.

**Contexto:**

- Aplicação CLI single-user
- Sincronização futura planejada

**Razão:**

- Zero-config (sem setup)
- Portável (arquivo único)
- Confiável (battle-tested)
- Adequado para volume esperado

**Trade-offs:**

- Não suporta múltiplos writes concorrentes
- Sem replicação nativa

**Mitigação:**

- Single-user primary use case
- Sync v2.0 será file-based ou API

**Decisão Final:** ACEITO
**Resultado:** Experiência de usuário simplificada.

### ADR-004: Click para CLI

**Decisão:** Click ao invés de argparse ou typer.

**Contexto:**

- CLI complexo com subcomandos
- Boa UX crítica

**Razão:**

- Melhor DX para CLIs complexos
- Decorators elegantes
- Auto-help generation
- Testing utilities built-in

**Decisão Final:** ACEITO
**Resultado:** CLI bem estruturado e testável.

---

## Padrões e Convenções

### Convenções de Código

**Naming:**

- Classes: PascalCase (`HabitInstance`)
- Funções: snake_case (`generate_instances`)
- Constantes: UPPER_SNAKE (`MAX_INSTANCES`)
- Privados: prefixo `_` (`_should_create`)

**Imports:**

```python
# Standard library
from datetime import date, time

# Third-party
from sqlmodel import Session, select

# Local
from src.timeblock.models import Habit
from src.timeblock.services import HabitService
```

**Type Hints:**

```python
def generate_instances(
    habit_id: int,
    start_date: date,
    end_date: date
) -> list[HabitInstance]:
    """Sempre type hints completos."""
    pass
```

### Padrões de Teste

**Estrutura:**

```
tests/
├── unit/              # Testes isolados
│   ├── test_models/
│   ├── test_services/
│   └── test_utils/
└── integration/       # Testes com DB
    └── test_flows/
```

**Naming:**

- Arquivos: `test_<module>.py`
- Classes: `Test<Feature>`
- Métodos: `test_<behavior>`

**Padrão BDD:**

```python
def test_generate_everyday_habit(self, everyday_habit):
    """Gera instâncias para hábito EVERYDAY durante 7 dias.

    DADO: Hábito com recorrência EVERYDAY
    QUANDO: Gerar instâncias para período de 7 dias
    ENTÃO: Deve criar exatamente 7 instâncias

    Regra de Negócio: Hábitos EVERYDAY geram uma instância por dia.
    """
    # Preparação
    # Ação
    # Verificação
```

### Git Workflow

**Branches:**

- `main` - produção
- `develop` - desenvolvimento
- `feat/*` - features
- `fix/*` - bugfixes

**Commits:**

```
type(scope): Descrição

Corpo (opcional)

Footer (opcional)
```

**Types:**

- `feat` - nova feature
- `fix` - correção de bug
- `refactor` - refatoração
- `test` - testes
- `docs` - documentação

---

## Evolução Futura

### v1.3.0 - Ambientes e Logging Avançado

**Planejado:**

- Ambientes formalizados (dev/test/prod)
- Alembic para migrations
- Logging JSON estruturado
- Métricas e dashboards

### v2.0 - Sincronização

**Planejado:**

- Sync Linux ↔ Android (Termux)
- API REST opcional
- Conflict resolution
- Offline-first

### v3.0 - Gamification

**Planejado:**

- Achievements system
- Streak tracking avançado
- Social features (opcional)
- Analytics dashboard

---

## Referências

- **SQLModel:** <https://sqlmodel.tiangolo.com/>
- **Click:** <https://click.palletsprojects.com/>
- **Python Logging:** <https://docs.python.org/3/library/logging.html>
- **Atomic Habits:** `docs/01-guides/PHILOSOPHY.md`

---

**Última Atualização:** 03 de Novembro de 2025

**Versão:** 1.2.0

**Próxima Revisão:** v1.3.0 (ambientes formalizados)
