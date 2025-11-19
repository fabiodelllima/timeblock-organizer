# Sessão MVP - Decisões Completas sobre Business Rules

- **Data:** 19 de novembro de 2025
- **Tipo:** Consolidação de Decisões Técnicas
- **Status:** [DEFINITIVO]
- **Prioridade:** CRÍTICA

---

## CONTEXTO

Sessão de esclarecimento de 56 perguntas enumeradas sobre Business Rules, comandos CLI, modelo de dados e escopo do MVP v1.4.0. Todas as decisões tomadas pelo desenvolvedor foram consolidadas neste documento para guiar a implementação.

**Metodologia aplicada:** DOCS/BR → BDD → TDD → CODE

---

## ÍNDICE

1. [Comandos CLI Básicos](#1-comandos-cli-basicos)
2. [Dashboard e Visualização](#2-dashboard-e-visualizacao)
3. [Modelo de Dados](#3-modelo-de-dados)
4. [Timer Commands](#4-timer-commands)
5. [Reports](#5-reports)
6. [Recurrence Patterns](#6-recurrence-patterns)
7. [Habit Template vs Instance](#7-habit-template-vs-instance)
8. [Skip Functionality](#8-skip-functionality)
9. [Completion Status](#9-completion-status)
10. [Testes E2E](#10-testes-e2e)
11. [Streak](#11-streak)
12. [Verificações Realizadas](#12-verificacoes-realizadas)
13. [Próximos Passos](#13-proximos-passos)

---

## 1. COMANDOS CLI BÁSICOS

### 1.1 Habit Create vs Add

**Pergunta 1:** Comando correto é `habit create` ou `habit add`?

**Decisão:** C) Aceitar ambos (aliases)

**Implementação:**

```python
@app.command(name="create")
@app.command(name="add")  # Alias
def create_habit(...):
    pass
```

---

### 1.2 Edição de Entidades

**Pergunta 2:** Como editar habit vs task?

**Decisão:** A) `habit update/edit` e `task update/edit` (são diferentes)

**Importante:** Habits e Tasks NÃO SÃO o mesmo.

---

### 1.3 Comando para Instâncias

**Pergunta 3:** schedule vs repeat vs generate?

**Decisão:** B) Comando correto é `repeat` (não generate)

**Esclarecimento adicional (Pergunta 5):** Confirmado `repeat` como comando oficial.

---

### 1.4 Flag --generate

**Pergunta 2 (segunda parte):** Flag `--generate` deve existir?

**Decisão:** A) Remover flag (legacy do POC)

**Justificativa:** Comando `repeat` é mais semântico.

---

## 2. DASHBOARD E VISUALIZAÇÃO

### 2.1 Comando Dashboard

**Pergunta 6:** Dashboard deveria existir no MVP?

**Decisão:** SIM, comando `timeblock dashboard` com interface mínima gerenciada por linha de comando.

---

### 2.2 Dashboard Colunas

**Pergunta 51:** Quais colunas mostrar?

**Tabela Habits:**

- ID
- Nome
- Horário
- Status

**Tabela Tasks:**

- ID
- Nome
- Status
- Data
- Horário
- Cor

---

### 2.3 Dashboard Modo de Exibição

**Pergunta 55:** Estático ou watch mode?

**Decisão:** C) Ambos (estático default + --watch opcional)

**Implementação:**

```bash
# Estático (default)
timeblock dashboard

# Watch mode (atualização a cada 5s)
timeblock dashboard --watch
```

**Esforço estimado:**

- Estático: ~2-3h
- Watch mode: +2h adicional
- Total: ~4-5h

---

## 3. MODELO DE DADOS

### 3.1 Campos HabitInstance

**Pergunta 8:** Modelo tem campos skip\_\* e substatus?

**Decisão:** A) Nenhum implementado atualmente

**Campos a adicionar:**

```python
class HabitInstance:
    # Campos existentes
    id: int
    habit_id: int
    scheduled_date: date
    start_time: time
    end_time: time
    status: HabitInstanceStatus

    # NOVOS campos necessários
    skip_reason: SkipReason | None = None
    skip_note: str | None = None
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None
```

---

### 3.2 Status vs Substatus Refatoração

**Pergunta 9:** Refatorar para Status+Substatus?

**Decisão:** A) Refatorar agora (breaking change necessário)

**Migração necessária:**

**Status atual:**

```python
class HabitInstanceStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    # ...
```

**Status novo (simplificado):**

```python
class Status(str, Enum):
    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"

class DoneSubstatus(str, Enum):
    FULL = "full"              # 90-110%
    OVERDONE = "overdone"      # 110-150%
    EXCESSIVE = "excessive"    # >150%
    PARTIAL = "partial"        # <90%

class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"
```

---

### 3.3 Routine Scope

**Pergunta 10:** Routine contém apenas Habits ou também Tasks?

**Decisão:** A) Sim, routine só tem habits (validação OK)

**Regra confirmada:** Tasks são independentes, não pertencem a routines.

---

### 3.4 SkipReason + NotDoneSubstatus

**Pergunta 46:** Usar ambos enums?

**Decisão:** A) Sim, usar AMBOS campos

**Modelo final:**

```python
class HabitInstance:
    not_done_substatus: NotDoneSubstatus  # Estado: JUSTIFIED/UNJUSTIFIED/IGNORED
    skip_reason: SkipReason | None        # Categoria: HEALTH/WORK/FAMILY (só se JUSTIFIED)
    skip_note: str | None                 # Nota adicional opcional
```

**SkipReason (8 categorias confirmadas):**

```python
class SkipReason(str, Enum):
    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    TRAVEL = "viagem"
    WEATHER = "clima"
    LACK_RESOURCES = "falta_recursos"
    EMERGENCY = "emergencia"
    OTHER = "outro"
```

**Fluxo:**

1. `habit skip 42 --category HEALTH` → `not_done_substatus = SKIPPED_JUSTIFIED, skip_reason = HEALTH`
2. 24h sem categoria → `not_done_substatus = SKIPPED_UNJUSTIFIED, skip_reason = None`

---

## 4. TIMER COMMANDS

### 4.1 Timer Implementado

**Pergunta 12:** Todos comandos timer implementados?

**Decisão:** C) Verificar código

**Verificação realizada:**

```bash
cli/src/timeblock/commands/timer.py
```

**Resultado:** [OK] TODOS os 6 comandos implementados

| Comando | Linha | Status                  |
| ------- | ----- | ----------------------- |
| start   | 103   | [OK]                    |
| pause   | 187   | [OK]                    |
| resume  | 204   | [OK]                    |
| stop    | 224   | [OK]                    |
| cancel  | 254   | [OK] (equivale a reset) |
| status  | 275   | [OK]                    |

**Nota:** `cancel` equivale a `reset` (cancela timer sem salvar).

---

### 4.2 Múltiplas Sessões Timer

**Perguntas 15/23/44:** Sistema permite múltiplas sessões do mesmo habit no mesmo dia?

**Decisão:** B) Não implementado, precisa implementar

**Cenário esperado:**

```bash
# Sessão 1 (manhã)
timer start Academia  # 60min
timer stop  # Salva sessão 1 (TimeLog)

# Sessão 2 (tarde) - MESMO habit, MESMO DIA
timer start Academia  # 35min
timer stop  # Salva sessão 2 (TimeLog separado)

# Total acumulado: 95min (106% meta) = OVERDONE
```

**Implementação necessária:**

- Permitir múltiplos TimeLogs para mesmo habit_instance_id
- Calcular completion_percentage somando todas sessões do dia
- Atualizar HabitInstance.status baseado na soma

---

## 5. REPORTS

### 5.1 Reports no MVP

**Perguntas 13/48:** Algum report já implementado?

**Decisão inicial:** B) Nenhum implementado

**Pergunta 54:** Implementar no MVP?

**Decisão final:** A) Sim, os 3 no MVP v1.4.0

