# TimeBlock Organizer - Status do Projeto

**Última Atualização:** 01 de Novembro de 2025  
**Versão Atual:** v1.0.0 (baseline estável) + v2.0-dev (85% completo)

## Visão Rápida

TimeBlock Organizer é um sistema inteligente de gerenciamento de tempo via CLI usando princípios de time blocking e hábitos atômicos. O diferencial é a reordenação adaptativa de eventos que detecta conflitos automaticamente e propõe reorganização inteligente.

### Estado Atual
```terminal
v1.0.0 (ESTÁVEL)    [OK] 141 testes, 99% cobertura, 3 comandos funcionais
v2.0-dev (85%)      [OK] Event Reordering Fase 1 completa, 8 grupos comando
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
7. EventReorderingService - (Fase 1: 100% completo)
8. ReportService - FUNCIONAL (daily, weekly, habit reports)
9. RoutineExecutionService - TODO (escopo a definir)

### Comandos CLI Funcionais (8 grupos)
```shell
# v1.0.0 Baseline
timeblock init          # Inicializar banco SQLite
timeblock add           # Criar eventos (formato v1.0)
timeblock list          # Listar eventos com filtros

# v2.0-dev Expandido
timeblock routine create/list/activate
timeblock habit create/list/update
timeblock task create/list/start/complete
timeblock timer start/stop/status
timeblock report daily/weekly/habit
timeblock schedule generate/list/edit
timeblock tag create/list/update
timeblock reschedule [preview]
```

### Testes e Qualidade
```terminal
Testes: 341 coletados, 28% cobertura
  - 43 arquivos teste
  - Unitários, integração, fixtures
  - Testes E2E: 0% (PENDENTE)

Regras de negócio: 33 catalogadas, testadas
Linter: Ruff configurado
Type checking: mypy parcialmente configurado
```

## O Que Está em Progresso

### Status Event Reordering
```terminal
FASE 0: Pré-requisitos [100% COMPLETO]
FASE 1: Event Reordering Core [100% COMPLETO]
  Sprint 1.1: Modelos Auxiliares [OK]
  Sprint 1.2: Detectar Conflitos [OK]
  Sprint 1.3: Calcular Prioridades [OK]
  Sprint 1.4: Propor Reordenação [OK]

FASE 2: Integração [INICIADA]
  - Integrar com HabitInstanceService
  - Integrar com TaskService
  - CLI preview das propostas

FASE 3: Aplicação [PENDENTE]
  - Implementação apply_reordering()
  - Confirmação interativa
```

## Débito Técnico

Ver [Débito Técnico](technical-debt.md) para detalhes completos.

1. **Cobertura 28% -> 80%** (15h) - ALTA prioridade
2. **Testes E2E Faltando** (12h) - ALTA prioridade
3. **Fase 2 Event Reordering** (8h) - ALTA prioridade

## Próximos Releases
```terminal
v1.0.0 (ATUAL)      [OK] Baseline (16 Out 2025)
v1.1.0 (PRÓXIMO)     Event Reordering completo (ETA: +1 semana)
v1.2.0 (MÉDIO)       HabitAtom refactor (ETA: +4 semanas)
v2.0.0 (FUTURO)      Sistema Completo (ETA: 6+ meses)
```

## Ações Imediatas

**ESTA SEMANA:**
- [ ] Event Reordering Fase 2 (8h)
- [ ] Testes E2E mínimos (12h)

**2 SEMANAS:**
- [ ] Event Reordering Fase 3 (6h)
- [ ] Release v1.1.0

---

**Próxima Atualização:** Após Fase 2 Event Reordering  
**Responsável:** Mantenedor do projeto  
**Documentos Relacionados:** [Débito Técnico](technical-debt.md) | [Roadmap](detailed-roadmap.md)
