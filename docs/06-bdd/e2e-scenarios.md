# BDD Scenarios - End-to-End Tests

- **Última Atualização:** 13 de novembro de 2025
- **Status:** [ATIVO]
- **Cobertura:** 5 workflows críticos de usuário

---

## 1. INTRODUÇÃO

### 1.1 Objetivo

Este documento define scenarios BDD (Behavior-Driven Development) para testes E2E do TimeBlock Organizer. Cada scenario valida um workflow completo de usuário, desde a interação via CLI até a persistência no banco de dados.

### 1.2 Formato Gherkin

Utilizamos formato Gherkin padrão:

- **Feature:** Funcionalidade de alto nível
- **Background:** Contexto comum a todos scenarios
- **Scenario:** Caso de uso específico
- **Given/When/Then:** Passos do teste

### 1.3 Mapeamento para BRs

Cada scenario mapeia para uma ou mais Business Rules (BRs) documentadas em `docs/04-specifications/business-rules/`.

---

## 2. SCENARIO 1: HABIT LIFECYCLE WORKFLOW

### 2.1 Feature

```gherkin
Feature: Workflow Completo de Hábitos
  Como usuário do TimeBlock
  Quero criar, gerar e completar hábitos
  Para gerenciar minha rotina diária de forma eficiente

  Background:
    Given sistema TimeBlock inicializado com sucesso
    And banco de dados limpo e isolado para teste
    And uma rotina padrão foi criada e está ativa
```

### 2.2 Scenario Principal

```gherkin
  Scenario: Criar hábito diário e marcar como completo
    Given eu tenho uma rotina ativa chamada "Rotina Matinal"
    When eu executo comando "habit create" com parâmetros:
      | parâmetro | valor      |
      | --title   | Meditação  |
      | --start   | 06:00      |
      | --end     | 06:20      |
      | --repeat  | EVERYDAY   |
    Then sistema confirma "Hábito criado com sucesso"
    And hábito "Meditação" é salvo no banco de dados

    When eu executo comando "schedule generate --days 7"
    Then sistema gera 7 instâncias (uma por dia)
    And confirma "7 instâncias geradas"

    When eu executo comando "list today"
    Then vejo hábito "Meditação" na lista
    And horário mostrado é "06:00"
    And status é "PLANNED"

    When eu executo comando "habit complete 1"
    Then sistema confirma "Hábito marcado como completo"

    When eu executo comando "list today" novamente
    Then vejo indicador visual de conclusão
    And status mudou para "COMPLETED"
```

### 2.3 BRs Validadas

- **BR-HABIT-001:** Criação de hábitos em rotinas
- **BR-HABIT-002:** Geração de instâncias de hábitos
- **BR-HABIT-003:** Completar instância de hábito
- **BR-ROUTINE-001:** Uma rotina pode ter múltiplos hábitos

### 2.4 Assertions Críticas

```python
assert result.exit_code == 0, "Comando deve executar com sucesso"
assert "criado" in result.output.lower(), "Feedback deve confirmar criação"
assert "7" in result.output, "Deve gerar exatamente 7 instâncias"
assert "Meditação" in result.output, "Nome do hábito deve aparecer"
assert (
    "✓" in result.output
    or "COMPLETED" in result.output
), "Deve mostrar indicador de conclusão"
```

---

## 3. SCENARIO 2: CONFLICT DETECTION WORKFLOW

### 3.1 Feature

```gherkin
Feature: Detecção e Resolução de Conflitos
  Como usuário do TimeBlock
  Quero que o sistema detecte conflitos de horário automaticamente
  Para reorganizar minha agenda sem sobreposições

  Background:
    Given sistema TimeBlock inicializado com sucesso
    And banco de dados limpo e isolado para teste
    And uma rotina padrão foi criada e está ativa
```

### 3.2 Scenario Principal

```gherkin
  Scenario: Sistema detecta conflito e propõe reorganização
    Given eu tenho uma rotina ativa

    When eu crio hábito "Exercício" com:
      | --title  | Exercício |
      | --start  | 09:00     |
      | --end    | 10:00     |
      | --repeat | EVERYDAY  |
    Then hábito é criado com sucesso

    When eu crio hábito "Leitura" com:
      | --title  | Leitura |
      | --start  | 09:30   |
      | --end    | 10:30   |
      | --repeat | EVERYDAY |
    Then hábito é criado com sucesso

    When eu executo "schedule generate --days 1"
    Then sistema gera 2 instâncias

    When eu executo "habit adjust 1 --start 09:00 --end 10:00"
    Then sistema detecta conflito de horário
    And exibe mensagem contendo "conflito" ou "overlap"
    And sistema propõe reorganização automática
    And exibe mensagem contendo "proposta" ou "reordering"
```

### 3.3 BRs Validadas

- **BR-EVENT-001:** Detecção de conflitos de horário
- **BR-EVENT-002:** Proposta de reorganização automática
- **BR-EVENT-003:** Aplicação de reorganização com confirmação do usuário

### 3.4 Assertions Críticas

```python
assert result.exit_code == 0 or "conflito" in result.output.lower()
assert (
    "conflito" in result.output.lower()
    or "overlap" in result.output.lower()
), "Sistema deve avisar sobre conflito"
assert (
    "proposta" in result.output.lower()
    or "reordering" in result.output.lower()
), "Sistema deve propor reorganização"
```

---

## 4. MATRIZ DE COBERTURA

### 4.1 BRs x Scenarios

| Business Rule  | S1  | S2  | S3  | S4  | S5  |
| -------------- | --- | --- | --- | --- | --- |
| BR-ROUTINE-001 | X   |     | X   |     |     |
| BR-HABIT-001   | X   |     | X   |     |     |
| BR-HABIT-002   | X   |     |     |     |     |
| BR-HABIT-003   | X   |     |     |     |     |
| BR-EVENT-001   |     | X   | X   |     | X   |
| BR-EVENT-002   |     | X   |     |     | X   |
| BR-EVENT-003   |     |     |     |     | X   |
| BR-EVENT-004   |     |     |     |     | X   |
| BR-TIMER-001   |     |     |     | X   |     |
| BR-TIMER-002   |     |     |     | X   |     |
| BR-TIMER-003   |     |     |     | X   |     |
| BR-LOG-001     |     |     |     | X   |     |
| BR-COMMON-001  |     |     | X   |     |     |
| BR-COMMON-003  |     |     | X   |     |     |

**Legenda:**

- S1: Habit Lifecycle
- S2: Conflict Detection
- S3: Event Creation
- S4: Timer Lifecycle
- S5: Event Reordering

---

## 5. CONVENÇÕES DE IMPLEMENTAÇÃO

### 5.1 Estrutura de Arquivo

```python
"""
E2E tests validando [Feature Name].

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from pathlib import Path
import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner
from src.timeblock.main import app


@pytest.fixture
def isolated_db(tmp_path: Path) -> Path:
    """Cria banco de dados temporário isolado."""
    db_path = tmp_path / "test.db"
    return db_path


class TestBR[Domain][Number][Context]:
    """
    E2E: [Feature Description]

    BRs cobertas:
    - BR-[DOMAIN]-[XXX]: [Description]
    """

    def test_br_[domain]_[number]_[scenario](
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: [Scenario description]

        DADO: [Context]
        QUANDO: [Action]
        ENTÃO: [Expected outcome]

        Referências:
            - BR-[DOMAIN]-[XXX]: [Description]
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()
        # Test implementation
```

---

**Data:** 13 de novembro de 2025

**Versão:** 1.0

**Status:** [ATIVO]
