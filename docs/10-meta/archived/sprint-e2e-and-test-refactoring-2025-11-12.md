# Sprint: E2E Tests + Refatoração Sistemática de Testes

- **Data de Criação:** 12 de novembro de 2025
- **Status:** [PLANEJAMENTO -> EXECUÇÃO]
- **Prioridade:** Alta
- **Estimativa:** 10-15 horas

---

## 1. CONTEXTO E MOTIVAÇÃO

### 1.1 Situação Atual

O projeto TimeBlock Organizer possui:

- **Documentação:** Excelente - 20 ADRs, 23+ Business Rules formalizadas
- **Código:** Funcional - 99% cobertura de testes, arquitetura sólida
- **Gap Crítico:** Apenas 1 de 45 arquivos de teste referencia explicitamente BRs

### 1.2 Problema Identificado

**Desalinhamento entre Documentação e Testes:**

```terminal
Situação Atual:
+------------------+
| Documentation    |  23 BRs documentadas (BR-DOMAIN-XXX)
| (Excelente)      |  ADR-019 define padrão test_br_*
+--------+---------+
         |  [X] Desconexão
         v
+------------------+
| Tests            |  45 arquivos, 99% coverage
| (Funcional)      |  Mas nomes genéricos (test_create, test_update)
+--------+---------+
         |  [OK] Valida corretamente
         v
+------------------+
| Code             |  Implementação sólida
| (Funcional)      |
+------------------+

Problema: Testes validam código mas não documentam BRs explicitamente
```

### 1.3 Impacto

**Para Desenvolvedores:**

- Difícil identificar qual teste valida qual BR
- Onboarding mais lento (precisa ler código para entender regras)
- Refatoração arriscada (não é óbvio quais BRs podem quebrar)

**Para o Projeto:**

- Viola filosofia docs > BDD > tests > code
- Requirements Traceability Matrix incompleta
- Testes não servem como documentação viva

### 1.4 Decisão Estratégica

**Priorização definida:**

1. **Opção B:** Completar E2E tests (validação de workflows)
2. **Opção A:** Refatoração sistemática (rastreabilidade BR-\*)
3. **Opção C:** Preencher BRs faltantes (postergar para Fase 3)

**Rationale:**

- E2E tests validam regras de negócio de ponta a ponta (valor imediato)
- Refatoração alinha projeto com sua própria filosofia (dívida técnica)
- BRs faltantes podem ser criadas conforme necessidade (não bloqueante)

---

## 2. OBJETIVOS

### 2.1 Objetivos Primários

**1. E2E Tests Completos**

- [DONE] 2 scenarios existentes (habit-generation, conflict-detection)
- [TODO] 3 scenarios novos (event-creation, timer-lifecycle, event-reordering)
- **Meta:** 5 scenarios E2E cobrindo workflows críticos

**2. Refatoração Sistemática**

- [TODO] Renomear 45 arquivos de teste para padrão `test_br_*`
- [TODO] Adicionar docstrings com referências explícitas a BRs
- [TODO] Atualizar RTM (Requirements Traceability Matrix)
- **Meta:** 100% rastreabilidade BR -> Test -> Code

### 2.2 Objetivos Secundários

- Identificar BRs sem testes (criar backlog)
- Consolidar padrões de teste (template)
- Melhorar documentação inline dos testes

### 2.3 Não-Objetivos (Fora de Escopo)

- [x] Criar novas BRs (usar as 23 existentes)
- [x] Refatorar código de produção (apenas testes)
- [x] Implementar novas features
- [x] Configurar CI/CD (postergar para sincronização completa)

---

## 3. FASE 1: E2E TESTS COMPLETOS

### 3.1 Scenarios Existentes

#### Scenario 1: Habit Generation Workflow

- **Arquivo:** `tests/e2e/test_habit_lifecycle.py::TestBRHabitWorkflow`
- **BRs Cobertas:** BR-HABIT-001, BR-HABIT-002, BR-HABIT-003
- **Status:** [DONE] Implementado

#### Scenario 2: Conflict Detection Workflow

- **Arquivo:** `tests/e2e/test_habit_lifecycle.py::TestBREventConflictWorkflow`
- **BRs Cobertas:** BR-EVENT-001, BR-EVENT-002
- **Status:** [DONE] Implementado

### 3.2 Scenarios Faltantes

#### Scenario 3: Event Creation Workflow

- **Arquivo:** `tests/e2e/test_event_creation.py` (NOVO)
- **BRs Cobertas:** BR-ROUTINE-001, BR-HABIT-001, BR-EVENT-001
- **Estimativa:** 45min
- **Detalhes:** Ver seção 3.3 para implementação completa

