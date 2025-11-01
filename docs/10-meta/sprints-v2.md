# Sprints v2.0 - Event Reordering

**Autor:** Fábio de Lima  
**Data:** Outubro-Novembro 2025

## Sprint 1.1: Models e Database [CONCLUÍDO]
**Duração:** 3h  
**Entregas:**
- ReorderingProposal, ProposedChange, ConflictInfo
- Testes de models

## Sprint 1.2: Conflict Detection [CONCLUÍDO]
**Duração:** 4h  
**Entregas:**
- Algoritmo de detecção de overlaps
- Query de eventos do dia

## Sprint 1.3: Reordering Algorithm [CONCLUÍDO]
**Duração:** 4h  
**Entregas:**
- Simple Cascade implementado
- Shift de eventos subsequentes

## Sprint 1.4: Proposal Generation [COMPLETO]
**Duração:** 3h  
**Status: 100% completo
**Correção:** Renomear original_start/end → current_start/end

## Sprint 2.1: TaskService Integration [CONCLUÍDO]
**Duração:** 3h  
**Entregas:**
- create_task retorna (Task, Proposal)
- Testes de integração

## Sprint 2.2: HabitInstanceService [PENDENTE]
**Duração:** 4h  
**Objetivo:** adjust_instance com reordering

## Sprint 2.3: TimerService [PENDENTE]
**Duração:** 4h  
**Objetivo:** start_timer com detecção

## Sprint 2.4: CLI Preview [PENDENTE]
**Duração:** 2h  
**Objetivo:** Display formatado de proposals

## Sprint 2.5: Integration Tests [PENDENTE]
**Duração:** 3h  
**Objetivo:** Cenários end-to-end

## Sprint 2.6: Documentation [PENDENTE]
**Duração:** 2h  
**Objetivo:** API docs completos
