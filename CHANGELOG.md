# Histórico de Mudanças

Todas as mudanças importantes do TimeBlock Organizer serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Não Lançado]

### Alterado (Documentação)

- **(2025-12-01)** Reorganização completa de docs/
  - Consolidado 4 documentos principais em `docs/core/`:
    - architecture.md (v2.0.0)
    - business-rules.md (v3.0.0, 50 BRs)
    - cli-reference.md (v1.4.0)
    - workflows.md (v2.1.0)
  - Padronizado 22 ADRs em `docs/decisions/` (formato ADR-XXX)
  - Corrigido ADR-021 duplicado para ADR-022
  - Movido 130+ docs obsoletos para `docs/archived/`
  - Renomeado: 02-diagrams para diagrams, 07-testing para testing
  - Atualizado links quebrados em ADRs e README

### BREAKING CHANGES

- **(2025-11-19)** Refatoração Status+Substatus em HabitInstance (BR-HABIT-INSTANCE-STATUS-001)
  - Campo `status` mudou de `HabitInstanceStatus` (5 valores) para `Status` (3 valores)
  - Valores antigos: PLANNED, IN_PROGRESS, PAUSED, COMPLETED, SKIPPED
  - Valores novos: PENDING, DONE, NOT_DONE
  - Mapeamento automático na migração:
    - PLANNED/IN_PROGRESS/PAUSED → PENDING
    - COMPLETED → DONE + done_substatus=FULL
    - SKIPPED → NOT_DONE + not_done_substatus=SKIPPED_UNJUSTIFIED
  - **Ação necessária:** Rodar migration_001_status_substatus.py
  - **Rollback disponível:** função downgrade() (perda de dados novos)
  - **Compatibilidade:** HabitInstanceStatus mantido como alias temporário (DEPRECATED)

### Adicionado

- **(2025-11-19)** Enums para rastreamento detalhado (BR-HABIT-INSTANCE-STATUS-001)

  - `Status`: PENDING, DONE, NOT_DONE
  - `DoneSubstatus`: FULL (90-110%), PARTIAL (<90%), OVERDONE (110-150%), EXCESSIVE (>150%)
  - `NotDoneSubstatus`: SKIPPED_JUSTIFIED, SKIPPED_UNJUSTIFIED, IGNORED
  - `SkipReason`: HEALTH, WORK, FAMILY, TRAVEL, WEATHER, LACK_RESOURCES, EMERGENCY, OTHER

- **(2025-11-19)** Novos campos em HabitInstance

  - `done_substatus`: DoneSubstatus (calculado baseado em completion %)
  - `not_done_substatus`: NotDoneSubstatus (categorização de skip/ignore)
  - `skip_reason`: SkipReason (categoria do skip justificado)
  - `skip_note`: str (nota adicional do usuário)
  - `completion_percentage`: int (% de completion persistido)

- **(2025-11-19)** Validações de consistência Status+Substatus

  - DONE requer done_substatus obrigatório
  - NOT_DONE requer not_done_substatus obrigatório
  - PENDING não pode ter substatus
  - Substatus são mutuamente exclusivos
  - SKIPPED_JUSTIFIED requer skip_reason obrigatório
  - skip_reason só permitido com SKIPPED_JUSTIFIED
  - Método `validate_status_consistency()` implementado

- **(2025-11-19)** Migração SQL (migration_001_status_substatus.py)

  - Adiciona 5 colunas: done_substatus, not_done_substatus, skip_reason, skip_note, completion_percentage
  - Migra dados automaticamente preservando informação
  - Função upgrade() e downgrade() para rollback
  - Metadata: version=001, name=status_substatus_refactoring

- **(2025-11-19)** Documentação completa (BR-HABIT-INSTANCE-STATUS-001)

  - BR-HABIT-INSTANCE-STATUS-001: Especificação detalhada
  - 18 cenários BDD (Gherkin DADO/QUANDO/ENTÃO)
  - ADR-021: Decisão arquitetural documentada
  - 14 testes unitários (100% passando)
  - Cobertura: 84% (habit_instance.py)

- **(2025-11-17)** Fixtures de integração para testes

  - `test_db` - Session com FK habilitado
  - `sample_routine` - Routine pré-criada
  - `sample_habits` - 3 Habits com recorrências diferentes
  - `sample_task` - Task padrão
  - PRAGMA foreign_keys=ON no integration_engine

- **(2025-11-17)** Validação BR-HABIT-004: Recurrence Pattern

  - Model `habit.py` valida recurrence via **init** override
  - 10 padrões suportados (MONDAY-SUNDAY, WEEKDAYS, WEEKENDS, EVERYDAY)
  - Mensagens de erro claras listando valores válidos

