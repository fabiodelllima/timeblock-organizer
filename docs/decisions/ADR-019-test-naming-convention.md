# ADR-019: Test Naming Convention and BR Traceability

- **Status:** Accepted
- **Data:** 2025-11-10
- **Decisores:** Felipe (Tech Lead)
- **Relacionado:** ADR-018 (Language Standards)

---

## Contexto

TimeBlock possui 24 Business Rules documentadas em `docs/04-specifications/business-rules/` e 45 arquivos de teste (238 testes passando), mas **ZERO rastreabilidade explícita** entre BRs, testes e código.

### Problema Identificado

**Nomenclatura atual:**

```python
class TestCreateHabit:
    def test_create_habit_success(self, test_routine):
        """Cria hábito com sucesso."""
```

**Problemas:**

1. Impossível identificar qual BR está sendo testada
2. Busca por `grep "BR-HABIT-001" tests/` retorna vazio
3. Testes não servem como documentação executável
4. Dificulta manutenção e onboarding
5. Não há como mapear BR → Test → Code

### Situação Atual (Verificada 2025-11-10)

```terminal
BRs documentadas:        24
Testes existentes:       238 (45 arquivos)
Rastreabilidade:         0% (ZERO referências explícitas)
```

---

## Decisão

Adotar **convenção de nomenclatura explícita** que vincula Business Rules aos testes.

### Formato de Classes

```python
class TestBR{Domain}{Number}{Description}:
    """
    Suite de testes para BR-{DOMAIN}-{NUMBER}: {Título da BR}.

    {Descrição opcional da suite}
    """
```

**Exemplos:**

```python
class TestBRHabit001Creation:
    """Suite de testes para BR-HABIT-001: Criação de Hábitos em Rotinas."""

class TestBREvent001Detection:
    """Suite de testes para BR-EVENT-001: Detecção de Conflitos."""
```

### Formato de Métodos

```python
def test_br_{domain}_{number}_{scenario}_{condition}(self):
    """
    BR-{DOMAIN}-{NUMBER}: {Descrição curta do cenário}.

    DADO: {precondições}
    QUANDO: {ação do usuário}
    ENTÃO: {resultado esperado}
    """
```

**Exemplos:**

```python
def test_br_habit_001_creates_successfully(self, test_routine):
    """
    BR-HABIT-001: Sistema cria hábito quando dados válidos são fornecidos.

    DADO: Uma rotina válida existe no sistema
    QUANDO: Usuário fornece título, horário e recorrência válidos
    ENTÃO: Hábito é criado e persistido com atributos corretos
    """

def test_br_habit_001_rejects_empty_title(self, test_routine):
    """
    BR-HABIT-001: Sistema rejeita criação quando título está vazio.

    DADO: Uma rotina válida existe
    QUANDO: Usuário tenta criar hábito com título vazio
    ENTÃO: ValueError é levantado com mensagem apropriada
    """
```

### Estrutura de Comentários AAA

Todos testes devem seguir padrão **Arrange-Act-Assert**:

```python
def test_br_habit_001_creates_successfully(self, test_routine):
    """
    BR-HABIT-001: Sistema cria hábito com dados válidos.

    DADO: Rotina válida existe
    QUANDO: Criar hábito com dados válidos
    ENTÃO: Hábito criado e persistido
    """
    # ARRANGE - Preparar dados de teste
    title = "Exercício Matinal"
    start = time(6, 0)
    end = time(7, 0)

    # ACT - Executar ação sendo testada
    habit = HabitService.create_habit(
        routine_id=test_routine.id,
        title=title,
        scheduled_start=start,
        scheduled_end=end,
        recurrence=Recurrence.EVERYDAY
    )

    # ASSERT - Verificar resultados esperados
    assert habit.id is not None
    assert habit.title == title
```

---

## Consequências

### Positivas

