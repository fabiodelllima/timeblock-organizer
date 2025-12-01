# Event Reordering - Especificação Algoritmica

## Visão Geral

Algoritmo core do TimeBlock que reorganiza eventos automaticamente para resolver conflitos temporais mantendo prioridades e constraints.

## Entrada

```python
@dataclass
class ReorderingInput:
    events: List[Event]          # Eventos no período
    time_window: TimeWindow       # Janela de análise
    constraints: List[Constraint] # Restrições
    preferences: UserPreferences  # Preferências
```

## Algoritmo

### Fase 1: Detecção de Conflitos

```python
def detect_conflicts(events: List[Event]) -> List[Conflict]:
    """
    Identifica sobreposições temporais.
    Complexidade: O(n²)
    """
    conflicts = []
    for i, event1 in enumerate(events):
        for event2 in events[i+1:]:
            if overlaps(event1, event2):
                conflicts.append(Conflict(event1, event2))
    return conflicts

def overlaps(e1: Event, e2: Event) -> bool:
    return (e1.start < e2.end) and (e2.start < e1.end)
```

### Fase 2: Geração de Propostas

```python
def generate_proposals(conflicts: List[Conflict]) -> List[ProposedChange]:
    """
    Gera sugestões priorizando manutenção de eventos de alta prioridade.
    """
    proposals = []
    for conflict in conflicts:
        # Determinar evento a mover (menor prioridade)
        to_move, anchor = (
            (conflict.event1, conflict.event2)
            if conflict.event1.priority < conflict.event2.priority
            else (conflict.event2, conflict.event1)
        )

        # Encontrar próximo slot livre
        new_slot = find_next_free_slot(to_move, anchor, all_events)

        proposals.append(ProposedChange(
            event_id=to_move.id,
            current_start=to_move.start,
            current_end=to_move.end,
            proposed_start=new_slot.start,
            proposed_end=new_slot.end,
            reason=f"Conflito com {anchor.title} (prioridade {anchor.priority})"
        ))

    return proposals
```

### Fase 3: Busca de Slot

```python
def find_next_free_slot(
    event: Event,
    after: Event,
    all_events: List[Event]
) -> TimeSlot:
    """
    Busca próximo horário livre após anchor event.
    """
    candidate_start = after.end
    duration = event.duration

    while True:
        candidate_end = candidate_start + duration
        slot = TimeSlot(candidate_start, candidate_end)

        # Verificar se slot está livre
        if not any(overlaps_slot(e, slot) for e in all_events):
            return slot

        # Avançar para depois do próximo conflito
        blocking = next(e for e in all_events if overlaps_slot(e, slot))
        candidate_start = blocking.end

        # Limite: não avançar mais de 7 dias
        if (candidate_start - event.start).days > 7:
            raise NoSlotFoundError("Sem slot disponível em 7 dias")
```

### Fase 4: Validação

```python
def validate_proposals(
    proposals: List[ProposedChange],
    constraints: List[Constraint]
) -> List[ProposedChange]:
    """
    Valida propostas contra constraints de negócio.
    """
    valid = []
    for proposal in proposals:
        if all(check_constraint(proposal, c) for c in constraints):
            valid.append(proposal)
        else:
            logger.warning(f"Proposta {proposal.id} violou constraint")

    return valid
```

### Fase 5: Aplicação

```python
def apply_proposals(
    events: List[Event],
    proposals: List[ProposedChange]
) -> List[Event]:
    """
    Aplica mudanças aceitas mantendo histórico.
    """
    event_map = {e.id: e for e in events}

    for proposal in proposals:
        event = event_map[proposal.event_id]

        # Guardar estado original
        event.original_start = event.start
        event.original_end = event.end

        # Aplicar mudança
        event.start = proposal.proposed_start
        event.end = proposal.proposed_end
        event.was_reordered = True
        event.reorder_reason = proposal.reason

    return list(event_map.values())
```

## Invariantes

**MUST sempre garantir:**

