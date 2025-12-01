# BR003: Reordering Logic Rules

## Regra

Event Reordering aplica mudanças validadas mantendo integridade do calendário.

## Fluxo

```terminal
Detectar → Propor → Validar → Preview → Aplicar
```

## Aplicação

```python
def apply_reordering(
    events: List[Event],
    proposals: List[ProposedChange]
) -> ReorderingResult:
    moved = []
    failed = []

    for proposal in proposals:
        try:
            event = get_event(proposal.event_id)

            # Backup
            event.original_start = event.start
            event.original_end = event.end

            # Aplicar
            event.start = proposal.proposed_start
            event.end = proposal.proposed_end
            event.was_reordered = True
            event.reorder_reason = proposal.reason

            save(event)
            moved.append(event)

        except Exception as e:
            failed.append((proposal, str(e)))

    return ReorderingResult(moved, failed)
```

## Rollback

```python
def rollback_reordering(event: Event) -> None:
    if event.was_reordered and event.original_start:
        event.start = event.original_start
        event.end = event.original_end
        event.was_reordered = False
        event.reorder_reason = None
        save(event)
```

## Constraints

**MUST:**

- Transação atômica (all or nothing)
- Manter histórico
- Validar antes de aplicar

**MUST NOT:**

- Aplicar sem preview aceito
- Perder estado original
- Silenciar erros

## Cascata

Máximo 3 iterações:

```python
MAX_ITERATIONS = 3

def resolve_with_cascade(events: List[Event]) -> List[ProposedChange]:
    all_proposals = []
    iteration = 0

    while iteration < MAX_ITERATIONS:
        conflicts = detect_conflicts(events)
        if not conflicts:
            break

        proposals = generate_proposals(conflicts)
        all_proposals.extend(proposals)

        # Simular
        events = simulate_apply(proposals, events)
        iteration += 1

    if iteration == MAX_ITERATIONS:
        raise CascadeTooComplexError()

    return all_proposals
```

## Histórico

```python
@dataclass
class ReorderingHistory:
    timestamp: datetime
    user_id: int
    events_moved: List[int]
    proposals: List[ProposedChange]
    success: bool
    reason: Optional[str]
```

## Métricas

```python
@dataclass
class ReorderingMetrics:
    total_proposals: int
    accepted: int
    rejected: int
    cascade_iterations: int
    execution_time_ms: float
```

## Validação Pré-Aplicação

```python
def validate_before_apply(proposals: List[ProposedChange]) -> bool:
    # Sem conflitos novos
    simulated = simulate_apply(proposals, events)
    if detect_conflicts(simulated):
        return False

    # Constraints OK
    if not all(check_constraints(p) for p in proposals):
        return False

    return True
```

## Testes

```python
def test_atomic_transaction():
    # Se 1 falha, nenhum aplica
    proposals = [valid_proposal, invalid_proposal]
    result = apply_reordering(events, proposals)
    assert result.moved == []

def test_rollback():
    event = move_event(event, new_time)
    rollback_reordering(event)
    assert event.start == original_start
```