**Reports a implementar:**

1. `report daily` - Hábitos e tasks do dia
2. `report weekly` - Resumo semanal com estatísticas
3. `report habit <id>` - Análise detalhada de um hábito

**Pergunta 24:** Ordem de prioridade?

**Decisão:** Tanto faz a ordem (implementar os 3)

---

## 6. RECURRENCE PATTERNS

### 6.1 RRULE Completo

**Pergunta 14:** 10 padrões suficientes ou RRULE completo?

**Decisão:** B) Implementar RRULE completo

**RRULE (RFC 5545):** Padrão para recorrências complexas.

**Exemplos:**

```python
# Simples
"FREQ=DAILY;INTERVAL=2"                     # A cada 2 dias
"FREQ=WEEKLY;BYDAY=MO,WE,FR"                # Seg, Qua, Sex

# Complexos
"FREQ=MONTHLY;BYMONTHDAY=15"                # Dia 15 de cada mês
"FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15"       # 15 de junho todo ano
"FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20251231" # Até data
"FREQ=MONTHLY;BYDAY=2MO"                    # Segunda segunda-feira do mês
```

**Implementação:** Usar biblioteca `python-dateutil` (rrule parser).

---

## 7. HABIT TEMPLATE VS INSTANCE

### 7.1 Edit Habit - Abordagens

