# Testes Falhando no Develop - Sprint 3.4 Phase 3

## Resumo

21 testes falhando após merge da feature pause/resume/cancel

## Categorias

### 1. Fixture sem Rotina Ativa (11 testes)

- E2E: 4 testes
- Habit Commands: 7 testes

**Problema:** Fixture não cria rotina ativa antes de criar hábitos

**Arquivos:**

- tests/e2e/test_event_creation.py (2 falhas)
- tests/e2e/test_habit_lifecycle.py (2 falhas)
- tests/integration/commands/test_habit_commands.py (7 falhas)

### 2. API Task Start Mudou (3 testes)

- test_task_cmd_start_001_task
- test_task_cmd_start_002_already_started
- test_task_cmd_start_003_invalid_id

**Problema:** API mudou (similar ao TimerService v2)

**Arquivo:**

- tests/integration/commands/test_task_commands.py

### 3. Schema Incompatível (7 testes)

- Testes de integração Habit/Task

**Problema:** Campo `done_substatus` não existe, FK constraints falhando

**Arquivos:**

- tests/integration/services/test_habit_instance_integration.py (3 falhas)
- tests/integration/services/test_task_integration.py (4 falhas)

## Ação Necessária

**Sprint 3.4 Phase 4:** Corrigir fixtures e atualizar testes para API v2

## Débito Técnico Já Marcado como Skip

- test_timer_integration.py (6 testes) - API v2 não suporta task_id
- test_migrations.py (6 testes) - migrate_v2() não implementado
