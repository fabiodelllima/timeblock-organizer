# TimeBlock Organizer - Status do Projeto

- **Última Atualização:** 01 de Novembro de 2025
- **Versão Atual:** v1.1.0 (Event Reordering - LANÇADO)

## Visão Rápida

TimeBlock Organizer é um sistema inteligente de gerenciamento de tempo via CLI usando princípios de time blocking e hábitos atômicos. O diferencial é a reordenação adaptativa de eventos que detecta conflitos automaticamente e propõe reorganização inteligente.

### Estado Atual

```terminal
v1.0.0 (ESTÁVEL)    [OK] 141 testes, 99% cobertura, baseline funcional
v1.1.0 (LANÇADO)    [OK] Event Reordering completo, 78 testes novos, 01 Nov 2025
v1.2.0 (PRÓXIMO)    Refatoração HabitAtom (ETA: 2 semanas)
```

## O Que Está Pronto

### Modelos Implementados (7 entidades)

**Core Models:**

- Event - Eventos básicos únicos (com EventStatus, EventColor enums)
- Routine - Container para hábitos recorrentes
- Habit - Padrão recorrente (template)
- HabitInstance - Ocorrência concreta em data específica
- Task - Evento único (substitui Event no futuro)
- TimeLog - Rastreamento de tempo real
- Tag - Categorização flexível

### Services Implementados (9 services)

1. RoutineService - CRUD para rotinas
2. HabitService - Gerenciamento de hábitos recorrentes
3. HabitInstanceService - Geração e ajuste de instâncias
4. TaskService - CRUD de tarefas únicas
5. TimerService - Start/pause/resume/stop timer
6. TagService - Gerenciamento de tags
7. **EventReorderingService** - [OK] LANÇADO v1.1.0 (90% cobertura)
8. ReportService - FUNCIONAL (daily, weekly, habit reports)
9. RoutineExecutionService - TODO (escopo a definir)

### Sistema de Reordenamento de Eventos - LANÇADO v1.1.0

**Status Geral:** [OK] LANÇADO em 01/Nov/2025

**Fase 1 - Core (100%):**

- [x] Sprint 1.1: Modelos Auxiliares (8 testes)
- [x] Sprint 1.2: Detectar Conflitos (9 testes)
- [x] Sprint 1.3: Calcular Prioridades (5 testes)
- [x] Sprint 1.4: Propor Reordenação (3 testes)

**Fase 2 - Integração (100%):**

- [x] Sprint 2.1: Integração TaskService (16 testes)
- [x] Sprint 2.2: HabitInstanceService (6 testes)
- [x] Sprint 2.3: TimerService (24 testes)
- [x] Sprint 2.4: CLI Preview (3 testes)

**Fase 3 - Aplicação (100%):**

- [x] Sprint 3.1: Apply Reordering (4 testes)
- [x] Sprint 3.2: Confirmação CLI (integrado)

**Cobertura de Código:**

```terminal
event_reordering_models.py      100% (45 linhas)
event_reordering_service.py      90% (168 linhas)
Total Event Reordering:          78 testes passando
```

### Comandos CLI Funcionais (9 grupos)

```shell
# v1.0.0 Baseline
timeblock init                    # Inicializar banco SQLite
timeblock add                     # Criar eventos (formato v1.0)
timeblock list                    # Listar eventos com filtros

# v1.1.0 Event Reordering
timeblock reschedule <id>         # Detecta e aplica reordenamento
timeblock reschedule preview <id> # Apenas visualiza proposta
timeblock reschedule <id> -y      # Aplica sem confirmação

# v2.0-dev Expandido
timeblock routine create/list/activate
timeblock habit create/list/update
timeblock task create/list/start/complete
timeblock timer start/stop/status
timeblock report daily/weekly/habit
timeblock schedule generate/list/edit
timeblock tag create/list/update
```

### Testes e Qualidade

```terminal
Testes Totais: 219 (141 baseline + 78 event reordering)
Cobertura Geral: ~50% (era 28%)
Event Reordering: 90% cobertura

Distribuição:
  - Testes unitários: 180
  - Testes integração: 39
  - Testes E2E: 0 (PENDENTE)

Status: [OK] 219 passando, 1 skip intencional
```

## O Que Está em Progresso

### v1.2.0 - Refatoração HabitAtom

**Início Previsto:** 02 de Novembro de 2025
**Status:** Planejamento

**Escopo:**

- Renomear HabitInstance -> HabitAtom
- Reposicionar filosoficamente (Atomic Habits)
- Melhorar testes como documentação viva
- Atualizar toda documentação técnica

**Estimativa:** 44h (~1-2 semanas)

## Débito Técnico

Ver [Débito Técnico](technical-debt.md) para detalhes completos.

**Resolvidos em v1.1.0:**

- [x] Event Reordering Fase 1 (era CRÍTICO)
- [x] Event Reordering Fase 2 (era 8h)
- [x] Event Reordering Fase 3 (era 6h)

**Pendentes:**

- [ ] Cobertura 50% -> 80% (estimativa: 10h) - MÉDIA prioridade
- [ ] Testes E2E Faltando (estimativa: 12h) - ALTA prioridade
- [ ] Refatoração HabitAtom (estimativa: 44h) - PRÓXIMO ciclo

## Próximos Releases

```terminal
v1.0.0 (LANÇADO)    [OK] Baseline (16 Out 2025)
v1.1.0 (LANÇADO)    [OK] Event Reordering (01 Nov 2025)
v1.2.0 (PRÓXIMO)    Refatoração HabitAtom (ETA: 15 Nov 2025)
v1.3.0 (MÉDIO)      Living Documentation (ETA: +6 semanas)
v2.0.0 (FUTURO)     Sistema Completo (ETA: 6+ meses)
```

## Ações Imediatas

**CONCLUÍDO:**

- [x] Event Reordering completo
- [x] Release v1.1.0 publicado
- [x] Documentação atualizada
- [x] CHANGELOG criado

**PRÓXIMA SEMANA:**

- [ ] Branch feat/habitatom-refactor
- [ ] Planejamento detalhado HabitAtom
- [ ] Início implementação

**2 SEMANAS:**

- [ ] Release v1.2.0 (HabitAtom)
- [ ] Testes E2E mínimos

## Métricas de Progresso

**v1.0.0 (Baseline):**

- Testes: 141
- Cobertura: 28%
- Comandos: 8 grupos

**v1.1.0 (Event Reordering):**

- Testes: 219 (+78, +55%)
- Cobertura: ~50% (+22pp)
- Comandos: 9 grupos (+reschedule)
- Features: Event Reordering completo

**Progresso Geral:**

- 2 releases públicos
- 219 testes (100% passando)
- 9 services implementados
- 7 entidades no modelo de dados

---

**Próxima Atualização:** Início do ciclo v1.2.0 (Refatoração HabitAtom)
**Responsável:** Mantenedor do projeto
**Documentos Relacionados:**

- [CHANGELOG](../../CHANGELOG.md)
- [Notas de Lançamento v1.1.0](release-notes-v1.1.0.md)
- [Débito Técnico](technical-debt.md)
- [Roadmap](detailed-roadmap.md)
- [Conclusão Event Reordering](event-reordering-completed.md)
