# Histórico de Mudanças

Todas as mudanças importantes do TimeBlock Organizer serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Não Lançado]

### Adicionado em 2025-11-16

#### **Sprint 1: ROUTINE - Implementação Completa**

**Models:**

- `routine.py` - Modelo Routine com is_active=False por padrão (BR-ROUTINE-001)
- `habit.py` - FK routine_id com ondelete=RESTRICT (BR-ROUTINE-002)

**Services:**

- `routine_service.py` - 5 operações principais:
  - `create()` - Cria routine inativa
  - `activate()` - Ativa routine e desativa outras
  - `get_active()` - Retorna routine ativa
  - `delete()` - Soft delete (padrão)
  - `hard_delete()` - Hard delete condicional (sem habits)

**Business Rules Implementadas (4/4):**

- BR-ROUTINE-001: Single Active Constraint
  - Apenas uma routine ativa por vez
  - Ativação desativa outras automaticamente
  - Nova routine criada inativa por padrão
- BR-ROUTINE-002: Habit Belongs to Routine
  - Habit vinculado obrigatoriamente a routine
  - FK com ondelete=RESTRICT protege dados
  - Delete behaviors: soft (padrão) e hard (condicional)
- BR-ROUTINE-003: Task Independent of Routine
  - Task não tem campo routine_id
  - Delete routine mantém tasks intactas
- BR-ROUTINE-004: Activation Cascade
  - Primeira routine ativada automaticamente
  - get_active retorna routine ativa
  - Habits filtrados por routine ativa

**Testes:**

- 18 novos testes unitários validando 4 BRs (18/18 GREEN)
- Classes organizadas por BR (TestBRRoutine001, TestBRRoutine002, etc)
- Padrão test*br*\* para rastreabilidade direta
- 100% cobertura nos modelos routine e habit

**Documentação:**

- `docs/04-specifications/business-rules/routine.md` - 4 BRs formalizadas
- `docs/06-bdd/scenarios/routine.feature` - 6 scenarios Gherkin
- `docs/sprints/sprint-1-routine-summary.md` - Resumo executivo

**Infrastructure:**

- `conftest.py` - PRAGMA foreign_keys habilitado no SQLite
- `conftest.py` - collections.abc.Generator (Python 3.9+)
- Event listener para configuração automática de FK

**Decisões Arquiteturais:**

- SQLModel mantido (validação runtime + 50-70% menos código)
- ondelete=RESTRICT protege integridade de dados
- Soft delete como padrão (preserva histórico)

**Métricas:**

- Testes: 18/18 GREEN ✓
- Coverage: 100% (models routine/habit)
- Ruff: All checks passed
- Arquivos modificados: 10 (+486 linhas / -93 linhas)

**Commits:**

- e97a1fd Merge branch 'feature/mvp-sprint1-routine' into develop
- 10d00d1 feat(routine): Implementa Sprint 1 ROUTINE - 4 BRs validadas (18/18 GREEN)
- 4e824a0 test(br): Adiciona 6 testes para delete behaviors e first routine
- 47a778c docs(bdd): Adiciona 6 scenarios para delete behaviors e first routine
- 3387ae8 docs(br): Atualiza routine.md com delete behaviors
- 5f4e0fc docs(sprint): Adiciona resumo executivo do Sprint 1 ROUTINE

---

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
  - 00-architecture-overview.md (visão geral consolidada)
  - 16-sync-architecture-v2.md (arquitetura de sincronização)
  - 17-user-control-philosophy.md (filosofia de controle do usuário)
  - 18-project-philosophy.md (filosofia de hábitos atômicos)

**Consolidação de Testing:**

- Unificada estrutura em `05-testing/` (removido `07-testing/`)
- Adicionados documentos navegáveis:
  - testing-philosophy.md (filosofia de testes)
  - requirements-traceability-matrix.md (RTM completo)
  - test-strategy.md (estratégia consolidada)
- 5 scenarios de teste agora acessíveis (event-creation, conflict-detection, event-reordering, habit-generation, timer-lifecycle)

**Impacto:**

- 20 ADRs navegáveis (vs 11 anteriormente)
- Estrutura de docs/ organizada e sem duplicações
- Melhor navegabilidade do site de documentação

**Commits:**

- docs(mkdocs): Adiciona 9 ADRs faltantes na navegação (8b88b7b)
- docs: Consolida arquitetura em 01-architecture/ (f3fcb5f)
- docs: Consolida testing em 05-testing/ (f465497)

### Planejado

- Sprint 2: HABIT (HabitService + recurrence logic)
- Refatoração HabitAtom (renomear HabitInstance para HabitAtom)
- Documentação Viva com BDD
- Funcionalidades avançadas de relatórios

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