**Pergunta 18:** Como editar template vs instance?

**Decisão:** `habit template edit` (NÃO precisa `habit instance edit`)

**Comandos definidos:**

```bash
# Editar template (afeta futuras instâncias)
habit template edit 42 --duration 90

# NÃO implementar habit instance edit
# (instâncias são imutáveis, apenas status muda)
```

**Justificativa:** Instâncias são geradas a partir do template. Editar instância individual quebra consistência. Apenas status e completion devem mudar.

---

### 7.2 Comando Renew

**Pergunta 19:** Comando renew documentado?

**Decisão:** Sim, encontrado no histórico (chats 14/11 e 18/10)

**Histórico consolidado:**

**Evolução:**

1. Versão inicial (18/10): Flag `--generate` no `habit create`
2. Problema (14/11): Sintaxe feia (`6months`)
3. Solução final: Comando dedicado `habit renew`

**Sintaxe aprovada:**

```bash
habit renew HABIT_ID [OPTIONS]

# Períodos predefinidos (limpo)
--for semester     # 6 meses
--for quarter      # 3 meses (DEFAULT)
--for month        # 1 mês

# OU customizado
--months 6
--weeks 2
--days 30
```

**Exemplos:**

```bash
habit renew 1                    # +3 meses (default: quarter)
habit renew 1 --for semester     # +6 meses
habit renew 1 --months 4         # +4 meses customizado
```

---

### 7.3 Aliases - Esforço

**Pergunta 20:** Demora muito criar aliases?

**Resposta técnica:** < 30min para implementar todos

**Decisão:** Implementar aliases agora

**Aliases principais:**

- create/add
- update/edit
- delete/remove
- list/ls

**Implementação Typer:**

```python
@app.command(name="create")
@app.command(name="add")  # Alias
def create_habit(...):
    pass
```

**Esforço total:** ~1h (implementação + testes)

---

## 8. SKIP FUNCTIONALITY

### 8.1 Comando Skip

**Pergunta 7:** Skip implementado?

**Decisão:** Ainda não implementado, mas muito bem documentado

**Ação:** Verificar BDD e TDD antes de implementar código.

---

### 8.2 Skip Categoria Obrigatória

**Pergunta 25:** Categoria obrigatória ao pular?

**Decisão:** A) Categoria obrigatória sempre

**Implementação:**

```bash
habit skip 42 --category HEALTH

# Sistema rejeita se não tiver categoria:
[ERRO] Categoria obrigatória. Use --category
```

---

### 8.3 Skip Justification Workflow

**Perguntas 37/45:** Notificação ativa ou reativa?

**Decisão:** A) Reativo (prompt em qualquer comando)

**Comportamento:**

```bash
# Skip com categoria
habit skip 42 --category HEALTH
# [OK] Hábito pulado com justificativa

# Após 24h sem categoria (se fosse permitido pular sem)
$ habit list
[WARN] Academia foi pulada ontem sem justificativa.
       Adicionar motivo agora? [Y/n]:
```

**Nota:** Como categoria é obrigatória (8.2), o prompt de 24h só aparece se houver bugs ou casos edge.

---

### 8.4 BDD/TDD para Skip

**Pergunta 50:** Testes já implementados?

**Status:** Não respondido diretamente (metodologia: docs > BDD > TDD > code)

**Ação necessária:**

1. Verificar se existem:
   - `tests/unit/test_services/test_habit_skip.py`
   - `tests/integration/test_habit_skip_integration.py`
   - `tests/e2e/test_skip_workflow.py`
2. Se NÃO existem: criar testes ANTES do código
3. Se existem: validar cobertura das 4 BRs

**BRs documentadas:**

- BR-HABIT-SKIP-001: Categorização obrigatória
- BR-HABIT-SKIP-002: Prazo 24h (não aplicável se categoria obrigatória)
- BR-HABIT-SKIP-003: Quebra streak
- BR-HABIT-SKIP-004: Histórico rastreável

