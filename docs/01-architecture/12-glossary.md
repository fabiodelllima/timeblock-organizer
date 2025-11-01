# Glossário

## Termos Fundamentais

### TimeBlock

**Definição:** Bloco de tempo alocado para uma atividade específica no calendário.

**Contexto:** Unidade básica de organização temporal do sistema.

**Não confundir com:** Event (que pode ocupar múltiplos TimeBlocks).

**Exemplo:** "Das 14:00 às 15:30 - Reunião de Sprint"

---

### Habit

**Definição:** Template ou blueprint para atividades recorrentes que o usuário deseja cultivar.

**Contexto:** Define o "o quê" e "quando" sem especificar data concreta.

**Não confundir com:** HabitInstance (materialização em data específica).

**Atributos:**

- `name`: Nome do hábito
- `default_duration`: Duração padrão
- `recurrence_rule`: Regra de recorrência (RRULE)
- `priority`: Nível de prioridade (1-5)

**Exemplo:** "Meditar por 15 minutos toda manhã às 7h"

---

### HabitInstance

**Definição:** Ocorrência específica e concreta de um Habit em data/hora determinada.

**Contexto:** Materialização de um Habit template no calendário real.

**Não confundir com:** Habit (que é o template).

**Atributos:**

- `habit_id`: Referência ao Habit pai
- `scheduled_date`: Data/hora planejada
- `actual_start_date`: Data/hora real de início
- `status`: Estado atual (planned, in_progress, completed, skipped)
- `duration`: Duração efetiva

**Estados possíveis:**

- `planned`: Agendado mas não iniciado
- `in_progress`: Execução em andamento
- `completed`: Concluído com sucesso
- `skipped`: Não realizado conscientemente
- `overdue`: Passou do prazo sem conclusão

**Exemplo:** "Meditação em 28/10/2025 às 07:00 (status: completed)"

---

### Event

**Definição:** Atividade agendada com início e fim definidos no calendário.

**Contexto:** Termo genérico que engloba Tasks, HabitInstances e outros compromissos.

**Tipos de Event:**

- Task: Atividade específica a realizar
- HabitInstance: Ocorrência de hábito recorrente
- Appointment: Compromisso fixo

**Exemplo:** "Reunião das 14h às 15h"

---

### Task

**Definição:** Atividade específica a ser realizada, com ou sem horário fixo.

**Contexto:** Pode ter deadline mas não necessariamente horário rígido.

**Atributos:**

- `title`: Título da tarefa
- `description`: Descrição detalhada
- `deadline`: Prazo final (opcional)
- `priority`: Nível de prioridade
- `status`: Estado atual
- `estimated_duration`: Duração estimada

**Exemplo:** "Finalizar relatório até sexta-feira"

---

### Routine

**Definição:** Conjunto ordenado de Habits que formam uma sequência lógica.

**Contexto:** Agrupa múltiplos Habits que geralmente acontecem em sequência.

**Exemplo:** "Rotina matinal: Acordar → Meditar → Exercícios → Café da manhã"

---

### Event Reordering

**Definição:** Algoritmo core que reorganiza eventos automaticamente para resolver conflitos temporais.

**Contexto:** Feature principal do TimeBlock. Detecta sobreposições e propõe mudanças respeitando prioridades.

**Funcionamento:**

1. Detecta conflitos temporais
2. Gera propostas de mudança
3. Valida contra constraints
4. Aplica mudanças aceitas

**Preserva:**

- Prioridades dos eventos
- Durações totais
- Constraints de negócio
- Histórico de mudanças

**Exemplo:** "Café das 9:30-10:00 conflita com Reunião das 9:00-10:00 (prioridade 5). Proposta: mover Café para 10:30-11:00"

---

### ProposedChange

**Definição:** Sugestão de mudança para resolver conflito de agendamento.

**Contexto:** Gerado pelo EventReorderingService e aguarda aprovação do usuário.

**Atributos:**