#### Scenario 4: Timer Lifecycle Workflow

- **Arquivo:** `tests/e2e/test_timer_lifecycle.py` (NOVO)
- **BRs Cobertas:** BR-TIMER-001, BR-TIMER-002, BR-LOG-001
- **Estimativa:** 45min
- **Detalhes:** Ver seção 3.4 para implementação completa

#### Scenario 5: Event Reordering Application Workflow

- **Arquivo:** `tests/e2e/test_event_reordering.py` (NOVO)
- **BRs Cobertas:** BR-EVENT-002, BR-EVENT-003, BR-EVENT-004
- **Estimativa:** 60min
- **Detalhes:** Ver seção 3.5 para implementação completa

### 3.3 Estrutura de Arquivos E2E

```terminal
tests/e2e/
├── conftest.py                      # Fixtures compartilhadas
├── test_habit_lifecycle.py          # [DONE] Existente (2 scenarios)
├── test_event_creation.py           # [TODO] NOVO (Scenario 3)
├── test_timer_lifecycle.py          # [TODO] NOVO (Scenario 4)
└── test_event_reordering.py         # [TODO] NOVO (Scenario 5)
```

### 3.4 Dependências Técnicas

**Para Scenario 4 (Timer):**

- `freezegun` ou `pytest-freezegun` para simular passagem de tempo
- Install: `pip install freezegun --break-system-packages`

**Para todos os scenarios:**

- `typer.testing.CliRunner` (já disponível)
- `pytest.fixture` para isolated_db (já existe)

---

## 4. FASE 2: REFATORAÇÃO SISTEMÁTICA

### 4.1 Escopo da Refatoração

**Total de arquivos:** 45 arquivos de teste
**Total de testes:** ~220 test methods

**Breakdown por domínio:**

```terminal
Domain           | Files | Tests | Estimativa
-----------------|-------|-------|------------
Validators       |   3   |  18   |  30min
Routine          |   5   |  25   |  1h
Habit            |   8   |  42   |  1.5h
HabitInstance    |   6   |  35   |  1h
Task             |   4   |  22   |  45min
Timer            |   5   |  28   |  1h
Event/Conflict   |   4   |  20   |  45min
Services         |  10   |  30   |  2h
-----------------|-------|-------|------------
TOTAL            |  45   | ~220  |  ~8h
```

### 4.2 Template de Renomeação

**Padrão atual (genérico):**

```python
def test_create_task_success():
    """Cria task com sucesso."""
    pass
```

**Padrão novo (BR-aligned):**

```python
class TestBRTask001Creation:
    """
    Testes validando BR-TASK-001: Criação de Tasks.

    BR-TASK-001: Tasks devem ter título, data/hora e duração.
    """

    def test_br_task_001_create_with_all_required_fields(self):
        """
        Valida BR-TASK-001: Task criada com campos obrigatórios.

        DADO: Título, data/hora e duração válidos
        QUANDO: Criar task
        ENTÃO: Task criada com sucesso
        E: Campos persistidos corretamente

        Referências:
            - BR-TASK-001: Regra de criação de tasks
            - ADR-007: Service Layer Pattern
        """
        # Implementação...
```

### 4.3 Plano de Refatoração por Domínio

Cada domínio será refatorado em commit separado seguindo estrutura:

1. Renomear classes para `TestBR{Domain}{Number}`
2. Renomear métodos para `test_br_{domain}_{number}_{scenario}`
3. Adicionar docstrings formato Gherkin (DADO/QUANDO/ENTÃO)
4. Incluir seção "Referências" com BRs e ADRs
5. Executar suite completa para validar
6. Commit individual

---

## 5. TIMELINE E MILESTONES

### 5.1 Cronograma Semanal

