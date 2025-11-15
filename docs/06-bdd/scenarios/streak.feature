# language: pt
Funcionalidade: Cálculo e Gerenciamento de Streak

  Como usuário do TimeBlock
  Quero acompanhar minha consistência em habits
  Para manter motivação e rastrear progresso

  Baseado em "Atomic Habits" (James Clear)
  Filosofia: Consistência > Perfeição

  Contexto:
    Dado que existe um habit "Academia" na rotina ativa

  # BR-STREAK-001: Calculation Algorithm
  Cenário: Calcular streak de dias consecutivos
    Dado que existem instances com status:
      | data       | status   |
      | 2025-11-14 | DONE     |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | DONE     |
      | 2025-11-11 | NOT_DONE |
      | 2025-11-10 | DONE     |
    Quando sistema calcula streak
    Então streak atual é 3 dias

  Cenário: Streak zerado quando último instance é NOT_DONE
    Dado que existem instances com status:
      | data       | status   |
      | 2025-11-14 | NOT_DONE |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | DONE     |
    Quando sistema calcula streak
    Então streak atual é 0 dias

  Cenário: PENDING não afeta cálculo de streak
    Dado que existem instances com status:
      | data       | status   |
      | 2025-11-16 | PENDING  |
      | 2025-11-15 | PENDING  |
      | 2025-11-14 | DONE     |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | NOT_DONE |
    Quando sistema calcula streak
    Então streak atual é 2 dias
    E instances PENDING são ignoradas

  Cenário: Streak zero quando não há instances DONE
    Dado que habit foi criado hoje
    E não há instances com status DONE
    Quando sistema calcula streak
    Então streak atual é 0 dias

  Cenário: Contagem do mais recente para o mais antigo
    Dado que existem instances de Academia:
      | data       | status   |
      | 2025-11-14 | DONE     |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | DONE     |
    Quando sistema calcula streak começando de hoje
    Então percorre instances de 14/11 → 13/11 → 12/11
    E para ao encontrar primeiro NOT_DONE ou fim da lista

  # BR-STREAK-002: Break Conditions
  Cenário: NOT_DONE sempre quebra streak (regra fundamental)
    Dado que streak atual é 20 dias
    Quando nova instance é marcada como NOT_DONE
    Então streak reseta para 0 dias
    E substatus NOT_DONE não importa

  Cenário: SKIPPED_JUSTIFIED quebra streak (impacto psicológico BAIXO)
    Dado que streak atual é 14 dias
    Quando instance é marcada como SKIPPED_JUSTIFIED (HEALTH)
    Então streak reseta para 0 dias
    E sistema exibe feedback compreensivo:
      """
      ✗ Academia pulada (justificado: Saúde)
        Streak quebrado: 14 → 0 dias
        Motivo registrado: Consulta médica

      Continue amanhã para recomeçar streak!
      """

  Cenário: SKIPPED_UNJUSTIFIED quebra streak (impacto psicológico MÉDIO)
    Dado que streak atual é 14 dias
    Quando instance é marcada como SKIPPED_UNJUSTIFIED
    Então streak reseta para 0 dias
    E sistema exibe warning moderado:
      """
      ✗ Academia pulada (sem justificativa)
        Streak quebrado: 14 → 0 dias

      [WARN] Skip sem justificativa.
             Adicionar motivo? [Y/n]:
      """

  Cenário: IGNORED quebra streak (impacto psicológico ALTO)
    Dado que streak atual é 7 dias
    E habit foi ignorado 3 vezes este mês
    Quando instance é marcada como IGNORED
    Então streak reseta para 0 dias
    E sistema exibe alerta forte:
      """
      [WARN] Academia ignorada (sem ação consciente)
             Streak quebrado: 7 → 0 dias

             3 ignores este mês.
             Considere ajustar horário ou meta.
      """

  Cenário: Todos substatus NOT_DONE quebram igualmente
    Dado que streak atual é 10 dias
    Quando instance é marcada como NOT_DONE com substatus "<substatus>"
    Então streak reseta para 0 dias

    Exemplos:
      | substatus            |
      | SKIPPED_JUSTIFIED    |
      | SKIPPED_UNJUSTIFIED  |
      | IGNORED              |

  # BR-STREAK-003: Maintain Conditions
  Cenário: DONE sempre mantém streak (regra fundamental)
    Dado que streak atual é 5 dias
    Quando nova instance é marcada como DONE
    Então streak incrementa para 6 dias
    E substatus DONE não importa

  Cenário: PARTIAL mantém streak sem penalidade
    Dado que streak atual é 5 dias
    Quando instance é marcada como DONE (PARTIAL - 67%)
    Então streak incrementa para 6 dias
    E sistema exibe feedback encorajador:
      """
      ✓ Sessão completa!
        Tempo: 60min (67% da meta)
        Status: DONE (PARTIAL)
        Streak: 6 dias ✓

      [INFO] Abaixo da meta, mas streak mantido!
      """

  Cenário: OVERDONE mantém streak com monitoramento
    Dado que streak atual é 8 dias
    Quando instance é marcada como DONE (OVERDONE - 111%)
    Então streak incrementa para 9 dias
    E sistema exibe info:
      """
      ✓ Sessão completa!
        Tempo: 100min (111% da meta)
        Status: DONE (OVERDONE)
        Streak: 9 dias ✓

      [INFO] Acima da meta. Frequente? Considere ajustar.
      """

  Cenário: EXCESSIVE mantém streak com warning de impacto
    Dado que streak atual é 12 dias
    E Academia ultrapassou meta afetando Trabalho e Inglês
    Quando instance é marcada como DONE (EXCESSIVE - 200%)
    Então streak incrementa para 13 dias
    E sistema exibe warning:
      """
      ✓ Sessão completa!
        Tempo: 180min (200% da meta)
        Status: DONE (EXCESSIVE)
        Streak: 13 dias ✓

      [WARN] Academia ultrapassou meta em 90min

      Impacto na rotina:
        - Trabalho: PERDIDO
        - Inglês: ATRASADO 1h

      Sugestão: Ajustar meta para 2h?
      """

  Cenário: FULL mantém streak com feedback positivo
    Dado que streak atual é 30 dias
    Quando instance é marcada como DONE (FULL - 100%)
    Então streak incrementa para 31 dias
    E sistema exibe celebração:
      """
      ✓ Sessão completa!
        Tempo: 90min (100% da meta)
        Status: DONE (FULL)

      ╔════════════════════════════════════════╗
      ║  MILESTONE: 31 DIAS CONSECUTIVOS!      ║
      ╠════════════════════════════════════════╣
      ║  Parabéns! Hábito consolidado.         ║
      ║  Continue assim!                       ║
      ╚════════════════════════════════════════╝
      """

  Cenário: Todos substatus DONE mantêm igualmente
    Dado que streak atual é 7 dias
    Quando instance é marcada como DONE com substatus "<substatus>"
    Então streak incrementa para 8 dias

    Exemplos:
      | substatus  |
      | EXCESSIVE  |
      | OVERDONE   |
      | FULL       |
      | PARTIAL    |

  # BR-STREAK-004: Psychological Feedback by Substatus
  Cenário: Feedback diferenciado por substatus NOT_DONE
    Quando instance quebra streak com substatus "<substatus>"
    Então tom do feedback é "<tom>"
    E impacto psicológico é "<impacto>"

    Exemplos:
      | substatus            | tom              | impacto |
      | SKIPPED_JUSTIFIED    | Compreensivo     | Baixo   |
      | SKIPPED_UNJUSTIFIED  | Moderado         | Médio   |
      | IGNORED              | Alerta Forte     | Alto    |

  Cenário: SKIPPED_JUSTIFIED usa linguagem compreensiva
    Dado que streak é quebrado por SKIPPED_JUSTIFIED
    Então feedback contém frases como:
      | frase                              |
      | Tudo bem, acontece                 |
      | Continue amanhã                    |
      | Motivo registrado                  |
    E NÃO contém frases como:
      | frase                              |
      | Você falhou                        |
      | Streak perdido                     |
      | Que pena                           |

  Cenário: SKIPPED_UNJUSTIFIED oferece adicionar justificativa
    Dado que streak é quebrado por SKIPPED_UNJUSTIFIED
    Então sistema pergunta "Adicionar motivo? [Y/n]"
    E oferece comando: "habit skip <id> --add-reason"

  Cenário: IGNORED usa warning forte
    Dado que streak é quebrado por IGNORED
    Então sistema usa símbolo [WARN] em vermelho
    E pergunta "Hábito está consolidado?"
    E sugere "Ajustar horário ou meta?"

  Cenário: Reports com análise de quebras
    Quando usuário executa "report habit Academia --period 30"
    Então sistema exibe breakdown:
      """
      Quebras este mês: 3x
        ├─ Skipped (justified): 2x  (Trabalho, Saúde)
        ├─ Skipped (unjust.): 0x
        └─ Ignored: 1x              [WARN]

      [INFO] Quebras justificadas são normais (67% deste mês)
      [WARN] 1 ignore detectado - atenção ao engajamento
      """

  Cenário: Milestones celebrados
    Quando streak atinge "<milestone>" dias
    Então sistema exibe celebração especial

    Exemplos:
      | milestone |
      | 7         |
      | 21        |
      | 30        |
      | 60        |
      | 90        |
      | 365       |

  Cenário: Feedback adaptado ao contexto
    Dado que usuário tem histórico de skips justificados (80%)
    Quando nova quebra por SKIPPED_JUSTIFIED
    Então feedback reconhece padrão:
      """
      ✗ Academia pulada (justificado)
        Streak: 5 → 0 dias

      Suas quebras são sempre justificadas ✓
      Padrão saudável de flexibilidade.
      """
