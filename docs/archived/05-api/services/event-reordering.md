# EventReorderingService

## Responsabilidade

Orquestra detecção e resolução de conflitos temporais.

## API

```python
class EventReorderingService:
    def __init__(self, session: Session):
        self.session = session

    def detect_and_propose(
        self,
        events: List[Event],
        time_window: Optional[TimeWindow] = None
    ) -> ReorderingProposal:
        """Detecta conflitos e gera propostas."""

    def apply_proposal(
        self,
        proposal: ReorderingProposal
    ) -> ReorderingResult:
        """Aplica mudanças validadas."""

    def rollback(self, event_ids: List[int]) -> None:
        """Reverte reordenação."""
```

## Exemplo

```python
service = EventReorderingService(session)

# Detectar e propor
proposal = service.detect_and_propose(events)

# Preview
display_proposal(proposal)

# Aplicar se aprovado
if user_accepts():
    result = service.apply_proposal(proposal)
    print(f"Movidos: {len(result.moved)}")
```

## Dependências

- ConflictDetector
- ProposalGenerator
- ConstraintValidator
