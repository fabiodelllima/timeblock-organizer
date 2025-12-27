# Architecture Decision Records (ADRs)

Registro de decisões arquiteturais do TimeBlock Organizer.

**Total:** 25 ADRs | **Status:** 23 aceitas, 2 propostas

---

## Por Categoria

### Models e Dados

| ADR                                                | Título                       |
| -------------------------------------------------- | ---------------------------- |
| [ADR-001](ADR-001-sqlmodel-orm.md)                 | SQLModel ORM                 |
| [ADR-004](ADR-004-habit-vs-instance.md)            | Habit vs Instance            |
| [ADR-010](ADR-010-recurrence-model.md)             | Recurrence Model             |
| [ADR-013](ADR-013-offline-first-schema.md)         | Offline-First Schema         |
| [ADR-015](ADR-015-habitinstance-naming.md)         | HabitInstance Naming         |
| [ADR-021](ADR-021-status-substatus-refactoring.md) | Status+Substatus Refactoring |

### CLI e UX

| ADR                                       | Título              |
| ----------------------------------------- | ------------------- |
| [ADR-002](ADR-002-typer-cli.md)           | Typer CLI           |
| [ADR-005](ADR-005-resource-first-cli.md)  | Resource-First CLI  |
| [ADR-006](ADR-006-textual-tui.md)         | Textual TUI         |
| [ADR-009](ADR-009-flags-consolidation.md) | Flags Consolidation |
| [ADR-014](ADR-014-sync-ux-flow.md)        | Sync UX Flow        |

### Lógica de Negócio

| ADR                                                 | Título                        |
| --------------------------------------------------- | ----------------------------- |
| [ADR-003](ADR-003-event-reordering.md)              | Event Reordering              |
| [ADR-007](ADR-007-service-layer.md)                 | Service Layer                 |
| [ADR-008](ADR-008-tuple-returns.md)                 | Tuple Returns                 |
| [ADR-011](ADR-011-conflict-philosophy.md)           | Conflict Philosophy           |
| [ADR-022](ADR-022-pause-tracking-simplification.md) | Pause Tracking Simplification |

### Sync Architecture

| ADR                                 | Título                    |
| ----------------------------------- | ------------------------- |
| [ADR-012](ADR-012-sync-strategy.md) | Queue-Based Sync Strategy |
| [ADR-014](ADR-014-sync-ux-flow.md)  | Connect Command UX Flow   |

### DevOps e Qualidade

| ADR                                               | Título                      |
| ------------------------------------------------- | --------------------------- |
| [ADR-016](ADR-016-alembic-timing.md)              | Alembic Timing              |
| [ADR-017](ADR-017-environment-strategy.md)        | Environment Strategy        |
| [ADR-018](ADR-018-language-standards.md)          | Language Standards          |
| [ADR-019](ADR-019-test-naming-convention.md)      | Test Naming Convention      |
| [ADR-020](ADR-020-business-rules-nomenclature.md) | Business Rules Nomenclature |
| [ADR-025](ADR-025-development-methodology.md)     | Development Methodology     |

### Microservices

| ADR                                           | Título                  |
| --------------------------------------------- | ----------------------- |
| [ADR-023](ADR-023-microservices-ecosystem.md) | Microservices Ecosystem |

### Infraestrutura

| ADR                                          | Título                          | Status   |
| -------------------------------------------- | ------------------------------- | -------- |
| [ADR-024](ADR-024-homelab-infrastructure.md) | Homelab Infrastructure Strategy | Proposto |

---

## Índice Numérico

| #   | Título                                                                    | Status   |
| --- | ------------------------------------------------------------------------- | -------- |
| 001 | [SQLModel ORM](ADR-001-sqlmodel-orm.md)                                   | Aceito   |
| 002 | [Typer CLI](ADR-002-typer-cli.md)                                         | Aceito   |
| 003 | [Event Reordering](ADR-003-event-reordering.md)                           | Aceito   |
| 004 | [Habit vs Instance](ADR-004-habit-vs-instance.md)                         | Aceito   |
| 005 | [Resource-First CLI](ADR-005-resource-first-cli.md)                       | Aceito   |
| 006 | [Textual TUI](ADR-006-textual-tui.md)                                     | Aceito   |
| 007 | [Service Layer](ADR-007-service-layer.md)                                 | Aceito   |
| 008 | [Tuple Returns](ADR-008-tuple-returns.md)                                 | Aceito   |
| 009 | [Flags Consolidation](ADR-009-flags-consolidation.md)                     | Aceito   |
| 010 | [Recurrence Model](ADR-010-recurrence-model.md)                           | Aceito   |
| 011 | [Conflict Philosophy](ADR-011-conflict-philosophy.md)                     | Aceito   |
| 012 | [Queue-Based Sync Strategy](ADR-012-sync-strategy.md)                     | Aceito   |
| 013 | [Offline-First Schema](ADR-013-offline-first-schema.md)                   | Aceito   |
| 014 | [Sync UX Flow](ADR-014-sync-ux-flow.md)                                   | Aceito   |
| 015 | [HabitInstance Naming](ADR-015-habitinstance-naming.md)                   | Aceito   |
| 016 | [Alembic Timing](ADR-016-alembic-timing.md)                               | Aceito   |
| 017 | [Environment Strategy](ADR-017-environment-strategy.md)                   | Aceito   |
| 018 | [Language Standards](ADR-018-language-standards.md)                       | Aceito   |
| 019 | [Test Naming Convention](ADR-019-test-naming-convention.md)               | Aceito   |
| 020 | [Business Rules Nomenclature](ADR-020-business-rules-nomenclature.md)     | Aceito   |
| 021 | [Status+Substatus Refactoring](ADR-021-status-substatus-refactoring.md)   | Aceito   |
| 022 | [Pause Tracking Simplification](ADR-022-pause-tracking-simplification.md) | Aceito   |
| 023 | [Microservices Ecosystem](ADR-023-microservices-ecosystem.md)             | Proposto |
| 024 | [Homelab Infrastructure Strategy](ADR-024-homelab-infrastructure.md)      | Proposto |
| 025 | [Development Methodology](ADR-025-development-methodology.md)             | Aceito   |

---

## Convenções

**Status:** Proposto | Aceito | Deprecado | Rejeitado

**Formato:** Ver [template.md](template.md)

**Nomenclatura:** `ADR-XXX-nome-descritivo.md`
