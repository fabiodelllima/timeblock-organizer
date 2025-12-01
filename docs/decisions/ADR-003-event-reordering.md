# ADR-003: Algoritmo de Event Reordering Baseado em Prioridades

- **Status**: Accepted
- **Data**: 2025-10-15

## Contextoo

TimeBlock precisa resolver conflitos de agenda automaticamente quando:

- Múltiplos eventos ocupam o mesmo horário
- HabitInstances conflitam com compromissos
- Usuário adiciona novo evento em slot ocupado

Requisitos:

- Mínima disrupção do calendário
- Respeitar prioridades do usuário
- Preservar durações dos eventos
- Permitir preview antes de aplicar

## Decisão

Implementamos algoritmo de reordenação baseado em **prioridades numéricas (1-5)** onde eventos de menor prioridade são movidos para resolver conflitos.

Fluxo:

1. Detectar conflitos temporais (O(n²))
2. Gerar propostas movendo evento de menor prioridade
3. Buscar próximo slot livre
4. Validar contra constraints
5. Apresentar preview para aprovação

## Alternativas Consideradas

### Resolução Manual

**Prós:**

- Controle total do usuário
- Sem decisões erradas

**Contras:**

- Carga cognitiva alta
- Não escala com muitos eventos
- Feature core perdida

### FIFO (First In First Out)

**Prós:**

- Simples de implementar
- Previsível

**Contras:**

- Ignora importância relativa
- Pode mover compromissos críticos

### Algoritmo de Scheduling Ótimo (Greedy)

**Prós:**

- Matematicamente ótimo
- Minimiza mudanças globais

**Contras:**

- Complexidade O(n log n) ou pior
- Overkill para uso típico (< 50 eventos/dia)
- Difícil explicar mudanças ao usuário

### Machine Learning

**Prós:**

- Aprende preferências do usuário

**Contras:**

- Requer dados históricos
- Imprevisível
- Overhead computacional

## Consequências

### Positivas

- Lógica simples e explicável
- Performance adequada (< 100ms para 50 eventos)
- Usuário controla via prioridades
- Preview evita surpresas

### Negativas

- Prioridades devem ser mantidas manualmente
- Algoritmo guloso (não considera efeito cascata completo)
- Pode criar novos conflitos em casos complexos

### Neutras

- Limite recursivo de 3 iterações previne loops infinitos
- Eventos com prioridade 5 nunca são movidos

## Validação

Consideramos acertada se:

- Taxa de resolução automática > 85%
- Taxa de aceitação de propostas > 70%
- Tempo de execução < 100ms (50 eventos)
- Zero loops infinitos em produção

## Implementação

Arquivo: `src/timeblock/services/event_reordering_service.py`

Classes principais:

- `EventReorderingService`: Orquestra o processo
- `ProposedChange`: Representa mudança sugerida
- `Conflict`: Representa sobreposição detectada

## Referências

- [RFC 5545 (iCalendar)](https://tools.ietf.org/html/rfc5545)
- [Interval Scheduling Problem](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Discussão sobre cascata](https://github.com/fabiodelllima/timeblock-organizer/issues/42)
