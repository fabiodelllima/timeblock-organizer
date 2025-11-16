# language: pt
Funcionalidade: Gerenciamento de Rotinas e Contexto

  Como usuário do TimeBlock
  Quero organizar habits em rotinas
  Para alternar entre contextos (manhã, trabalho, noite)

  # BR-ROUTINE-001: Single Active Constraint
  Cenário: Apenas uma rotina ativa por vez
    Dado que existem rotinas:
      | nome            | is_active |
      | Rotina Matinal  | true      |
      | Rotina Trabalho | false     |
      | Rotina Noite    | false     |
    Quando sistema valida constraint
    Então apenas 1 rotina tem is_active = true

  Cenário: Ativar rotina desativa todas as outras
    Dado que "Rotina Matinal" está ativa
    Quando usuário executa "routine activate 'Rotina Trabalho'"
    Então "Rotina Trabalho" fica ativa
    E "Rotina Matinal" fica inativa
    E sistema exibe:
      """
      [INFO] Rotina "Rotina Matinal" desativada
      [OK] Rotina "Rotina Trabalho" ativada
      
      Agora a rotina ativa é: Rotina Trabalho (8 hábitos)
      """

  Cenário: Criar rotina não ativa automaticamente
    Quando usuário executa "routine create 'Rotina Fim de Semana'"
    Então nova rotina é criada com is_active = false
    E rotina ativa anterior permanece ativa

  Cenário: Deletar rotina ativa não deixa nenhuma ativa
    Dado que "Rotina Matinal" está ativa
    Quando usuário executa "routine delete 'Rotina Matinal'"
    Então rotina é deletada
    E nenhuma rotina fica ativa

  Cenário: Ativação via trigger/constraint SQL
    Dado que banco tem trigger "enforce_single_active_routine"
    Quando UPDATE routine SET is_active = true WHERE id = 2
    Então trigger desativa automaticamente rotinas com id != 2

  # BR-ROUTINE-002: Habit Belongs to Routine
  Cenário: Habit requer routine_id (NOT NULL)
    Quando tentativa de criar habit sem routine_id
    Então sistema retorna erro "routine_id obrigatório"

  Cenário: Habit criado em rotina válida
    Dado que existe rotina "Rotina Matinal" com id 1
    Quando usuário cria habit com routine_id = 1
    Então habit é criado com sucesso
    E habit pertence à "Rotina Matinal"

  Cenário: Habit com routine_id inválido
    Quando tentativa de criar habit com routine_id = 999
    Então sistema retorna erro "Rotina não encontrada"
    E constraint de foreign key é violada

  Cenário: Relacionamento 1:N (Routine → Habits)
    Dado que existe rotina "Rotina Matinal"
    Quando rotina contém habits:
      | título          |
      | Academia        |
      | Meditação       |
      | Café da manhã   |
    Então rotina tem 3 habits vinculados
    E todos habits têm routine_id = 1

  Cenário: Deletar rotina com habits (cascade ou block)
    Dado que "Rotina Matinal" contém 5 habits
    Quando usuário executa "routine delete 'Rotina Matinal'"
    Então sistema pergunta:
      """
      Rotina contém 5 habits.
      [1] Deletar rotina E habits (cascade)
      [2] Cancelar operação
      """

  Cenário: Deletar rotina com --purge remove habits
    Dado que "Rotina Matinal" contém 5 habits
    Quando usuário executa "routine delete 'Rotina Matinal' --purge"
    Então rotina é deletada
    E todos 5 habits são deletados

  # BR-ROUTINE-003: Task Independent of Routine
  Cenário: Task não possui campo routine_id
    Quando modelo Task é verificado
    Então campo routine_id NÃO existe

  Cenário: Task criada independente de rotina ativa
    Dado que "Rotina Trabalho" está ativa
    Quando usuário cria task "Dentista (25/11 14:30)"
    Então task é criada sem routine_id
    E task não depende de rotina ativa

  Cenário: task list mostra todas tasks (não filtra por rotina)
    Dado que "Rotina Matinal" está ativa
    E existem tasks:
      | título            |
      | Dentista          |
      | Reunião cliente   |
    Quando usuário executa "task list"
    Então sistema exibe todas 2 tasks
    E não filtra por rotina ativa

  Cenário: Trocar rotina não afeta tasks
    Dado que existem tasks "Dentista" e "Reunião cliente"
    E "Rotina Matinal" está ativa
    Quando usuário executa "routine activate 'Rotina Trabalho'"
    E usuário executa "task list"
    Então mesmas 2 tasks são exibidas

  Cenário: Deletar rotina não afeta tasks
    Dado que existem 3 tasks criadas
    E "Rotina Matinal" é deletada
    Quando usuário executa "task list"
    Então todas 3 tasks permanecem

  Cenário: Task vs Habit (diferenças)
    Então diferenças são:
      | aspecto      | Task           | Habit                |
      | Recorrência  | Única/pontual  | Recorrente           |
      | Routine      | Não pertence   | Pertence (obrigatório)|
      | Contexto     | Independente   | Depende de routine   |
      | Exemplo      | Dentista 14:30 | Academia 07:00-08:30 |

  # BR-ROUTINE-004: Activation Cascade
  Cenário: habit list mostra apenas habits da rotina ativa
    Dado que "Rotina Matinal" está ativa com habits:
      | título      |
      | Academia    |
      | Meditação   |
    E "Rotina Trabalho" está inativa com habits:
      | título         |
      | Daily Standup  |
      | Deep Work      |
    Quando usuário executa "habit list"
    Então sistema exibe apenas:
      | título      |
      | Academia    |
      | Meditação   |

  Cenário: habit create usa rotina ativa automaticamente
    Dado que "Rotina Matinal" está ativa (id = 1)
    Quando usuário executa "habit create --title 'Leitura'"
    Então habit é criado com routine_id = 1
    E sistema exibe:
      """
      ✓ Hábito criado na rotina ativa: Rotina Matinal
      """

  Cenário: Trocar rotina muda contexto de habit list
    Dado que "Rotina Matinal" está ativa
    Quando usuário executa "habit list"
    Então exibe habits de "Rotina Matinal"
    
    Quando usuário executa "routine activate 'Rotina Trabalho'"
    E usuário executa "habit list"
    Então exibe habits de "Rotina Trabalho"

  Cenário: Erro quando nenhuma rotina ativa
    Dado que todas rotinas estão inativas
    Quando usuário executa "habit list"
    Então sistema retorna erro:
      """
      [ERROR] Nenhuma rotina ativa.
              
      Para ativar uma rotina:
        routine list
        routine activate <id>
      """

  Cenário: Flag --all-routines escapa contexto
    Dado que "Rotina Matinal" está ativa
    Quando usuário executa "habit list --all-routines"
    Então sistema exibe habits de TODAS rotinas:
      | título         | rotina          |
      | Academia       | Matinal         |
      | Meditação      | Matinal         |
      | Daily Standup  | Trabalho        |
      | Deep Work      | Trabalho        |

  Cenário: Flag --routine especifica rotina diferente
    Dado que "Rotina Matinal" está ativa
    Quando usuário executa "habit create --routine 2 --title 'Teste'"
    Então habit é criado em rotina id = 2
    E não usa rotina ativa

  Cenário: Commands independentes de rotina ativa
    Dado que "Rotina Matinal" está ativa
    Então commands independentes são:
      | command         | comportamento                |
      | routine list    | Mostra TODAS rotinas         |
      | task list       | Mostra TODAS tasks           |
      | report habit 42 | Aceita habit_id (não filtro) |

  Cenário: Contexto de rotina no prompt CLI
    Dado que "Rotina Matinal" está ativa
    Quando usuário abre CLI
    Então prompt exibe:
      """
      TimeBlock [Rotina Matinal] >
      """

  Cenário: Ativar rotina vazia (sem habits)
    Dado que existe rotina "Rotina Fim de Semana" sem habits
    Quando usuário executa "routine activate 'Rotina Fim de Semana'"
    Então rotina é ativada
    E sistema exibe:
      """
      [OK] Rotina "Rotina Fim de Semana" ativada
      
      Rotina vazia. Adicione habits:
        habit create --title "Nome" --start HH:MM --end HH:MM
      """

