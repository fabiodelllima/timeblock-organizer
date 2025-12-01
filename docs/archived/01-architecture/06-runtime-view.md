# 6. Visão de Runtime

## Cenário: Adicionar Hábito

1. User: `timeblock habit add "Meditar"`
2. CLI valida args
3. HabitService cria Habit
4. Gera HabitInstances (30 dias)
5. Detecta conflitos
6. Retorna resultado

## Cenário: Reordering

1. User: `timeblock reschedule --preview`
2. EventReorderingService detecta conflitos
3. Gera propostas
4. Display preview
5. User aceita
6. Aplica mudanças
