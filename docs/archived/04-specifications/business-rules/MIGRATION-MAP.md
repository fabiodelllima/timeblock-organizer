# Mapa de Migração - Business Rules

- **Versão:** 2.0
- **Data:** 11 de Novembro de 2025
- **Contexto:** Migração de nomenclatura conforme ADR-020

---

## Padrão Antigo → Padrão Novo

### Tasks (TASK)

| Antigo      | Novo                   | Descrição             |
| ----------- | ---------------------- | --------------------- |
| BR-TASK-001 | BR-TASK-CREATE-001     | Criação de task       |
| BR-TASK-002 | BR-TASK-CREATE-002     | Agendamento temporal  |
| BR-TASK-003 | BR-TASK-CREATE-003     | Prioridade            |
| BR-TASK-004 | BR-TASK-UPDATE-001     | Atualização de campos |
| BR-TASK-005 | BR-TASK-DELETE-001     | Deleção de task       |
| BR-TASK-006 | BR-TASK-LIST-001       | Listagem básica       |
| BR-TASK-007 | BR-TASK-FILTER-001     | Filtro por data       |
| BR-TASK-008 | BR-TASK-VALIDATION-001 | Validação de título   |
| BR-TASK-009 | BR-TASK-VALIDATION-002 | Validação de horário  |

### Hábitos (HABIT)

| Antigo       | Novo                | Descrição                |
| ------------ | ------------------- | ------------------------ |
| BR-HABIT-001 | BR-HABIT-CREATE-001 | Criação de hábito        |
| BR-HABIT-002 | BR-HABIT-CREATE-002 | Validação de recorrência |
| BR-HABIT-003 | BR-HABIT-LIST-001   | Listagem de hábitos      |
| BR-HABIT-004 | BR-HABIT-DELETE-001 | Deleção de hábito        |

### Eventos (EVENT)

| Antigo       | Novo                  | Descrição                 |
| ------------ | --------------------- | ------------------------- |
| BR-EVENT-001 | BR-EVENT-CONFLICT-001 | Detecção de conflitos     |
| BR-EVENT-002 | BR-EVENT-REORDER-001  | Proposta de reorganização |
| BR-EVENT-003 | BR-EVENT-LIST-001     | Listagem de eventos       |

---

## BRs Novas (Criadas no Sprint 2)

### Já Documentadas nos Testes

**TASK:**

- BR-TASK-CREATE-004 a 006: Criação com descrição, cor, campos opcionais
- BR-TASK-INPUT-001 a 005: Validação de inputs
- BR-TASK-REORDER-001 a 006: Reorganização e conflitos

**HABIT:**

- BR-HABIT-REORDER-001 a 005: Reorganização de instâncias

**EVENT:**

- BR-EVENT-FILTER-001 a 006: Filtros temporais
- BR-EVENT-LIST-002 a 003: Listagem com dados

**SYSTEM:**

- BR-SYSTEM-INIT-001 a 004: Inicialização do sistema
- BR-CLI-MAIN-001: Comando version

**DATABASE:**

- BR-DB-MIGRATE-001 a 006: Criação de tabelas

**TEST:**

- BR-TEST-INFRA-001: Infraestrutura de testes

---

## Status de Documentação

| BR                    | Testes | Docs | Status      |
| --------------------- | ------ | ---- | ----------- |
| BR-TASK-CREATE-\*     | SIM    | MIGR | Migrar docs |
| BR-TASK-INPUT-\*      | SIM    | NAO  | Criar docs  |
| BR-TASK-VALIDATION-\* | SIM    | MIGR | Migrar docs |
| BR-TASK-REORDER-\*    | SIM    | NAO  | Criar docs  |
| BR-HABIT-CREATE-\*    | SIM    | MIGR | Migrar docs |
| BR-HABIT-LIST-\*      | SIM    | MIGR | Migrar docs |
| BR-HABIT-DELETE-\*    | SIM    | MIGR | Migrar docs |
| BR-HABIT-REORDER-\*   | SIM    | NAO  | Criar docs  |
| BR-EVENT-FILTER-\*    | SIM    | NAO  | Criar docs  |
| BR-EVENT-LIST-\*      | SIM    | MIGR | Migrar docs |
| BR-SYSTEM-INIT-\*     | SIM    | NAO  | Criar docs  |
| BR-CLI-MAIN-\*        | SIM    | NAO  | Criar docs  |
| BR-DB-MIGRATE-\*      | SIM    | NAO  | Criar docs  |
| BR-TEST-INFRA-\*      | SIM    | NAO  | Criar docs  |

**Legenda:**

- SIM = Implementado
- MIGR = Precisa migrar/atualizar
- NAO = Precisa criar do zero

---

## Próximos Passos

1. [CONCLUIDO] Criar este mapa (MIGRATION-MAP.md)
2. [PENDENTE] Atualizar arquivos existentes (tasks.md, habit-instances.md, event-reordering.md)
3. [PENDENTE] Criar arquivos novos para BRs faltantes
4. [PENDENTE] Atualizar índice em `docs/07-testing/README.md`
5. [PENDENTE] Atualizar RTM

---

**Referências:**

- ADR-020: Business Rules Nomenclature
- Sprint 2: Test Refactoring (origem das novas BRs)
