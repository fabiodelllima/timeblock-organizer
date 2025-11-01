# Cenários: Timer

## TC-TM-001: Ciclo Completo

**Given:** Event planejado  
**When:** start → pause → resume → stop  
**Then:** TimeLog correto, elapsed acumulado

## TC-TM-002: Apenas 1 Timer Ativo

**Given:** Timer já rodando  
**When:** Tentar iniciar outro  
**Then:** TimerAlreadyRunningError

## TC-TM-003: Transição Inválida

**Given:** Timer IDLE  
**When:** pause()  
**Then:** InvalidStateError
