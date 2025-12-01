# language: pt
Funcionalidade: Timer e Tracking de Tempo

  Como usuário do TimeBlock
  Quero rastrear tempo dedicado a habits
  Para calcular completion % e substatus

  Contexto:
    Dado que existe um habit "Academia" com duração esperada de 90 minutos

  # BR-TIMER-001: Single Active Timer Constraint
  Cenário: Apenas um timer ativo por vez
    Dado que timer de "Academia" está RUNNING
    Quando tentativa de iniciar timer de "Meditação"
    Então sistema retorna erro:
      """
      [ERROR] Timer já ativo: Academia (45min decorridos)

      Opções:
        [1] Pausar Academia e iniciar Meditação
        [2] Cancelar Academia (reset) e iniciar Meditação
        [3] Continuar com Academia
      """

  Cenário: Timer PAUSED bloqueia novo start
    Dado que timer de "Academia" está PAUSED
    Quando tentativa de iniciar timer de "Meditação"
    Então sistema retorna erro "Timer já ativo (pausado)"

  Cenário: Timer após stop NÃO bloqueia novo start
    Dado que timer de "Academia" foi stopped
    Quando usuário executa "timer start Meditação"
    Então novo timer inicia com sucesso
    E timer anterior não está mais ativo

  Cenário: Múltiplas sessões do mesmo habit permitidas
    Dado que timer de "Academia" foi stopped (sessão 1: 60min)
    Quando usuário executa "timer start Academia"
    Então novo timer inicia com sucesso (sessão 2)
    E ambas sessões serão acumuladas

  # BR-TIMER-002: State Transitions
  Cenário: Estados válidos: apenas RUNNING e PAUSED
    Quando sistema verifica enum TimerStatus
    Então apenas 2 estados existem:
      | estado  |
      | RUNNING |
      | PAUSED  |

  Cenário: Fluxo normal (start → pause → resume → stop)
    Quando usuário executa "timer start Academia"
    Então status é RUNNING

    Quando usuário executa "timer pause"
    Então status é PAUSED

    Quando usuário executa "timer resume"
    Então status é RUNNING

    Quando usuário executa "timer stop"
    Então timer não existe mais (finalizado)
    E sessão foi salva como DONE

  Cenário: stop salva sessão e marca DONE
    Dado que timer está RUNNING há 90 minutos
    Quando usuário executa "timer stop"
    Então sessão é salva com duration = 90
    E instance é marcada como DONE
    E done_substatus é calculado

  Cenário: reset cancela sem salvar
    Dado que timer está RUNNING há 30 minutos
    Quando usuário executa "timer reset"
    Então timer não existe mais (cancelado)
    E sessão NÃO é salva
    E instance permanece PENDING

  Cenário: pause só funciona em RUNNING
    Dado que timer está PAUSED
    Quando tentativa de executar "timer pause"
    Então sistema retorna erro "Timer já está pausado"

  Cenário: resume só funciona em PAUSED
    Dado que timer está RUNNING
    Quando tentativa de executar "timer resume"
    Então sistema retorna erro "Timer não está pausado"

  Cenário: stop funciona em RUNNING ou PAUSED
    Dado que timer está em estado "<estado>"
    Quando usuário executa "timer stop"
    Então sessão é salva com sucesso

    Exemplos:
      | estado  |
      | RUNNING |
      | PAUSED  |

  Cenário: reset funciona em RUNNING ou PAUSED
    Dado que timer está em estado "<estado>"
    Quando usuário executa "timer reset"
    Então timer é cancelado sem salvar

    Exemplos:
      | estado  |
      | RUNNING |
      | PAUSED  |

  # BR-TIMER-003: Multiple Sessions Same Day
  Cenário: Duas sessões acumulam duração (PARTIAL → OVERDONE)
    Dado que usuário faz sessão 1 de "Academia": 60min
    Quando usuário faz sessão 2 de "Academia": 35min
    Então duração total é 95min
    E completion é 106%
    E done_substatus é OVERDONE

  Cenário: CLI exibe breakdown de múltiplas sessões
    Dado que usuário completou 2 sessões de "Academia"
    Quando último "timer stop" é executado
    Então sistema exibe:
      """
      ✓ Sessão 2 completa: 35min

      ╔════════════════════════════════╗
      ║  TOTAL DO DIA: Academia        ║
      ╠════════════════════════════════╣
      ║  Sessões: 2                    ║
      ║  Tempo: 95min (106% da meta)   ║
      ║  Status: DONE (OVERDONE)       ║
      ╚════════════════════════════════╝
      """

  Cenário: Três sessões levam a EXCESSIVE
    Quando usuário completa sessões de "Academia":
      | sessão | duração |
      | 1      | 60min   |
      | 2      | 40min   |
      | 3      | 70min   |
    Então duração total é 170min
    E completion é 189%
    E done_substatus é EXCESSIVE

  Cenário: Cada stop salva uma sessão independente
    Quando usuário executa fluxo:
      | comando              | resultado         |
      | timer start Academia | Timer iniciado    |
      | timer stop           | Sessão 1 salva    |
      | timer start Academia | Timer iniciado    |
      | timer stop           | Sessão 2 salva    |
    Então 2 sessões independentes existem
    E ambas têm duração registrada

  Cenário: Instance marcada DONE após primeira sessão
    Dado que instance está PENDING
    Quando primeira sessão é completada (60min)
    Então instance é marcada como DONE
    E done_substatus é PARTIAL (67%)

    Quando segunda sessão é adicionada (35min)
    Então done_substatus é atualizado para OVERDONE (106%)

  # BR-TIMER-004: Manual Log Validation
  Cenário: Log manual com horários (start + end)
    Quando usuário executa "habit log Academia --start 07:00 --end 08:30"
    Então duração calculada é 90min
    E completion é 100%
    E done_substatus é FULL

  Cenário: Log manual com duração
    Quando usuário executa "habit log Academia --duration 90"
    Então duração é 90min
    E completion é 100%

  Cenário: Validação: start < end
    Quando usuário executa "habit log Academia --start 08:00 --end 07:00"
    Então sistema retorna erro "Horário de fim antes do início"

  Cenário: Validação: duração positiva
    Quando usuário executa "habit log Academia --duration -10"
    Então sistema retorna erro "Duração deve ser positiva"

  Cenário: Validação: apenas um método
    Quando usuário executa "habit log Academia --start 07:00 --end 08:00 --duration 60"
    Então sistema retorna erro "Use start+end OU duration, não ambos"

  Cenário: Validação: bloqueia se timer ativo
    Dado que timer de "Academia" está RUNNING
    Quando usuário executa "habit log Academia --duration 90"
    Então sistema retorna erro:
      """
      [ERROR] Timer ativo para Academia
              Stop timer primeiro: timer stop
      """

  Cenário: Adicionar nova sessão manual em habit DONE
    Dado que "Academia" já tem 1 sessão (timer): 60min
    Quando usuário executa "habit log Academia --duration 30"
    Então sistema pergunta:
      """
      Habit já completo (1 sessão: 60min).
      Adicionar nova sessão? [y/N]:
      """
    E ao confirmar, nova sessão é adicionada
    E total acumulado é 90min

  # BR-TIMER-005: Completion Percentage Calculation
  Cenário: Fórmula de completion
    Dado que duração esperada é 90min
    Quando duração real acumulada é <real>min
    Então completion é <percentage>%

    Exemplos:
      | real | percentage |
      | 180  | 200.00     |
      | 135  | 150.00     |
      | 100  | 111.11     |
      | 90   | 100.00     |
      | 60   | 66.67      |

  Cenário: Substatus baseado em thresholds
    Dado que duração esperada é 90min
    Quando completion é <percentage>%
    Então done_substatus é "<substatus>"

    Exemplos:
      | percentage | substatus  |
      | 200        | EXCESSIVE  |
      | 150        | EXCESSIVE  |
      | 149        | OVERDONE   |
      | 111        | OVERDONE   |
      | 110        | OVERDONE   |
      | 109        | FULL       |
      | 100        | FULL       |
      | 90         | FULL       |
      | 89         | PARTIAL    |
      | 67         | PARTIAL    |

  Cenário: Múltiplas sessões acumuladas no cálculo
    Dado que existem sessões:
      | tipo  | duração |
      | timer | 60min   |
      | timer | 25min   |
      | log   | 10min   |
    Quando completion é calculado
    Então total acumulado é 95min
    E completion é 106%
    E done_substatus é OVERDONE

  Cenário: Pausas descontadas do tempo total
    Dado que timer iniciou às 07:00
    E timer foi pausado das 07:30 às 07:40 (10min)
    E timer foi pausado das 08:10 às 08:15 (5min)
    E timer parou às 08:45
    Quando completion é calculado
    Então tempo total decorrido é 105min
    E pausas totalizam 15min
    E duração efetiva é 90min
    E completion é 100%

  Cenário: Arredondamento para 2 casas decimais
    Dado que duração esperada é 90min
    Quando duração real é 85min
    Então completion é 94.44%
    E não 94.444444...%

  # BR-TIMER-006: Pause Tracking
  Cenário: Pausar cria TimeLog
    Dado que timer está RUNNING
    Quando usuário executa "timer pause"
    Então TimeLog é criado com:
      | campo       | valor              |
      | timer_id    | <id do timer>      |
      | pause_start | <timestamp atual>  |
      | pause_end   | NULL               |
      | duration    | NULL               |

  Cenário: Resumir finaliza TimeLog
    Dado que timer está PAUSED há 10 minutos
    Quando usuário executa "timer resume"
    Então TimeLog é atualizado com:
      | campo       | valor              |
      | pause_end   | <timestamp atual>  |
      | duration    | 10                 |

  Cenário: Múltiplas pausas rastreadas
    Quando usuário executa fluxo:
      | comando      | horário | resultado               |
      | timer start  | 07:00   | Timer iniciado          |
      | timer pause  | 07:30   | TimeLog 1 criado        |
      | timer resume | 07:40   | TimeLog 1 finalizado    |
      | timer pause  | 08:10   | TimeLog 2 criado        |
      | timer resume | 08:15   | TimeLog 2 finalizado    |
      | timer stop   | 08:45   | Timer finalizado        |
    Então 2 TimeLogs existem:
      | log | pause_start | pause_end | duration |
      | 1   | 07:30       | 07:40     | 10min    |
      | 2   | 08:10       | 08:15     | 5min     |

  Cenário: CLI exibe pausas no output final
    Dado que timer teve 2 pausas (10min + 5min)
    Quando usuário executa "timer stop"
    Então sistema exibe:
      """
      ✓ SESSÃO COMPLETA!
      ╔════════════════════════════════════════╗
      ║ Academia (14/11/2025)                  ║
      ╠════════════════════════════════════════╣
      ║ Programado: 07:00 → 08:30 (90min)      ║
      ║ Real: 07:00 → 08:45 (105min total)     ║
      ╠════════════════════════════════════════╣
      ║ Pausas: 2x (15min total)               ║
      ║   1. 07:30-07:40 (10min)               ║
      ║   2. 08:10-08:15 (5min)                ║
      ╠════════════════════════════════════════╣
      ║ Tempo efetivo: 90min                   ║
      ║ Completion: 100%                       ║
      ║ Status: DONE (FULL)                    ║
      ╚════════════════════════════════════════╝
      """

  Cenário: Pausas opcionais (reason)
    Quando usuário pausa timer
    E adiciona reason "Telefone tocou"
    Então TimeLog tem reason = "Telefone tocou"

  Cenário: Duração efetiva descontando pausas
    Dado que timer rodou das 07:00 às 08:00 (60min)
    E teve pausas de 5min + 3min + 2min
    Quando duração efetiva é calculada
    Então tempo bruto é 60min
    E pausas totalizam 10min
    E duração efetiva é 50min
