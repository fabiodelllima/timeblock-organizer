# BDD Tests - Behavior Driven Development

## Estrutura

```terminal
tests/bdd/
├── features/           # Arquivos .feature (Gherkin PT-BR)
├── step_defs/          # Implementação dos steps
└── README.md           # Este arquivo
```

## Status

**IMPORTANTE:** Estrutura criada mas **NÃO IMPLEMENTADA** ainda.

Esta estrutura serve como:

1. Preparação para implementação futura (Sprint 2+)
2. Demonstração de intenção arquitetural
3. Placeholder para testes E2E em linguagem natural

## Implementação Futura

### Sprint 2-3: Implementar BDD

- Instalar pytest-bdd ou behave
- Implementar step definitions
- Integrar com fixtures existentes
- Rodar em CI/CD

### Exemplo de Uso Futuro

```python
# step_defs/habit_steps.py
from pytest_bdd import scenarios, given, when, then

scenarios('../features/habit_creation.feature')

@given('que existe uma rotina chamada "Matinal"')
def rotina_matinal(test_routine):
    return test_routine

@when('eu crio um hábito com os seguintes dados:')
def criar_habito(context):
    # Implementar
    pass
```

## Referências

- ADR-020: BDD Implementation (a ser criado)
- Pytest-BDD: <https://pytest-bdd.readthedocs.io/>
- Gherkin Language: <https://cucumber.io/docs/gherkin/>
