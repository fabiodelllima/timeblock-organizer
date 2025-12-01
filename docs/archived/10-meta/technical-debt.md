# Débito Técnico - Análise Completa

- **Data:** 31 de Outubro de 2025
- **Status:** Rastreamento ativo
- Este documento consolida todo débito técnico identificado, priorizado por severidade e impacto em releases.

## Bloqueadores Críticos (Previnem Release)

**Severidade:** CRÍTICA
**Impacto:** Bloqueia Event Reordering Fase 2
**Esforço:** 2-3 horas
**Prioridade:** IMEDIATA

**Problema:**

```python
# event_reordering_service.py linha ~294
ProposedChange(
    original_start=...,  # [X] Campo não existe
    original_end=...,    # [X] Campo não existe
    # Faltando event_title  # [X] Campo obrigatório
)
```

**Solução:**

```python
ProposedChange(
    event_id=event_id,
    event_type=event_type,
    event_title=event_title,      # [VÁLIDO] Adicionar
    current_start=current_start,   # [VÁLIDO] Correto
    current_end=current_end,       # [VÁLIDO] Correto
    proposed_start=new_start,
    proposed_end=new_end,
    priority=priority
)
```

**Testes Falhando:**

- `test_critical_events_dont_move` (linha 77)
- `test_low_priority_stacks_sequentially` (linha 142)

**Ação:** Corrigir HOJE antes de qualquer outro trabalho.

---

### DB2: Testes E2E Faltando

**Severidade:** ALTA
**Impacto:** Release v1.0/v2.0 sem garantias end-to-end
**Esforço:** 12 horas
**Prioridade:** ALTA

**Cobertura Faltante:**

1. **Workflow completo de rotina** (2h)

   - Criar rotina -> adicionar hábitos -> gerar instâncias -> rastrear -> completar

2. **Conflito e reordenação** (3h)

   - Task sobrepõe habit -> detectar conflito -> propor -> aceitar -> aplicar

3. **Timer cruza meia-noite** (2h)

   - Iniciar timer 23h -> cruza meia-noite -> parar 1h -> validar duração

4. **Workflow múltiplos dias** (3h)

   - Criar hábitos para semana inteira -> pular alguns -> checar conformidade

5. **Filtragem por tag** (2h)
   - Criar eventos tagueados -> filtrar por tag -> gerar relatório de tag

**Recomendação:** Implementar cenários 1-2 como mínimo para v1.0 (5h), adiar 3-5 para v1.1.

---

### DB3: Cobertura de Testes 75% -> 90%

- **Severidade:** MÉDIA
- **Impacto:** Qualidade geral
- **Esforço:** 10 horas
- **Prioridade:** MÉDIA

**Gaps Específicos:**

1. **Propriedades de Model** (5h)

   ```python
      # Testes faltando:
      - HabitInstance.is_overdue (propriedade calculada)
      - Task.is_completed (propriedade)
      - Habit.next_occurrence (método helper)
      - Routine.active_habits (propriedade)
   ```

2. **Parsers CLI** (3h)

   ```python
      # Não testados:
      - date_parser.py (today, this-week, next-month)
      - time_parser.py (formatos HHh, HHhMM)
      - rrule_parser.py (strings de recorrência)
   ```

3. **Gaps de Integração** (2h)

   ```python
      # Cenários não cobertos:
      - TaskService + TimerService juntos
      - HabitInstanceService + EventReorderingService
      - Múltiplos services em sequência
   ```

**Recomendação:** Abordar propriedades de model primeiro (afeta regras de negócio), adiar parsers para v1.1.

---

## Débito Arquitetural (Não-Bloqueante)

### DA1: Tuple Returns Deprecados

- **Severidade:** MÉDIA
- **Impacto:** Manutenibilidade futura
- **Esforço:** 4 horas
- **Prioridade:** MÉDIA (Fase 2)

**Problema:**

```python
# Anti-pattern atual:
def create_task(...) -> tuple[Task | None, str | None]:
    if validation_error:
        return None, "Mensagem de erro"
    return task, None
```

**Problemas:**

- Composição de função difícil
- Tratamento de erro inconsistente
- Type hints confusas

**Solução (ADR-008):**

```python
# Abordagem 1: Retorno direto + raise exception
def create_task(...) -> Task:
    if validation_error:
        raise ValueError("Mensagem de erro")
    return task

# Abordagem 2: Tipo Result (se complexo)
@dataclass
class Result[T]:
    value: T | None
    error: str | None

def create_task(...) -> Result[Task]:
    ...
```

**Arquivos Afetados:**

- `habit_service.py` (8 métodos)
- `task_service.py` (5 métodos)
- `timer_service.py` (4 métodos)
- `habit_instance_service.py` (6 métodos)

**Timing:** Entre v1.1 e v1.2 (não bloqueante).

---

### DA2: Type Hints Estritos (mypy)

- **Severidade:** BAIXA
- **Impacto:** Experiência do desenvolvedor
- **Esforço:** 2 horas
- **Prioridade:** BAIXA

**Gaps:**

- Algumas funções sem type hints completas
- mypy não configurado estritamente
- `Any` usado em alguns lugares

**Ação:** Incremental, não-bloqueante.

---

## Features Faltando (Roadmap)

### F1: ReportService

- **Escopo:** v1.0 (definitivo)
- **Esforço:** 8 horas
- **Dependências:** Event Reordering completo

**Funcionalidade Requerida:**

