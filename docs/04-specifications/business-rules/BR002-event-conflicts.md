# BR002: Event Conflict Resolution Rules

## Regra

Sistema detecta e resolve conflitos temporais automaticamente baseado em prioridades.

## Definição de Conflito

```python
def is_conflict(e1: Event, e2: Event) -> bool:
    return (e1.start < e2.end) and (e2.start < e1.end)
```

## Prioridades

| Valor | Categoria   | Comportamento         |
| ----- | ----------- | --------------------- |
| 5     | Alta        | Fixo, nunca move      |
| 4     | Média-alta  | Move só se necessário |
| 3     | Média       | Padrão, flexível      |
| 2     | Média-baixa | Move facilmente       |
| 1     | Baixa       | Move primeiro         |

## Resolução

### Algoritmo

1. Identificar conflito
2. Determinar evento de menor prioridade
3. Buscar próximo slot livre
4. Gerar proposta
5. Validar constraints
6. Apresentar preview
7. Aplicar se aceito

### Empate de Prioridade

```python
if e1.priority == e2.priority:
    # Move o mais recente (último criado)
    to_move = e1 if e1.created_at > e2.created_at else e2
```

## Constraints

**MUST:**

- Preservar duração original
- Respeitar prioridade 5 (nunca mover)
- Manter dentro de 7 dias

**SHOULD:**

- Minimizar deslocamento temporal
- Preferir slots adjacentes

**MUST NOT:**

- Criar novos conflitos
- Violar janela de trabalho (ex: 08:00-18:00)
- Mover eventos passados

## Casos

### Conflito Simples

```terminal
09:00-10:00 Reunião (P5)
09:30-10:00 Café (P3)

→ Mover Café para 10:00-10:30
```

### Conflito em Cascata

```terminal
09:00-10:00 A (P5)
09:30-10:30 B (P3)
10:00-11:00 C (P3)

→ B para 10:30-11:30, C para 11:30-12:30
```

### Hard Conflict (Manual)

```terminal
09:00-10:00 A (P5)
09:00-10:00 B (P5)

→ Requer intervenção manual
```

## Validações

```python
def validate_resolution(proposal: ProposedChange) -> bool:
    # Não criar novo conflito
    if creates_new_conflict(proposal):
        return False

    # Dentro de janela
    if proposal.proposed_start.hour < 8 or proposal.proposed_end.hour > 18:
        return False

    # Máximo 7 dias
    if (proposal.proposed_start - proposal.current_start).days > 7:
        return False

    return True
```

## Métricas

- Taxa de resolução automática: > 85%
- Taxa de aceitação: > 70%
- Conflitos manuais: < 15%

## Testes

```python
def test_priority_resolution():
    high = Event(priority=5, start="09:00", end="10:00")
    low = Event(priority=2, start="09:30", end="10:00")

    resolution = resolve_conflict(high, low)
    assert resolution.event_to_move == low

def test_tie_breaks_by_created_at():
    e1 = Event(priority=3, created_at="2025-01-01")
    e2 = Event(priority=3, created_at="2025-01-02")

    resolution = resolve_conflict(e1, e2)
    assert resolution.event_to_move == e2
```