- `event_id`: ID do evento a mover
- `current_start`: Horário atual de início
- `current_end`: Horário atual de fim
- `proposed_start`: Horário proposto de início
- `proposed_end`: Horário proposto de fim
- `reason`: Motivo da mudança
- `status`: pending, accepted, rejected

**Exemplo:**

```python
ProposedChange(
    event_id=42,
    current_start="09:30",
    current_end="10:00",
    proposed_start="10:30",
    proposed_end="11:00",
    reason="Conflito com Reunião (prioridade maior)"
)
```

---

### Timer

**Definição:** Funcionalidade para tracking de tempo real em atividades.

**Contexto:** Permite medir duração efetiva vs planejada.

**Estados:**

- `idle`: Não iniciado
- `running`: Contagem ativa
- `paused`: Pausado temporariamente
- `completed`: Finalizado

**Comandos:**

- `start`: Inicia contagem
- `pause`: Pausa contagem
- `resume`: Retoma contagem
- `stop`: Finaliza e registra

**Exemplo:** "Timer: 00:12:34 (running) - Meditação"

---

### Resource-first CLI

**Definição:** Paradigma de design onde comandos CLI começam com o recurso, não a ação.

**Contexto:** Decisão arquitetural para melhor UX e descoberta de comandos.

**Formato:** `timeblock <resource> <action> [options]`

**Exemplo correto:** `timeblock habit add "Meditar"`
**Exemplo incorreto:** `timeblock add habit "Meditar"`

**Benefícios:**

- Agrupa comandos relacionados
- Facilita descoberta (tab completion)
- Consistência semântica

---

### Conflict

**Definição:** Situação onde dois ou mais eventos ocupam o mesmo período temporal.

**Contexto:** Detectado pelo EventReorderingService como sobreposição de timestamps.

**Tipos:**

- **Hard Conflict**: Sobreposição total ou parcial de horários fixos
- **Soft Conflict**: Eventos flexíveis competindo pelo mesmo slot

**Resolução:** Event Reordering propõe mudanças baseadas em prioridades

---

### Priority

**Definição:** Nível de importância de um evento (escala 1-5).

**Contexto:** Usado pelo Event Reordering para decidir qual evento mover em conflitos.

**Escala:**

- `1`: Baixa (pode ser movido facilmente)
- `2`: Média-baixa
- `3`: Média (padrão)
- `4`: Média-alta
- `5`: Alta (fixo, não deve ser movido)

---

### RRULE

**Definição:** Formato padrão (RFC 5545) para expressar regras de recorrência.

**Contexto:** Usado para definir quando Habits devem gerar HabitInstances.

**Exemplos:**

- Diário: `FREQ=DAILY`
- Semanal (seg/qua/sex): `FREQ=WEEKLY;BYDAY=MO,WE,FR`
- Mensal (dia 15): `FREQ=MONTHLY;BYMONTHDAY=15`

---

## Conceitos Descartados

### HabitAtom

**Status:** DEPRECATED - Não implementado

**Razão original:** Representar unidade atômica indivisível de hábito.

**Decisão:** Mantemos apenas Habit e HabitInstance como termos oficiais.

**Ver:** [ADR-004](../03-decisions/004-habit-vs-instance.md)

---

## Abreviações

| Sigla | Significado                  |
| ----- | ---------------------------- |
| BR    | Business Rule                |
| ADR   | Architecture Decision Record |
| TUI   | Terminal User Interface      |
| CLI   | Command Line Interface       |
| CRUD  | Create, Read, Update, Delete |
| UTC   | Coordinated Universal Time   |
| RRULE | Recurrence Rule (RFC 5545)   |

---

## Relacionamentos Entre Conceitos

```terminal
Habit (template)
  └─ gera múltiplos → HabitInstance (ocorrências)

Event (conceito geral)
  ├─ Task
  ├─ HabitInstance
  └─ Appointment

Routine
  └─ contém múltiplos → Habit

Conflict
  └─ resolvido por → Event Reordering
      └─ gera → ProposedChange
```