---

## 9. COMPLETION STATUS

### 9.1 OVERDONE vs EXCESSIVE

**Pergunta 47:** Sistema analisa impacto sempre?

**Decisão:** A) Sim, sempre (BR-HABIT-INSTANCE-006)

**Thresholds (BR-HABIT-INSTANCE-003):**

```python
if completion > 150%:  # EXCESSIVE (PROBLEMA GRAVE)
    substatus = DoneSubstatus.EXCESSIVE
elif completion > 110%:  # OVERDONE (ATENÇÃO)
    substatus = DoneSubstatus.OVERDONE
elif completion >= 90%:  # FULL (IDEAL)
    substatus = DoneSubstatus.FULL
else:  # PARTIAL (<90%)
    substatus = DoneSubstatus.PARTIAL
```

**Comportamento esperado:**

```bash
# Após timer stop com EXCESSIVE
timer stop

[WARN] Academia ultrapassou meta em 90min (150%)

Impacto na rotina:
  - Trabalho: PERDIDO (não iniciado)
  - Inglês: ATRASADO 1h

Sugestão: Ajustar meta de 60m para 90m? [Y/n]:
```

**Implementação:** Sistema SEMPRE calcula e exibe impacto ao ultrapassar meta.

---

## 10. TESTES E2E

### 10.1 Estado Atual

**Pergunta 49:** Testes E2E corrigidos?

**Status:** Não respondido (metodologia: rever todos os testes)

**Documento referenciado:** `e2e-tests-analysis-2025-11-13.md`

**Problemas conhecidos (13/11):**

- 2 testes E2E FALHANDO
- Fixture `isolated_db` não sendo usada
- Comandos CLI mudaram

**Ação necessária:**

1. Verificar se testes foram corrigidos desde 13/11
2. Se NÃO: corrigir antes de prosseguir com novas features
3. Atualizar fixtures e comandos CLI

---

## 11. STREAK

### 11.1 Escopo Alterado

**Decisão anterior:** Streak fora do MVP (v1.5.0+)

**Pergunta 11:** Implementar no MVP?

**Decisão:** B) Implementar no MVP v1.4.0 (MUDOU!)

---

### 11.2 Recomendação de Escopo

**Pergunta 56:** Completo, simplificado ou postergar?

**Recomendação:** B) Simplificado (2 BRs no MVP, 2 BRs em v1.5.0+)

**Justificativa da recomendação:**

**Funcionalidades MVP v1.4.0 planejadas:**

1. Habit CRUD completo
2. Timer (6 comandos)
3. Skip com categorização
4. Dashboard (habits + tasks)
5. Reports (3 tipos)
6. HabitInstance com substatus
7. **Streak simplificado** ← Sinergia perfeita

**Análise:**

- Skip quebra streak → integração natural
- Dashboard mostra streak → motivação visual
- Reports incluem streak stats → análise básica
- Fundação para features avançadas (freeze, histórico)

**Escopo recomendado MVP:**

- [OK] BR-STREAK-001: Cálculo diário (contador dias consecutivos)
- [OK] BR-STREAK-002: Quebra com skip (reset para 0)

**Postergar para v1.5.0+:**

- [ ] BR-STREAK-003: Congelamento (freeze durante viagens)
- [ ] BR-STREAK-004: Histórico avançado (maior streak, gráficos)

**Esforço estimado:**

- Simplificado (MVP): ~3-4h
- Completo (4 BRs): ~6-8h
- Diferença: 2-4h economizados para v1.5.0+

---

## 12. VERIFICAÇÕES REALIZADAS

### 12.1 Timer Commands - Verificação Completa

**Comando executado:**

```bash
cd /run/media/.../timeblock-organizer
ls cli/src/timeblock/commands/timer.py
grep -n "def.*timer" cli/src/timeblock/commands/timer.py
```

**Resultado:**

```
cli/src/timeblock/commands/timer.py
36:def _display_timer(timelog_id: int):
103:def start_timer(
187:def pause_timer():
204:def resume_timer():
224:def stop_timer():
254:def cancel_timer():
275:def timer_status():
```

**Status:** [OK] Todos os 6 comandos implementados

