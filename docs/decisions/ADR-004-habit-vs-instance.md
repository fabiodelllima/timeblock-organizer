# ADR-004: Separação Habit vs HabitInstance

- **Status:** Accepted
- **Data:** 2025-09-20

## Contextoo

Sistema precisa representar tanto templates de hábitos recorrentes quanto suas ocorrências específicas.

Requisitos:

- Template reutilizável (ex: "Meditar 15min")
- Ocorrências individuais com status próprio
- Histórico de execuções
- Flexibility para override por instância

## Decisão

Separar em duas entidades:

- **Habit**: Template imutável
- **HabitInstance**: Ocorrência mutável com data específica

## Alternativas

### Entidade Única

**Prós:** Simples, menos joins
**Contras:** Mistura template com estado, dificulta histórico

### Event Sourcing

**Prós:** Auditoria completa
**Contras:** Complexidade excessiva para o caso

### HabitAtom (tentativa inicial)

**Prós:** Nome diferente
**Contras:** Sem valor semântico, confuso

## Consequências

### Positivas

- Template isolado (modificar não afeta histórico)
- Cada instância tem status independente
- Queries simples: "todas instâncias de Habit X"
- Override de duração/horário por instância

### Negativas

- Join necessário para buscar instância com template
- Duplicação de campos (duration pode estar em ambos)

### Neutras

- Pattern bem estabelecido (Template Method)

## Validação

- Zero bugs de estado compartilhado
- Modificar Habit não quebra histórico
- Queries de "completion rate" simples

## Implementação

```python
class Habit(SQLModel, table=True):
    id: int
    name: str
    default_duration: int
    recurrence_rule: str
    priority: int = 3

class HabitInstance(SQLModel, table=True):
    id: int
    habit_id: int  # FK
    scheduled_date: datetime
    actual_start_date: Optional[datetime]
    status: HabitStatus
    duration: Optional[int]  # Override
```
