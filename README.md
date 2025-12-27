# TimeBlock Organizer

> Gerenciador de tempo CLI baseado em time blocking e hábitos atômicos

```
╔═══════════════════════════════════════════════════════════════╗
║  TimeBlock Organizer v2.0.0                                   ║
║  ───────────────────────────────────────────────────────────  ║
║  [x] 492 testes  [x] 99% cobertura  [x] 25 ADRs  [x] 50+ BRs  ║
╚═══════════════════════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-492%20passing-success.svg)](cli/tests/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](cli/tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Visão Geral

TimeBlock Organizer é uma ferramenta CLI para gerenciamento de tempo usando time blocking e inspirada em "Atomic Habits" de James Clear. O sistema aprende com padrões do usuário ao invés de impor agendamentos rígidos.

**Filosofia:** Usuário no controle. Conflitos são informados, nunca bloqueados.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TIMEBLOCK ORGANIZER                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   ROUTINE   │───>│    HABIT    │───>│ HABIT ATOM  │              │
│  │  (coleção)  │    │  (template) │    │ (instância) │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│         │                  │                  │                     │
│         │                  │                  v                     │
│         │                  │           ┌─────────────┐              │
│         │                  │           │    TIMER    │              │
│         │                  │           │  (tracking) │              │
│         │                  │           └─────────────┘              │
│         │                  │                                        │
│         v                  v                                        │
│  ┌─────────────────────────────────────────────────────┐            │
│  │                      TASK                           │            │
│  │               (evento pontual)                      │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
│   CLI    │────>│ COMMANDS │────>│ SERVICES │────>│   MODELS   │
│  (Typer) │     │          │     │          │     │ (SQLModel) │
└──────────┘     └──────────┘     └──────────┘     └────────────┘
                                        │                │
                                        v                v
                                  ┌──────────┐     ┌──────────┐
                                  │  UTILS   │     │  SQLite  │
                                  │          │     │    DB    │
                                  └──────────┘     └──────────┘
```

### Camadas

```
╔═══════════════════════════════════════════════════════════════════╗
║ PRESENTATION                                                      ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ commands/  │ routine, habit, task, timer, tag, report         │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════╣
║ BUSINESS LOGIC                                                    ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ services/  │ routine, habit, habit_instance, task, timer...   │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════╣
║ DATA ACCESS                                                       ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ models/    │ Routine, Habit, HabitInstance, Task, TimeLog     │ ║
║ │ database/  │ engine, migrations                               │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Estados do Sistema

### HabitInstance Status

```
                    ┌─────────────┐
                    │   PENDING   │
                    │  (aguarda)  │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           v               v               v
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │    DONE     │ │  NOT_DONE   │ │   OVERDUE   │
    │ (completo)  │ │  (pulado)   │ │  (atrasado) │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │
           v               v
    ┌─────────────┐ ┌─────────────────────┐
    │  Substatus  │ │  Substatus          │
    ├─────────────┤ ├─────────────────────┤
    │ FULL        │ │ SKIPPED_JUSTIFIED   │
    │ PARTIAL     │ │ SKIPPED_UNJUSTIFIED │
    │ OVERDONE    │ │ IGNORED             │
    │ EXCESSIVE   │ └─────────────────────┘
    └─────────────┘

```

### Timer Flow

```
    ┌─────────┐
    │  IDLE   │
    └────┬────┘
         │ start
         v
    ┌─────────┐
    │ RUNNING │<─────────┐
    └────┬────┘          │
         │               │
    ┌────┴────┐     resume
    │         │          │
    v         v          │
┌───────┐ ┌───────┐      │
│ stop  │ │ pause │──────┘
└───┬───┘ └───────┘
    │
    v
