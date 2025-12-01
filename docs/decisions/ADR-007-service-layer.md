# ADR-007: Service Layer Pattern

- **Status:** Accepted
- **Data:** 2025-09-18

## Contextoo

Commands acessando models diretamente cria acoplamento e dificulta:

- Validação de regras de negócio
- Testes unitários
- Reutilização de lógica

## Decisão

Camada de Services entre Commands e Models.

**Estrutura:**

```terminal
Commands (CLI) → Services → Models (DB)
```

## Alternativas

### Repository Pattern

**Prós:** Abstrai DB completamente
**Contras:** Overhead para SQLite simples

### Commands diretos em Models

**Prós:** Menos código
**Contras:** Lógica dispersa, difícil testar

### Domain Services (DDD)

**Prós:** Separação clara
**Contras:** Over-engineering para o escopo

## Consequências

### Positivas

- Business logic centralizada
- Commands enxutos
- Testes unitários isolados
- Transações controladas

### Negativas

- Camada adicional
- Boilerplate moderado

### Neutras

- Pattern estabelecido

## Validação

- 100% cobertura em services
- Commands < 30 linhas
- Zero lógica de negócio em commands

## Implementação

```python
class HabitService:
    def __init__(self, session: Session):
        self.session = session

    def create_instances(self, habit: Habit) -> List[HabitInstance]:
        # Business logic aqui
        ...
```