# --- BR-ROUTINE-002: Delete Behaviors ---

  Cenário: Soft delete por padrão (is_active=False)
    Dado que existe rotina "Rotina Matinal" com 8 habits
    E rotina está ativa
    Quando usuário executa "routine delete 1"
    E confirma ação
    Então routine.is_active = False
    E habits permanecem vinculados
    E dados permanecem no banco
    E sistema exibe:
      """
      [WARN] Desativar rotina "Rotina Matinal"?
             - 8 hábitos permanecem vinculados
             - Rotina pode ser reativada depois
      
      Confirmar? (s/N): s
      [OK] Rotina "Rotina Matinal" desativada
      """

  Cenário: Hard delete sem habits funciona
    Dado que existe rotina "Rotina Teste" sem habits
    Quando usuário executa "routine delete 1 --purge"
    E confirma ação
    Então rotina é REMOVIDA do banco
    E sistema exibe:
      """
      [WARN] Deletar PERMANENTEMENTE rotina "Rotina Teste"?
             Esta ação NÃO pode ser desfeita.
      
      Confirmar? (s/N): s
      [OK] Rotina deletada permanentemente
      """

  Cenário: Hard delete com habits bloqueia (MVP)
    Dado que existe rotina "Rotina Matinal" com 8 habits
    Quando usuário executa "routine delete 1 --purge"
    Então sistema BLOQUEIA delete
    E exibe mensagem de erro:
      """
      [ERROR] Não é possível deletar rotina com hábitos
      
      Rotina "Rotina Matinal" possui 8 hábitos:
      1. Academia
      2. Meditação
      ...
      
      Ações disponíveis:
      1. Mover hábitos para outra rotina (Sprint 2)
      2. Deletar hábitos também com --cascade (Sprint 2)
      
      Para deletar a rotina vazia, remova os hábitos primeiro.
      """

