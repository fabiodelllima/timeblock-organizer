# Cenários: Habit Generation

## TC-HG-001: Geração Diária

**Given:** Habit com RRULE "FREQ=DAILY"  
**When:** generate_instances(30 dias)  
**Then:** 30 instâncias criadas

## TC-HG-002: Geração Semanal

**Given:** Habit "FREQ=WEEKLY;BYDAY=MO,WE,FR"  
**When:** generate_instances(4 semanas)  
**Then:** 12 instâncias (3/semana × 4)

## TC-HG-003: RRULE Inválido

**Given:** RRULE "INVALID"  
**When:** create_habit()  
**Then:** ValueError raised