| Comando | Implementado | Linha |
| ------- | ------------ | ----- |
| start   | [OK]         | 103   |
| pause   | [OK]         | 187   |
| resume  | [OK]         | 204   |
| stop    | [OK]         | 224   |
| cancel  | [OK]         | 254   |
| status  | [OK]         | 275   |

**Observação:** `cancel_timer` equivale a `reset` (cancela sem salvar).

---

### 12.2 Comando Renew - Histórico Encontrado

**Busca realizada:** `conversation_search` nos últimos chats

**Resultados:**

- Chat 14/11/2025: Discussão sobre sintaxe limpa (sem `6months`)
- Chat 18/10/2025: Versão inicial com flag `--generate`

**Consenso estabelecido:**

```bash
habit renew HABIT_ID [OPTIONS]

# Períodos predefinidos
--for semester     # 6 meses
--for quarter      # 3 meses (DEFAULT)
--for month        # 1 mês

# OU customizado
--months N
--weeks N
--days N
```

**Status:** [OK] Documentado, precisa implementar

---

## 13. PRÓXIMOS PASSOS

### 13.1 Business Rules a Documentar

**Prioridade CRÍTICA (implementar no MVP v1.4.0):**

1. **BR-HABIT-RENEW-001:** Renovação automática de instâncias

   - Default: 3 meses (quarter)
   - Suporta períodos predefinidos e customizados
   - Sistema notifica 7 dias antes de expirar

2. **BR-HABIT-TEMPLATE-001:** Edição de template

   - Comando: `habit template edit`
   - Afeta apenas futuras instâncias
   - Instâncias já criadas mantêm valores originais

3. **BR-DASHBOARD-001:** Exibição de dashboard

   - Tabela Habits: ID, Nome, Horário, Status
   - Tabela Tasks: ID, Nome, Status, Data, Horário, Cor
   - Modo estático (default) + watch opcional

4. **BR-TIMER-MULTISESSION-001:** Múltiplas sessões por dia

   - Permite N TimeLogs para mesmo habit_instance_id
   - Completion calculado somando todas sessões
   - Status atualizado baseado na soma

5. **BR-REPORT-DAILY-001:** Relatório diário

   - Lista habits e tasks do dia
   - Mostra status, completion, streak

6. **BR-REPORT-WEEKLY-001:** Relatório semanal

   - Resumo 7 dias
   - Estatísticas: completion média, streaks, skips

7. **BR-REPORT-HABIT-001:** Análise de hábito

   - Histórico completo de um habit
   - Gráficos de evolução, padrões

8. **BR-STREAK-001:** Cálculo de streak

   - Incrementa +1 a cada dia DONE (FULL/OVERDONE/EXCESSIVE)
   - Reset para 0 em NOT_DONE ou skip

9. **BR-STREAK-002:** Quebra de streak com skip

   - Skip SEMPRE quebra streak (reset para 0)
   - Vale para SKIPPED_JUSTIFIED e UNJUSTIFIED

10. **BR-RRULE-001:** Suporte a RRULE completo
    - Parser RFC 5545
    - Validação de padrões complexos
    - Geração de instâncias baseada em RRULE

---

### 13.2 Refatorações Necessárias

#### **1. Modelo HabitInstance - Breaking Change**

**Adicionar campos:**

```python
class HabitInstance:
    # Novos campos
    skip_reason: SkipReason | None = None
    skip_note: str | None = None
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None
    streak_current: int = 0  # Se streak no MVP
```

**Migração SQL necessária:**

```sql
ALTER TABLE habit_instances ADD COLUMN skip_reason VARCHAR(50);
ALTER TABLE habit_instances ADD COLUMN skip_note TEXT;
ALTER TABLE habit_instances ADD COLUMN done_substatus VARCHAR(50);
ALTER TABLE habit_instances ADD COLUMN not_done_substatus VARCHAR(50);
ALTER TABLE habit_instances ADD COLUMN streak_current INTEGER DEFAULT 0;
```

#### **2. Status → Status+Substatus - Breaking Change**

**Substituir:**

```python
# Antes
status: HabitInstanceStatus  # PLANNED, IN_PROGRESS, COMPLETED, SKIPPED

# Depois
status: Status  # PENDING, DONE, NOT_DONE
done_substatus: DoneSubstatus | None  # FULL, OVERDONE, EXCESSIVE, PARTIAL
not_done_substatus: NotDoneSubstatus | None  # SKIPPED_JUSTIFIED, UNJUSTIFIED, IGNORED
```