# --- BR-ROUTINE-004: First Routine Flow ---

  Cenário: Criar habit sem rotina orienta criação
    Dado que NÃO existe nenhuma rotina
    Quando usuário executa "habit create --title 'Academia'"
    Então sistema exibe wizard interativo:
      """
      [ERROR] Nenhuma rotina existe
      
      Para criar hábitos, primeiro crie uma rotina.
      
      Deseja criar uma rotina agora? (S/n): s
      
      Nome da rotina: Rotina Matinal
      [OK] Rotina "Rotina Matinal" criada e ativada
      
      Agora você pode criar o hábito "Academia". Continuar? (S/n): s
      
      [OK] Hábito "Academia" criado na rotina "Rotina Matinal"
      """

  Cenário: routine init cria rotina padrão
    Dado que NÃO existe nenhuma rotina
    Quando usuário executa "routine init"
    Então sistema exibe wizard:
      """
      [INFO] Criar rotina padrão?
      
      Opções:
      1. Rotina Diária (recomendado para iniciantes)
      2. Criar rotina personalizada
      
      Escolha (1/2): 1
      [OK] Rotina "Minha Rotina Diária" criada e ativada
      
      Próximo passo: habit create --title "Seu Primeiro Hábito"
      """

  Cenário: Primeira rotina criada fica ativa automaticamente
    Dado que NÃO existe nenhuma rotina
    Quando usuário cria primeira rotina "Rotina Matinal"
    Então routine.is_active = True AUTOMATICAMENTE
    E sistema exibe:
      """
      [OK] Rotina "Rotina Matinal" criada e ativada automaticamente
      
      Como esta é sua primeira rotina, ela já está ativa.
      """
