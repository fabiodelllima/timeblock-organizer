# Prompt para Próximo Chat - TimeBlock Organizer

**Copie e cole no início do novo chat:**

---

Olá! Estou continuando o desenvolvimento do **TimeBlock Organizer**, um CLI para gerenciar hábitos recorrentes e resolver conflitos de agenda automaticamente.

## Contextoo do Projeto

**Repositório:** <https://github.com/fabiodelllima/timeblock-organizer>
**Versão Atual:** v0.9 (pré-release)
**Meta:** Release v1.0

### Stack Técnica

- Python 3.11+
- SQLite (local-first)
- SQLModel (ORM)
- Typer (CLI)
- Pytest (testes)

### Arquitetura

```terminal
CLI Commands → Services (business logic) → Models (SQLModel) → SQLite
```

## Estado Atual

### COMPLETO

- Documentação arc42 (12 seções)
- ADRs 001-008
- Business Rules BR001-BR004
- Models: Habit, HabitInstance, Task, Timer
- Services: Habit, Task, Timer, EventReordering
- CLI: habit, task, timer, reschedule commands
- Tests: Unit 85%, Integration 70%

### DÉBITO TÉCNICO CRÍTICO

1. **Tuple Returns Deprecated** (ADR-008)

   - Services retornando `(success, data, error)`
   - Migrar para: return direto ou raise exception
   - Esforço: 4h

2. **E2E Tests Ausentes** (0%)

   - 5 cenários críticos sem testes
   - Impede release v1.0
   - Esforço: 12h

3. **Coverage 75% → 90%**
   - Unit tests: 85% → 90% (faltam model properties)
   - Integration: 70% → 80% (faltam CLI parsers)
   - Esforço: 10h

### FEATURES FALTANDO

1. **ReportService** (prioridade alta)

   - Completion rate
   - Time variance
   - Daily/weekly summaries
   - Esforço: 8h

2. **RoutineService** (prioridade TBD)

   - Executar sequência de habits
   - Escopo v1.0 ou v2.0?
   - Esforço: 12h

3. **Config Management**
   - `.timeblockrc` persistente
   - `config set/get/list` commands
   - Esforço: 4h

## Dúvidas Pendentes

1. **Routine está no escopo v1.0?**
2. **Reports: quais métricas essenciais?**
3. **Notificações: incluir em v1.0?**
4. **Performance: testar com quantos eventos?**

## Documentação

**Localização:** `docs/`
**Tool:** mkdocs-material
**Status:** 100% estruturado

Arquivos importantes:

- `docs/10-meta/problemas-e-solucoes.md` - Histórico sessão anterior
- `docs/04-specifications/business-rules/` - Regras de negócio
- `docs/03-decisions/` - ADRs
- `ROADMAP.md` - Planejamento geral

## Objetivo da Sessão

**Prioridade 1:** Remover tuple returns
**Prioridade 2:** Implementar E2E tests
**Prioridade 3:** ReportService

**Abordagem Sugerida:**

1. Partir das business rules documentadas
2. Escrever testes primeiro (TDD)
3. Refatorar código existente
4. Validar com testes

## Comandos Úteis

```shell
# Testes
pytest
pytest --cov

# Docs
mkdocs serve

# Estrutura
tree cli/src/timeblock/
```

## Perguntas para Iniciar

1. Por qual débito técnico começar?
2. Routine entra em v1.0?
3. Alguma dúvida sobre as business rules?

---

**Nota:** Este projeto usa TDD rigoroso. Sempre escrever testes antes de implementar features.