**Migração de dados:**

```sql
-- Mapear status antigo para novo
UPDATE habit_instances SET
    status = CASE
        WHEN status = 'COMPLETED' THEN 'DONE'
        WHEN status = 'SKIPPED' THEN 'NOT_DONE'
        ELSE 'PENDING'
    END,
    not_done_substatus = CASE
        WHEN status = 'SKIPPED' THEN 'SKIPPED_UNJUSTIFIED'
        ELSE NULL
    END;
```

---

### 13.3 Testes a Criar/Revisar

**Seguir metodologia rigorosa:** DOCS/BR → BDD → TDD → CODE

**1. Verificar testes existentes:**

```bash
# Unit tests
find tests/unit -name "test_*.py" | wc -l

# Integration tests
find tests/integration -name "test_*.py" | wc -l

# E2E tests
find tests/e2e -name "test_*.py" | wc -l
```

**2. Criar testes faltantes para BRs novas:**

**Skip (se não existem):**

- `tests/unit/test_services/test_habit_skip_service.py`
- `tests/integration/test_habit_skip_integration.py`
- `tests/e2e/test_skip_workflow.py`

**Renew:**

- `tests/unit/test_services/test_habit_renew_service.py`
- `tests/integration/test_habit_renew_integration.py`

**Dashboard:**

- `tests/unit/test_commands/test_dashboard.py`
- `tests/e2e/test_dashboard_workflow.py`

**Reports (3 tipos):**

- `tests/unit/test_services/test_report_daily.py`
- `tests/unit/test_services/test_report_weekly.py`
- `tests/unit/test_services/test_report_habit.py`
- `tests/integration/test_reports_integration.py`

**Streak:**

- `tests/unit/test_services/test_streak_service.py`
- `tests/integration/test_streak_integration.py`

**Timer multisession:**

- `tests/unit/test_services/test_timer_multisession.py`
- `tests/integration/test_timer_multisession_integration.py`

---

### 13.4 Comandos CLI a Implementar/Refatorar

**Novos comandos:**

1. `habit renew` - Renovar instâncias
2. `habit template edit` - Editar template
3. `dashboard` - Exibir dashboard
4. `dashboard --watch` - Dashboard com auto-refresh
5. `report daily` - Relatório diário
6. `report weekly` - Relatório semanal
7. `report habit` - Análise de hábito

**Aliases a adicionar:**

- `habit create` / `habit add`
- `habit update` / `habit edit`
- `habit delete` / `habit remove`
- `habit list` / `habit ls`
- `task create` / `task add`
- `task update` / `task edit`
- `task delete` / `task remove`
- `task list` / `task ls`

**Remover (legacy):**

- Flag `--generate` do `habit create`
- Comando `schedule generate` (redundante com `renew`)

---

### 13.5 Documentação a Atualizar

**1. Business Rules (docs/04-specifications/business-rules/):**

- Criar 10 novos arquivos BR (listados em 13.1)
- Atualizar índice `COMPLETE-BUSINESS-RULES.md`

**2. CLI Reference (docs/08-user-guides/cli-reference.md):**

- Adicionar comandos novos (renew, dashboard, reports)
- Documentar aliases
- Remover comandos legacy

**3. ADRs (docs/03-decisions/):**

- ADR-021: Refatoração Status+Substatus
- ADR-022: RRULE Implementation
- ADR-023: Dashboard Design Decisions
- ADR-024: Streak Simplified Scope

**4. CHANGELOG.md:**

- Adicionar seção `[Não Lançado]` com todas mudanças
- Marcar breaking changes explicitamente

---

### 13.6 Plano de Implementação Sugerido

#### **Sprint 1: Fundação (1-2 dias)**

1. Refatorar modelo HabitInstance (campos novos)
2. Migração SQL + testes
3. Refatorar Status → Status+Substatus
4. Atualizar todos testes afetados

#### **Sprint 2: Skip + Streak (2-3 dias)**

1. Documentar BR-HABIT-SKIP-001 a 004
2. Criar testes skip (unit/integration/e2e)
3. Implementar skip service
4. Implementar skip CLI
5. Documentar BR-STREAK-001 e 002
6. Implementar streak service (simplificado)
7. Integrar streak com skip

#### **Sprint 3: Timer Multisession (1 dia)**