- **(2025-11-17)** Business Rules HABIT implementadas
  - BR-HABIT-001: Title Validation (não vazio, max 200 chars, trim)
  - BR-HABIT-002: Time Range Validation (start < end)
  - BR-HABIT-003: Routine Association (FK constraint, delete RESTRICT)
  - BR-HABIT-004: Recurrence Pattern (enum validado)
  - BR-HABIT-005: Color Validation (hex format opcional)

### Modificado

- **(2025-11-19)** HabitInstance model refatorado

  - Status simplificado: 3 valores ao invés de 5
  - Sistema Status+Substatus para granularidade
  - Property `is_overdue` preservada (compatível)
  - Exports atualizados em `models/__init__.py`

- **(2025-11-17)** Services refatorados com Dependency Injection

  - `task_service.py` - Todos métodos aceitam session opcional
  - `timer_service.py` - start_timer, stop_timer, etc. com session
  - `event_reordering_service.py` - detect_conflicts com session
  - `habit_service.py` - CRUD completo com session opcional
  - `habit_instance_service.py` - Geração e marcação com session
  - Padrão: if session → usar injetada, else → criar própria

- **(2025-11-17)** Database engine com FK habilitado

  - `engine.py` - PRAGMA foreign_keys=ON no SQLite

- **(2025-11-17)** Imports refatorados
  - `routine_service.py` - Importa de src.timeblock.models
  - `conftest.py` - sqlalchemy.orm.Session → sqlmodel.Session

### Corrigido

- **(2025-11-17)** Testes de integração com Dependency Injection
  - 6 testes de timer integration corrigidos (FK constraints resolvidos)
  - 4 testes de fixtures validation corrigidos
  - Services agora aceitam session opcional: `session: Session | None = None`
  - Testes isolados com transações compartilhadas
  - Código produção mantém compatibilidade (backward compatible)

---

## [1.3.0] - 2025-11-08

### Adicionado em 2025-11-08

#### **Consolidação de Testing e Qualidade**

**Estrutura de Testing:**

- Consolidada estrutura em `05-testing/` (removido `07-testing/` duplicado)
- Adicionados documentos navegáveis:
  - `testing-philosophy.md` - Filosofia de testes do projeto
  - `requirements-traceability-matrix.md` - RTM completo com rastreabilidade BR → Test → Code
  - `test-strategy.md` - Estratégia consolidada de testes
- 5 scenarios de teste agora acessíveis:
  - event-creation
  - conflict-detection
  - event-reordering
  - habit-generation
  - timer-lifecycle

**Glossário Completo:**

- Glossário expandido para 298 linhas em `01-architecture/12-glossary.md`
- Todos termos principais definidos (TimeBlock, Habit, HabitInstance, Event, etc)
- HabitAtom marcado como DEPRECATED (apenas marketing)
- Relacionamentos entre conceitos documentados

**Business Rules Formalizadas:**

- `event-reordering.md` - Especificação formal completa (222 linhas)
- Princípios fundamentais: Controle Explícito do Usuário, Informação sem Imposição
- BR-EVENT-001 a BR-EVENT-007 documentadas
- Mudança de propósito: Sistema apenas DETECTA conflitos, não propõe reordenamento automático

**Impacto:**

- Testing structure consolidada e sem duplicações
- Glossário completo e preciso
- Business Rules formalmente especificadas
- Alinhamento filosofia: usuário sempre no controle

**Commits:**

- docs: Consolida testing em 05-testing/
- docs(glossary): Expande glossário com todos termos
- docs(specs): Formaliza Business Rules event-reordering

---

## [1.2.2] - 2025-11-10

### Adicionado em 2025-11-10

#### **Sistema de Logging Estruturado - Sprint 1.3**

**Módulo de Logging:**

- `cli/src/timeblock/utils/logger.py` (118 linhas)
  - `setup_logger()` com rotating file handler
  - `get_logger()` helper para obter logger configurado
  - `disable_logging()` / `enable_logging()` para testes
  - Formato estruturado: `[timestamp] [level] [module] message`
  - Suporte a console e arquivo com rotação automática (10MB, 5 backups)

**Testes de Logging:**

- `cli/tests/unit/test_utils/test_logger.py` (277 linhas)
- TestSetupLogger: 6+ testes de configuração
- TestGetLogger: testes de obtenção de logger
- TestDisableEnableLogging: testes de controle
- 100% cobertura do módulo logger

**Integração:**

- Logs estruturados em services principais
- Níveis configuráveis: DEBUG, INFO, WARNING, ERROR
- Log rotation automática para evitar crescimento descontrolado

**Métricas:**

- 6+ novos testes (todos passando)
- Módulo completo e documentado
- Pronto para uso em produção

**Commits:**

- feat(logging): Implementa sistema de logging estruturado
- test(logging): Adiciona 6 testes para logger.py
- docs(logging): Documenta uso e configuração

