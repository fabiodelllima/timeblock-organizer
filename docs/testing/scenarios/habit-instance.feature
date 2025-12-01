# language: pt
Funcionalidade: Estados e Transições de HabitInstance

  Como sistema TimeBlock
  Quero gerenciar estados de habit instances
  Para rastrear execução e calcular métricas

  Contexto:
    Dado que existe uma rotina "Rotina Matinal" ativa
    E existe um habit "Academia" com duração esperada de 90 minutos

  # BR-HABIT-INSTANCE-001: Status Transitions
  Cenário: Transição PENDING → DONE via timer stop
    Dado que existe um instance com status "PENDING"
    Quando timer é iniciado
    E timer é parado após 90 minutos
    Então o status muda para "DONE"
    E o done_substatus é calculado

  Cenário: Transição PENDING → NOT_DONE via skip
    Dado que existe um instance com status "PENDING"
    Quando usuário executa "habit skip Academia --reason HEALTH"
    Então o status muda para "NOT_DONE"
    E o not_done_substatus é "SKIPPED_JUSTIFIED"

  Cenário: Transição PENDING → NOT_DONE via timeout (48h)
    Dado que existe um instance com status "PENDING" criado há 49 horas
    Quando job de timeout executa
    Então o status muda para "NOT_DONE"
    E o not_done_substatus é "IGNORED"

  Cenário: Transições proibidas de DONE
    Dado que existe um instance com status "DONE"
    Quando tentativa de mudar para "PENDING"
    Então o sistema retorna erro "Status DONE é final"
    
    Quando tentativa de mudar para "NOT_DONE"
    Então o sistema retorna erro "Status DONE é final"

  Cenário: Transições proibidas de NOT_DONE
    Dado que existe um instance com status "NOT_DONE"
    Quando tentativa de mudar para "PENDING"
    Então o sistema retorna erro "Status NOT_DONE é final"
    
    Quando tentativa de mudar para "DONE"
    Então o sistema retorna erro "Status NOT_DONE é final"

  # BR-HABIT-INSTANCE-002: Substatus Assignment
  Cenário: DONE sempre tem done_substatus
    Dado que instance transiciona para "DONE"
    Então done_substatus NÃO pode ser NULL
    E not_done_substatus deve ser NULL

  Cenário: NOT_DONE sempre tem not_done_substatus
    Dado que instance transiciona para "NOT_DONE"
    Então not_done_substatus NÃO pode ser NULL
    E done_substatus deve ser NULL

  Cenário: PENDING tem ambos substatus NULL
    Dado que instance está com status "PENDING"
    Então done_substatus deve ser NULL
    E not_done_substatus deve ser NULL

  Cenário: Substatus mutuamente exclusivos
    Dado que instance tem status "DONE"
    Quando tentativa de setar not_done_substatus
    Então o sistema retorna erro "Substatus mutuamente exclusivos"

  # BR-HABIT-INSTANCE-003: Completion Thresholds
  Cenário: EXCESSIVE quando completion > 150%
    Dado que duração esperada é 90 minutos
    Quando duração real é 180 minutos
    Então completion é 200%
    E done_substatus é "EXCESSIVE"
    E sistema exibe warning sobre impacto

  Cenário: OVERDONE quando completion 110-150%
    Dado que duração esperada é 90 minutos
    Quando duração real é 100 minutos
    Então completion é 111%
    E done_substatus é "OVERDONE"
    E sistema exibe info sobre recorrência

  Cenário: FULL quando completion 90-110%
    Dado que duração esperada é 90 minutos
    Quando duração real é 90 minutos
    Então completion é 100%
    E done_substatus é "FULL"
    E sistema exibe feedback positivo

  Cenário: PARTIAL quando completion < 90%
    Dado que duração esperada é 90 minutos
    Quando duração real é 60 minutos
    Então completion é 67%
    E done_substatus é "PARTIAL"
    E sistema mantém streak

  Esquema do Cenário: Edge cases de thresholds
    Dado que duração esperada é 90 minutos
    Quando duração real é <real> minutos
    Então completion é <percentage>%
    E done_substatus é "<substatus>"

    Exemplos:
      | real | percentage | substatus  |
      | 136  | 151.11     | EXCESSIVE  |
      | 135  | 150.00     | EXCESSIVE  |
      | 134  | 148.89     | OVERDONE   |
      | 100  | 111.11     | OVERDONE   |
      | 99   | 110.00     | OVERDONE   |
      | 98   | 108.89     | FULL       |
      | 90   | 100.00     | FULL       |
      | 81   | 90.00      | FULL       |
      | 80   | 88.89      | PARTIAL    |

  # BR-HABIT-INSTANCE-004: Streak Calculation with Substatus
  Cenário: Qualquer DONE mantém streak
    Dado que streak atual é 5 dias
    E last instance foi DONE com substatus "<substatus>"
    Quando nova instance é marcada como DONE
    Então streak incrementa para 6 dias

    Exemplos:
      | substatus  |
      | EXCESSIVE  |
      | OVERDONE   |
      | FULL       |
      | PARTIAL    |

  Cenário: Qualquer NOT_DONE quebra streak
    Dado que streak atual é 14 dias
    E nova instance é marcada como NOT_DONE com substatus "<substatus>"
    Então streak reseta para 0 dias

    Exemplos:
      | substatus            |
      | SKIPPED_JUSTIFIED    |
      | SKIPPED_UNJUSTIFIED  |
      | IGNORED              |

  Cenário: EXCESSIVE mantém streak mas alerta impacto
    Dado que streak atual é 12 dias
    Quando instance é marcada como DONE (EXCESSIVE)
    Então streak incrementa para 13 dias
    E sistema exibe warning:
      """
      [WARN] Academia ultrapassou meta em Xmin
             
      Impacto na rotina:
        - <habit>: PERDIDO/ATRASADO
      """

  # BR-HABIT-INSTANCE-005: Ignored Auto-Assignment
  Cenário: Instance PENDING por < 48h não é ignored
    Dado que instance foi criado há 24 horas
    Quando job de timeout executa
    Então status permanece "PENDING"

  Cenário: Instance PENDING por > 48h é ignored
    Dado que instance foi criado há 49 horas
    E status é "PENDING"
    Quando job de timeout executa
    Então status muda para "NOT_DONE"
    E not_done_substatus é "IGNORED"
    E ignored_at timestamp é registrado

  Cenário: Apenas instances PENDING são verificadas
    Dado que existem instances com status "DONE" e "NOT_DONE"
    Quando job de timeout executa
    Então apenas instances "PENDING" são processadas
    E instances "DONE" e "NOT_DONE" não são alteradas

  Cenário: User ação antes de 48h previne IGNORED
    Dado que instance foi criado há 30 horas
    Quando usuário executa "habit skip Academia --reason WORK"
    Então status é "NOT_DONE"
    E not_done_substatus é "SKIPPED_JUSTIFIED"
    E job de timeout NÃO marca como IGNORED

  # BR-HABIT-INSTANCE-006: Impact Analysis on EXCESSIVE/OVERDONE
  Cenário: EXCESSIVE com impacto em habits posteriores
    Dado que Academia está agendada para 07:00-08:30 (90min)
    E Trabalho está agendado para 09:00-12:00 (180min)
    E Inglês está agendado para 13:00-14:00 (60min)
    Quando Academia termina às 10:00 (180min real)
    Então done_substatus é "EXCESSIVE"
    E sistema detecta impacto:
      | habit    | impacto   |
      | Trabalho | PERDIDO   |
      | Inglês   | ATRASADO  |
    E sistema sugere "Ajustar meta de Academia para 2h?"

  Cenário: OVERDONE sem impacto (gap suficiente)
    Dado que Academia está agendada para 07:00-08:30 (90min)
    E Inglês está agendado para 14:00-15:00 (60min)
    Quando Academia termina às 09:00 (120min real)
    Então done_substatus é "OVERDONE"
    E nenhum habit foi afetado
    E sistema exibe info:
      """
      [INFO] Acima da meta. Frequente? Considere ajustar para 2h.
      """

  Cenário: FULL sem análise de impacto
    Dado que Academia termina exatamente no horário (90min)
    Quando done_substatus é "FULL"
    Então análise de impacto NÃO é executada

  Cenário: PARTIAL sem análise de impacto
    Dado que Academia termina antes do horário (60min)
    Quando done_substatus é "PARTIAL"
    Então análise de impacto NÃO é executada
