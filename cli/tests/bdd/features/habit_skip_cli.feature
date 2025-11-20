# language: pt
Funcionalidade: Comando CLI Habit Skip (BR-CLI-HABIT-SKIP-001)

  Como usuário do TimeBlock
  Quero usar timeblock habit skip no terminal
  Para marcar hábitos como skipped rapidamente

  Contexto:
    Dado que existe uma rotina ativa "Rotina Matinal"
    E existe um habit "Academia" com ID 1
    E existe uma HabitInstance com ID 42 para hoje

  Cenário: Skip com categoria via flag
    Quando usuário executa comando "habit skip 42 --category WORK --note 'Reunião urgente'"
    Então comando deve ter sucesso
    E output deve conter "skipped"
    E HabitInstance 42 deve ter status NOT_DONE
    E HabitInstance 42 deve ter skip_reason WORK
    E HabitInstance 42 deve ter skip_note "Reunião urgente"

  Cenário: Skip com categoria sem nota
    Quando usuário executa comando "habit skip 42 --category FAMILY"
    Então comando deve ter sucesso
    E HabitInstance 42 deve ter skip_reason FAMILY
    E HabitInstance 42 deve ter skip_note NULL

  Cenário: Erro ao skip de instance inexistente
    Quando usuário executa comando "habit skip 999 --category HEALTH"
    Então comando deve falhar
    E output deve conter "não encontrada"

  Cenário: Erro ao usar categoria inválida
    Quando usuário executa comando "habit skip 42 --category INVALID"
    Então comando deve falhar
    E output deve conter "inválida"
