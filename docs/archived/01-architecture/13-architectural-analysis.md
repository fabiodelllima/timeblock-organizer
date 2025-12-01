# Análise Arquitetural Completa

**Versão**: 2.0
**Data**: 21 de Outubro de 2025

---

## Inferências sobre Arquitetura

### Influência de Domain-Driven Design

Projeto demonstra forte influência de princípios DDD através da separação clara entre entities, services e repositories. Estrutura de packages e nomeação sugerem familiaridade com estes conceitos.

### Evolução para Web

Ausência de camada API REST/GraphQL sugere concepção inicial como ferramenta pessoal, mas escolha de Textual indica intenção futura de deployment web.

### Type Safety e Validação

Uso extensivo de type hints e Pydantic indica preferência por type safety. Validação em tempo de compilação (mypy) e runtime (Pydantic) cria múltiplas camadas de defesa.

### Preferência por Simplicidade

Escolha de não usar framework pesado como Django demonstra valorização de simplicidade. Projeto compõe bibliotecas focadas (Typer, Rich, SQLModel).

### Modularidade e Navegabilidade

Padrão de manter arquivos pequenos (~100 linhas) revela preferência por componentes focados.

### Cultura de Testes

Estrutura de testes bem organizada com separação unit/integration/e2e demonstra cultura de qualidade. Meta de 95% de cobertura mostra comprometimento.

---

## Diagramas de Sequência Detalhados

### 1. Criar e Ativar Rotina

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant RS as RoutineService
    participant RR as RoutineRepository
    participant DB as SQLite

    User->>CLI: routine create "Morning Routine"
    CLI->>RS: create_routine("Morning Routine")

    RS->>RS: Validate name
    RS->>RR: find_by_name("Morning Routine")
    RR->>DB: SELECT * FROM routine WHERE name=?
    DB-->>RR: None
    RR-->>RS: None

    RS->>RS: Create Routine model
    RS->>RR: save(routine)
    RR->>DB: INSERT INTO routine VALUES(...)
    DB-->>RR: routine with id=1
    RR-->>RS: routine

    RS->>RR: activate(routine.id)
    RR->>DB: UPDATE routine SET is_active=true WHERE id=1
    DB-->>RR: Success
    RR-->>RS: Success

    RS-->>CLI: routine
    CLI-->>User: Routine created and activated
```

### 2. Timer Completo

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant TMS as TimerService
    participant TLR as TimeLogRepository
    participant HIR as HabitInstanceRepository
    participant DB

    User->>CLI: timer start (selects Gym)
    CLI->>TMS: start_timer(habit_instance_id=10)

    TMS->>TLR: find_active()
    TLR->>DB: SELECT * FROM time_log WHERE end_time IS NULL
    DB-->>TLR: None
    TLR-->>TMS: None

    TMS->>DB: BEGIN TRANSACTION
    TMS->>TLR: save(time_log)
    TLR->>DB: INSERT INTO time_log VALUES (...)

    TMS->>HIR: update_status(10, 'in_progress')
    HIR->>DB: UPDATE habit_instance SET status='in_progress'

    TMS->>DB: COMMIT
    TMS-->>CLI: timer_active

    Note over User: Timer runs 82 minutes

    User->>CLI: timer stop
    CLI->>TMS: stop_timer(time_log_id=42)

    TMS->>DB: BEGIN TRANSACTION
    TMS->>TLR: update(time_log)
    TMS->>HIR: update_status(10, 'completed')
    TMS->>DB: COMMIT

    TMS-->>CLI: time_log
    CLI-->>User: Timer stopped Duration: 1h 22m
```

---

**Documento criado**: 21 de Outubro de 2025
**Versão**: 2.0