1. **Preservação de Duração:** `duration(after) == duration(before)`
2. **Respeito a Prioridades:** Eventos prioridade 5 nunca movem
3. **Mínima Disrupção:** Mover menor número possível
4. **Constraints Válidos:** Nenhuma regra violada
5. **Histórico Preservado:** Estado original sempre recuperável

## Casos Especiais

### Conflito em Cascata

```python
def handle_cascade(initial_proposals: List[ProposedChange]) -> List[ProposedChange]:
    """
    Quando mover evento cria novo conflito.
    Máximo 3 iterações.
    """
    all_proposals = initial_proposals
    iteration = 0

    while iteration < 3:
        # Aplicar propostas temporariamente
        temp_events = simulate_apply(all_proposals)

        # Detectar novos conflitos
        new_conflicts = detect_conflicts(temp_events)
        if not new_conflicts:
            break

        # Gerar novas propostas
        new_proposals = generate_proposals(new_conflicts)
        all_proposals.extend(new_proposals)
        iteration += 1

    if iteration == 3:
        raise RequiresManualInterventionError("Cascata muito complexa")

    return all_proposals
```

### Eventos Fixos (Anchored)

```python
# Eventos com priority=5 são fixos
if event.priority == 5:
    event.can_be_moved = False
```

### Janela Insuficiente

```python
if not enough_space_in_window(events, time_window):
    suggestions = [
        "Estender janela de tempo",
        "Reduzir durações de eventos flexíveis",
        "Mover alguns eventos para outro dia"
    ]
    raise InsufficientSpaceError(suggestions)
```

## Métricas

```python
@dataclass
class ReorderingMetrics:
    conflicts_detected: int
    proposals_generated: int
    proposals_accepted: int
    proposals_rejected: int
    execution_time_ms: float

    @property
    def resolution_rate(self) -> float:
        return self.proposals_accepted / self.conflicts_detected

    @property
    def acceptance_rate(self) -> float:
        return self.proposals_accepted / self.proposals_generated
```

**Metas:**

- Resolution rate > 85%
- Acceptance rate > 70%
- Execution time < 100ms (50 eventos)

## Exemplo Completo

```python
# Input
events = [
    Event(id=1, title="Reunião", start="09:00", end="10:00", priority=5),
    Event(id=2, title="Café", start="09:30", end="10:00", priority=3),
    Event(id=3, title="Email", start="10:00", end="10:30", priority=2)
]

# Fase 1: Detectar conflitos
conflicts = detect_conflicts(events)
# [Conflict(event1=Reunião, event2=Café)]

# Fase 2: Gerar propostas
proposals = generate_proposals(conflicts)
# [ProposedChange(
#     event_id=2,
#     current_start="09:30",
#     proposed_start="10:30",
#     reason="Conflito com Reunião (prioridade 5)"
# )]

# Fase 3: Validar
valid_proposals = validate_proposals(proposals, constraints)
# [ProposedChange(...)]  # OK

# Fase 4: Apresentar preview ao usuário
display_preview(valid_proposals)

# Fase 5: Aplicar (após aprovação)
reordered = apply_proposals(events, valid_proposals)
# [
#   Event(id=1, start="09:00", end="10:00"),  # Mantido
#   Event(id=2, start="10:30", end="11:00"),  # Movido
#   Event(id=3, start="10:00", end="10:30")   # Mantido
# ]
```

## Testes

**Casos críticos:**

- 2 eventos conflitantes
- 3+ eventos sobrepostos
- Cascata de conflitos
- Todos eventos priority=5
- Janela insuficiente
- Evento de 8h+ (dia inteiro)

## Limitações Conhecidas

1. Algoritmo guloso (não global optimal)
2. Não considera preferências horárias (manhã vs tarde)
3. Não agrupa eventos relacionados automaticamente
4. Limite hard de 3 iterações cascata

## Melhorias Futuras

- Considerar energia do usuário por horário
- Machine learning para preferências
- Otimização global (backtracking)
- Sugestão de compressão de durações
