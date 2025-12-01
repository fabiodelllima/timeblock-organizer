# language: pt
Funcionalidade: Skip de Habit com Justificativa

  Como usuário do TimeBlock
  Quero pular habits quando necessário
  Para manter flexibilidade sem perder rastreamento

  Contexto:
    Dado que existe uma rotina "Rotina Matinal" ativa
    E existe um habit "Academia" agendado para hoje às 07:00

  # BR-HABIT-SKIP-001: Categorização de Skip com Enum
  Cenário: Skip com categoria válida (HEALTH)
    Quando usuário executa "habit skip Academia --reason HEALTH --note 'Consulta médica'"
    Então o habit "Academia" tem status "NOT_DONE"
    E o habit "Academia" tem substatus "SKIPPED_JUSTIFIED"
    E o skip_reason é "saude"
    E o skip_note é "Consulta médica"
    E o streak de "Academia" é quebrado

  Cenário: Skip com todas as 8 categorias
    Quando usuário tenta skip com reason "HEALTH"
    Então o skip_reason deve ser "saude"

    Quando usuário tenta skip com reason "WORK"
    Então o skip_reason deve ser "trabalho"

    Quando usuário tenta skip com reason "FAMILY"
    Então o skip_reason deve ser "familia"

    Quando usuário tenta skip com reason "PERSONAL"
    Então o skip_reason deve ser "pessoal"

    Quando usuário tenta skip com reason "WEATHER"
    Então o skip_reason deve ser "clima"

    Quando usuário tenta skip com reason "FATIGUE"
    Então o skip_reason deve ser "cansaco"

    Quando usuário tenta skip com reason "EMERGENCY"
    Então o skip_reason deve ser "emergencia"

    Quando usuário tenta skip com reason "OTHER"
    Então o skip_reason deve ser "outro"

  Cenário: Skip com categoria inválida
    Quando usuário executa "habit skip Academia --reason INVALID"
    Então o sistema retorna erro "Categoria inválida"
    E o habit "Academia" permanece com status "PENDING"

  # BR-HABIT-SKIP-002: Campos de Skip
  Cenário: Skip note limitado a 200 caracteres
    Dado que skip_note tem 200 caracteres
    Quando usuário executa skip com essa nota
    Então o skip é registrado com sucesso

    Dado que skip_note tem 201 caracteres
    Quando usuário executa skip com essa nota
    Então o sistema retorna erro "skip_note deve ter no máximo 200 caracteres"

  Cenário: Skip note é opcional
    Quando usuário executa "habit skip Academia --reason HEALTH"
    Então o habit é marcado como SKIPPED_JUSTIFIED
    E o skip_reason é "saude"
    E o skip_note é NULL

  Cenário: Skip fields NULL quando não skipped
    Dado que habit "Academia" está com status "DONE"
    Então o skip_reason deve ser NULL
    E o skip_note deve ser NULL

  # BR-HABIT-SKIP-003: Prazo para Justificar Skip
  Cenário: Justificar skip dentro de 24h
    Dado que usuário fez skip sem justificativa às 08:00 do dia 14/11
    E agora são 18:00 do dia 14/11 (10h depois)
    Quando usuário executa "habit skip Academia --add-reason WORK"
    Então o substatus muda de "SKIPPED_UNJUSTIFIED" para "SKIPPED_JUSTIFIED"
    E o skip_reason é "trabalho"

  Cenário: Justificar skip após 24h (prazo expirado)
    Dado que usuário fez skip sem justificativa às 08:00 do dia 14/11
    E agora são 09:00 do dia 15/11 (25h depois)
    Quando usuário executa "habit skip Academia --add-reason WORK"
    Então o sistema retorna erro "Prazo de 24h expirado"
    E o substatus permanece "SKIPPED_UNJUSTIFIED"

  Cenário: Skip sem justificativa mostra deadline
    Quando usuário executa "habit skip Academia --no-reason"
    Então o sistema exibe mensagem:
      """
      [WARN] Skip sem justificativa
             Prazo para justificar: até <data + 24h>
      """
    E o substatus é "SKIPPED_UNJUSTIFIED"

  # BR-HABIT-SKIP-004: CLI Prompt Interativo
  Cenário: Prompt interativo com 9 opções
    Quando usuário executa "habit skip Academia" sem flags
    Então o sistema exibe prompt:
      """
      Motivo do skip:
      [1] Saúde (consulta, doença)
      [2] Trabalho (reunião, deadline)
      [3] Família (evento, emergência)
      [4] Pessoal (outro motivo)
      [5] Clima (chuva, frio extremo)
      [6] Cansaço/Fadiga
      [7] Emergência (não categorizada)
      [8] Outro motivo
      [9] Pular agora, justificar depois

      Escolha [1-9]:
      """

  Cenário: Escolher opção 1-8 cria SKIPPED_JUSTIFIED
    Dado que usuário executa "habit skip Academia"
    Quando usuário escolhe opção "2" (Trabalho)
    E usuário digita nota "Reunião urgente"
    Então o substatus é "SKIPPED_JUSTIFIED"
    E o skip_reason é "trabalho"
    E o skip_note é "Reunião urgente"

  Cenário: Escolher opção 9 cria SKIPPED_UNJUSTIFIED
    Dado que usuário executa "habit skip Academia"
    Quando usuário escolhe opção "9" (Justificar depois)
    Então o substatus é "SKIPPED_UNJUSTIFIED"
    E o skip_reason é NULL
    E o skip_note é NULL
    E o sistema exibe prazo de 24h

  Cenário: Skip com flag --reason pula prompt
    Quando usuário executa "habit skip Academia --reason HEALTH"
    Então o prompt interativo NÃO é exibido
    E o substatus é "SKIPPED_JUSTIFIED"
    E o skip_reason é "saude"

  Cenário: Prompt para nota é opcional
    Dado que usuário executa "habit skip Academia"
    E usuário escolhe opção "6" (Cansaço)
    Quando sistema pergunta "Adicionar nota? (opcional)"
    E usuário pressiona Enter sem digitar
    Então o skip_note é NULL
    E o skip_reason é "cansaco"