┌─────────┐
│  DONE   │
└─────────┘
```

---

## Estrutura do Projeto

```
timeblock-organizer/
├── cli/
│   ├── src/timeblock/
│   │   ├── commands/          # Comandos CLI
│   │   │   ├── routine.py     #   Gerencia rotinas
│   │   │   ├── habit.py       #   Gerencia hábitos e instâncias
│   │   │   ├── task.py        #   Gerencia tarefas
│   │   │   ├── timer.py       #   Controle de timer
│   │   │   ├── tag.py         #   Gerencia tags
│   │   │   └── report.py      #   Relatórios
│   │   │
│   │   ├── services/          # Camada de negócio
│   │   │   ├── routine_service.py
│   │   │   ├── habit_service.py
│   │   │   ├── habit_instance_service.py
│   │   │   ├── task_service.py
│   │   │   ├── timer_service.py
│   │   │   └── tag_service.py
│   │   │
│   │   ├── models/            # Modelos de dados
│   │   │   ├── routine.py
│   │   │   ├── habit.py
│   │   │   ├── habit_instance.py
│   │   │   ├── task.py
│   │   │   ├── time_log.py
│   │   │   ├── tag.py
│   │   │   └── enums.py
│   │   │
│   │   ├── database/          # Persistência
│   │   │   ├── engine.py
│   │   │   └── migrations/
│   │   │
│   │   └── utils/             # Helpers
│   │
│   └── tests/                 # 492 testes
│       ├── unit/              #   ~350 (70%)
│       ├── integration/       #   ~120 (25%)
│       ├── e2e/               #   ~22 (5%)
│       └── bdd/               #   Cenários Gherkin
│
├── docs/
│   └── core/                  # Documentação válida
│       ├── architecture.md    #   29 KB
│       ├── business-rules.md  #   44 KB (50+ BRs)
│       ├── cli-reference.md   #   65 KB
│       └── workflows.md       #   133 KB
│
└── scripts/                   # Automação
```

---

## Instalação

```bash
git clone https://github.com/fabiodelllima/timeblock-organizer.git
cd timeblock-organizer/cli

python -m venv venv
source venv/bin/activate

pip install -e .
```

---

## Comandos

### Visão Geral

```
┌────────────────────────────────────────────────────────────────────┐
│ RECURSO      │ DESCRIÇÃO                                           │
├────────────────────────────────────────────────────────────────────┤
│ routine      │ Gerencia rotinas (coleções de hábitos)              │
│ habit        │ Gerencia hábitos (templates recorrentes)            │
│ habit atom   │ Gerencia instâncias de hábitos (ocorrências)        │
│ task         │ Gerencia tarefas (eventos únicos)                   │
│ timer        │ Controla cronômetro                                 │
│ tag          │ Gerencia categorias (cor + título)                  │
│ report       │ Gera relatórios de produtividade                    │
└────────────────────────────────────────────────────────────────────┘
```

### Comandos por Recurso

```
routine
├── create     Cria nova rotina
├── edit       Edita rotina existente
├── delete     Remove rotina
├── list       Lista rotinas
├── activate   Ativa rotina
└── deactivate Desativa rotina

habit
├── create     Cria novo hábito
├── edit       Edita hábito existente
├── delete     Remove hábito
├── list       Lista hábitos
├── renew      Renova instâncias
├── details    Mostra detalhes
└── skip       Wizard para pular instância

habit atom
├── create     Cria instância avulsa
├── edit       Edita instância
├── delete     Remove instância
├── list       Lista instâncias
├── skip       Pula instância
└── log        Registra tempo manualmente

task
├── create     Cria nova tarefa
├── edit       Edita tarefa
├── delete     Remove tarefa
├── list       Lista tarefas
├── complete   Marca como concluída
└── uncheck    Reverte para pendente

timer
├── start      Inicia cronômetro
├── pause      Pausa cronômetro
├── resume     Retoma cronômetro
├── stop       Para e salva
├── reset      Cancela sem salvar
└── status     Mostra status atual
```

### Exemplos

```bash
# Rotinas
timeblock routine create "Rotina Matinal"
timeblock routine activate 1
timeblock routine list

# Hábitos
timeblock habit create --title "Academia" --start 07:00 --end 08:30 --repeat weekdays
timeblock habit renew 1 month 3      # Renova para 3 meses
timeblock habit list

# Instâncias (habit atom)
timeblock habit atom list            # Lista instâncias de hoje
timeblock habit atom list -w         # Lista da semana
timeblock habit atom skip 42         # Pula instância