```python
class ReportService:
    @staticmethod
    def completion_rate(start_date, end_date) -> float:
        """% de hábitos completados vs planejados"""

    @staticmethod
    def time_variance_analysis(habit_id) -> dict:
        """Diferença entre horários agendados vs reais"""

    @staticmethod
    def daily_summary(date) -> DailySummary:
        """Resumo do dia: planejado, completado, pulado"""

    @staticmethod
    def weekly_summary(start_date) -> WeeklySummary:
        """Resumo semanal com tendências"""

    @staticmethod
    def habit_streak(habit_id) -> int:
        """Dias consecutivos sem pular"""
```

**Comandos CLI:**

```shell
timeblock report daily           # Resumo de hoje
timeblock report week            # Resumo da semana
timeblock report habit <id>      # Análise de hábito único
timeblock report completion      # Taxa de conclusão geral
```

---

### F2: Execução RoutineService

- **Escopo:** TBD (v1.0 ou v2.0?)
- **Esforço:** 12 horas
- **Complexidade:** Média-Alta

**Proposta:**

```python
class RoutineService:
    @staticmethod
    def execute_routine(routine_id: int, date: date):
        """Executar rotina sequencialmente com prompts"""
        # Para cada hábito na rotina:
        # 1. Mostrar próximo hábito
        # 2. Auto-iniciar timer?
        # 3. Aguardar conclusão
        # 4. Marcar como completo
        # 5. Próximo hábito
```

**Discussão Necessária:**

- Útil ou overengineering?
- Usuário prefere controle manual?
- Adiar automação para v2.0?

**Recomendação:** Mover para v1.1 (pós-release), coletar feedback real de usuário primeiro.

---

### F3: Gerenciamento de Config

- **Escopo:** v1.0
- **Esforço:** 4 horas
- **Complexidade:** Baixa

**Arquivo:** `.timeblockrc` ou `config.json`

```json
{
  "default_routine": 1,
  "work_hours_start": "09:00",
  "work_hours_end": "17:00",
  "enable_notifications": false,
  "timer_sound": "bell",
  "date_format": "YYYY-MM-DD",
  "time_format": "HH:MM"
}
```

**Comandos CLI:**

```shell
timeblock config set default_routine 1
timeblock config get default_routine
timeblock config list
timeblock config reset
```

---

### F4: Export/Import

- **Escopo:** v1.1 (pós-release)
- **Esforço:** 6 horas

**Formatos:**

- Markdown (legível por humanos)
- JSON (legível por máquinas)
- iCalendar (cross-platform)

```shell
timeblock export --format md --output agenda.md
timeblock import agenda.json
```

---

### F5: TUI (Textual)

- **Escopo:** v2.0 (futuro)
- **Esforço:** 20 horas
- **Framework:** Textual (Python TUI)

Adiar para v2.0 após CLI provada e estável.

---

### F6: Sync Google Calendar

- **Escopo:** v2.0 (futuro)
- **Esforço:** 30 horas
- **Complexidade:** Alta

**Features:**

- Sync bidirecional
- Resolução de conflitos
- Integração OAuth
- Sync seletiva (tags/categorias)

---

## Débito de Qualidade e Documentação

### Q1: Testes BDD/DDD

- **Escopo:** Fase 4 (incremental, não-bloqueante)
- **Esforço:** 80 horas (3 semanas)
- **Framework:** pytest-bdd

**Objetivo:** Testes como documentação viva.

**Exemplo:**

```gherkin
Feature: Reordenação de Hábitos
  Como usuário
  Eu quero que o sistema reorganize meus hábitos automaticamente
  Para adaptar minha agenda quando conflitos surgirem

  Scenario: Task sobrepõe hábito de baixa prioridade
    Given Eu tenho um hábito "Exercício" de 07:00 a 08:00
    And Eu tenho uma tarefa "Reunião Importante" de 07:30 a 08:30
    When O sistema detecta o conflito
    Then Ele deve propor mover "Exercício" antes ou depois
    And Prioridade da tarefa deve ser NORMAL
    And Prioridade do hábito deve ser BAIXA
```

**Recomendação:** Começar com docstrings ricas (Fase 3), avaliar benefício, decidir sobre pytest-bdd depois.

---

### Q2: Living Documentation

- **Escopo:** Fase 4
- **Ferramentas:** MkDocs (site), BUSINESS_RULES.md auto-gerado

**Estrutura:**

```terminal
docs/
+-- index.md
+-- primeiros-passos/
+-- guia-usuario/
+-- tecnico/
|   +-- arquitetura.md
|   +-- regras-negocio.md  # Auto-gerado
|   +-- referencia-api.md  # Auto-gerado
+-- desenvolvimento/
    +-- contribuindo.md
    +-- testes.md
    +-- roadmap.md
```

---

## Resumo de Priorização

### URGENTE (Hoje)

- [ ] 

### ALTA (Esta Semana)

- [ ] Completar Event Reordering Fase 2 (6-8h)
- [ ] F1: Implementar ReportService básico (8h)

### MÉDIA (2 Semanas)

- [ ] DB2: Testes E2E mínimos (5h para cenários 1-2)
- [ ] Event Reordering Fase 3 (6h)
- [ ] Release v1.1.0

### BAIXA (1 Mês)

- [ ] DB3: Cobertura -> 90% (propriedades de model primeiro)
- [ ] DA1: Refatorar tuple returns
- [ ] F3: Gerenciamento de config
- [ ] Release v1.2.0

### FUTURO (v2.0+)

- [ ] F5: TUI com Textual
- [ ] F6: Sync Google Calendar
- [ ] Q1: Testes BDD (se valor comprovado)
- [ ] Q2: Living documentation

---

- **Rastreamento:** Atualizar este documento após cada sprint.
- **Cadência de Revisão:** Semanal durante desenvolvimento ativo.
- **Responsável:** Tech lead do projeto.