```terminal
Semana de 12-17 Nov 2025
+------------+----------------------------------+----------+
| Dia        | Tarefas                          | Duração  |
+------------+----------------------------------+----------+
| Ter 12 Nov | [DONE] CHANGELOG commit          | 5min     |
|            | [DONE] Custom Instructions       | 15min    |
|            | [TODO] Criar docs/10-meta/plan   | 30min    |
|            | [TODO] Fase 1: E2E Scenario 3    | 45min    |
|            | [TODO] Fase 1: E2E Scenario 4    | 45min    |
|            | [TODO] Fase 1: E2E Scenario 5    | 60min    |
|            | [    ] Commit e merge E2E        | 15min    |
+------------+----------------------------------+----------+
| Qua 13 Nov | [TODO] Fase 2: Mapeamento        | 2h       |
|            | [TODO] Refactor: Validators      | 30min    |
|            | [TODO] Refactor: Routine         | 1h       |
+------------+----------------------------------+----------+
| Qui 14 Nov | [TODO] Refactor: Habit           | 1.5h     |
|            | [TODO] Refactor: HabitInstance   | 1h       |
|            | [TODO] Refactor: Task            | 45min    |
+------------+----------------------------------+----------+
| Sex 15 Nov | [TODO] Refactor: Timer           | 1h       |
|            | [TODO] Refactor: Event/Conflict  | 45min    |
|            | [TODO] Refactor: Services        | 2h       |
+------------+----------------------------------+----------+
| Sáb 16 Nov | [TODO] Atualizar RTM final       | 1h       |
|            | [TODO] Atualizar CHANGELOG.md    | 30min    |
|            | [TODO] Gerar relatório completo  | 30min    |
+------------+----------------------------------+----------+
```

### 5.2 Milestones

**M1: E2E Tests Completos** (12 Nov EOD)

- [ ] 5 scenarios E2E implementados
- [ ] Todos testes passando
- [ ] Branch merged para develop

**M2: Mapeamento Completo** (13 Nov EOD)

- [ ] Documento BR->Tests criado
- [ ] Lista de BRs sem testes identificada

**M3: Refatoração 50% Completa** (14 Nov EOD)

- [ ] 4 domínios refatorados
- [ ] ~100 testes renomeados

**M4: Refatoração 100% Completa** (15 Nov EOD)

- [ ] Todos 8 domínios refatorados
- [ ] 220 testes renomeados

**M5: Documentação Sincronizada** (16 Nov EOD)

- [ ] RTM 100% atualizada
- [ ] CHANGELOG completo

---

## 6. CRITÉRIOS DE SUCESSO

### 6.1 Métricas Quantitativas

**E2E Tests:**

- [ ] 5 scenarios implementados
- [ ] 100% workflows críticos cobertos
- [ ] 0 testes E2E falhando

**Refatoração:**

- [ ] 45 arquivos renomeados (100%)
- [ ] 220 testes com padrão BR-\* (100%)
- [ ] 220 docstrings com referências BR (100%)

**Rastreabilidade:**

- [ ] 23 BRs mapeadas em RTM (100%)
- [ ] Cada BR tem >=1 teste unit (100%)
- [ ] Workflows críticos têm E2E test (100%)

### 6.2 Checklist de Validação Final

- [ ] Todos 5 E2E scenarios implementados e passando
- [ ] Zero testes com nomes genéricos
- [ ] 100% classes de teste seguem padrão TestBRDomainXXX
- [ ] 100% métodos seguem padrão test_br_domain_xxx_scenario
- [ ] RTM lista todos testes para cada BR
- [ ] CHANGELOG documenta todo trabalho
- [ ] Cobertura de código mantida em 99%+

---

## 7. RISCOS E MITIGAÇÕES

### 7.1 Riscos Técnicos

#### **R1: Quebra de testes durante refatoração**

- **Probabilidade:** Média
- **Impacto:** Alto
- **Mitigação:** Executar suite completa após cada commit

#### **R2: E2E tests flaky (intermitentes)**

- **Probabilidade:** Média
- **Impacto:** Médio
- **Mitigação:** Usar isolated_db fixture, mockar tempo

#### **R3: Mapeamento BR->Tests incompleto**

- **Probabilidade:** Baixa
- **Impacto:** Alto
- **Mitigação:** Revisão detalhada, validação cruzada

---

## 8. REFERÊNCIAS

### 8.1 Documentos Relacionados

- **ADR-019:** Test Naming Convention
- **ADR-020:** Business Rules Nomenclature
- **RTM:** Requirements Traceability Matrix
- **Test Strategy:** Estratégia de Testes
- **ROADMAP:** Roadmap v2.0

### 8.2 Padrões e Convenções

- **Commit Messages:** Brazilian Portuguese, conventional format
- **Code:** English (files, classes, methods)
- **Docs:** Portuguese (comments, docstrings, documentation)
- **Test Naming:** `test_br_{domain}_{number}_{scenario}`
- **Class Naming:** `TestBR{Domain}{Number}{Context}`

---

**Data:** 12 de novembro de 2025

**Versão:** 1.0

**Status:** [PRONTO PARA EXECUÇÃO]

**Última atualização:** 2025-11-12 21:00 BRT