# Timer
timeblock timer start 42             # Inicia timer para instância 42
timeblock timer pause
timeblock timer resume
timeblock timer stop

# Tarefas
timeblock task create -l "Dentista" -D "2025-12-01 14:30"
timeblock task list
timeblock task complete 1
```

---

## Stack Tecnológico

```
┌────────────────────────────────────────────────────────────────────┐
│ COMPONENTE      │ TECNOLOGIA           │ VERSÃO                    │
├────────────────────────────────────────────────────────────────────┤
│ Runtime         │ Python               │ 3.13+                     │
│ ORM             │ SQLModel             │ 0.0.14+                   │
│ CLI Framework   │ Typer                │ 0.9.0+                    │
│ Terminal UI     │ Rich                 │ 13.7.0+                   │
│ Database        │ SQLite               │ 3.x                       │
│ Testing         │ pytest + pytest-cov  │ 8.0.0+                    │
│ Linting         │ ruff                 │ 0.1.0+                    │
│ Type Checking   │ mypy                 │ 1.8.0+                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Métricas

```
╔════════════════════════════════════════════════════════════════════╗
║                         MÉTRICAS v2.0.0                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║   Testes          492        ████████████████████████████  100%    ║
║   Cobertura       99%        ███████████████████████████░   99%    ║
║   Modelos         7+1        ████████░░░░░░░░░░░░░░░░░░░░   27%    ║
║   Services        8          ████████░░░░░░░░░░░░░░░░░░░░   27%    ║
║   ADRs            24         ██████████████████████░░░░░░   73%    ║
║   Business Rules  50+        ██████████████████████████░░   87%    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Documentação

A documentação válida está consolidada em `docs/core/`:

```
docs/core/
├── architecture.md     # Stack, camadas, princípios      (29 KB)
├── business-rules.md   # 50+ BRs formalizadas            (44 KB)
├── cli-reference.md    # Referência completa CLI         (65 KB)
└── workflows.md        # Fluxos, estados, cenários BDD   (133 KB)
```

---

## Desenvolvimento

### Metodologia

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   DOCS   │────>│   BDD    │────>│   TDD    │────>│   CODE   │
│          │     │          │     │          │     │          │
│ BR-XXX   │     │ Gherkin  │     │ test_*   │     │ impl     │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

1. Documentar Business Rule (BR-DOMAIN-XXX)
2. Escrever cenário BDD (DADO/QUANDO/ENTÃO)
3. Criar teste que falha (RED)
4. Implementar código (GREEN)
5. Refatorar mantendo testes verdes

### Comandos

```bash
# Testes
python -m pytest tests/ -v
python -m pytest tests/unit/ -v --cov=src/timeblock

# Qualidade
ruff check .
ruff format .
mypy src/
```

### Commits

```
type(scope): Descrição em português

Tipos: feat, fix, refactor, test, docs, chore
```

---

## Roadmap

```
┌────────────────────────────────────────────────────────────────────┐
│ VERSÃO │ STATUS    │ FEATURES                                      │
├────────────────────────────────────────────────────────────────────┤
│ v1.0.0 │ [DONE]    │ CLI básica, CRUD eventos                      │
│ v1.1.0 │ [DONE]    │ Event reordering                              │
│ v1.2.x │ [DONE]    │ Logging, docs consolidados                    │
│ v1.3.0 │ [DONE]    │ Business rules formalizadas                   │
│ v1.4.0 │ [CURRENT] │ MVP Event Reordering, E2E tests               │
├────────────────────────────────────────────────────────────────────┤
│ v1.5.0 │ [PLANNED] │ Infra Foundation (Docker, CI/CD)              │
│ v2.0.0 │ [PLANNED] │ FastAPI REST API + Raspberry Pi Homelab       │
│ v3.0.0 │ [FUTURE]  │ Microservices Ecosystem (Kafka)               │
│ v4.0.0 │ [FUTURE]  │ Android App (Kotlin)                          │
└────────────────────────────────────────────────────────────────────┘
```
