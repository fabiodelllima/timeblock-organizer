# Integração da Documentação Completa

- **Versão:** 2.1.0
- **Data de Criação:** 30 de Outubro de 2025
- **Última Atualização:** 30 de Outubro de 2025
- **Autores:** Equipe TimeBlock + Análise Automatizada
- **Status:** Documento Mestre Ativo

---

## Propósito do Documento

Este documento integra três fontes críticas de informação sobre o TimeBlock Organizer:

1. **Documentação Anteriores** (25-28 Outubro 2025): Progresso do projeto, filosofia de design, catálogo de regras de negócio
2. **Análise Técnica Atual** (30 Outubro 2025): Divergências código-documentação, problemas específicos, verificações automatizadas
3. **Planejamento Consolidado**: Roadmap integrado de 32 horas para completar documentação

Este é o **documento mestre único** que deve ser consultado antes de iniciar qualquer sessão de desenvolvimento ou documentação do projeto.

---

## Índice

1. [Estado Atual do Projeto](#1-estado-atual-do-projeto)
2. [Filosofia e Decisões Fundamentais](#2-filosofia-e-decisões-fundamentais)
3. [Catálogo Completo de Regras de Negócio](#3-catálogo-completo-de-regras-de-negócio)
4. [Problemas Técnicos Identificados](#4-problemas-técnicos-identificados)
5. [Infraestrutura de Documentação](#5-infraestrutura-de-documentação)
6. [Plano de Ação Integrado](#6-plano-de-ação-integrado)
7. [Métricas de Qualidade](#7-métricas-de-qualidade)
8. [Guia de Uso deste Documento](#8-guia-de-uso-deste-documento)

---

## 1. Estado Atual do Projeto

### 1.1 Visão Geral

- **Versão Atual:** v1.0.0 (estável)
- **Versão em Desenvolvimento:** v2.0.0 (45% concluído)
- **Branch Principal:** `feat/event-reordering-core`
- **Último Commit Verificado:** `6e5cde4`
- **Último Sprint Completado:** Sprint 2.1 (TaskService Integration)

### 1.2 Progresso por Fase

#### Fase 0: Fundação (100% Completa)

- **Período:** Até 25 de Outubro de 2025
- **Status:** CONCLUÍDA

**Entregas:**

- CLI básica funcional com Typer
- SQLModel ORM configurado com SQLite
- Models principais: Event, Routine, Habit, HabitInstance, Task, TimeLog, Tag
- Commands básicos: add, list, schedule, timer, init
- Testes unitários: 181 testes com 99% de cobertura
- Services: HabitService, TaskService, RoutineService, TagService, TimerService

**Artefatos:**

- Código fonte estável em `cli/src/timeblock/`
- Suite de testes em `cli/tests/`
- Banco de dados SQLite funcional

#### Fase 1: Event Reordering Core (75% Completa, BLOQUEADA)

- **Período:** 25-28 de Outubro de 2025
- **Status:** COMPLETA - Sprint 1.4 resolvido
- **Branch:** `feat/event-reordering-core`

**Entregas Completadas:**

- EventReorderingService básico implementado
- Detecção de conflitos funcionando
- Models: ReorderingProposal, ProposedChange, ConflictInfo

**Bloqueador Crítico:**
[RESOLVIDO] Sprint 1.4 completo
[RESOLVIDO] Sprint 1.4 completo

```python
# BUG ATUAL (linha ~294 de event_reordering_service.py):
ProposedChange(
    event_id=event.id,
    event_type=event_type,
    original_start=event.scheduled_start,  # [ERRO] Campo não existe
    original_end=event.scheduled_end,      # [ERRO] Campo não existe
    new_start=new_start,
    new_end=new_end
)

# CORREÇÃO NECESSÁRIA:
ProposedChange(
    event_id=event.id,
    event_type=event_type,
    event_title=event.title,               # [ADICIONAR]
    current_start=event.scheduled_start,   # [CORRIGIR]
    current_end=event.scheduled_end,       # [CORRIGIR]
    proposed_start=new_start,              # [CORRIGIR]
    proposed_end=new_end                   # [CORRIGIR]
)
```

**Próximos Passos:**

1. Corrigir bug do Sprint 1.4 (2-3h)
2. Completar Sprint 2.2: HabitInstanceService Integration (4h)
3. Completar Sprint 2.3: TimerService Integration (4h)
4. Completar Sprint 2.4: CLI Preview de Propostas (2h)

**Tempo Estimado para Conclusão:** 12-14 horas

#### Fase 2: Event Reordering Integration (0%, Aguardando)

- **Status:** AGUARDANDO conclusão da Fase 1
- **Dependência:** Bug Sprint 1.4 corrigido

**Sprints Planejados:**

- Sprint 2.1: TaskService Integration [CONCLUÍDO]
- Sprint 2.2: HabitInstanceService Integration [PENDENTE]
- Sprint 2.3: TimerService Integration [PENDENTE]
- Sprint 2.4: CLI Preview [PENDENTE]
- Sprint 2.5: Testes de Integração [PENDENTE]
- Sprint 2.6: Documentação [PENDENTE]

**Tempo Estimado:** 10-14 horas após conclusão da Fase 1

#### Fase 3: HabitAtom Refactor (0%, Planejada)

- **Status:** PLANEJADA
- **Dependência:** Fases 1 e 2 completas
- **Decisão:** Renomear HabitInstance → HabitAtom

**Rationale:**
Baseado no livro "Atomic Habits" de James Clear:

- HabitAtom representa unidade atômica de execução de hábito
- Pequeno o suficiente para ser executável
- Grande o suficiente para fazer diferença
- Composto ao longo do tempo resulta em transformação

**Entregas Planejadas:**

- Migration: `ALTER TABLE habit_instance RENAME TO habit_atom`
- Renomear classe: `HabitInstance` → `HabitAtom`
- Atualizar HabitInstanceService → HabitAtomService
- Atualizar todos os comandos CLI
- Atualizar 100% dos testes
- Documentação completa da filosofia Atomic Habits

**Tempo Estimado:** 44 horas

#### Fase 4: Living Documentation (0%, Futura)

- **Status:** FUTURA
- **Conceito:** Testes como documentação viva

**Objetivos:**

- Testes expressam regras de negócio em linguagem natural
- Docstrings referenciam regras específicas (RN-XXX)
- Extração automática de regras dos testes
- Geração de documentação navegável
- Specification by Example com Gherkin

**Tempo Estimado:** 80 horas (incremental)

### 1.3 Cobertura de Testes

```terminal
Módulo                  | Cobertura | Testes
------------------------|-----------|--------
models/                 | 100%      | 45
services/               | 98%       | 78
commands/               | 95%       | 33
utils/                  | 99%       | 25
------------------------|-----------|--------
TOTAL                   | 99%       | 181
```

**Gaps de Cobertura Conhecidos:**

- `HabitInstance.is_overdue` property não testada
- Cascade delete em relationships não testado explicitamente
- Edge cases de meia-noite não testados

### 1.4 Releases Planejadas

| Versão | Data Estimada | Principais Features         | Status       |
| ------ | ------------- | --------------------------- | ------------ |
| v1.0.0 | Outubro/2025  | CLI básica, eventos simples | CONCLUÍDO    |
| v1.1.0 | Novembro/2025 | Event Reordering completo   | EM ANDAMENTO |
| v1.2.0 | Novembro/2025 | HabitAtom refactor          | PLANEJADO    |
| v1.3.0 | Dezembro/2025 | Living Documentation        | PLANEJADO    |
| v2.0.0 | Janeiro/2026  | TUI rica (Textual)          | PLANEJADO    |

---

## 2. Filosofia e Decisões Fundamentais

### 2.1 Filosofia de Tratamento de Conflitos

**DECISÃO ARQUITETURAL CRÍTICA:**

O TimeBlock Organizer **não bloqueia** eventos sobrepostos intencionalmente. Esta é uma decisão de design fundamental que permeia todo o sistema.

#### Três Princípios Fundamentais

##### **Princípio 1: Vida Real Tem Conflitos**

- Reuniões de emergência surgem sem aviso
- Compromissos mudam de última hora
- Prioridades se ajustam dinamicamente
- Sistema deve refletir realidade, não idealização

##### **Princípio 2: Autonomia do Usuário**

- Usuário decide suas prioridades
- Usuário conhece seu contexto melhor que o sistema
- Usuário escolhe qual evento executar quando há sobreposição
- Sistema oferece sugestões, não impõe decisões

##### **Princípio 3: Flexibilidade > Rigidez**

- Sistema se adapta à realidade do usuário
- Não força estruturas artificiais
- Permite decisões contextuais
- Propõe reorganização mas não exige aceitação

#### Implementação Técnica

##### **Pattern de Retorno: Tupla (Entity, Proposal)**

Todos os services que podem gerar conflitos retornam tupla:

```python
def create_task(...) -> tuple[Task, ReorderingProposal | None]:
    """Cria task e detecta conflitos, mas não bloqueia criação."""
    task = create_in_db(...)
    conflicts = detect_conflicts(task)

    if conflicts:
        proposal = generate_reordering_proposal(conflicts)
        return task, proposal

    return task, None
```

**Decisão do Usuário:**

```python
# Na CLI:
task, proposal = TaskService.create_task(...)

# Task FOI CRIADA independente de conflitos
display_success(task)

# Se há proposta, mostrar OPCIONALMENTE
if proposal and proposal.has_conflicts:
    display_proposal(proposal)

    if user_accepts():
        apply_reordering(proposal)
    # Senão, mantém como está (conflito persiste)
```

#### Cenário Exemplo

```python
# Segunda-feira específica:
Habit: "Exercício" 7h-8h (rotina diária)
Task: "Reunião urgente com cliente" 7h30-8h30 (criada agora)

# Opção 1: Priorizar reunião
timeblock habit skip <id> --reason "Reunião urgente"

# Opção 2: Ajustar horário do exercício
timeblock habit adjust <id> -s 6h -e 7h
# Sistema marca user_override=True

# Opção 3: Fazer ambos parcialmente
timeblock timer start --habit <id>
timeblock timer stop  # após 15min, então vai para reunião
```

#### Benefícios desta Abordagem

**Para o Usuário:**

- Controle total sobre agenda
- Sem frustrações com bloqueios
- Adaptação a mudanças rápidas
- Flexibilidade para situações inesperadas

**Para o Sistema:**

- Menos regras complexas para gerenciar
- Código mais simples e manutenível
- Menos casos edge para testar
- Menos chance de estados inconsistentes

**Para o Futuro:**

- Fácil adicionar sugestões baseadas em IA
- Possível implementar múltiplos modos (strict, flexible)
- Espaço para personalização avançada

**Referências:**

- ADR-011: Filosofia de Conflitos (A CRIAR)
- RN-ER01: Definição de Conflito
- RN-ER03: Propostas Não-Bloqueantes

### 2.2 Atomic Habits: Fundamento Conceitual

**Inspiração:** Livro "Atomic Habits" de James Clear

**Conceito Central:**
HabitInstance representa a menor unidade executável de um hábito - um "átomo" de hábito.

**Características de um Átomo de Hábito:**

- Pequeno o suficiente para ser executável diariamente
- Grande o suficiente para fazer diferença
- Composto ao longo do tempo: 1% melhor cada dia
- Transformação emerge da repetição

**Migração Planejada:**
HabitInstance → HabitAtom (Fase 3) reflete esse conceito fundamental.

### 2.3 Decisões Arquiteturais Documentadas (ADRs)

#### ADRs Existentes

##### **ADR-001: SQLModel ORM**

- Escolha de SQLModel sobre SQLAlchemy puro
- Integração com Pydantic para validação
- Type hints nativos

##### **ADR-002: Typer CLI**

- Framework CLI com suporte a subcomandos
- Type hints para validação automática
- Help text automático

##### **ADR-003: Event Reordering Strategy**

- Algoritmo Simple Cascade escolhido
- Propostas opcionais, não obrigatórias

##### **ADR-004: Habit vs Instance Separation**

- Habit = template/blueprint
- HabitInstance = ocorrência específica
- Separação permite tracking granular

##### **ADR-005: Resource-First CLI Design**

- Verbos após substantivos: `timeblock habit create`
- Consistência com REST APIs
- Mais intuitivo que `timeblock create habit`

##### **ADR-006: Textual TUI (Futuro)**

- TUI rica planejada para v2.0
- Textual framework escolhido
- CLI permanece para automação

##### **ADR-007: Service Layer Pattern**

- Business logic em services
- Commands são thin wrappers
- Facilita testes unitários

##### **ADR-008: Tuple Returns (Deprecated)**

- Services retornam tupla (entity, proposal)
- Pattern a ser substituído por estruturas explícitas
- Mantido temporariamente para v1.x

#### ADRs Pendentes (A Criar)

##### **ADR-009: Consolidação de Flags Override**

- Decisão: manter apenas `user_override` ou ambos os flags
- Problema: `manually_adjusted` e `user_override` redundantes
- **CRÍTICO** - Bloqueia refatorações

##### **ADR-010: Modelo de Recorrência**

- Decisão: manter dias individuais ou implementar WEEKLY_ON
- Implementação atual: MONDAY, TUESDAY, etc
- Documentação: WEEKLY_ON com recurrence_days
- **ALTO** - Inconsistência doc-código

##### **ADR-011: Filosofia de Conflitos**

- Documentar decisão de não-bloqueio
- Rationale dos três princípios
- Impacto em todo o sistema
- **CRÍTICO** - Fundamento do design

---

## 3. Catálogo Completo de Regras de Negócio

### 3.1 Organização das Regras

Total de **51 regras** catalogadas, organizadas em 13 domínios:

1. Validações de Tempo (RN001-RN006)
2. Modelo Event (RN007-RN010)
3. Modelo Routine (RN011-RN013)
4. Modelo Habit (RN014-RN018)
5. Modelo HabitInstance (RN019-RN024)
6. Modelo Task (RN025-RN027)
7. Modelo TimeLog (RN028-RN030)
8. Detecção de Conflitos (RN031-RN033)
9. Priorização (RN034-RN036)
10. Geração Automática (RN037-RN040)
11. CLI (RN041-RN046)
12. Tags (RN047-RN048)
13. Funcionalidades Futuras (RN049-RN051)

### 3.2 Regras Críticas para Desenvolvimento

#### RN-R01: Estrutura de Rotina

**Regra:** Uma Rotina é um agrupamento lógico de Hábitos relacionados que compartilham contexto temporal ou temático.

**Invariantes:**

- Toda Rotina deve ter um nome único e não-vazio
- Rotina pode conter zero ou mais Hábitos
- Rotina tem flag `is_active` que determina se seus Hábitos geram instâncias

**Implementação:** `cli/src/timeblock/models/routine.py`

**Testes:** `cli/tests/unit/test_models.py::test_routine_creation`

#### RN-H01: Estrutura de Hábito

**Regra:** Um Hábito é um template de evento recorrente vinculado a uma Rotina.

**Campos Obrigatórios:**

- `routine_id`: FK para Routine
- `title`: Nome do hábito (não-vazio)
- `scheduled_start`: Horário ideal de início (time)
- `scheduled_end`: Horário ideal de fim (time)
- `recurrence`: Padrão de recorrência (Enum)

**PROBLEMA IDENTIFICADO:**
Campo `scheduled_duration_minutes` mencionado em documentação mas NÃO existe no modelo implementado.

**Resolução Pendente:** ADR-012 (A CRIAR)

**Implementação:** `cli/src/timeblock/models/habit.py`

#### RN-HI02: Estados de Instância

**Regra:** Uma HabitInstance transita por estados bem definidos durante seu ciclo de vida.

**Estados Implementados:**

- `PLANNED`: Estado inicial após geração
- `IN_PROGRESS`: Atividade em execução
- `PAUSED`: Atividade pausada (pode ser resumida)
- `COMPLETED`: Estado final, irreversível
- `SKIPPED`: Usuário decidiu não fazer

**PROBLEMA IDENTIFICADO:**

- Estado `PAUSED` existe no código mas NÃO documentado
- Estado `CANCELLED` documentado mas NÃO existe no código

**Correção Necessária:**

```python
class HabitInstanceStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"           # [DOCUMENTAR]
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"     # [ADICIONAR]
```

**Implementação:** `cli/src/timeblock/models/habit_instance.py`

**Referência:** Diagrama de estados em `docs/02-diagrams/states/event-states.md` (A CRIAR)

#### RN-HI04: User Override Flag

**Regra:** Flag `user_override` é setada para True sempre que usuário modifica horários manualmente.

**PROBLEMA IDENTIFICADO:**
Existem DOIS flags no código:

- `manually_adjusted: bool`
- `user_override: bool`

Documentação menciona apenas `user_override`.

**Decisão Pendente:** ADR-009

- Opção A: Consolidar em `user_override` apenas
- Opção B: Manter ambos com semântica clara

**Uso Atual:**

```python
# Código usa ambos sem distinção clara:
instance.manually_adjusted = True  # Quando?
instance.user_override = True      # Quando?
```

**Implementação:** `cli/src/timeblock/models/habit_instance.py`

#### RN-ER01: Definição de Conflito

**Regra:** Conflito ocorre quando dois eventos têm sobreposição temporal no mesmo dia.

**Detecção Formal:**

```terminal
Sejam Event A e Event B no mesmo dia:
- A: [T1, T2]
- B: [T3, T4]

Conflito existe se: (T1 < T4) AND (T3 < T2)
```

**Tolerância:** 1 minuto (sobreposição < 1min não é conflito)

**IMPORTANTE:** Conflito detectado NÃO bloqueia criação (ver Filosofia de Conflitos)

**Implementação:** `cli/src/timeblock/services/event_reordering_service.py`

#### RN-ER02: Algoritmo de Reordenação (Simple Cascade)

**Regra:** Quando evento atrasa ΔT minutos, todos eventos subsequentes do mesmo dia são shiftados em ΔT minutos.

**Algoritmo:**

```terminal
1. Calcular ΔT = (novo_horário - horário_planejado)
2. Ordenar todos eventos do dia por start_time
3. Encontrar posição de E na lista
4. Para cada evento subsequente S:
   - novo_start(S) = atual_start(S) + ΔT
   - novo_end(S) = atual_end(S) + ΔT
   - Criar ProposedChange para S
5. Retornar ReorderingProposal
```

**Preservação:** Intervalos entre eventos são mantidos

[RESOLVIDO] Sprint 1.4 completo
[RESOLVIDO] Sprint 1.4 completo
**Implementação:** `cli/src/timeblock/services/event_reordering_service.py::propose_reordering()`

#### RN-ER03: Propostas, Não Aplicação Automática

**Regra:** Event Reordering **propõe** mudanças mas **não as aplica automaticamente**.

**Rationale:** Respeitar autonomia do usuário. Sistema oferece sugestão inteligente mas controle final é humano.

**Fluxo:**

1. Conflito detectado
2. Sistema gera ReorderingProposal
3. CLI exibe proposta formatada
4. Usuário aceita ou rejeita
5. Se aceito, mudanças aplicadas transacionalmente

**Exceção:** Se proposta causaria eventos após 23:00, adiciona aviso.

**Implementação:** Services retornam tupla `(entity, proposal | None)`

### 3.3 Regras por Categoria

Para listagem completa das 51 regras, consultar:

- `docs/04-specifications/business-rules/CATALOG-COMPLETE.md` (A CRIAR)
- Documentos de conversas anteriores: `REGRAS-DE-NEGOCIO-COMPLETAS.md`

---

## 4. Problemas Técnicos Identificados

### 4.1 Problemas Críticos (Bloqueadores)

#### P001: Bug Sprint 1.4 - ProposedChange com Campos Incorretos

- **Severidade:** CRÍTICA
- **Status:** RESOLVIDO
- **Descoberto:** 25 de Outubro de 2025

**Descrição:**
Método `propose_reordering()` cria `ProposedChange` com campos que não existem no modelo.

**Localização:** `cli/src/timeblock/services/event_reordering_service.py` linha ~294

**Código Atual (Incorreto):**

```python
ProposedChange(
    event_id=event.id,
    event_type=event_type,
    original_start=event.scheduled_start,  # [ERRO] Campo não existe
    original_end=event.scheduled_end,      # [ERRO] Campo não existe
    new_start=new_start,
    new_end=new_end
)
```

**Correção Necessária:**

```python
ProposedChange(
    event_id=event.id,
    event_type=event_type,
    event_title=event.title,               # [ADICIONAR]
    current_start=event.scheduled_start,   # [CORRIGIR]
    current_end=event.scheduled_end,       # [CORRIGIR]
    proposed_start=new_start,              # [CORRIGIR]
    proposed_end=new_end                   # [CORRIGIR]
)
```

**Impacto:** Impede conclusão da Fase 1 e início da Fase 2

**Tempo de Correção:** 2-3 horas (incluindo testes)

**Próximos Passos:**

1. Atualizar modelo `ProposedChange` em `event_reordering_models.py`
2. Corrigir `propose_reordering()` method
3. Atualizar testes existentes
4. Adicionar testes para novos campos
5. Commit: "fix(event-reordering): Corrige campos de ProposedChange"

#### P002: Estado CANCELLED Ausente no Enum

- **Severidade:** CRÍTICA
- **Status:** PENDENTE
- **Impacto:** Violação da regra RN-HI02 e RN-R03

**Descrição:**
Estado `CANCELLED` está documentado mas não existe no código.

**Localização:** `cli/src/timeblock/models/habit_instance.py`

**Código Atual:**

```python
class HabitInstanceStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    # [FALTA] CANCELLED
```

**Correção Necessária:**

```python
class HabitInstanceStatus(str, Enum):
    """Status de instância de hábito.

    Transições permitidas:
    - PLANNED → IN_PROGRESS, SKIPPED, CANCELLED
    - IN_PROGRESS → PAUSED, COMPLETED, SKIPPED
    - PAUSED → IN_PROGRESS, SKIPPED
    - COMPLETED, SKIPPED, CANCELLED → Estado final
    """
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"  # [ADICIONAR]
```

**Implementação Adicional Necessária:**

```python
# Em routine_service.py
@staticmethod
def deactivate_routine(routine_id: int) -> tuple[Routine, int]:
    """Desativa rotina e cancela instâncias futuras."""
    # ... código de desativação ...

    # Cancela instâncias futuras
    for habit in routine.habits:
        instances = session.exec(
            select(HabitInstance)
            .where(HabitInstance.habit_id == habit.id)
            .where(HabitInstance.status == HabitInstanceStatus.PLANNED)
            .where(HabitInstance.date >= date.today())
        ).all()

        for instance in instances:
            instance.status = HabitInstanceStatus.CANCELLED
            cancelled_count += 1

    return routine, cancelled_count
```

**Tempo de Correção:** 2 horas

**Próximos Passos:**

1. Adicionar `CANCELLED` ao enum
2. Implementar `deactivate_routine()` method
3. Atualizar diagrama de estados
4. Adicionar testes de transição para CANCELLED
5. Commit: "feat(models): Adiciona estado CANCELLED e lógica de desativação"

#### P003: Flags Redundantes (user_override vs manually_adjusted)

- **Severidade:** ALTA
- **Status:** PENDENTE
- **Impacto:** Confusão no código, possível inconsistência

**Descrição:**
Modelo `HabitInstance` tem dois flags similares sem diferenciação clara.

**Localização:** `cli/src/timeblock/models/habit_instance.py`

**Código Atual:**

```python
class HabitInstance(SQLModel, table=True):
    manually_adjusted: bool = Field(default=False)
    user_override: bool = Field(default=False)
    # Quando usar cada um? Diferença não está clara
```

**Opções de Resolução:**

##### **Opção A: Consolidar (Recomendada para MVP)**

```python
class HabitInstance(SQLModel, table=True):
    user_override: bool = Field(
        default=False,
        description="True se instância foi modificada manualmente pelo usuário"
    )
    # [REMOVER] manually_adjusted
```

##### **Opção B: Manter com Semântica Clara**

```python
class HabitInstance(SQLModel, table=True):
    manually_adjusted: bool = Field(
        default=False,
        description="Horários foram ajustados. Pode ser revertido em sync."
    )
    user_override: bool = Field(
        default=False,
        description="Usuário decidiu não seguir template. Permanente."
    )
```

**Decisão Requerida:** ADR-009 (A CRIAR)

**Tempo de Correção:** 3 horas (incluindo migration se consolidar)

### 4.2 Problemas de Alta Prioridade

#### P004: Estado PAUSED Não Documentado

- **Severidade:** MÉDIA
- **Status:** PENDENTE

**Descrição:**
Estado `PAUSED` existe no código mas não está documentado formalmente.

**Correção Necessária:**

- Adicionar `PAUSED` ao diagrama de estados
- Documentar transições: `IN_PROGRESS ↔ PAUSED`
- Atualizar docstring de `HabitInstanceStatus`

**Tempo de Correção:** 1 hora

#### P005: Campo scheduled_duration_minutes Ausente

- **Severidade:** MÉDIA
- **Status:** PENDENTE

**Descrição:**
Documentação especifica `scheduled_duration_minutes` mas campo não existe no modelo.

**Opções:**

1. Adicionar campo ao modelo
2. Atualizar documentação para refletir uso de start/end apenas

**Decisão Requerida:** ADR-012 (A CRIAR)

**Tempo de Correção:** 2 horas (se adicionar campo) ou 30min (se ajustar docs)

#### P006: Modelo de Recorrência Inconsistente

- **Severidade:** MÉDIA
- **Status:** PENDENTE

**Descrição:**
Documentação especifica `WEEKLY_ON` com `recurrence_days`, mas código usa dias individuais (MONDAY, TUESDAY, etc).

**Decisão Requerida:** ADR-010

**Tempo de Correção:** 4 horas (se implementar WEEKLY_ON) ou 1h (se ajustar docs)

### 4.3 Problemas de Qualidade de Documentação

#### P007: Emojis Presentes no Código e Documentação

- **Severidade:** BAIXA
- **Status:** PENDENTE
- **Violação:** Padrões de código estabelecidos

**Localizações Identificadas:**

```python
# cli/src/timeblock/utils/proposal_display.py
console.print("\n[bold yellow][LISTA] Mudanças Propostas:[/bold yellow]")
```

**Documento de Regras:**
Múltiplos emojis em exemplos: [INVÁLIDO] [VÁLIDO] [AVISO] [CONFIG] [NOTA]

**Correção Necessária:**

```shell
# Executar script de substituição automática
./fix_emojis.sh

# Substituições:
# [INVÁLIDO] → [INVÁLIDO]
# [VÁLIDO] → [VÁLIDO]
# [AVISO] → [AVISO]
# etc.
```

**Tempo de Correção:** 1 hora

#### P008: Links Quebrados (404)

- **Severidade:** MÉDIA
- **Status:** PENDENTE
- **Total:** 10 arquivos ausentes

**Arquivos Ausentes:**

1. `docs/02-diagrams/c4-model/L3-components-core.md`
2. `docs/02-diagrams/sequences/habit-instantiation.md`
3. `docs/02-diagrams/states/event-states.md`
4. `docs/05-api/models/event-models.md`
5. `docs/05-api/models/habit-models.md`
6. `docs/05-api/cli/options.md`
7. `docs/07-testing/fixtures/database.md`
8. `docs/07-testing/fixtures/time.md`
9. `docs/07-testing/scenarios/event-creation.md`
10. `docs/07-testing/scenarios/conflict-detection.md`

**Prioridade de Criação:**

- CRÍTICA: event-states.md, conflict-detection.md, habit-instantiation.md
- ALTA: event-models.md, habit-models.md
- MÉDIA: Restantes

**Tempo de Correção:** 6 horas (páginas críticas) + 5 horas (restantes)

---

## 5. Infraestrutura de Documentação

### 5.1 MkDocs Configurado

- **Status:** OPERACIONAL
- **Framework:** MkDocs Material
- **Idioma:** Português (pt-BR)

**Arquivo de Configuração:** `mkdocs.yml` (201 linhas)

**Features Habilitadas:**

- Navigation tabs (sticky)
- Navigation sections (expand)
- Search (multilingual: pt/en)
- Code copy buttons
- Table of contents (follow)
- Syntax highlighting
- Mermaid diagrams

**Temas:**

- Modo claro/escuro toggle
- Cores: Indigo primary, Indigo accent
- Fontes: Roboto (text), Roboto Mono (code)

**Plugins:**

- Search com suporte a português

**Extensões Markdown:**

- Admonitions (caixas de aviso)
- Code highlighting
- Footnotes
- TOC com permalinks
- Mermaid para diagramas
- Task lists
- Emojis (via Material)

### 5.2 Estrutura de Diretórios

```terminal
docs/
├── 01-architecture/          # Arquitetura (arc42)
│   ├── README.md
│   ├── 01-introduction-goals.md
│   ├── 02-constraints.md
│   ├── 03-context-scope.md
│   ├── 04-solution-strategy.md
│   ├── 05-building-blocks.md
│   ├── 06-runtime-view.md
│   ├── 07-deployment.md
│   ├── 08-crosscutting.md
│   ├── 09-decisions-index.md
│   ├── 10-quality.md
│   ├── 11-risks-debt.md
│   └── 12-glossary.md
│
├── 02-diagrams/              # Diagramas visuais
│   ├── README.md
│   ├── c4-model/             # C4 Model (Context, Containers, Components, Code)
│   │   ├── L1-system-context.md
│   │   ├── L2-containers.md
│   │   └── L3-components-core.md [CRIAR]
│   ├── sequences/            # Diagramas de sequência
│   │   ├── event-reordering.md
│   │   └── habit-instantiation.md [CRIAR]
│   ├── states/               # Máquinas de estado
│   │   ├── timer-states.md
│   │   └── event-states.md [CRIAR]
│   └── data/                 # Modelos de dados
│       └── er-diagram.md
│
├── 03-decisions/             # Architecture Decision Records
│   ├── README.md
│   ├── template.md
│   ├── 001-sqlmodel-orm.md
│   ├── 002-typer-cli.md
│   ├── 003-event-reordering.md
│   ├── 004-habit-vs-instance.md
│   ├── 005-resource-first-cli.md
│   ├── 006-textual-tui.md
│   ├── 007-service-layer.md
│   ├── 008-tuple-returns.md
│   ├── 009-flags-consolidation.md [CRIAR]
│   ├── 010-recurrence-model.md [CRIAR]
│   └── 011-conflict-philosophy.md [CRIAR]
│
├── 04-specifications/        # Especificações técnicas
│   ├── README.md
│   ├── business-rules/       # Regras de negócio
│   │   ├── BR001-habit-scheduling.md
│   │   ├── BR002-event-conflicts.md
│   │   ├── BR003-reordering-logic.md
│   │   ├── BR004-timer-behavior.md
│   │   └── CATALOG-COMPLETE.md [CRIAR]
│   ├── algorithms/           # Algoritmos detalhados
│   │   ├── event-reordering.md
│   │   ├── conflict-detection.md
│   │   └── event-reordering-formal-spec.md [CRIAR]
│   ├── protocols/            # Protocolos do sistema
│   │   ├── validation.md
│   │   └── error-handling.md
│   └── philosophy/           # Filosofia de design
│       └── conflict-philosophy.md [CRIAR]
│
├── 05-api/                   # Documentação de APIs internas
│   ├── README.md
│   ├── services/             # Services
│   │   ├── event-reordering.md
│   │   ├── habit-service.md
│   │   └── timer-service.md
│   ├── models/               # Models
│   │   ├── event-models.md [CRIAR]
│   │   └── habit-models.md [CRIAR]
│   └── cli/                  # CLI
│       ├── commands.md
│       └── options.md [CRIAR]
│
├── 06-development/           # Guias de desenvolvimento
│   ├── README.md
│   ├── setup.md
│   ├── workflow.md
│   └── testing.md
│
├── 07-testing/               # Estratégia de testes
│   ├── README.md
│   ├── test-plan.md
│   ├── fixtures/             # Fixtures
│   │   ├── database.md [CRIAR]
│   │   └── time.md [CRIAR]
│   └── scenarios/            # Cenários de teste
│       ├── event-creation.md [CRIAR]
│       └── conflict-detection.md [CRIAR]
│
├── 08-user-guides/           # Guias do usuário
│   ├── README.md
│   ├── getting-started.md
│   ├── cli-reference.md
│   ├── faq.md
│   ├── workflows/            # Workflows de uso
│   │   ├── README.md
│   │   └── v1.0-baseline.md
│   ├── tutorials/            # Tutoriais passo a passo
│   └── reference/            # Material de referência
│       ├── rrule-examples.md
│       └── priority-guide.md
│
├── 09-research/              # Pesquisa e contexto
│   ├── README.md
│   ├── documentation-methodologies.md
│   └── topics/
│       ├── scheduling-algorithms.md
│       ├── time-management.md
│       └── habit-formation.md
│
└── 10-meta/                  # Meta-documentação
    ├── README.md
    ├── project-status.md
    ├── technical-debt.md
    ├── detailed-roadmap.md
    ├── pending-decisions.md
    ├── success-metrics.md
    ├── problemas-e-solucoes.md
    ├── changelog.md
    ├── prompt-proximo-chat.md
    └── templates/
        ├── adr-template.md
        └── issue-template.md
```

### 5.3 Comandos MkDocs

**Servir localmente:**

```shell
cd /path/to/timeblock-organizer
mkdocs serve
# Acesse: http://127.0.0.1:8000
```

**Build estático:**

```shell
mkdocs build
# Output: site/
```

**Deploy para GitHub Pages:**

```shell
mkdocs gh-deploy
```

**Verificar links:**

```shell
linkchecker http://127.0.0.1:8000
```

---

## 6. Plano de Ação Integrado

### 6.1 Visão Geral

- **Tempo Total Estimado:** 32 horas
- **Distribuição:** 3 fases ao longo de 2-3 semanas
- **Paralelização:** Algumas tarefas podem ser executadas em paralelo

### 6.2 Fase Imediata (8 horas)

**Objetivo:** Corrigir problemas críticos bloqueadores

#### Dia 1 (4 horas)

##### **Tarefa 1.1: Remover Emojis (1h)**

```shell
# Executar script de substituição
cat > fix_emojis.sh << 'EOF'
#!/bin/bash
# Substituir emojis por símbolos ASCII
DOC_FILE="docs/04-specifications/business-rules/REGRAS-NEGOCIO-COMPLETO.md"
sed -i 's/[INVÁLIDO]/[INVÁLIDO]/g' "$DOC_FILE"
sed -i 's/[VÁLIDO]/[VÁLIDO]/g' "$DOC_FILE"
sed -i 's/[AVISO]/[AVISO]/g' "$DOC_FILE"
# ... mais substituições
EOF

chmod +x fix_emojis.sh
./fix_emojis.sh

# Corrigir código Python
sed -i 's/[LISTA] Mudanças Propostas:/>>> MUDANÇAS PROPOSTAS:/g' \
    cli/src/timeblock/utils/proposal_display.py

# Commit
git add .
git commit -m "fix: Remove emojis de código e documentação"
```

##### **Tarefa 1.2: Corrigir Bug Sprint 1.4 (3h)**

```shell
# 1. Atualizar modelo ProposedChange
# Editar: cli/src/timeblock/services/event_reordering_models.py

# 2. Corrigir propose_reordering()
# Editar: cli/src/timeblock/services/event_reordering_service.py

# 3. Atualizar testes
# Editar: cli/tests/unit/test_services/test_event_reordering_service.py

# 4. Executar testes
pytest cli/tests/unit/test_services/test_event_reordering_service.py -v

# 5. Commit
git add cli/src/timeblock/services/
git add cli/tests/
git commit -m "fix(event-reordering): Corrige campos de ProposedChange

- Renomeia original_start/end para current_start/end
- Renomeia new_start/end para proposed_start/end
- Adiciona event_title ao modelo
- Atualiza testes existentes
- Resolve bug do Sprint 1.4"
```

#### Dia 2 (4 horas)

##### **Tarefa 2.1: Adicionar Estado CANCELLED (2h)**

```shell
# 1. Atualizar enum
# Editar: cli/src/timeblock/models/habit_instance.py
# Adicionar CANCELLED ao HabitInstanceStatus

# 2. Implementar deactivate_routine()
# Editar: cli/src/timeblock/services/routine_service.py

# 3. Adicionar testes
# Criar: cli/tests/unit/test_services/test_routine_deactivation.py

# 4. Executar testes
pytest cli/tests/unit/test_services/ -v

# 5. Commit
git add cli/src/timeblock/models/habit_instance.py
git add cli/src/timeblock/services/routine_service.py
git add cli/tests/
git commit -m "feat(models): Adiciona estado CANCELLED e lógica de desativação

- Adiciona CANCELLED ao HabitInstanceStatus enum
- Implementa RoutineService.deactivate_routine()
- Cancela instâncias futuras ao desativar rotina
- Adiciona testes de transição para CANCELLED
- Resolve regra RN-R03"
```

##### **Tarefa 2.2: Criar Documentação de Filosofia de Conflitos (2h)**

```shell
# 1. Criar diretório
mkdir -p docs/04-specifications/philosophy

# 2. Criar arquivo
cat > docs/04-specifications/philosophy/conflict-philosophy.md << 'EOF'
# Filosofia de Tratamento de Conflitos

## Decisão Fundamental

O TimeBlock Organizer **não bloqueia** eventos sobrepostos intencionalmente.

## Três Princípios

### 1. Vida Real Tem Conflitos
[Conteúdo da seção 2.1 deste documento]

### 2. Autonomia do Usuário
[Conteúdo da seção 2.1 deste documento]

### 3. Flexibilidade > Rigidez
[Conteúdo da seção 2.1 deste documento]

## Implementação Técnica
[Pattern de tupla (entity, proposal)]

## Exemplos Práticos
[Cenários de uso]
EOF

# 3. Atualizar mkdocs.yml
# Adicionar entrada em nav:

# 4. Commit
git add docs/04-specifications/philosophy/
git add mkdocs.yml
git commit -m "docs: Documenta filosofia de tratamento de conflitos

- Cria docs/04-specifications/philosophy/conflict-philosophy.md
- Documenta decisão de não-bloquear conflitos
- Explica três princípios fundamentais
- Inclui exemplos práticos de uso
- Base para ADR-011"
```

### 6.3 Fase Curto Prazo (16 horas)

**Objetivo:** Expandir documentação e resolver inconsistências

#### Dias 3-4 (8 horas)

##### **Tarefa 3.1: Criar event-states.md (2h)**

```shell
# Criar diagrama completo de estados
# Usar conteúdo já preparado na análise anterior
cat > docs/02-diagrams/states/event-states.md << 'EOF'
# Diagrama de Estados: Events (HabitInstance)

[Conteúdo completo com Mermaid diagram]
EOF

git add docs/02-diagrams/states/event-states.md
git commit -m "docs: Adiciona diagrama de estados de HabitInstance"
```

##### **Tarefa 3.2: Expandir Catálogo de Regras (4h)**

```shell
# Integrar 51 regras das conversas anteriores
cat > docs/04-specifications/business-rules/CATALOG-COMPLETE.md << 'EOF'
# Catálogo Completo de Regras de Negócio

Total: 51 regras

[RN001-RN051 detalhadas]
EOF

git add docs/04-specifications/business-rules/CATALOG-COMPLETE.md
git commit -m "docs: Adiciona catálogo completo de 51 regras de negócio"
```

##### **Tarefa 3.3: Atualizar Project Status (2h)**

```shell
# Documentar fases 0-4 com progresso atual
# Editar: docs/10-meta/project-status.md

git add docs/10-meta/project-status.md
git commit -m "docs: Atualiza status do projeto com fases detalhadas

- Documenta Fase 0: 100% completa
- Documenta Fase 1: 75% completa (bloqueada)
- Documenta Fase 2: 0% (aguardando)
- Adiciona releases planejadas v1.0-v2.0
- Registra Sprint 2.1 completado"
```

#### Dias 5-6 (8 horas)

##### **Tarefa 4.1: Criar ADRs Faltantes (3h)**

```shell
# ADR-009: Flags Consolidation
cat > docs/03-decisions/009-flags-consolidation.md << 'EOF'
# ADR-009: Consolidação de Flags Override

## Status
PROPOSTO

## Contextoo
[Problema dos dois flags]

## Decisão
[Manter apenas user_override]

## Consequências
[Migration necessária, simplificação do código]
EOF

# ADR-010: Recurrence Model
# ADR-011: Conflict Philosophy
# [Criar similarmente]

git add docs/03-decisions/009-*.md
git add docs/03-decisions/010-*.md
git add docs/03-decisions/011-*.md
git commit -m "docs: Adiciona ADRs 009, 010, 011

- ADR-009: Consolidação de flags override
- ADR-010: Modelo de recorrência
- ADR-011: Filosofia de conflitos"
```

##### **Tarefa 4.2: Criar Páginas API e Testing (5h)**

```shell
# event-models.md
# habit-models.md
# database.md
# time.md
# event-creation.md
# [Criar todas as páginas faltantes]

git add docs/05-api/models/
git add docs/07-testing/fixtures/
git add docs/07-testing/scenarios/
git commit -m "docs: Completa documentação de API e Testing

- Adiciona event-models.md e habit-models.md
- Documenta fixtures de database e time
- Adiciona cenários de teste
- Resolve 6 links quebrados (404)"
```

### 6.4 Fase Consolidação (8 horas)

**Objetivo:** Finalizar especificações e integrar tudo

#### Dias 7-8 (8 horas)

##### **Tarefa 5.1: Especificação Formal de Event Reordering (4h)**

```shell
# Criar especificação completa com pseudo-código
cat > docs/04-specifications/algorithms/event-reordering-formal-spec.md << 'EOF'
# Especificação Formal: Event Reordering

## Definição Matemática

Dado um conjunto de eventos E = {e₁, e₂, ..., eₙ} no dia D...

## Algoritmo (Pseudo-código)

```

FUNCTION propose_reordering(triggered_event, all_events):
[Pseudo-código formal]

```terminal

## Complexidade Computacional

Tempo: O(n log n) onde n = número de eventos no dia
Espaço: O(n) para armazenar proposta

## Edge Cases

1. Evento após meia-noite
2. Múltiplos eventos simultâneos
3. Ciclos de dependência
[...]

## Casos de Teste

[Matriz de casos de teste]
EOF

git add docs/04-specifications/algorithms/event-reordering-formal-spec.md
git commit -m "docs: Adiciona especificação formal de Event Reordering

- Define algoritmo matematicamente
- Inclui pseudo-código formal
- Documenta complexidade computacional
- Lista edge cases conhecidos
- Adiciona matriz de casos de teste"
```

##### **Tarefa 5.2: Revisão Final e Integração (4h)**

```shell
# 1. Verificar todos os links
linkchecker http://127.0.0.1:8000 > link_check_report.txt

# 2. Corrigir links quebrados identificados
# [Iterar sobre relatório]

# 3. Testar build do MkDocs
mkdocs build --strict

# 4. Atualizar README principal do projeto
# Adicionar links para documentação

# 5. Commit final
git add .
git commit -m "docs: Finaliza integração da documentação

- Corrige todos os links quebrados
- Atualiza README principal
- Valida build do MkDocs
- Documentação 95% completa
- Resolve todos os problemas críticos"

# 6. Tag de release
git tag -a v1.1.0-docs -m "Release: Documentação Completa v1.1.0"
git push origin develop --tags
```

### 6.5 Checklist de Execução

```markdown
### Fase Imediata (8h)

- [ ] Remover emojis de código e docs (1h)
- [x] Bug Sprint 1.4 resolvido (3h)
- [ ] Adicionar estado CANCELLED (2h)
- [ ] Documentar filosofia de conflitos (2h)

### Fase Curto Prazo (16h)

- [ ] Criar event-states.md (2h)
- [ ] Expandir catálogo de regras (4h)
- [ ] Atualizar project-status (2h)
- [ ] Criar ADRs 009, 010, 011 (3h)
- [ ] Criar páginas API e Testing (5h)

### Fase Consolidação (8h)

- [ ] Especificar formalmente Event Reordering (4h)
- [ ] Revisão final e integração (4h)

### Total: 32 horas
```

---

## 7. Métricas de Qualidade

### 7.1 Estado Atual

| Métrica                        | Valor Atual | Meta | Status     |
| ------------------------------ | ----------- | ---- | ---------- |
| Cobertura de Código            | 99%         | 100% | [VERDE]    |
| Testes Passando                | 181/181     | 100% | [VERDE]    |
| Cobertura de Regras de Negócio | 70%         | 100% | [AMARELO]  |
| Links Quebrados                | 10          | 0    | [VERMELHO] |
| Inconsistências Críticas       | 4           | 0    | [VERMELHO] |
| Emojis no Código               | 1           | 0    | [AMARELO]  |
| Português Correto              | 100%        | 100% | [VERDE]    |
| Especificações Formais         | 20%         | 90%  | [VERMELHO] |
| ADRs Documentados              | 8           | 11   | [AMARELO]  |
| Páginas 404                    | 10          | 0    | [VERMELHO] |

### 7.2 Estado Pós-Execução do Plano (Estimado)

| Métrica                        | Valor Esperado | Status Esperado |
| ------------------------------ | -------------- | --------------- |
| Cobertura de Regras de Negócio | 95%            | [VERDE]         |
| Links Quebrados                | 0              | [VERDE]         |
| Inconsistências Críticas       | 0              | [VERDE]         |
| Emojis no Código               | 0              | [VERDE]         |
| Especificações Formais         | 85%            | [VERDE]         |
| ADRs Documentados              | 11             | [VERDE]         |
| Páginas 404                    | 0              | [VERDE]         |

### 7.3 KPIs de Desenvolvimento

**Velocidade de Desenvolvimento:**

- Sprints completados: 2.1 de ~12 planejados
- Taxa de conclusão: ~17% do roadmap v2.0
- Bloqueadores ativos: 0

**Qualidade de Código:**

- Cobertura de testes: 99%
- Testes passando: 100%
- Dívida técnica: Média (tuple returns deprecated)

**Documentação:**

- Cobertura: 70% → 95% (após execução do plano)
- Atualização: Última em 28/10/2025
- Próxima revisão: Após conclusão do plano (estimado 14/11/2025)

---

## 8. Guia de Uso deste Documento

### 8.1 Quando Consultar

**Antes de Iniciar Sessão de Desenvolvimento:**

- Ler seção 1 (Estado Atual do Projeto)
- Verificar bloqueadores na seção 4.1
- Consultar plano de ação na seção 6

**Durante Desenvolvimento:**

- Consultar regras de negócio na seção 3
- Verificar filosofia de design na seção 2
- Checar problemas conhecidos na seção 4

**Ao Documentar:**

- Seguir estrutura da seção 5
- Usar métricas da seção 7 como guia
- Atualizar este documento conforme necessário

### 8.2 Como Atualizar

**Periodicidade:** Após cada fase concluída ou decisão arquitetural importante

**Responsável:** Tech Lead ou quem completar a tarefa

**Processo:**

1. Abrir `docs/10-meta/INTEGRACAO-DOCUMENTACAO-COMPLETA.md`
2. Atualizar seção relevante
3. Atualizar data de "Última Atualização" no topo
4. Commit: "docs(meta): Atualiza integração com [mudança]"

**Seções que Requerem Atualização Frequente:**

- 1.2: Progresso por Fase
- 4.1: Problemas Críticos (quando resolvidos)
- 7.1: Métricas de Qualidade
- 6.5: Checklist de Execução

### 8.3 Documentos Relacionados

**Documentos de Apoio:**

- `analise-documentacao-regras-negocio.md`: Análise técnica detalhada
- `guia-pratico-correcoes.md`: Comandos específicos para correções
- `analise-comparativa-artifacts.md`: Comparação com conversas anteriores

**Conversas Anteriores Relevantes:**

- 25-28 Outubro 2025: Documentação de progresso e regras
- Chat sobre filosofia de conflitos
- Chat sobre HabitAtom refactor

**Próximos Documentos a Criar:**

- ADR-009, 010, 011
- CATALOG-COMPLETE.md (51 regras)
- event-reordering-formal-spec.md

### 8.4 Contatos e Questões

**Para Decisões Arquiteturais:**

- Criar ADR em `docs/03-decisions/`
- Discutir em reunião de arquitetura
- Documentar rationale

**Para Bugs Identificados:**

- Abrir issue no GitHub
- Referenciar este documento
- Adicionar à seção 4 se crítico

**Para Dúvidas sobre Regras:**

- Consultar seção 3 deste documento
- Verificar CATALOG-COMPLETE.md quando criado
- Referenciar código fonte como fonte final de verdade

---

## Conclusão

Este documento integra três meses de trabalho, múltiplas conversas e análises detalhadas sobre o TimeBlock Organizer. Ele serve como **ponto de entrada único** para entender o estado atual, problemas conhecidos e caminho à frente.

**Principais Takeaways:**

1. **Progresso Sólido:** Fase 0 completa, v1.0.0 estável, 99% de cobertura de testes

2. **Sprint 1.4:** Resolvido

3. **Filosofia Clara:** Sistema não bloqueia conflitos - decisão fundamental que guia design

4. **Documentação em Progresso:** 70% completa, 32 horas estimadas para 95%

5. **Caminho Bem Definido:** Plano de 3 fases para completar documentação e resolver problemas

**Próximos Passos Imediatos:**

1. Executar Fase Imediata do plano (8h)
2. Resolver bug Sprint 1.4
3. Criar documentação de filosofia de conflitos
4. Adicionar estado CANCELLED ao código

**Visão de Longo Prazo:**

- v1.1.0: Event Reordering completo (Novembro 2025)
- v1.2.0: HabitAtom refactor (Novembro 2025)
- v2.0.0: TUI rica com Textual (Janeiro 2026)

Este documento vive e evolui com o projeto. Mantenha-o atualizado e ele será o guia definitivo do TimeBlock Organizer.

---

- **Documento Criado:** 30 de Outubro de 2025
- **Versão:** 2.1.0
- **Próxima Revisão:** 14 de Novembro de 2025 (após execução do plano)
- **Localização:** `docs/10-meta/INTEGRACAO-DOCUMENTACAO-COMPLETA.md`
