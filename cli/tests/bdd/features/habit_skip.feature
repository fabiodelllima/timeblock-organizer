# language: pt
Funcionalidade: Skip de Habit com Categorização (BR-HABIT-SKIP-001)

  Como usuário do TimeBlock
  Quero marcar hábitos como skipped com categoria
  Para rastrear razões de interrupção e identificar padrões

  Contexto:
    Dado que existe uma rotina "Rotina Matinal"
    E existe um habit "Academia" agendado para hoje às 07:00-08:30
    E existe uma HabitInstance com status "PENDING"

  # SCENARIO 1: Skip com categoria HEALTH e nota
  Cenário: Skip com categoria HEALTH
    Quando usuário marca skip com categoria "HEALTH" e nota "Gripe, febre 38°C"
    Então o status deve ser "NOT_DONE"
    E o substatus deve ser "SKIPPED_JUSTIFIED"
    E o skip_reason deve ser "saude"
    E o skip_note deve ser "Gripe, febre 38°C"
    E done_substatus deve ser NULL
    E completion_percentage deve ser NULL

  # SCENARIO 2: Skip com categoria WORK sem nota
  Cenário: Skip com categoria WORK sem nota
    Quando usuário marca skip com categoria "WORK" sem nota
    Então o status deve ser "NOT_DONE"
    E o substatus deve ser "SKIPPED_JUSTIFIED"
    E o skip_reason deve ser "trabalho"
    E o skip_note deve ser NULL

  # SCENARIO 7: Erro - HabitInstance não existe
  Cenário: Erro ao skip de instância inexistente
    Quando usuário tenta skip de HabitInstance com ID 99999
    Então o sistema deve retornar erro "HabitInstance 99999 not found"

  # SCENARIO 8: Erro - Nota muito longa (>500 chars)
  Cenário: Erro ao tentar skip com nota muito longa
    Dado que skip_note tem 501 caracteres
    Quando usuário tenta skip com categoria "HEALTH" e essa nota
    Então o sistema deve retornar erro "Skip note must be <= 500 characters"
