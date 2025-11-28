# Event Reordering Test Scenarios

## TC-001: Conflito Simples

**Given:** 2 eventos sobrepostos, prioridades diferentes  
**When:** Executar reordering  
**Then:** Evento menor prioridade movido

## TC-002: Cascata

**Given:** 3+ eventos sobrepostos  
**When:** Resolver primeiro conflito  
**Then:** Resolver conflitos subsequentes

## TC-003: Hard Conflict

**Given:** 2 eventos prioridade 5  
**When:** Detectar conflito  
**Then:** Marcar como manual