1. **Rastreabilidade Bidirecional:** `grep "BR-HABIT-001"` encontra docs + testes + código
2. **Documentação Executável:** Testes servem como especificação viva
3. **Onboarding Facilitado:** Novos devs entendem BR → Test → Code
4. **Busca Eficiente:** IDEs mostram BR em tooltips e autocomplete
5. **Alinhamento com Indústria:** Padrão similar a Microsoft/Google

### Negativas

1. **Refactoring Necessário:** 45 arquivos de teste precisam renomeação
2. **Nomes Mais Longos:** Métodos terão 40-60 caracteres (mitigado com docstrings)
3. **Histórico Git:** Quebra git blame (solucionado com `git blame -C`)

### Neutras

1. Requer atualização de ADR-018 (Language Standards)
2. Nova seção em `docs/07-testing/README.md`
3. Criação de Requirements Traceability Matrix (ADR-021)

---

## Implementação

### Cronograma (Incremental por Domínio)

#### **Sprint 1 (Semanas 1-2): HABITS**

- Renomear testes habits (8 BRs, ~10 arquivos)
- Criar RTM para domínio habits
- Validar formato e processo

#### **Sprint 2 (Semanas 3-4): TASKS**

- Renomear testes tasks (9 BRs, ~8 arquivos)
- Expandir RTM

#### **Sprint 3 (Semanas 5-6): EVENTS**

- Renomear testes events (7 BRs, ~5 arquivos)
- Expandir RTM

#### **Sprint 4 (Semanas 7-8): CONSOLIDAÇÃO**

- Timer, Routines, Utils
- RTM completo
- Documentação final

### Exemplo de Refactoring

**Antes:**

```python
# tests/unit/test_services/test_habit_service_crud.py

class TestCreateHabit:
    """Testes para create_habit."""

    def test_create_habit_success(self, test_routine):
        """Cria hábito com sucesso."""
        habit = HabitService.create_habit(...)
        assert habit.id is not None
```

**Depois:**

```python
# tests/unit/habits/services/test_habit_service_br_habit_001.py

class TestBRHabit001Creation:
    """
    Suite de testes para BR-HABIT-001: Criação de Hábitos em Rotinas.

    Valida todos os cenários de criação de hábitos, incluindo validações
    de título, horários e recorrência conforme especificado na BR.
    """

    def test_br_habit_001_creates_successfully(self, test_routine):
        """
        BR-HABIT-001: Sistema cria hábito quando dados válidos fornecidos.

        DADO: Rotina válida existe no sistema
        QUANDO: Usuário cria hábito com título, horário e recorrência válidos
        ENTÃO: Hábito é criado e persistido com atributos corretos
        """
        # ARRANGE
        title = "Exercício Matinal"
        start = time(6, 0)
        end = time(7, 0)

        # ACT
        habit = HabitService.create_habit(
            routine_id=test_routine.id,
            title=title,
            scheduled_start=start,
            scheduled_end=end,
            recurrence=Recurrence.EVERYDAY
        )

        # ASSERT
        assert habit.id is not None
        assert habit.title == title
        assert habit.scheduled_start == start
```

---

## Alternativas Consideradas

### Alternativa 1: Manter Nomenclatura Atual

**Rejeitada:** Zero rastreabilidade, não escala.

### Alternativa 2: Usar Apenas Docstrings

```python
def test_create_habit_success(self):
    """BR-HABIT-001: Sistema cria hábito..."""
```

**Rejeitada:** Não aparece em relatórios pytest, dificulta busca.

### Alternativa 3: Tags pytest

```python
@pytest.mark.br_habit_001
def test_create_habit_success(self):
    pass
```

**Rejeitada:**

- Não escala (1 tag por teste = 238+ tags)
- Dificulta busca textual
- Não aparece em IDEs

### Alternativa 4: Comentários no Código

```python
def test_create_habit_success(self):
    # Valida BR-HABIT-001
    pass
```

**Rejeitada:** Comentários não são indexáveis, não aparecem em relatórios.

---

## Padrões e Convenções

### Idioma

Seguindo ADR-018 (Language Standards):