1. Documentar BR-TIMER-MULTISESSION-001
2. Criar testes multisession
3. Refatorar timer service
4. Atualizar completion calculation

#### **Sprint 4: Dashboard (2 dias)**

1. Documentar BR-DASHBOARD-001
2. Criar testes dashboard
3. Implementar dashboard estático
4. Implementar dashboard watch mode
5. Integrar com Rich library

#### **Sprint 5: Reports (3 dias)**

1. Documentar BR-REPORT-DAILY/WEEKLY/HABIT
2. Criar testes reports (unit/integration)
3. Implementar report daily
4. Implementar report weekly
5. Implementar report habit
6. Integrar com Rich (tabelas, gráficos ASCII)

#### **Sprint 6: Renew + RRULE (2-3 dias)**

1. Documentar BR-HABIT-RENEW-001
2. Documentar BR-RRULE-001
3. Implementar parser RRULE (python-dateutil)
4. Criar testes renew
5. Implementar renew service
6. Implementar renew CLI

#### **Sprint 7: Polimento (1-2 dias)**

1. Criar aliases (create/add, etc)
2. Atualizar CLI reference
3. Criar ADRs novos
4. Atualizar CHANGELOG
5. Revisar cobertura de testes (meta: 99%+)
6. Corrigir E2E tests quebrados

**Total estimado:** 12-15 dias de trabalho

---

## 14. RESUMO EXECUTIVO

### 14.1 Decisões Críticas Tomadas

1. **Refatoração Status+Substatus:** Breaking change aprovado
2. **Streak no MVP:** Versão simplificada (2 BRs)
3. **Dashboard:** Estático + watch mode
4. **Reports:** Todos os 3 no MVP
5. **Skip:** Categoria obrigatória sempre
6. **RRULE:** Implementação completa (RFC 5545)
7. **Aliases:** Implementar para melhor UX
8. **Comando schedule:** Eliminar (redundante)

---

### 14.2 Funcionalidades MVP v1.4.0 Confirmadas

**Core:**

- [OK] Habit CRUD (create/update/delete/list)
- [OK] Task CRUD (create/update/delete/list)
- [OK] Timer (6 comandos: start/pause/resume/stop/cancel/status)
- [OK] Timer multisession (múltiplas sessões por dia)

**Skip & Streak:**

- [NOVO] Skip com categorização obrigatória (8 categorias)
- [NOVO] Streak simplificado (cálculo + quebra)

**Visualização:**

- [NOVO] Dashboard (habits + tasks, estático + watch)
- [NOVO] Reports (daily/weekly/habit)

**Gestão de Instâncias:**

- [NOVO] Renew (renovar instâncias com períodos predefinidos)
- [NOVO] Template edit (editar hábito sem afetar instâncias criadas)
- [NOVO] RRULE completo (padrões complexos de recorrência)

**UX:**

- [NOVO] Aliases (create/add, edit/update, delete/remove, list/ls)
- [NOVO] Status+Substatus (PENDING/DONE/NOT_DONE + detalhes)

---

### 14.3 Métricas de Qualidade Mantidas

- **Cobertura de testes:** 99%+ (meta mantida)
- **Metodologia:** DOCS/BR → BDD → TDD → CODE (rigorosa)
- **Commits:** Atômicos, mensagens em PT-BR
- **Gitflow:** feature branches → develop → main
- **Documentação:** Arc42, ADRs, BRs formalizadas

---

### 14.4 Próxima Ação Imediata

**Antes de qualquer implementação:**

1. [ ] Ler COMPLETO: `docs/01-architecture/`
2. [ ] Ler COMPLETO: `docs/04-specifications/business-rules/`
3. [ ] Ler COMPLETO: `docs/08-user-guides/cli-reference.md`
4. [ ] Analisar: `git log --oneline -50`
5. [ ] Verificar branch: `git branch`
6. [ ] Verificar versão: `git tag -l` + `CHANGELOG.md`

**Depois da leitura:**

1. [ ] Criar 10 Business Rules novas (seção 13.1)
2. [ ] Atualizar índice BRs
3. [ ] Criar BDD scenarios (Gherkin)
4. [ ] Criar testes (TDD - RED)
5. [ ] Implementar (GREEN)
6. [ ] Refatorar (REFACTOR)
7. [ ] Validar cobertura 99%+
8. [ ] Commit atômico por BR

---

**Versão:** 1.0

**Próxima revisão:** Após implementação Sprint 1
