# BDD Scenarios Inventory

## Gerado em: Sat 15 Nov 22:20:46 -03 2025

### File: habit-instance.feature

- Cenário: Transição PENDING → DONE via timer stop
- Cenário: Transição PENDING → NOT_DONE via skip
- Cenário: Transição PENDING → NOT_DONE via timeout (48h)
- Cenário: Transições proibidas de DONE
- Cenário: Transições proibidas de NOT_DONE
- Cenário: DONE sempre tem done_substatus
- Cenário: NOT_DONE sempre tem not_done_substatus
- Cenário: PENDING tem ambos substatus NULL
- Cenário: Substatus mutuamente exclusivos
- Cenário: EXCESSIVE quando completion > 150%
- Cenário: OVERDONE quando completion 110-150%
- Cenário: FULL quando completion 90-110%
- Cenário: PARTIAL quando completion < 90%
- Esquema do Cenário: Edge cases de thresholds
- Cenário: Qualquer DONE mantém streak
- Cenário: Qualquer NOT_DONE quebra streak
- Cenário: EXCESSIVE mantém streak mas alerta impacto
- Cenário: Instance PENDING por < 48h não é ignored
- Cenário: Instance PENDING por > 48h é ignored
- Cenário: Apenas instances PENDING são verificadas
- Cenário: User ação antes de 48h previne IGNORED
- Cenário: EXCESSIVE com impacto em habits posteriores
- Cenário: OVERDONE sem impacto (gap suficiente)
- Cenário: FULL sem análise de impacto
- Cenário: PARTIAL sem análise de impacto

### File: routine.feature

- Cenário: Apenas uma rotina ativa por vez
- Cenário: Ativar rotina desativa todas as outras
- Cenário: Criar rotina não ativa automaticamente
- Cenário: Deletar rotina ativa não deixa nenhuma ativa
- Cenário: Ativação via trigger/constraint SQL
- Cenário: Habit requer routine_id (NOT NULL)
- Cenário: Habit criado em rotina válida
- Cenário: Habit com routine_id inválido
- Cenário: Relacionamento 1:N (Routine → Habits)
- Cenário: Deletar rotina com habits (cascade ou block)
- Cenário: Deletar rotina com --purge remove habits
- Cenário: Task não possui campo routine_id
- Cenário: Task criada independente de rotina ativa
- Cenário: task list mostra todas tasks (não filtra por rotina)
- Cenário: Trocar rotina não afeta tasks
- Cenário: Deletar rotina não afeta tasks
- Cenário: Task vs Habit (diferenças)
- Cenário: habit list mostra apenas habits da rotina ativa
- Cenário: habit create usa rotina ativa automaticamente
- Cenário: Trocar rotina muda contexto de habit list
- Cenário: Erro quando nenhuma rotina ativa
- Cenário: Flag --all-routines escapa contexto
- Cenário: Flag --routine especifica rotina diferente
- Cenário: Commands independentes de rotina ativa
- Cenário: Contexto de rotina no prompt CLI
- Cenário: Ativar rotina vazia (sem habits)

### File: skip.feature

- Cenário: Skip com categoria válida (HEALTH)
- Cenário: Skip com todas as 8 categorias
- Cenário: Skip com categoria inválida
- Cenário: Skip note limitado a 200 caracteres
- Cenário: Skip note é opcional
- Cenário: Skip fields NULL quando não skipped
- Cenário: Justificar skip dentro de 24h
- Cenário: Justificar skip após 24h (prazo expirado)
- Cenário: Skip sem justificativa mostra deadline
- Cenário: Prompt interativo com 9 opções
- Cenário: Escolher opção 1-8 cria SKIPPED_JUSTIFIED
- Cenário: Escolher opção 9 cria SKIPPED_UNJUSTIFIED
- Cenário: Skip com flag --reason pula prompt
- Cenário: Prompt para nota é opcional

### File: streak.feature

- Cenário: Calcular streak de dias consecutivos
- Cenário: Streak zerado quando último instance é NOT_DONE
- Cenário: PENDING não afeta cálculo de streak
- Cenário: Streak zero quando não há instances DONE
- Cenário: Contagem do mais recente para o mais antigo
- Cenário: NOT_DONE sempre quebra streak (regra fundamental)
- Cenário: SKIPPED_JUSTIFIED quebra streak (impacto psicológico BAIXO)
- Cenário: SKIPPED_UNJUSTIFIED quebra streak (impacto psicológico MÉDIO)
- Cenário: IGNORED quebra streak (impacto psicológico ALTO)
- Cenário: Todos substatus NOT_DONE quebram igualmente
- Cenário: DONE sempre mantém streak (regra fundamental)
- Cenário: PARTIAL mantém streak sem penalidade
- Cenário: OVERDONE mantém streak com monitoramento
- Cenário: EXCESSIVE mantém streak com warning de impacto
- Cenário: FULL mantém streak com feedback positivo
- Cenário: Todos substatus DONE mantêm igualmente
- Cenário: Feedback diferenciado por substatus NOT_DONE
- Cenário: SKIPPED_JUSTIFIED usa linguagem compreensiva
- Cenário: SKIPPED_UNJUSTIFIED oferece adicionar justificativa
- Cenário: IGNORED usa warning forte
- Cenário: Reports com análise de quebras
- Cenário: Milestones celebrados
- Cenário: Feedback adaptado ao contexto

### File: timer.feature

- Cenário: Apenas um timer ativo por vez
- Cenário: Timer PAUSED bloqueia novo start
- Cenário: Timer após stop NÃO bloqueia novo start
- Cenário: Múltiplas sessões do mesmo habit permitidas
- Cenário: Estados válidos: apenas RUNNING e PAUSED
- Cenário: Fluxo normal (start → pause → resume → stop)
- Cenário: stop salva sessão e marca DONE
- Cenário: reset cancela sem salvar
- Cenário: pause só funciona em RUNNING
- Cenário: resume só funciona em PAUSED
- Cenário: stop funciona em RUNNING ou PAUSED
- Cenário: reset funciona em RUNNING ou PAUSED
- Cenário: Duas sessões acumulam duração (PARTIAL → OVERDONE)
- Cenário: CLI exibe breakdown de múltiplas sessões
- Cenário: Três sessões levam a EXCESSIVE
- Cenário: Cada stop salva uma sessão independente
- Cenário: Instance marcada DONE após primeira sessão
- Cenário: Log manual com horários (start + end)
- Cenário: Log manual com duração
- Cenário: Validação: start < end
- Cenário: Validação: duração positiva
- Cenário: Validação: apenas um método
- Cenário: Validação: bloqueia se timer ativo
- Cenário: Adicionar nova sessão manual em habit DONE
- Cenário: Fórmula de completion
- Cenário: Substatus baseado em thresholds
- Cenário: Múltiplas sessões acumuladas no cálculo
- Cenário: Pausas descontadas do tempo total
- Cenário: Arredondamento para 2 casas decimais
- Cenário: Pausar cria TimeLog
- Cenário: Resumir finaliza TimeLog
- Cenário: Múltiplas pausas rastreadas
- Cenário: CLI exibe pausas no output final
- Cenário: Pausas opcionais (reason)
- Cenário: Duração efetiva descontando pausas
