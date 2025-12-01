# Algoritmos de Agendamento

## Problema: Interval Scheduling

**Definição:** Dado conjunto de tarefas com horários início/fim, selecionar subconjunto máximo não-conflitante.

**Classificação:** NP-completo para weighted interval scheduling

**Relevância TimeBlock:** Event Reordering usa variante com prioridades.

## Algoritmo Greedy

**Estratégia:** Ordenar por horário fim, selecionar primeiro disponível.

**Complexidade:** O(n log n)

**Implementação TimeBlock:**

```python
def simple_cascade_reorder(events, delay_minutes):
    """Shift todos eventos subsequentes pelo delay."""
    sorted_events = sorted(events, key=lambda e: e.start_time)

    for event in sorted_events:
        event.start_time += delay_minutes
        event.end_time += delay_minutes

    return sorted_events
```

## Weighted Interval Scheduling

**Problema:** Maximizar valor total considerando pesos/prioridades.

**Solução:** Dynamic programming O(n²)

**TimeBlock v1.1:** Usa abordagem simplificada com 4 níveis prioridade.

## Referências

CORMEN, T. H. et al. **Introduction to Algorithms**. 3. ed. Cambridge: MIT Press, 2009. Chapter 16: Greedy Algorithms. ISBN 978-0262033848.

KLEINBERG, J.; TARDOS, É. **Algorithm Design**. Boston: Addison-Wesley, 2005. Chapter 4: Greedy Algorithms. ISBN 978-0321295354.

WIKIPEDIA. **Interval scheduling**. Disponível em: <https://en.wikipedia.org/wiki/Interval_scheduling>. Acesso em: 31 out. 2025.
