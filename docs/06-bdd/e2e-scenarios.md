# BDD Scenarios - End-to-End Tests

- **Última Atualização:** 27 de novembro de 2025
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
      | parâmetro  | valor      |
      | --title    | Meditação  |
      | --start    | 06:00      |
      | --end      | 06:20      |
      | --repeat   | EVERYDAY   |
      | --generate | 1          |
    Then sistema confirma "Hábito criado com sucesso"
    And hábito "Meditação" é salvo no banco de dados
    And sistema gera ~31 instâncias (um mês)
    And confirma "instâncias geradas"

    When eu executo comando "list --day 0"
    Then vejo hábito "Meditação" na lista
    And horário mostrado é "06:00"
    And status é "PLANNED"

    When eu executo comando "habit complete 1"
    Then sistema confirma "Hábito marcado como completo"

    When eu executo comando "list --day 0" novamente
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
assert "instância" in result.output.lower(), "Deve confirmar geração de instâncias"
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
      | --title    | Exercício |
      | --start    | 09:00     |
      | --end      | 10:00     |
      | --repeat   | EVERYDAY  |
      | --generate | 1         |
    Then hábito é criado com sucesso
    And instâncias são geradas

    When eu crio hábito "Leitura" com:
      | --title    | Leitura  |
      | --start    | 09:30    |
      | --end      | 10:30    |
      | --repeat   | EVERYDAY |
      | --generate | 1        |
    Then hábito é criado com sucesso
    And instâncias são geradas

    When eu executo "habit edit 1 --start 09:00 --end 10:00"
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

## 6. REFERÊNCIA DE API

### 6.1 Comandos Utilizados nos Scenarios

| Comando          | Descrição                        | Exemplo                                                                             |
| ---------------- | -------------------------------- | ----------------------------------------------------------------------------------- |
| `habit create`   | Cria hábito com geração opcional | `habit create --title "X" --start 06:00 --end 07:00 --repeat EVERYDAY --generate 1` |
| `habit edit`     | Edita instância específica       | `habit edit 42 --start 18:00`                                                       |
| `habit complete` | Marca instância como completa    | `habit complete 42`                                                                 |
| `habit skip`     | Marca instância como pulada      | `habit skip 42 --reason "viagem"`                                                   |
| `list --day 0`   | Lista eventos de hoje            | `list --day 0`                                                                      |
| `list --week 0`  | Lista eventos desta semana       | `list --week 0`                                                                     |
| `list --week +N` | Lista próximas N semanas         | `list --week +4`                                                                    |

### 6.2 APIs Depreciadas

> **Nota:** As seguintes APIs estão depreciadas e serão removidas na v2.0.0.
> Ver `docs/10-meta/deprecation-notices.md` para detalhes de migração.

| Depreciado                                         | Substituição                    |
| -------------------------------------------------- | ------------------------------- |
| `schedule generate HABIT_ID --from DATE --to DATE` | `habit create ... --generate N` |
| `list today`                                       | `list --day 0`                  |
| `list week`                                        | `list --week 0`                 |
| `habit adjust`                                     | `habit edit`                    |

---

**Data:** 27 de novembro de 2025

**Versão:** 1.1

**Status:** [ATIVO]