- **Nomes:** Inglês (PEP 8)
- **Docstrings:** Português BR
- **Comentários:** Português BR

### Mapeamento BR → Test

| Elemento  | Formato                                | Exemplo                                  |
| --------- | -------------------------------------- | ---------------------------------------- |
| Classe    | `TestBR{Domain}{Number}{Desc}`         | `TestBRHabit001Creation`                 |
| Método    | `test_br_{domain}_{number}_{scenario}` | `test_br_habit_001_creates_successfully` |
| Docstring | DADO-QUANDO-ENTÃO                      | Ver exemplo acima                        |

### Uma BR, Múltiplos Testes

Uma BR pode ter múltiplos cenários:

```python
class TestBRHabit001Creation:
    """Testes para BR-HABIT-001."""

    def test_br_habit_001_creates_with_all_fields(self):
        """BR-HABIT-001: Cria com todos campos."""

    def test_br_habit_001_creates_without_optional(self):
        """BR-HABIT-001: Cria sem campos opcionais."""

    def test_br_habit_001_rejects_empty_title(self):
        """BR-HABIT-001: Rejeita título vazio."""
```

---

## Integração com Outros ADRs

- **ADR-018:** Language Standards (nomenclatura PT-BR/EN)
- **ADR-020:** BDD Implementation (features BDD complementam testes)
- **ADR-021:** Requirements Traceability Matrix (rastreabilidade completa)
- **ADR-022:** E2E Test Coverage (E2E seguem mesmo padrão)

---

## Validação

### Critérios de Sucesso

1. ✓ 100% testes seguem padrão `test_br_*`
2. ✓ `grep "BR-HABIT-001" tests/` retorna todos testes da BR
3. ✓ RTM mapeia 100% das BRs
4. ✓ Pylance/IDEs mostram BRs em tooltips
5. ✓ Documentação sincronizada

### Métricas

```bash
# Verificar conformidade
grep -r "class Test" tests/ | grep -v "TestBR" | wc -l  # Deve ser 0

# Verificar rastreabilidade
grep -r "BR-HABIT-001" tests/ | wc -l  # Deve ser >0 para cada BR

# Listar BRs sem testes
# (Script em desenvolvimento)
```

---

## Referências

### Acadêmicas

- Microsoft: Unit Testing Best Practices (Azure DevOps Docs)
- Google: Software Engineering at Google, Chapter 12 (Testing)
- IEEE 829-2008: Standard for Software Test Documentation
- Requirements Traceability em Big Techs (Pesquisa 2025-11-10)

### Internas

- BR-HABIT-001 a BR-HABIT-008: `docs/04-specifications/business-rules/habit-instances.md`
- BR-TASK-001 a BR-TASK-009: `docs/04-specifications/business-rules/tasks.md`
- BR-EVENT-001 a BR-EVENT-007: `docs/04-specifications/business-rules/event-reordering.md`
- Análise do projeto: `docs/10-meta/ANALISE-PROJETO-TIMEBLOCK.md`

### Ferramentas

- pytest: Test discovery e relatórios
- pytest-html: Relatórios HTML com BRs visíveis
- grep/ripgrep: Busca textual por BRs

---

## Notas de Implementação

### Scripts Auxiliares

Criar `scripts/validate-test-naming.py` para validar conformidade.

### Pre-commit Hook (Futuro)

```yaml
# .pre-commit-config.yaml
- id: validate-br-naming
  name: Validar nomenclatura BR-*
  entry: python scripts/validate-test-naming.py
```

### Documentação Relacionada

- `docs/07-testing/README.md`: Atualizar com novos padrões
- `docs/07-testing/requirements-traceability-matrix.md`: Criar RTM
- `docs/07-testing/test-naming-examples.md`: Criar guia de exemplos

---

## Histórico

- **2025-11-10:** Criado (versão 1.0)
- **2025-11-10:** Implementado factories (commit 00bf542)
- **Próximo:** Implementar Sprint 1 (renomear testes habits)