---

## [1.2.1] - 2025-11-11

### Adicionado em 2025-11-11

#### **Reorganização e Consolidação da Documentação**

**Estrutura de Documentação:**

- 9 ADRs agora navegáveis no mkdocs (ADR-012 a ADR-020)
  - ADR-012: Sync Strategy
  - ADR-013: Offline-First Schema
  - ADR-014: Sync UX Flow
  - ADR-015: HabitInstance Naming
  - ADR-016: Alembic Timing
  - ADR-017: Environment Strategy
  - ADR-018: Language Standards
  - ADR-019: Test Naming Convention
  - ADR-020: Business Rules Nomenclature

**Consolidação de Arquitetura:**

- Unificada estrutura em `01-architecture/` (removidos `02-architecture/` e `01-guides/`)
- Adicionados documentos navegáveis:
  - `00-architecture-overview.md` - Visão geral consolidada (20KB)
  - `16-sync-architecture-v2.md` - Arquitetura de sincronização v2.0
  - `17-user-control-philosophy.md` - Filosofia de controle do usuário (15KB)
  - `18-project-philosophy.md` - Filosofia de hábitos atômicos (12KB)

**Impacto:**

- 20 ADRs navegáveis (vs 11 anteriormente) = +82%
- Estrutura de docs/ organizada e sem duplicações
- Melhor navegabilidade do site de documentação
- Documentação de filosofia e princípios do projeto

**Commits:**

- docs(mkdocs): Adiciona 9 ADRs faltantes na navegação (8b88b7b)
- docs: Consolida arquitetura em 01-architecture/ (f3fcb5f)
- docs: Remove duplicações e organiza estrutura

---

## [1.1.0] - 2025-11-01

### Adicionado em 2025-11-01

#### **Sistema de Reordenamento de Eventos - Implementação Completa**

- Detecção automática de conflitos entre eventos agendados
- Cálculo de prioridades baseado em status e prazos (CRITICAL, HIGH, NORMAL, LOW)
- Algoritmo de reordenamento sequencial que respeita prioridades
- Confirmação interativa antes de aplicar mudanças
- Novo comando CLI: `timeblock reschedule [preview] [--auto-approve]`

**Services Aprimorados:**

- `TaskService.update_task()` agora retorna tupla com ReorderingProposal opcional
- `HabitInstanceService.adjust_instance_time()` integrado com detecção de conflitos
- `TimerService.start_timer()` detecta conflitos ao iniciar timers

**Novos Componentes:**

- `EventReorderingService` - Lógica central de reordenamento (90% cobertura de testes)
- `event_reordering_models.py` - Estruturas de dados (EventPriority, Conflict, ProposedChange, ReorderingProposal)
- `proposal_display.py` - Saída CLI formatada com Rich para propostas
- `reschedule.py` - Implementação do comando CLI

**Testes:**

- 78 novos testes (219 total, +55% de aumento)
- 100% cobertura em event_reordering_models
- 90% cobertura em event_reordering_service
- Testes de integração para todos os services afetados

**Documentação:**

- Documentação técnica completa em `docs/10-meta/event-reordering-completed.md`
- Retrospectiva de sprints em `docs/10-meta/sprints-v2.md`
- Arquitetura e documentação de API atualizadas

### Alterado

- Services agora retornam tuplas onde apropriado para incluir propostas de reordenamento
- Mensagens de erro aprimoradas com informações de conflito

### Corrigido

- Nenhum (sem bugs corrigidos, este é um release puramente de features)

### Mudanças Incompatíveis

- Nenhuma

### Performance

- Detecção de conflitos otimizada para complexidade O(n log n)
- Consultas eficientes de eventos em intervalos de datas

### Guia de Migração

Nenhuma migração necessária. Todas as mudanças são retrocompatíveis.

---

## [1.0.0] - 2025-10-16

### Adicionado em 2025-10-16

- Release baseline inicial
- Inicialização do banco de dados SQLite
- Operações CRUD básicas para eventos
- Listagem de eventos com filtros (dia, semana)
- Suporte a formato brasileiro de tempo (7h, 14h30)
- Detecção básica de conflitos (apenas aviso, não bloqueante)
- Suporte para eventos que cruzam meia-noite
- 141 testes com 99% de cobertura

**Comandos CLI:**

- `timeblock init` - Inicializar banco de dados
- `timeblock add` - Criar eventos
- `timeblock list` - Listar eventos com filtros

### Limitações Conhecidas

- Sem hábitos recorrentes
- Sem reordenamento automático
- Sem relatórios ou analytics
- CLI básica (sem TUI)

---

[Não Lançado]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/fabiodelllima/timeblock-organizer/releases/tag/v1.0.0
