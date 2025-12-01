# TimeBlock Organizer - Workflows Completos

**Versão:** 2.1.0

**Data:** 01 de Dezembro de 2025

**Status:** Documento Consolidado (SSOT)

**Alinhado com:** architecture.md v2.0.0, business-rules.md v3.0.0, cli-reference.md v1.4.0

---

## Índice

1. [Visão Geral e Filosofia](#1-visão-geral-e-filosofia)
2. [Entidades e Relacionamentos](#2-entidades-e-relacionamentos)
3. [Diagramas de Estado](#3-diagramas-de-estado)
4. [Fluxo 1: Setup Inicial](#4-fluxo-1-setup-inicial)
5. [Fluxo 2: Gerenciamento de Rotinas](#5-fluxo-2-gerenciamento-de-rotinas)
6. [Fluxo 3: Ciclo de Vida de Habits](#6-fluxo-3-ciclo-de-vida-de-habits)
7. [Fluxo 4: Geração de HabitInstances](#7-fluxo-4-geração-de-habitinstances)
8. [Fluxo 5: Timer Completo](#8-fluxo-5-timer-completo)
9. [Fluxo 6: Gerenciamento de Tasks](#9-fluxo-6-gerenciamento-de-tasks)
10. [Fluxo 7: Skip de HabitInstance](#10-fluxo-7-skip-de-habitinstance)
11. [Fluxo 8: Detecção de Conflitos](#11-fluxo-8-detecção-de-conflitos)
12. [Fluxo 9: Streak e Consistência](#12-fluxo-9-streak-e-consistência)
13. [Fluxo 10: Relatórios e Analytics](#13-fluxo-10-relatórios-e-analytics)
14. [Cenários BDD Completos](#14-cenários-bdd-completos)
15. [Tratamento de Erros](#15-tratamento-de-erros)
16. [Validações de Input](#16-validações-de-input)
17. [Integração entre Componentes](#17-integração-entre-componentes)
18. [Referências Cruzadas](#18-referências-cruzadas)

---

## 1. Visão Geral e Filosofia

### 1.1 Propósito do Sistema

O TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada nos princípios de:

- **Time Blocking:** Alocação de blocos de tempo para atividades específicas
- **Atomic Habits (James Clear):** Pequenas ações consistentes geram grandes resultados
- **Offline-First:** Funciona completamente sem conexão

### 1.2 Princípios Fundamentais

#### Princípio 1: Controle Explícito do Usuário

O sistema **informa, sugere e facilita, mas NUNCA decide**. Cada alteração na agenda requer aprovação explícita.

```
[SISTEMA] Conflito detectado entre Academia (07:00-08:00) e Reunião (07:30-08:30)
          Sobreposição de 30 minutos.

[SISTEMA] Deseja continuar mesmo assim? [S/n]: _
```

#### Princípio 2: Informação sem Imposição

O sistema PODE e DEVE apresentar informações sobre conflitos e possíveis ajustes.
Porém, estas informações são SEMPRE sugestões, NUNCA ações automáticas.

#### Princípio 3: Routine como Ideal

A rotina representa o cenário IDEAL de execução. Ajustes pontuais são adaptações necessárias, mas o objetivo é retornar ao plano ideal.

#### Princípio 4: Adaptabilidade

O sistema se adapta à realidade. Quando algo atrasa, informa e permite reorganização. A filosofia é: "A vida acontece, o sistema se ajusta."

#### Princípio 5: Preservação de Intenção

Mudanças preservam a intenção original. Se planejou 30min de meditação, a duração é mantida mesmo que horário mude.

#### Princípio 6: Transparência

Toda mudança é explicável e reversível. Usuário sempre tem controle final.

### 1.3 Hierarquia Metodológica

```
+------------------------------------------------------------------+
|                    1. DOCUMENTATION                              |
|    docs/core/business-rules.md                                   |
|    - Business Rules documentadas (BR-DOMAIN-XXX)                 |
|    - 50 regras formalizadas                                      |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    2. BDD (Behavior-Driven)                      |
|    Cenários em formato Gherkin (DADO/QUANDO/ENTÃO)               |
|    Documentação executável                                       |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    3. TESTS                                      |
|    tests/unit/         -> Validam BRs isoladamente               |
|    tests/integration/  -> Validam workflows                      |
|    tests/e2e/          -> Validam experiência completa           |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    4. IMPLEMENTATION                             |
|    src/timeblock/services/  -> Lógica de negócio                 |
|    src/timeblock/commands/  -> Interface CLI                     |
+------------------------------------------------------------------+
```

### 1.4 Stack Tecnológica

| Componente | Tecnologia | Versão | Razão                     |
| ---------- | ---------- | ------ | ------------------------- |
| Linguagem  | Python     | 3.13+  | Produtividade, ecosystem  |
| CLI        | Typer      | 0.x    | Type hints, auto-complete |
| ORM        | SQLModel   | 0.0.x  | Pydantic + SQLAlchemy     |
| Database   | SQLite     | 3.x    | Zero-config, portável     |
| Output     | Rich       | 13.x   | Terminal formatting       |

---

## 2. Entidades e Relacionamentos

### 2.1 Diagrama ER

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
┌─────────────┐      1:N     ┌────────────────────┐
│    Habit    │─────────────→│  HabitInstance     │
│─────────────│              │────────────────────│
│ id          │              │ id                 │
│ routine_id  │              │ habit_id           │
│ title       │              │ date               │
│ start/end   │              │ start/end          │
│ recurrence  │              │ status             │
│ tag_id (FK) │              │ done_substatus     │
└─────────────┘              │ not_done_substatus │
                             │ skip_reason        │
                             │ skip_note          │
                             └────────────────────┘

┌──────────────┐      ┌─────────────┐
│    Task      │      │     Tag     │
│──────────────│      │─────────────│
│ id           │      │ id          │
│ title        │      │ name        │
│ datetime     │      │ color       │
│ completed_dt │      └─────────────┘
│ tag_id (FK)  │
└──────────────┘

┌─────────────┐
│   TimeLog   │
│─────────────│
│ id          │
│ instance_id │
│ task_id     │
│ start_time  │
│ end_time    │
│ duration    │
│ paused_dur  │
└─────────────┘
```

### 2.2 Entidades e Referências

| Entidade      | Descrição                     | BRs Relacionadas           |
| ------------- | ----------------------------- | -------------------------- |
| Routine       | Agrupamento de hábitos        | BR-ROUTINE-001 a 006       |
| Habit         | Template de evento recorrente | BR-HABIT-001 a 005         |
| HabitInstance | Ocorrência em data específica | BR-HABITINSTANCE-001 a 005 |
| Task          | Evento pontual não-recorrente | BR-TASK-001 a 006          |
| Tag           | Categoria com cor             | BR-TAG-001 a 002           |
| TimeLog       | Registro de tempo             | BR-TIMER-001 a 007         |

### 2.3 Glossário de Termos

| Termo         | Definição                                               |
| ------------- | ------------------------------------------------------- |
| Conflito      | Dois eventos ocupam mesmo intervalo temporal            |
| Streak        | Dias consecutivos com status DONE                       |
| Skip          | Pular hábito conscientemente (com ou sem justificativa) |
| Substatus     | Qualificação adicional de DONE ou NOT_DONE              |
| Completion %  | Percentual de tempo realizado vs planejado              |
| Routine Ativa | Rotina que define contexto para comandos habit          |

---

## 3. Diagramas de Estado

### 3.1 Status de HabitInstance (BR-HABITINSTANCE-001)

```
┌──────────────────────────────────────────────────────────────┐
│                    STATUS DE HABITINSTANCE                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│     ┌─────────────┐                                          │
│     │   PENDING   │  ← Estado inicial                        │
│     └──────┬──────┘                                          │
│            │                                                 │
│     ┌──────┴──────┐                                          │
│     │             │                                          │
│     v             v                                          │
│  ┌──────┐    ┌──────────┐                                    │
│  │ DONE │    │ NOT_DONE │                                    │
│  └──┬───┘    └────┬─────┘                                    │
│     │             │                                          │
│     v             v                                          │
│  Substatus:    Substatus:                                    │
│  - FULL        - SKIPPED_JUSTIFIED                           │
│  - PARTIAL     - SKIPPED_UNJUSTIFIED                         │
│  - OVERDONE    - IGNORED                                     │
│  - EXCESSIVE                                                 │
│                                                              │
│  [Estados finais - não há transição de volta]                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Transições válidas:**

| De      | Para     | Via                          |
| ------- | -------- | ---------------------------- |
| PENDING | DONE     | timer stop ou habit atom log |
| PENDING | NOT_DONE | habit atom skip ou timeout   |

### 3.2 Estados de Timer (BR-TIMER-002)

```
┌──────────────────────────────────────────────────────────────┐
│                     ESTADOS DE TIMER                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│     ┌────────────┐                                           │
│     │  NO TIMER  │  ← Estado inicial                         │
│     └──────┬─────┘                                           │
│            │ start                                           │
│            v                                                 │
│     ┌────────────┐                                           │
│     │  RUNNING   │◄─────────┐                                │
│     └──────┬─────┘          │                                │
│            │                │ resume                         │
│     ┌──────┼──────┐         │                                │
│     │pause │stop  │reset    │                                │
│     v      v      v         │                                │
│  ┌──────┐ ┌────┐ ┌────────┐ │                                │
│  │PAUSED│ │DONE│ │CANCELED│ │                                │
│  └──┬───┘ └────┘ └────────┘ │                                │
│     │                       │                                │
│     └───────────────────────┘                                │
│                                                              │
│  DONE: Salva TimeLog, marca instância DONE                   │
│  CANCELED: Descarta sessão, instância continua PENDING       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Comandos e transições:**

| Comando | De             | Para     | Efeito             |
| ------- | -------------- | -------- | ------------------ |
| start   | NO TIMER       | RUNNING  | Cria timer         |
| pause   | RUNNING        | PAUSED   | Pausa contagem     |
| resume  | PAUSED         | RUNNING  | Retoma contagem    |
| stop    | RUNNING/PAUSED | NO TIMER | Salva e marca DONE |
| reset   | RUNNING/PAUSED | NO TIMER | Cancela sem salvar |

### 3.3 Ciclo de Vida de Routine (BR-ROUTINE-001)

```
┌──────────────────────────────────────────────────────────────┐
│                   CICLO DE VIDA DE ROUTINE                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│     ┌────────────┐                                           │
│     │ NOT EXISTS │                                           │
│     └──────┬─────┘                                           │
│            │ create                                          │
│            v                                                 │
│     ┌────────────┐     activate      ┌────────────┐          │
│     │  INACTIVE  │──────────────────→│   ACTIVE   │          │
│     └──────┬─────┘                   └──────┬─────┘          │
│            │                                │                │
│            │←───────────────────────────────┘                │
│            │     deactivate / activate(outro)                │
│            │                                                 │
│     ┌──────┴─────────────────────────────────────┐           │
│     │                                            │           │
│     │ soft delete (desativa)   hard delete       │           │
│     v                          (--purge)         v           │
│  ┌──────────┐                              ┌───────────┐     │
│  │ DISABLED │                              │  DELETED  │     │
│  └──────────┘                              └───────────┘     │
│                                                              │
│  Constraint: Apenas UMA rotina ACTIVE por vez                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Fluxo 1: Setup Inicial

### 4.1 Diagrama de Sequência

```
┌─────────┐          ┌─────────┐          ┌────────────┐
│ Usuário │          │   CLI   │          │  Services  │
└───┬─────┘          └────┬────┘          └──────┬─────┘
    │                     │                      │
    │  routine create     │                      │
    │  "Rotina Matinal"   │                      │
    │────────────────────>│                      │
    │                     │   RoutineService     │
    │                     │   .create()          │
    │                     │─────────────────────>│
    │                     │                      │
    │                     │   [Primeira rotina?] │
    │                     │   Auto-ativa         │
    │                     │<─────────────────────│
    │                     │                      │
    │  [OK] Rotina        │                      │
    │  criada e ativada   │                      │
    │<────────────────────│                      │
    │                     │                      │
```

### 4.2 Workflow Completo

```
┌──────────────────────────────────────────────────────────────┐
│                    SETUP INICIAL                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CRIAR PRIMEIRA ROTINA                                    │
│     $ timeblock routine create "Rotina Matinal"              │
│     → Rotina criada E ativada automaticamente                │
│     → BR-ROUTINE-001: Primeira rotina auto-ativa             │
│                                                              │
│  2. CRIAR HÁBITOS                                            │
│     $ timeblock habit create \                               │
│         --title "Academia" \                                 │
│         --start 07:00 \                                      │
│         --end 08:30 \                                        │
│         --repeat WEEKDAYS \                                  │
│         --renew month 3                                      │
│     → Hábito criado na rotina ativa                          │
│     → Instâncias geradas para 3 meses                        │
│     → BR-ROUTINE-004: Contexto da rotina ativa               │
│     → BR-HABIT-003: Geração de instâncias                    │
│                                                              │
│  3. CRIAR TAGS (opcional)                                    │
│     $ timeblock tag create --title "Saúde" --color sage      │
│     → Tag disponível para hábitos e tasks                    │
│     → BR-TAG-001: Cor obrigatória, título opcional           │
│                                                              │
│  4. CRIAR TASKS                                              │
│     $ timeblock task create \                                │
│         --title "Dentista" \                                 │
│         --datetime "2025-12-15 14:30"                        │
│     → Task independente de rotina                            │
│     → BR-ROUTINE-003: Task não pertence a rotina             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Regras Aplicadas

| Passo | Regra          | Comportamento                      |
| ----- | -------------- | ---------------------------------- |
| 1     | BR-ROUTINE-001 | Primeira rotina auto-ativa         |
| 2     | BR-ROUTINE-004 | Habit criado na rotina ativa       |
| 2     | BR-HABIT-003   | Instâncias geradas automaticamente |
| 3     | BR-TAG-001     | Cor obrigatória com default        |
| 4     | BR-ROUTINE-003 | Task independente de rotina        |

---

## 5. Fluxo 2: Gerenciamento de Rotinas

### 5.1 Ativação de Rotina

```
┌──────────────────────────────────────────────────────────────┐
│                   ATIVAÇÃO DE ROTINA                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ANTES:                                                      │
│  ┌────────────────────┐  ┌────────────────────┐              │
│  │ Rotina Matinal     │  │ Rotina Trabalho    │              │
│  │ is_active: TRUE    │  │ is_active: FALSE   │              │
│  └────────────────────┘  └────────────────────┘              │
│                                                              │
│  COMANDO:                                                    │
│  $ timeblock routine activate 2                              │
│                                                              │
│  PROCESSAMENTO (BR-ROUTINE-001):                             │
│  1. Desativar TODAS as rotinas                               │
│     UPDATE routines SET is_active = FALSE                    │
│  2. Ativar apenas a escolhida                                │
│     UPDATE routines SET is_active = TRUE WHERE id = 2        │
│                                                              │
│  DEPOIS:                                                     │
│  ┌────────────────────┐  ┌────────────────────┐              │
│  │ Rotina Matinal     │  │ Rotina Trabalho    │              │
│  │ is_active: FALSE   │  │ is_active: TRUE    │              │
│  └────────────────────┘  └────────────────────┘              │
│                                                              │
│  OUTPUT:                                                     │
│  [INFO] Rotina "Rotina Matinal" desativada                   │
│  [OK] Rotina "Rotina Trabalho" ativada                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Soft Delete vs Hard Delete

```
┌──────────────────────────────────────────────────────────────┐
│                   DELEÇÃO DE ROTINA                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  SOFT DELETE (padrão) - BR-ROUTINE-006:                      │
│  $ timeblock routine delete 1                                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [WARN] Desativar rotina "Rotina Matinal"?              │  │
│  │        - 8 hábitos permanecem vinculados               │  │
│  │        - Rotina pode ser reativada depois              │  │
│  │ Confirmar? (s/N): _                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  → Rotina desativada (is_active = FALSE)                     │
│  → Hábitos preservados                                       │
│  → Pode reativar depois                                      │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  HARD DELETE (--purge) - BR-ROUTINE-006:                     │
│  $ timeblock routine delete 1 --purge                        │
│                                                              │
│  CASO 1: Rotina SEM hábitos                                  │
│  → Deletada permanentemente                                  │
│                                                              │
│  CASO 2: Rotina COM hábitos                                  │
│  → [ERROR] Não é possível deletar rotina com hábitos         │
│  → Deve deletar hábitos primeiro                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Fluxo 3: Ciclo de Vida de Habits

### 6.1 Criação de Hábito

```
┌──────────────────────────────────────────────────────────────┐
│                    CRIAÇÃO DE HÁBITO                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  COMANDO:                                                    │
│  $ timeblock habit create \                                  │
│      --title "Academia" \                                    │
│      --start 07:00 \                                         │
│      --end 08:30 \                                           │
│      --repeat WEEKDAYS \                                     │
│      --color sage \                                          │
│      --renew month 3                                         │
│                                                              │
│  VALIDAÇÕES (BR-HABIT-001):                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. Title não vazio (após trim)                         │  │
│  │ 2. Title <= 200 caracteres                             │  │
│  │ 3. start < end                                         │  │
│  │ 4. Recurrence válida (enum)                            │  │
│  │ 5. Rotina ativa existe (ou --routine especificado)     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  PROCESSAMENTO:                                              │
│  1. Cria registro Habit no banco                             │
│  2. Identifica rotina ativa (BR-ROUTINE-004)                 │
│  3. Gera instâncias para período (BR-HABIT-003):             │
│     - Data início: hoje                                      │
│     - Data fim: hoje + 3 meses                               │
│     - Apenas dias que batem com recurrence                   │
│                                                              │
│  OUTPUT:                                                     │
│  [OK] Hábito "Academia" criado                               │
│  [INFO] 65 instâncias geradas até 28/02/2026                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Modificação de Hábito (BR-HABIT-004)

```
┌──────────────────────────────────────────────────────────────┐
│                  MODIFICAÇÃO DE HÁBITO                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  COMANDO:                                                    │
│  $ timeblock habit edit 1 --start 06:30 --end 08:00          │
│                                                              │
│  PROCESSAMENTO:                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. Atualiza template Habit                             │  │
│  │                                                        │  │
│  │ 2. Identifica instâncias afetadas:                     │  │
│  │    - Status = PENDING                                  │  │
│  │    - date >= hoje                                      │  │
│  │                                                        │  │
│  │ 3. Atualiza instâncias filtradas:                      │  │
│  │    - scheduled_start = novo valor                      │  │
│  │    - scheduled_end = novo valor                        │  │
│  │                                                        │  │
│  │ 4. Preserva instâncias DONE e NOT_DONE                 │  │
│  │    (histórico intacto para relatórios)                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  EXEMPLO:                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Instância 21/11 - DONE (07:00-08:30) → Não alterada    │  │
│  │ Instância 22/11 - DONE (07:00-08:30) → Não alterada    │  │
│  │ Instância 25/11 - PENDING (07:00-08:30) → 06:30-08:00  │  │
│  │ Instância 26/11 - PENDING (07:00-08:30) → 06:30-08:00  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  OUTPUT:                                                     │
│  [OK] Hábito "Academia" atualizado                           │
│  [INFO] 45 instâncias futuras ajustadas                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.3 Deleção de Hábito (BR-HABIT-005)

```
┌──────────────────────────────────────────────────────────────┐
│                    DELEÇÃO DE HÁBITO                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  COMANDO:                                                    │
│  $ timeblock habit delete 1                                  │
│                                                              │
│  FLUXO INTERATIVO:                                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Hábito: Academia (ID: 1)                               │  │
│  │ Instâncias pendentes: 45                               │  │
│  │ Instâncias concluídas: 18                              │  │
│  │                                                        │  │
│  │ Instâncias pendentes serão removidas.                  │  │
│  │ Histórico será preservado para relatórios.             │  │
│  │                                                        │  │
│  │ Confirma exclusão? [s/N]: _                            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  PROCESSAMENTO:                                              │
│  1. Remove instâncias com status = PENDING                   │
│  2. Preserva instâncias DONE e NOT_DONE                      │
│  3. Remove registro Habit                                    │
│                                                              │
│  RESULTADO:                                                  │
│  - Relatórios continuam funcionando com histórico            │
│  - Novas instâncias não são mais geradas                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Fluxo 4: Geração de HabitInstances

### 7.1 Geração Automática (BR-HABIT-003)

```
┌──────────────────────────────────────────────────────────────┐
│                  GERAÇÃO DE HABITINSTANCES                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  TRIGGER: habit create --renew month 3                       │
│                                                              │
│  ALGORITMO:                                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ def generate_instances(habit, period, n):              │  │
│  │     start_date = date.today()                          │  │
│  │     end_date = start_date + relativedelta(months=n)    │  │
│  │                                                        │  │
│  │     for day in date_range(start_date, end_date):       │  │
│  │         if matches_recurrence(day, habit.recurrence):  │  │
│  │             if not instance_exists(habit.id, day):     │  │
│  │                 create_instance(                       │  │
│  │                     habit_id=habit.id,                 │  │
│  │                     date=day,                          │  │
│  │                     scheduled_start=habit.start,       │  │
│  │                     scheduled_end=habit.end,           │  │
│  │                     status=Status.PENDING              │  │
│  │                 )                                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  EXEMPLO:                                                    │
│  Habit: Academia, WEEKDAYS, 07:00-08:30                      │
│  Período: 01/12/2025 a 28/02/2026 (3 meses)                  │
│                                                              │
│  Dezembro: 23 dias úteis → 23 instâncias                     │
│  Janeiro:  23 dias úteis → 23 instâncias                     │
│  Fevereiro: 20 dias úteis → 20 instâncias                    │
│  Total: 66 instâncias geradas                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 Renovação Manual

```
┌──────────────────────────────────────────────────────────────┐
│                   RENOVAÇÃO DE INSTÂNCIAS                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  COMANDO:                                                    │
│  $ timeblock habit renew 1 month 3                           │
│                                                              │
│  PROCESSAMENTO:                                              │
│  1. Identifica última instância existente                    │
│  2. Gera a partir do dia seguinte                            │
│  3. Não duplica instâncias existentes                        │
│                                                              │
│  OUTPUT:                                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Hábito: Academia                                       │  │
│  │ Período: 01/03/2026 a 31/05/2026                       │  │
│  │ Instâncias criadas: 65                                 │  │
│  │ Instâncias já existentes (ignoradas): 0                │  │
│  │ Total de instâncias pendentes: 110                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 7.3 Padrões de Recorrência (BR-HABIT-002)

| Recurrence | Descrição        | Dias                    |
| ---------- | ---------------- | ----------------------- |
| MONDAY     | Apenas segundas  | seg                     |
| TUESDAY    | Apenas terças    | ter                     |
| WEDNESDAY  | Apenas quartas   | qua                     |
| THURSDAY   | Apenas quintas   | qui                     |
| FRIDAY     | Apenas sextas    | sex                     |
| SATURDAY   | Apenas sábados   | sáb                     |
| SUNDAY     | Apenas domingos  | dom                     |
| WEEKDAYS   | Dias úteis       | seg-sex                 |
| WEEKENDS   | Fim de semana    | sáb-dom                 |
| EVERYDAY   | Todos os dias    | seg-dom                 |
| Lista      | Dias específicos | MONDAY,WEDNESDAY,FRIDAY |

---

## 8. Fluxo 5: Timer Completo

### 8.1 Workflow de Timer (BR-TIMER-001 a BR-TIMER-006)

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW DE TIMER                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. START                                                    │
│     $ timeblock timer start 42                               │
│                                                              │
│     Verificações:                                            │
│     - Timer já ativo? → Menu de opções (BR-TIMER-001)        │
│     - Instância existe? → Validação                          │
│     - Instância PENDING? → OK para iniciar                   │
│                                                              │
│     Resultado:                                               │
│     [OK] Timer iniciado: Academia (07:00-08:30)              │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  2. PAUSE (opcional)                                         │
│     $ timeblock timer pause                                  │
│                                                              │
│     Resultado:                                               │
│     [OK] Timer pausado: Academia                             │
│     Tempo decorrido: 00:15:30                                │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  3. RESUME (após pause)                                      │
│     $ timeblock timer resume                                 │
│                                                              │
│     Resultado:                                               │
│     [OK] Timer retomado: Academia                            │
│     Tempo pausado total: 00:05:00                            │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  4. STOP                                                     │
│     $ timeblock timer stop                                   │
│                                                              │
│     Processamento:                                           │
│     a) Calcula tempo efetivo                                 │
│     b) Cria TimeLog no banco                                 │
│     c) Calcula completion % (BR-TIMER-005)                   │
│     d) Define substatus (BR-HABITINSTANCE-003)               │
│     e) Marca instância como DONE                             │
│                                                              │
│     Resultado:                                               │
│     ┌──────────────────────────────────────────────────────┐ │
│     │ [OK] Timer finalizado: Academia                      │ │
│     │                                                      │ │
│     │ Tempo planejado: 1h30min                             │ │
│     │ Tempo trabalhado: 1h25min                            │ │
│     │ Tempo pausado: 5min                                  │ │
│     │ Substatus: FULL (94%)                                │ │
│     │                                                      │ │
│     │ Instância marcada como concluída.                    │ │
│     └──────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 Timer com Conflito (BR-TIMER-001)

```
┌──────────────────────────────────────────────────────────────┐
│                 TIMER COM CONFLITO ATIVO                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  SITUAÇÃO:                                                   │
│  Timer ativo para Academia (15min decorridos)                │
│  Usuário tenta iniciar timer para Meditação                  │
│                                                              │
│  COMANDO:                                                    │
│  $ timeblock timer start 43                                  │
│                                                              │
│  FLUXO INTERATIVO:                                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [ERROR] Timer já ativo: Academia (15min decorridos)    │  │
│  │                                                        │  │
│  │ Opções:                                                │  │
│  │   [1] Pausar Academia e iniciar Meditação              │  │
│  │   [2] Cancelar Academia (reset) e iniciar Meditação    │  │
│  │   [3] Continuar com Academia                           │  │
│  │                                                        │  │
│  │ Escolha [1-3]: _                                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  OPÇÃO 1: Pausar e iniciar outro                             │
│  - Academia pausado                                          │
│  - Meditação iniciada                                        │
│  - Pode retomar Academia depois                              │
│                                                              │
│  OPÇÃO 2: Cancelar e iniciar outro                           │
│  - Academia cancelada (tempo descartado)                     │
│  - Instância Academia volta para PENDING                     │
│  - Meditação iniciada                                        │
│                                                              │
│  OPÇÃO 3: Continuar atual                                    │
│  - Nenhuma alteração                                         │
│  - Meditação não iniciada                                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.3 Cálculo de Substatus (BR-HABITINSTANCE-003)

```
┌──────────────────────────────────────────────────────────────┐
│                  CÁLCULO DE SUBSTATUS                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  FÓRMULA:                                                    │
│  completion = (tempo_real / tempo_planejado) * 100           │
│                                                              │
│  THRESHOLDS:                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Completion %  │  Substatus  │  Feedback                │  │
│  │───────────────│─────────────│──────────────────────────│  │
│  │   > 150%      │  EXCESSIVE  │  [WARN] Ultrapassou meta │  │
│  │  110-150%     │  OVERDONE   │  [INFO] Acima da meta    │  │
│  │   90-110%     │  FULL       │  [OK] Perfeito           │  │
│  │   < 90%       │  PARTIAL    │  Abaixo da meta          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  EXEMPLO:                                                    │
│  Planejado: 90 minutos (1h30)                                │
│  Real: 85 minutos                                            │
│  Completion: 85/90 = 94.4%                                   │
│  Substatus: FULL (entre 90-110%)                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.4 Log Manual (BR-TIMER-007)

```
┌──────────────────────────────────────────────────────────────┐
│                     LOG MANUAL                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  MODO INTERVALO:                                             │
│  $ timeblock habit atom log 42 --start 07:15 --end 08:20     │
│                                                              │
│  MODO DURAÇÃO:                                               │
│  $ timeblock habit atom log 42 --duration 65                 │
│                                                              │
│  PROCESSAMENTO:                                              │
│  1. Cria TimeLog com valores fornecidos                      │
│  2. Calcula completion %                                     │
│  3. Define substatus                                         │
│  4. Marca instância como DONE                                │
│                                                              │
│  VALIDAÇÃO:                                                  │
│  - Não pode misturar modos (--start/--end OU --duration)     │
│  - --start requer --end (BR-CLI-001)                         │
│  - --duration deve ser positivo                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.5 Múltiplas Sessões (BR-TIMER-004)

```
┌──────────────────────────────────────────────────────────────┐
│                  MÚLTIPLAS SESSÕES                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  CENÁRIO:                                                    │
│  Academia planejada: 90 minutos                              │
│  Usuário faz em duas sessões                                 │
│                                                              │
│  SESSÃO 1 (manhã):                                           │
│  $ timeblock timer start 42                                  │
│  ... (trabalha 60 minutos)                                   │
│  $ timeblock timer stop                                      │
│  → TimeLog 1: 60 minutos                                     │
│  → Status: DONE, Substatus: PARTIAL (67%)                    │
│                                                              │
│  SESSÃO 2 (tarde):                                           │
│  $ timeblock timer start 42                                  │
│  ... (trabalha 30 minutos)                                   │
│  $ timeblock timer stop                                      │
│  → TimeLog 2: 30 minutos                                     │
│  → Tempo acumulado: 90 minutos                               │
│  → Status: DONE, Substatus: FULL (100%)                      │
│                                                              │
│  REGRA:                                                      │
│  Substatus é recalculado sobre tempo ACUMULADO               │
│  de todas as sessões do dia.                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Fluxo 6: Gerenciamento de Tasks

### 9.1 Ciclo de Vida de Task (BR-TASK-001 a BR-TASK-006)

```
┌──────────────────────────────────────────────────────────────┐
│                   CICLO DE VIDA DE TASK                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CRIAÇÃO                                                  │
│     $ timeblock task create \                                │
│         --title "Dentista" \                                 │
│         --datetime "2025-12-15 14:30"                        │
│                                                              │
│     Estado inicial:                                          │
│     - completed_datetime = NULL (pendente)                   │
│     - Aparece em task list                                   │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  2. CONCLUSÃO                                                │
│     $ timeblock task complete 1                              │
│                                                              │
│     Estado após:                                             │
│     - completed_datetime = now()                             │
│     - Sai de task list (pendentes)                           │
│     - Aparece em task list --done                            │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  3. REVERSÃO (BR-TASK-005)                                   │
│     $ timeblock task uncheck 1                               │
│     # ou                                                     │
│     $ timeblock task edit 1 --status pending                 │
│                                                              │
│     Estado após:                                             │
│     - completed_datetime = NULL                              │
│     - Volta para task list                                   │
│     - Permite edição completa novamente                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Diferenças Task vs HabitInstance

| Aspecto     | Task               | HabitInstance          |
| ----------- | ------------------ | ---------------------- |
| Recorrência | Não                | Sim (via Habit)        |
| Pertence a  | Nenhuma entidade   | Habit → Routine        |
| Timer       | Não suportado      | Suportado              |
| Status      | completed_datetime | Status enum            |
| Substatus   | Não tem            | DoneSubstatus/NotDone  |
| Skip        | Não aplicável      | Sim, com justificativa |
| Streak      | Não participa      | Participa do cálculo   |
| Relatórios  | Listagem simples   | Analytics completos    |

---

## 10. Fluxo 7: Skip de HabitInstance

### 10.1 Workflow de Skip (BR-SKIP-001 a BR-SKIP-004)

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW DE SKIP                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  OPÇÃO 1: Wizard Interativo                                  │
│  $ timeblock habit skip                                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Instâncias pendentes hoje:                             │  │
│  │                                                        │  │
│  │ [1] Academia (07:00-08:30)                             │  │
│  │ [2] Meditação (06:00-06:20)                            │  │
│  │ [3] Leitura (21:00-22:00)                              │  │
│  │                                                        │  │
│  │ Qual deseja pular? [1-3]: 1                            │  │
│  │                                                        │  │
│  │ Por que você está pulando Academia hoje?               │  │
│  │                                                        │  │
│  │ [1] Saúde                                              │  │
│  │ [2] Trabalho                                           │  │
│  │ [3] Família                                            │  │
│  │ [4] Viagem                                             │  │
│  │ [5] Clima                                              │  │
│  │ [6] Falta de recursos                                  │  │
│  │ [7] Emergência                                         │  │
│  │ [8] Outro                                              │  │
│  │ [9] Sem justificativa                                  │  │
│  │                                                        │  │
│  │ Escolha [1-9]: 1                                       │  │
│  │                                                        │  │
│  │ Deseja adicionar uma nota? (Enter para pular):         │  │
│  │ Dor nas costas                                         │  │
│  │                                                        │  │
│  │ [OK] Academia pulada (motivo: Saúde)                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  OPÇÃO 2: Comando Direto                                     │
│  $ timeblock habit atom skip 42 --reason HEALTH \            │
│      --note "Dor nas costas"                                 │
│                                                              │
│  Resultado igual ao wizard.                                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 10.2 Categorias de Skip (BR-SKIP-001)

| Valor | Código         | Descrição                    | Substatus           |
| ----- | -------------- | ---------------------------- | ------------------- |
| 1     | HEALTH         | Saúde (doença, consulta)     | SKIPPED_JUSTIFIED   |
| 2     | WORK           | Trabalho (reunião, deadline) | SKIPPED_JUSTIFIED   |
| 3     | FAMILY         | Família (evento, emergência) | SKIPPED_JUSTIFIED   |
| 4     | TRAVEL         | Viagem/Deslocamento          | SKIPPED_JUSTIFIED   |
| 5     | WEATHER        | Clima (chuva, frio)          | SKIPPED_JUSTIFIED   |
| 6     | LACK_RESOURCES | Falta de recursos            | SKIPPED_JUSTIFIED   |
| 7     | EMERGENCY      | Emergências                  | SKIPPED_JUSTIFIED   |
| 8     | OTHER          | Outros (com nota)            | SKIPPED_JUSTIFIED   |
| 9     | (sem)          | Sem justificativa            | SKIPPED_UNJUSTIFIED |

### 10.3 Campos de Skip (BR-SKIP-002)

```python
class HabitInstance:
    # ... outros campos ...
    skip_reason: SkipReason | None    # Categoria (obrigatório se justified)
    skip_note: str | None             # Nota opcional (max 500 chars)
```

**Regras de Consistência:**

| Substatus           | skip_reason | skip_note |
| ------------------- | ----------- | --------- |
| SKIPPED_JUSTIFIED   | Obrigatório | Opcional  |
| SKIPPED_UNJUSTIFIED | NULL        | Opcional  |

---

## 11. Fluxo 8: Detecção de Conflitos

### 11.1 Definição de Conflito (BR-REORDER-001)

```
┌──────────────────────────────────────────────────────────────┐
│                  DETECÇÃO DE CONFLITOS                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  DEFINIÇÃO:                                                  │
│  Conflito = dois eventos com sobreposição temporal           │
│             no mesmo dia.                                    │
│                                                              │
│  FÓRMULA:                                                    │
│  Evento A: [T1, T2]                                          │
│  Evento B: [T3, T4]                                          │
│  Conflito se: (T1 < T4) AND (T3 < T2)                        │
│                                                              │
│  TIPOS DE SOBREPOSIÇÃO:                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │  TOTAL:                                                │  │
│  │  A: ████████████████████                               │  │
│  │  B:     ████████████                                   │  │
│  │                                                        │  │
│  │  PARCIAL:                                              │  │
│  │  A: ████████████████                                   │  │
│  │  B:          ████████████████                          │  │
│  │                                                        │  │
│  │  ADJACENTE (SEM conflito):                             │  │
│  │  A: ████████████                                       │  │
│  │  B:             ████████████                           │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 11.2 Escopo Temporal (BR-REORDER-002)

```
┌──────────────────────────────────────────────────────────────┐
│                    ESCOPO TEMPORAL                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  REGRA: Conflitos são detectados apenas no MESMO DIA.        │
│                                                              │
│  EXEMPLO 1 - Conflito (mesmo dia):                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 01/12/2025                                             │  │
│  │   Academia: 07:00-08:30                                │  │
│  │   Reunião:  07:30-09:00                                │  │
│  │   → CONFLITO DETECTADO (30min sobreposição)            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  EXEMPLO 2 - Sem conflito (dias diferentes):                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 01/12/2025: Academia 07:00-08:30                       │  │
│  │ 02/12/2025: Reunião 07:00-08:30                        │  │
│  │   → SEM CONFLITO (dias diferentes)                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 11.3 Apresentação de Conflitos (BR-REORDER-003)

```
┌──────────────────────────────────────────────────────────────┐
│                APRESENTAÇÃO DE CONFLITOS                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  QUANDO APRESENTAR:                                          │
│  1. Após criar/ajustar evento que resulta em conflito        │
│  2. Antes de iniciar timer, se houver conflitos              │
│  3. Quando usuário solicita visualização                     │
│                                                              │
│  FORMATO:                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [WARN] Conflito detectado:                             │  │
│  │   - Academia: 07:00-08:30                              │  │
│  │   - Reunião: 07:30-09:00                               │  │
│  │   Sobreposição: 60 minutos                             │  │
│  │                                                        │  │
│  │ Deseja continuar mesmo assim? [S/n]: _                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 11.4 Conflitos Não Bloqueiam (BR-REORDER-004)

```
┌──────────────────────────────────────────────────────────────┐
│              CONFLITOS SÃO INFORMATIVOS                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  PRINCÍPIO:                                                  │
│  Conflitos são informativos, NÃO impeditivos.                │
│  Sistema avisa, usuário decide.                              │
│                                                              │
│  COMPORTAMENTOS:                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Timer start com conflito:                              │  │
│  │   → Avisa, pergunta confirmação                        │  │
│  │   → Permite iniciar se confirmado                      │  │
│  │                                                        │  │
│  │ Criar evento com conflito:                             │  │
│  │   → Avisa, pergunta confirmação                        │  │
│  │   → Permite criar se confirmado                        │  │
│  │                                                        │  │
│  │ Editar evento gerando conflito:                        │  │
│  │   → Avisa, pergunta confirmação                        │  │
│  │   → Permite editar se confirmado                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  JUSTIFICATIVA:                                              │
│  Usuário pode ter contexto que sistema desconhece.           │
│  Ex: Reunião online durante Academia (fazendo exercícios     │
│  leves enquanto ouve a reunião).                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 11.5 Persistência de Conflitos (BR-REORDER-005)

```
Conflitos NÃO são persistidos no banco.
São calculados dinamicamente quando necessário.

Justificativa:
- Conflitos são relação temporal entre eventos
- Eventos podem mudar a qualquer momento
- Cálculo dinâmico garante dados sempre atualizados
```

---

## 12. Fluxo 9: Streak e Consistência

### 12.1 Algoritmo de Streak (BR-STREAK-001)

```
┌──────────────────────────────────────────────────────────────┐
│                   ALGORITMO DE STREAK                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  DEFINIÇÃO:                                                  │
│  Streak = dias consecutivos com status DONE,                 │
│           contados do mais recente para trás.                │
│                                                              │
│  ALGORITMO:                                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ def calculate_streak(habit_id: int) -> int:            │  │
│  │     instances = get_instances_by_date(habit_id)        │  │
│  │     streak = 0                                         │  │
│  │                                                        │  │
│  │     for instance in reversed(instances):               │  │
│  │         if instance.status == Status.DONE:             │  │
│  │             streak += 1                                │  │
│  │         elif instance.status == Status.NOT_DONE:       │  │
│  │             break  # Para no primeiro NOT_DONE         │  │
│  │         # PENDING não conta nem quebra                 │  │
│  │                                                        │  │
│  │     return streak                                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  REGRAS:                                                     │
│  1. Direção: presente → passado                              │
│  2. Conta: apenas DONE (qualquer substatus)                  │
│  3. Para: no primeiro NOT_DONE                               │
│  4. Ignora: PENDING (futuro)                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 12.2 Condições de Quebra (BR-STREAK-002)

```
┌──────────────────────────────────────────────────────────────┐
│                  CONDIÇÕES DE QUEBRA                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  REGRA: Streak SEMPRE quebra quando status = NOT_DONE,       │
│         independente do substatus.                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Substatus           │ Quebra? │ Impacto Psicológico    │  │
│  │─────────────────────│─────────│────────────────────────│  │
│  │ SKIPPED_JUSTIFIED   │   Sim   │ Baixo                  │  │
│  │ SKIPPED_UNJUSTIFIED │   Sim   │ Médio                  │  │
│  │ IGNORED             │   Sim   │ Alto                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  FILOSOFIA (Atomic Habits - James Clear):                    │
│  - Consistência > Perfeição                                  │
│  - "Nunca pule dois dias seguidos"                           │
│  - Skip consciente ainda é quebra                            │
│  - Diferenciamos impacto psicológico, não o fato da quebra   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 12.3 Condições de Manutenção (BR-STREAK-003)

```
┌──────────────────────────────────────────────────────────────┐
│                 CONDIÇÕES DE MANUTENÇÃO                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  REGRA: Streak SEMPRE mantém quando status = DONE,           │
│         independente do substatus.                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Substatus │ Mantém? │ Feedback                         │  │
│  │───────────│─────────│──────────────────────────────────│  │
│  │ FULL      │   Sim   │ [OK] Perfeito                    │  │
│  │ PARTIAL   │   Sim   │ Encorajador                      │  │
│  │ OVERDONE  │   Sim   │ Info                             │  │
│  │ EXCESSIVE │   Sim   │ Warning                          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  FILOSOFIA: "Melhor feito que perfeito"                      │
│                                                              │
│  Fazer 20 minutos de um hábito de 30 minutos                 │
│  é infinitamente melhor que não fazer nada.                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 12.4 Dias Sem Instância (BR-STREAK-004)

```
┌──────────────────────────────────────────────────────────────┐
│                 DIAS SEM INSTÂNCIA                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  REGRA: Dias sem instância NÃO quebram streak.               │
│                                                              │
│  EXEMPLO:                                                    │
│  Habit: Academia (WEEKDAYS)                                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Segunda (01/12): Academia DONE     → streak = 1        │  │
│  │ Terça (02/12):   Academia DONE     → streak = 2        │  │
│  │ Quarta (03/12):  Academia DONE     → streak = 3        │  │
│  │ Quinta (04/12):  Academia DONE     → streak = 4        │  │
│  │ Sexta (05/12):   Academia DONE     → streak = 5        │  │
│  │ Sábado (06/12):  SEM INSTÂNCIA     → streak = 5        │  │
│  │ Domingo (07/12): SEM INSTÂNCIA     → streak = 5        │  │
│  │ Segunda (08/12): Academia DONE     → streak = 6        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  JUSTIFICATIVA:                                              │
│  Ausência de instância é neutra.                             │
│  Apenas NOT_DONE ativo quebra streak.                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 12.5 Visualização de Streak

```
┌──────────────────────────────────────────────────────────────┐
│                 VISUALIZAÇÃO DE STREAK                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  $ timeblock habit details 1                                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Hábito: Academia (ID: 1)                               │  │
│  │ ════════════════════════════════════════               │  │
│  │                                                        │  │
│  │ Estatísticas:                                          │  │
│  │   Taxa de conclusão: 90%                               │  │
│  │   Streak atual: 5 dias                                 │  │
│  │   Streak recorde: 12 dias                              │  │
│  │   Tempo médio: 1h25min                                 │  │
│  │                                                        │  │
│  │ Calendário do mês:                                     │  │
│  │   S  T  Q  Q  S  S  D                                  │  │
│  │   ●  ●  ●  ●  ●  ○  ○   (● = DONE, ○ = sem instância)  │  │
│  │   ●  ●  ●  ●  ●  ○  ○                                  │  │
│  │   ●  ●  x  ●  ●  ○  ○   (x = NOT_DONE)                 │  │
│  │   ●  ·  ·  ·  ·  ·  ·   (· = PENDING)                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 13. Fluxo 10: Relatórios e Analytics

### 13.1 Estrutura de Relatório

```
┌──────────────────────────────────────────────────────────────┐
│                  ESTRUTURA DE RELATÓRIO                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  $ timeblock report                                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Relatório: Dezembro 2025                               │  │
│  │ ════════════════════════════════════════               │  │
│  │                                                        │  │
│  │ Resumo Geral:                                          │  │
│  │   Taxa de conclusão: 85%                               │  │
│  │   Hábitos rastreados: 5                                │  │
│  │   Tempo total: 45h 30min                               │  │
│  │                                                        │  │
│  │ Por Hábito:                                            │  │
│  │   Academia                                             │  │
│  │     Conclusão: 90% (18/20)                             │  │
│  │     Streak atual: 5 dias                               │  │
│  │     Tempo médio: 1h25min                               │  │
│  │                                                        │  │
│  │   Meditação                                            │  │
│  │     Conclusão: 95% (28/30)                             │  │
│  │     Streak atual: 12 dias                              │  │
│  │     Tempo médio: 18min                                 │  │
│  │                                                        │  │
│  │ Distribuição por Substatus:                            │  │
│  │   FULL: 70%                                            │  │
│  │   PARTIAL: 20%                                         │  │
│  │   OVERDONE: 8%                                         │  │
│  │   EXCESSIVE: 2%                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 13.2 Filtros de Período

| Flag        | Descrição           | Exemplo                            |
| ----------- | ------------------- | ---------------------------------- |
| --week      | Semana atual        | report -w                          |
| --month     | Mês atual (default) | report -m                          |
| --quarter   | Trimestre atual     | report -q                          |
| --semester  | Semestre atual      | report --semester                  |
| --year      | Ano atual           | report -y                          |
| --from/--to | Range customizado   | report -f 2025-01-01 -t 2025-06-30 |

### 13.3 Métricas Calculadas

```
┌──────────────────────────────────────────────────────────────┐
│                  MÉTRICAS CALCULADAS                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  TAXA DE CONCLUSÃO:                                          │
│  = (instâncias DONE / total instâncias no período) * 100     │
│                                                              │
│  TEMPO TOTAL:                                                │
│  = soma(TimeLog.duration) para período                       │
│                                                              │
│  TEMPO MÉDIO:                                                │
│  = tempo_total / quantidade_sessões                          │
│                                                              │
│  STREAK:                                                     │
│  = dias consecutivos DONE (mais recente para trás)           │
│                                                              │
│  DISTRIBUIÇÃO SUBSTATUS:                                     │
│  = contagem de cada substatus / total DONE                   │
│                                                              │
│  VARIAÇÃO:                                                   │
│  = ((período_atual - período_anterior) / anterior) * 100     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 14. Cenários BDD Completos

### 14.1 Cenário: Primeira Rotina

```gherkin
Funcionalidade: Setup Inicial do Sistema
  Como usuário novo
  Quero criar minha primeira rotina
  Para começar a organizar meus hábitos

  Cenário: Criar primeira rotina
    Dado que não existe nenhuma rotina no sistema
    Quando executo "routine create 'Rotina Matinal'"
    Então a rotina "Rotina Matinal" deve ser criada
    E a rotina deve estar ativa automaticamente
    E deve exibir "[OK] Rotina 'Rotina Matinal' criada e ativada"

  Cenário: Criar segunda rotina
    Dado que existe a rotina "Rotina Matinal" ativa
    Quando executo "routine create 'Rotina Trabalho'"
    Então a rotina "Rotina Trabalho" deve ser criada
    E a rotina "Rotina Trabalho" deve estar inativa
    E a rotina "Rotina Matinal" deve permanecer ativa
```

### 14.2 Cenário: Timer com Conflito

```gherkin
Funcionalidade: Gerenciamento de Timer
  Como usuário
  Quero controlar meu tempo em hábitos
  Para rastrear minha produtividade

  Cenário: Iniciar timer com conflito de horário
    Dado que existe uma instância "Academia" às 07:00-08:30
    E existe uma instância "Reunião" às 07:30-09:00
    Quando executo "timer start" para "Academia"
    Então deve exibir aviso de conflito com "Reunião"
    E deve mostrar sobreposição de 60 minutos
    E deve solicitar confirmação para continuar

  Cenário: Timer com múltiplas sessões
    Dado que a instância 42 tem tempo planejado de 90 minutos
    E já existe um TimeLog de 60 minutos para hoje
    Quando inicio timer para instância 42
    E trabalho por mais 30 minutos
    E executo "timer stop"
    Então o tempo total deve ser 90 minutos
    E o substatus deve ser FULL (100%)
```

### 14.3 Cenário: Skip com Justificativa

```gherkin
Funcionalidade: Skip de Hábitos
  Como usuário
  Quero pular um hábito com justificativa
  Para manter registro do motivo

  Cenário: Skip justificado com nota
    Dado que existe uma instância PENDING de "Academia"
    Quando executo "habit atom skip 42 --reason HEALTH --note 'Dor nas costas'"
    Então a instância deve ter status NOT_DONE
    E o substatus deve ser SKIPPED_JUSTIFIED
    E o skip_reason deve ser HEALTH
    E o skip_note deve ser "Dor nas costas"
    E o streak do hábito deve ser quebrado

  Cenário: Skip sem justificativa
    Dado que existe uma instância PENDING de "Academia"
    Quando executo wizard de skip e escolho opção 9
    Então a instância deve ter status NOT_DONE
    E o substatus deve ser SKIPPED_UNJUSTIFIED
    E o skip_reason deve ser NULL
```

### 14.4 Cenário: Cálculo de Streak

```gherkin
Funcionalidade: Cálculo de Streak
  Como usuário
  Quero ver minha sequência de dias consecutivos
  Para acompanhar minha consistência

  Cenário: Streak com dias sem instância
    Dado que o hábito "Academia" é WEEKDAYS
    E as instâncias de seg a sex estão DONE
    E hoje é domingo
    Quando calculo o streak
    Então o streak deve ser 5 dias
    E o fim de semana não deve quebrar o streak

  Cenário: Streak quebrado por NOT_DONE
    Dado que as instâncias de seg a qua estão DONE
    E a instância de qui está NOT_DONE
    E as instâncias de sex a hoje estão DONE
    Quando calculo o streak
    Então o streak deve ser 2 dias (sex + hoje)
    E não deve contar seg a qua
```

---

## 15. Tratamento de Erros

### 15.1 Hierarquia de Exceções

```
┌──────────────────────────────────────────────────────────────┐
│                 HIERARQUIA DE EXCEÇÕES                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  TimeBlockError (base)                                       │
│  ├── ValidationError                                         │
│  │   ├── InvalidTimeError                                    │
│  │   ├── InvalidDateError                                    │
│  │   ├── InvalidRecurrenceError                              │
│  │   └── EmptyTitleError                                     │
│  │                                                           │
│  ├── EntityNotFoundError                                     │
│  │   ├── RoutineNotFoundError                                │
│  │   ├── HabitNotFoundError                                  │
│  │   ├── InstanceNotFoundError                               │
│  │   └── TaskNotFoundError                                   │
│  │                                                           │
│  ├── StateError                                              │
│  │   ├── NoActiveRoutineError                                │
│  │   ├── TimerAlreadyActiveError                             │
│  │   ├── NoActiveTimerError                                  │
│  │   └── InvalidStatusTransitionError                        │
│  │                                                           │
│  └── BusinessRuleViolationError                              │
│      ├── DuplicateRoutineNameError                           │
│      ├── RoutineWithHabitsError                              │
│      └── DependentFlagsError                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 15.2 Mensagens de Erro Padrão

| Exceção                 | Código | Mensagem                                       |
| ----------------------- | ------ | ---------------------------------------------- |
| NoActiveRoutineError    | E001   | "Nenhuma rotina ativa. Use 'routine activate'" |
| TimerAlreadyActiveError | E002   | "Timer já ativo: {habit} ({tempo} decorridos)" |
| InstanceNotFoundError   | E003   | "Instância ID {id} não encontrada"             |
| DependentFlagsError     | E004   | "--{flag1} requer --{flag2} (e vice-versa)"    |
| InvalidTimeError        | E005   | "Hora início deve ser menor que hora fim"      |

---

## 16. Validações de Input

### 16.1 Validações de Flags (BR-CLI-001)

```
┌───────────────────────────────────────────────────────────────┐
│                  VALIDAÇÕES DE FLAGS                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  PARES OBRIGATÓRIOS:                                          │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Flag Principal │ Requer  │ Comando Afetado             │   │
│  │────────────────│─────────│─────────────────────────────│   │
│  │ --start        │ --end   │ habit create, habit atom    │   │
│  │ --end          │ --start │ habit create, habit atom    │   │
│  │ --from         │ --to    │ report                      │   │
│  │ --to           │ --from  │ report                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                               │
│  MUTUAMENTE EXCLUSIVOS:                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Grupo                      │ Contexto                   │  │
│  │────────────────────────────│────────────────────────────│  │
│  │ --color / --tag            │ habit, task                │  │
│  │ --start+--end / --duration │ habit atom log             │  │
│  │ --today / --week           │ habit atom list, task list │  │
│  │ Flags de período           │ report                     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 16.2 Formatos de Datetime (BR-CLI-002)

```
┌──────────────────────────────────────────────────────────────┐
│                 FORMATOS DE DATETIME                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  DATETIME (--datetime):                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Formato          │ Exemplo          │ Resultado        │  │
│  │──────────────────│──────────────────│──────────────────│  │
│  │ YYYY-MM-DD HH:MM │ 2025-12-25 14:30 │ 2025-12-25 14:30 │  │
│  │ YYYY-MM-DD HHhMM │ 2025-12-25 14h30 │ 2025-12-25 14:30 │  │
│  │ YYYY-MM-DD HHh   │ 2025-12-25 14h   │ 2025-12-25 14:00 │  │
│  │ DD-MM-YYYY HH:MM │ 25-12-2025 14:30 │ 2025-12-25 14:30 │  │
│  │ DD-MM-YYYY HHhMM │ 25-12-2025 14h30 │ 2025-12-25 14:30 │  │
│  │ DD-MM-YYYY HHh   │ 25-12-2025 14h   │ 2025-12-25 14:00 │  │
│  │ DD/MM/YYYY HH:MM │ 25/12/2025 14:30 │ 2025-12-25 14:30 │  │
│  │ DD/MM/YYYY HHhMM │ 25/12/2025 14h30 │ 2025-12-25 14:30 │  │
│  │ DD/MM/YYYY HHh   │ 25/12/2025 14h   │ 2025-12-25 14:00 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  DATE (--date, --from, --to):                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Formato    │ Exemplo    │ Resultado                    │  │
│  │────────────│────────────│──────────────────────────────│  │
│  │ YYYY-MM-DD │ 2025-12-25 │ 2025-12-25                   │  │
│  │ DD-MM-YYYY │ 25-12-2025 │ 2025-12-25                   │  │
│  │ DD/MM/YYYY │ 25/12/2025 │ 2025-12-25                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  TIME (--start, --end):                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Formato │ Exemplo │ Resultado                          │  │
│  │─────────│─────────│────────────────────────────────────│  │
│  │ HH:MM   │ 07:30   │ 07:30                              │  │
│  │ HHh     │ 7h      │ 07:00                              │  │
│  │ HHhMM   │ 7h30    │ 07:30                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 16.3 Validações de Strings (BR-VAL-003)

| Campo       | Limite       | Validação                |
| ----------- | ------------ | ------------------------ |
| title       | 1-200 chars  | Não vazio após trim      |
| description | 0-2000 chars | Opcional                 |
| name        | 1-200 chars  | Único (case-insensitive) |
| note        | 0-500 chars  | Opcional                 |

---

## 17. Integração entre Componentes

### 17.1 Diagrama de Camadas

```
┌──────────────────────────────────────────────────────────────┐
│                      CAMADAS DA APLICAÇÃO                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                     CLI LAYER                          │  │
│  │              (commands/*.py)                           │  │
│  │                                                        │  │
│  │  routine.py  habit.py  task.py  timer.py  report.py    │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           v                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   SERVICE LAYER                        │  │
│  │              (services/*.py)                           │  │
│  │                                                        │  │
│  │  RoutineService   HabitService   TaskService           │  │
│  │  HabitInstanceService   TimerService   ReportService   │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           v                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    MODEL LAYER                         │  │
│  │               (models/*.py)                            │  │
│  │                                                        │  │
│  │  Routine   Habit   HabitInstance   Task   Tag          │  │
│  │  TimeLog   Status   Recurrence   SkipReason            │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           v                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   DATABASE LAYER                       │  │
│  │              (database/*.py)                           │  │
│  │                                                        │  │
│  │               SQLite + SQLModel                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 17.2 Fluxo de Dados: Criar Hábito com Timer

```
┌────────────────────────────────────────────────────────────────┐
│               FLUXO: CRIAR E EXECUTAR HÁBITO                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. CRIAR HÁBITO                                               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ CLI: habit create --title "Academia" ...             │      │
│  │           │                                          │      │
│  │           v                                          │      │
│  │ HabitService.create_habit()                          │      │
│  │           │                                          │      │
│  │           v                                          │      │
│  │ HabitInstanceService.generate_instances()            │      │
│  │           │                                          │      │
│  │           v                                          │      │
│  │ Database: INSERT habit, INSERT habit_instances       │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                │
│  2. INICIAR TIMER                                              │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ CLI: timer start 42                                  │      │
│  │           │                                          │      │
│  │           v                                          │      │
│  │ TimerService.start_timer(instance_id=42)             │      │
│  │           │                                          │      │
│  │           ├─> Verifica timer ativo (BR-TIMER-001)    │      │
│  │           ├─> Verifica conflitos (BR-REORDER-001)    │      │
│  │           v                                          │      │
│  │ Database: INSERT time_log (start_time)               │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                │
│  3. PARAR TIMER                                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ CLI: timer stop                                        │    │
│  │           │                                            │    │
│  │           v                                            │    │
│  │ TimerService.stop_timer()                              │    │
│  │           │                                            │    │
│  │           ├─> Calcula duração                          │    │
│  │           ├─> Calcula completion % (BR-TIMER-005)      │    │
│  │           ├─> Define substatus (BR-HABITINSTANCE-003)  │    │
│  │           v                                            │    │
│  │ HabitInstanceService.mark_done(instance_id, substatus) │    │
│  │           │                                            │    │
│  │           v                                            │    │
│  │ Database: UPDATE time_log, UPDATE habit_instance       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 17.3 Dependências entre Services

```
┌──────────────────────────────────────────────────────────────┐
│                DEPENDÊNCIAS ENTRE SERVICES                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐                                         │
│  │ RoutineService  │                                         │
│  └────────┬────────┘                                         │
│           │ usa                                              │
│           v                                                  │
│  ┌─────────────────┐     ┌─────────────────────────┐         │
│  │  HabitService   │────>│ HabitInstanceService    │         │
│  └────────┬────────┘     └───────────┬─────────────┘         │
│           │                          │                       │
│           └──────────┬───────────────┘                       │
│                      │ usa                                   │
│                      v                                       │
│  ┌───────────────────────────────────────────────────┐       │
│  │              TimerService                         │       │
│  │  - start_timer(instance_id)                       │       │
│  │  - stop_timer() -> HabitInstanceService.mark_done │       │
│  └──────────────────────┬────────────────────────────┘       │
│                         │ usa                                │
│                         v                                    │
│  ┌─────────────────────────────────────────────────┐         │
│  │           ConflictDetectionService              │         │
│  │  - detect_conflicts(date, events)               │         │
│  │  - get_overlapping_events(event_id)             │         │
│  └─────────────────────────────────────────────────┘         │
│                                                              │
│  ┌─────────────────┐     ┌─────────────────┐                 │
│  │   TaskService   │     │  ReportService  │                 │
│  └─────────────────┘     └────────┬────────┘                 │
│     (independente)                │ usa                      │
│                                   v                          │
│                        ┌─────────────────────────┐           │
│                        │ HabitInstanceService    │           │
│                        │ TimerService (TimeLog)  │           │
│                        └─────────────────────────┘           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 18. Referências Cruzadas

### 18.1 Mapeamento BR → Seção

| BR                   | Domínio       | Seção neste Documento                |
| -------------------- | ------------- | ------------------------------------ |
| BR-ROUTINE-001       | Routine       | 5.1 Ativação de Rotina               |
| BR-ROUTINE-002       | Routine       | 2.1 Diagrama ER                      |
| BR-ROUTINE-003       | Routine       | 9.2 Diferenças Task vs HabitInstance |
| BR-ROUTINE-004       | Routine       | 4.2 Workflow Completo                |
| BR-ROUTINE-005       | Routine       | 16.3 Validações de Strings           |
| BR-ROUTINE-006       | Routine       | 5.2 Soft Delete vs Hard Delete       |
| BR-HABIT-001         | Habit         | 6.1 Criação de Hábito                |
| BR-HABIT-002         | Habit         | 7.3 Padrões de Recorrência           |
| BR-HABIT-003         | Habit         | 7.1 Geração Automática               |
| BR-HABIT-004         | Habit         | 6.2 Modificação de Hábito            |
| BR-HABIT-005         | Habit         | 6.3 Deleção de Hábito                |
| BR-HABITINSTANCE-001 | HabitInstance | 3.1 Status de HabitInstance          |
| BR-HABITINSTANCE-002 | HabitInstance | 3.1 Status de HabitInstance          |
| BR-HABITINSTANCE-003 | HabitInstance | 8.3 Cálculo de Substatus             |
| BR-HABITINSTANCE-004 | HabitInstance | 15.1 Hierarquia de Exceções          |
| BR-HABITINSTANCE-005 | HabitInstance | 6.2 Modificação de Hábito            |
| BR-SKIP-001          | Skip          | 10.2 Categorias de Skip              |
| BR-SKIP-002          | Skip          | 10.3 Campos de Skip                  |
| BR-SKIP-003          | Skip          | 15.1 Hierarquia de Exceções          |
| BR-SKIP-004          | Skip          | 10.1 Workflow de Skip                |
| BR-STREAK-001        | Streak        | 12.1 Algoritmo de Streak             |
| BR-STREAK-002        | Streak        | 12.2 Condições de Quebra             |
| BR-STREAK-003        | Streak        | 12.3 Condições de Manutenção         |
| BR-STREAK-004        | Streak        | 12.4 Dias Sem Instância              |
| BR-TASK-001          | Task          | 9.1 Ciclo de Vida de Task            |
| BR-TASK-002          | Task          | 9.1 Ciclo de Vida de Task            |
| BR-TASK-003          | Task          | 9.2 Diferenças Task vs HabitInstance |
| BR-TASK-004          | Task          | 13.1 Estrutura de Relatório          |
| BR-TASK-005          | Task          | 9.1 Ciclo de Vida de Task            |
| BR-TASK-006          | Task          | 9.2 Diferenças Task vs HabitInstance |
| BR-TIMER-001         | Timer         | 8.2 Timer com Conflito               |
| BR-TIMER-002         | Timer         | 3.2 Estados de Timer                 |
| BR-TIMER-003         | Timer         | 8.1 Workflow de Timer                |
| BR-TIMER-004         | Timer         | 8.5 Múltiplas Sessões                |
| BR-TIMER-005         | Timer         | 8.3 Cálculo de Substatus             |
| BR-TIMER-006         | Timer         | 8.1 Workflow de Timer                |
| BR-TIMER-007         | Timer         | 8.4 Log Manual                       |
| BR-REORDER-001       | Event Reorder | 11.1 Definição de Conflito           |
| BR-REORDER-002       | Event Reorder | 11.2 Escopo Temporal                 |
| BR-REORDER-003       | Event Reorder | 11.3 Apresentação de Conflitos       |
| BR-REORDER-004       | Event Reorder | 11.4 Conflitos Não Bloqueiam         |
| BR-REORDER-005       | Event Reorder | 11.5 Persistência de Conflitos       |
| BR-REORDER-006       | Event Reorder | 11.5 (planejado v2.0)                |
| BR-VAL-001           | Validação     | 16.2 Formatos de Datetime            |
| BR-VAL-002           | Validação     | 16.2 Formatos de Datetime            |
| BR-VAL-003           | Validação     | 16.3 Validações de Strings           |
| BR-CLI-001           | CLI           | 16.1 Validações de Flags             |
| BR-CLI-002           | CLI           | 16.2 Formatos de Datetime            |
| BR-TAG-001           | Tag           | 2.1 Diagrama ER                      |
| BR-TAG-002           | Tag           | 2.1 Diagrama ER                      |

### 18.2 Referências para Outros Documentos

| Documento         | Conteúdo                     | Localização                 |
| ----------------- | ---------------------------- | --------------------------- |
| architecture.md   | Camadas, stack, princípios   | docs/core/architecture.md   |
| business-rules.md | Todas as 50 BRs detalhadas   | docs/core/business-rules.md |
| cli-reference.md  | Sintaxe completa de comandos | docs/core/cli-reference.md  |

### 18.3 Referências Externas

| Recurso       | URL                                    |
| ------------- | -------------------------------------- |
| Atomic Habits | <https://jamesclear.com/atomic-habits> |
| SQLModel      | <https://sqlmodel.tiangolo.com/>       |
| Typer         | <https://typer.tiangolo.com/>          |
| Rich          | <https://rich.readthedocs.io/>         |

---

## Apêndice A: Glossário Completo

| Termo            | Definição                                                |
| ---------------- | -------------------------------------------------------- |
| Conflito         | Dois eventos ocupam mesmo intervalo temporal             |
| Completion %     | Percentual de tempo realizado vs planejado               |
| DONE             | Status: hábito concluído                                 |
| DoneSubstatus    | Qualificação de DONE: FULL, PARTIAL, OVERDONE, EXCESSIVE |
| HabitInstance    | Ocorrência de hábito em data específica                  |
| NOT_DONE         | Status: hábito não concluído                             |
| NotDoneSubstatus | Qualificação de NOT*DONE: SKIPPED*\*, IGNORED            |
| PENDING          | Status: aguardando execução                              |
| Recurrence       | Padrão de repetição de hábito                            |
| Routine          | Agrupamento de hábitos relacionados                      |
| Skip             | Pular hábito conscientemente                             |
| SkipReason       | Motivo categorizado do skip                              |
| SSOT             | Single Source of Truth                                   |
| Streak           | Dias consecutivos com status DONE                        |
| Substatus        | Qualificação adicional de status final                   |
| TimeLog          | Registro de sessão de timer                              |

---

## Apêndice B: Changelog do Documento

| Versão | Data       | Alterações                                    |
| ------ | ---------- | --------------------------------------------- |
| 2.1.0  | 01/12/2025 | Regeneração completa alinhada com docs/core/  |
|        |            | - Nomenclatura BR-REORDER-(não BR-EVENT-)     |
|        |            | - Status: PENDING, DONE, NOT_DONE             |
|        |            | - Substatuses alinhados com business-rules.md |
|        |            | - Comandos CLI atualizados (habit atom)       |
|        |            | - Referências cruzadas completas              |
| 2.0.0  | 01/12/2025 | Versão inicial consolidada (desalinhada)      |

---

**Documento consolidado em:** 01 de Dezembro de 2025

**Alinhamento verificado com:**

- architecture.md v2.0.0
- business-rules.md v3.0.0
- cli-reference.md v1.4.0

**Total de BRs referenciadas:** 50
