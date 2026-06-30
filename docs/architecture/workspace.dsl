workspace "ATOMVS Time Planner Terminal" "Arquitetura C4 do planejador de blocos de tempo baseado em terminal." {

    model {

        // ---------------------------------------------------------------
        // Ator
        // ---------------------------------------------------------------
        usuario = person "Usuário" {
            description "Pessoa que planeja tempo e acompanha hábitos via terminal."
        }

        // ---------------------------------------------------------------
        // Sistemas externos
        // ---------------------------------------------------------------
        terminal = softwareSystem "Terminal / Console" {
            description "Emulador de terminal do sistema operacional."
            tags "Externa"
        }

        sistemaArquivos = softwareSystem "Sistema de Arquivos" {
            description "Armazena banco SQLite, backups e logs; segue especificação XDG Base Directory."
            tags "Externa"
        }

        richLib = softwareSystem "Rich" {
            description "Biblioteca Python de formatação de saída no terminal (tabelas, cores, painéis)."
            tags "Externa"
        }

        // ---------------------------------------------------------------
        // Sistema principal
        // ---------------------------------------------------------------
        atomvs = softwareSystem "ATOMVS" {
            description "Aplicação de planejamento de tempo por blocos e acompanhamento de hábitos no terminal."

            // -----------------------------------------------------------
            // Containers
            // -----------------------------------------------------------
            cli = container "CLI" {
                description "Interface de linha de comando; comandos: routine, habit, task, tag, timer, reschedule, init, demo."
                technology "Python / Typer"
            }

            tui = container "TUI" {
                description "Interface visual no terminal; telas: Dashboard, Rotinas, Hábitos, Tarefas, Timer."
                technology "Python / Textual"

                // Componentes da TUI
                compApp = component "TimeBlockApp" {
                    description "Classe principal do Textual; gerencia telas, keybindings e ciclo de vida."
                    technology "Textual App"
                }
                compDashboard = component "DashboardScreen" {
                    description "Tela principal; orquestra AgendaPanel, HabitsPanel, TasksPanel, TimerPanel e MetricsPanel."
                    technology "Textual Screen"
                }
                compLoader = component "Loader" {
                    description "Módulo de carregamento de dados; chama serviços e retorna dicts para os painéis."
                    technology "Python"
                }
                compCrudHabits = component "CRUD Hábitos" {
                    description "Módulo de operações CRUD de hábitos no dashboard (criar, marcar, pular, excluir)."
                    technology "Python"
                }
                compCrudTasks = component "CRUD Tarefas" {
                    description "Módulo de operações CRUD de tarefas no dashboard (criar, concluir, reagendar, excluir)."
                    technology "Python"
                }
                compCrudRoutines = component "CRUD Rotinas" {
                    description "Módulo de operações CRUD de rotinas no dashboard (criar, ativar, excluir)."
                    technology "Python"
                }
                compAgendaPanel = component "AgendaPanel" {
                    description "Painel de linha do tempo do dia com blocos de 15 minutos."
                    technology "Textual Widget"
                }
                compHabitsPanel = component "HabitsPanel" {
                    description "Painel que exibe instâncias de hábitos do dia agrupadas por hábito."
                    technology "Textual Widget"
                }
                compTasksPanel = component "TasksPanel" {
                    description "Painel que exibe tarefas em 4 grupos: pendentes, próximas, concluídas e canceladas."
                    technology "Textual Widget"
                }
                compTimerPanel = component "TimerPanel" {
                    description "Painel de exibição do timer ativo com controles de início, pausa e parada."
                    technology "Textual Widget"
                }
                compFormModal = component "FormModal" {
                    description "Modal genérico de formulário para captura de dados do usuário."
                    technology "Textual Screen"
                }
                compConfirmDialog = component "ConfirmDialog" {
                    description "Modal de confirmação sim/não."
                    technology "Textual Screen"
                }
                compNavBar = component "NavBar" {
                    description "Barra lateral de navegação entre telas."
                    technology "Textual Widget"
                }
                compHeaderBar = component "HeaderBar" {
                    description "Barra superior com rotina ativa, data e métricas."
                    technology "Textual Widget"
                }
                compStatusBar = component "StatusBar" {
                    description "Barra de rodapé com dicas contextuais por painel focado."
                    technology "Textual Widget"
                }
            }

            servicos = container "Camada de Serviços" {
                description "Lógica de negócio da aplicação."
                technology "Python"

                // Componentes de serviço
                svcRoutine = component "RoutineService" {
                    description "CRUD de rotinas; ativação exclusiva, soft delete, auto-ativação da primeira rotina."
                    technology "Python / SQLModel Session"
                }
                svcHabit = component "HabitService" {
                    description "CRUD de hábitos; soft delete (archived_at), hard delete com cascade."
                    technology "Python / SQLModel Session"
                }
                svcHabitInstance = component "HabitInstanceService" {
                    description "Geração de instâncias por recorrência; marcação de conclusão, pulo e ajuste de horário."
                    technology "Python / SQLModel Session"
                }
                svcTask = component "TaskService" {
                    description "Ciclo de vida de tarefas: criação, conclusão, cancelamento, reabertura, reagendamento."
                    technology "Python / SQLModel Session"
                }
                svcTimer = component "TimerService" {
                    description "Máquina de estados do timer: RUNNING, PAUSED, DONE, CANCELLED; cálculo de duração."
                    technology "Python / SQLModel Session"
                }
                svcTag = component "TagService" {
                    description "CRUD de tags com validação de unicidade case-insensitive."
                    technology "Python / SQLModel Session"
                }
                svcEventReordering = component "EventReorderingService" {
                    description "Detecção de conflitos de sobreposição temporal entre tarefas, instâncias e eventos."
                    technology "Python / SQLModel Session"
                }
                svcBackup = component "BackupService" {
                    description "Backup timestamped do banco; limite de 50 cópias; restauração com pré-backup."
                    technology "Python / shutil"
                }
            }

            modelos = container "Modelos" {
                description "Entidades de domínio: Routine, Habit, HabitInstance, Task, Event, Tag, TimeLog; enums de status."
                technology "Python / SQLModel"
            }

            banco = container "Banco de Dados" {
                description "Persistência local em ~/.local/share/atomvs/atomvs.db; PRAGMA foreign_keys=ON; migrações automáticas."
                technology "SQLite"
                tags "Banco"
            }

            utilitarios = container "Utilitários" {
                description "Logger JSON estruturado, validadores de entrada, helpers e parser de datas."
                technology "Python"
            }
        }

        // ---------------------------------------------------------------
        // Relações — contexto do sistema
        // ---------------------------------------------------------------
        usuario -> atomvs "Planeja tempo e acompanha hábitos" "Terminal"
        atomvs -> terminal "Renderiza interface" "stdout/stdin"
        atomvs -> sistemaArquivos "Persiste dados, backups e logs" "I/O de arquivos"
        atomvs -> richLib "Formata saída no terminal" "API Python"

        // ---------------------------------------------------------------
        // Relações — containers
        // ---------------------------------------------------------------
        usuario -> cli "Executa comandos (atomvs routine create, ...)" "Terminal"
        usuario -> tui "Interage visualmente (atomvs sem argumentos)" "Terminal"

        cli -> servicos "Invoca operações de negócio"
        tui -> servicos "Invoca operações de negócio via service_action()"

        servicos -> modelos "Manipula entidades de domínio"
        modelos -> banco "Persiste e consulta dados" "SQLAlchemy / SQLModel"

        cli -> richLib "Formata tabelas e saída colorida" "API Python"
        tui -> richLib "Formata renderização de painéis" "API Python"
        tui -> terminal "Renderiza interface TUI" "stdout/stdin"
        cli -> terminal "Exibe saída formatada" "stdout/stdin"

        banco -> sistemaArquivos "Armazena atomvs.db" "I/O de arquivos"
        servicos -> utilitarios "Usa validação, logging e helpers de data"
        utilitarios -> sistemaArquivos "Escreve logs JSON" "I/O de arquivos"

        // ---------------------------------------------------------------
        // Relações — componentes da TUI
        // ---------------------------------------------------------------
        compApp -> compDashboard "Monta e exibe tela principal"
        compApp -> compNavBar "Compõe barra lateral de navegação"
        compApp -> compHeaderBar "Compõe barra superior"
        compApp -> compStatusBar "Compõe barra de rodapé"

        compDashboard -> compLoader "Carrega dados para os painéis"
        compDashboard -> compCrudHabits "Delega operações CRUD de hábitos"
        compDashboard -> compCrudTasks "Delega operações CRUD de tarefas"
        compDashboard -> compCrudRoutines "Delega operações CRUD de rotinas"
        compDashboard -> compAgendaPanel "Compõe painel de agenda"
        compDashboard -> compHabitsPanel "Compõe painel de hábitos"
        compDashboard -> compTasksPanel "Compõe painel de tarefas"
        compDashboard -> compTimerPanel "Compõe painel de timer"

        compCrudHabits -> compFormModal "Abre formulário de hábito"
        compCrudHabits -> compConfirmDialog "Abre confirmação de exclusão"
        compCrudTasks -> compFormModal "Abre formulário de tarefa"
        compCrudTasks -> compConfirmDialog "Abre confirmação de exclusão"
        compCrudRoutines -> compFormModal "Abre formulário de rotina"
        compCrudRoutines -> compConfirmDialog "Abre confirmação de exclusão"

        compLoader -> svcRoutine "Carrega rotina ativa"
        compLoader -> svcHabitInstance "Carrega e gera instâncias"
        compLoader -> svcHabit "Carrega hábitos"
        compLoader -> svcTask "Carrega tarefas pendentes"
        compLoader -> svcTimer "Carrega timer ativo"
        compLoader -> svcEventReordering "Carrega conflitos do dia"

        compCrudHabits -> svcHabit "Cria/edita/exclui hábito"
        compCrudHabits -> svcHabitInstance "Marca conclusão/pulo de instância"
        compCrudHabits -> svcTimer "Consulta timer ativo"
        compCrudTasks -> svcTask "Cria/conclui/cancela/reagenda tarefa"
        compCrudTasks -> svcEventReordering "Detecta conflitos ao reagendar"
        compCrudRoutines -> svcRoutine "Cria/ativa/exclui rotina"
        compCrudRoutines -> svcHabit "Consulta hábitos da rotina"

        // ---------------------------------------------------------------
        // Relações — componentes dos serviços
        // ---------------------------------------------------------------
        svcHabitInstance -> svcEventReordering "Detecta conflitos ao ajustar horário"
        svcTask -> svcEventReordering "Detecta conflitos ao reagendar"
        svcBackup -> sistemaArquivos "Copia e restaura arquivo do banco" "shutil"

        svcRoutine -> modelos "Manipula Routine e Habit"
        svcHabit -> modelos "Manipula Habit e TimeLog"
        svcHabitInstance -> modelos "Manipula HabitInstance, Habit e TimeLog"
        svcTask -> modelos "Manipula Task"
        svcTimer -> modelos "Manipula TimeLog e HabitInstance"
        svcTag -> modelos "Manipula Tag"
        svcEventReordering -> modelos "Consulta Task, HabitInstance e Event"

        // ---------------------------------------------------------------
        // Nó de deployment
        // ---------------------------------------------------------------
        deploymentEnvironment "Local" {
            deploymentNode "Máquina do Usuário" {
                description "Computador pessoal com terminal."
                technology "Linux / macOS / Windows (WSL)"

                deploymentNode "Processo Python" {
                    description "Interpretador Python 3.14 executando o ATOMVS."
                    technology "CPython 3.14"

                    cliInstance = containerInstance cli
                    tuiInstance = containerInstance tui
                    servicosInstance = containerInstance servicos
                    modelosInstance = containerInstance modelos
                    utilInstance = containerInstance utilitarios
                }

                deploymentNode "Sistema de Arquivos Local" {
                    description "Diretório XDG: ~/.local/share/atomvs/"
                    technology "ext4 / APFS / NTFS"

                    bancoInstance = containerInstance banco
                }
            }
        }
    }

    views {

        // ---------------------------------------------------------------
        // Vista de contexto do sistema
        // ---------------------------------------------------------------
        systemContext atomvs "ContextoDoSistema" {
            title "ATOMVS — Contexto do Sistema (C4 Nível 1)"
            include *
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista de containers
        // ---------------------------------------------------------------
        container atomvs "Containers" {
            title "ATOMVS — Containers (C4 Nível 2)"
            include *
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista de componentes — TUI
        // ---------------------------------------------------------------
        component tui "ComponentesTUI" {
            title "TUI — Componentes (C4 Nível 3)"
            include *
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista de componentes — Camada de Serviços
        // ---------------------------------------------------------------
        component servicos "ComponentesServicos" {
            title "Camada de Serviços — Componentes (C4 Nível 3)"
            include *
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista dinâmica — Criar um hábito via TUI
        // ---------------------------------------------------------------
        dynamic atomvs "FluxoCriarHabito" {
            title "Fluxo: Criar um hábito via TUI"
            usuario -> tui "Pressiona tecla 'n' no painel de hábitos"
            tui -> servicos "Chama HabitService.create_habit() via service_action()"
            servicos -> modelos "Instancia entidade Habit com recorrência"
            modelos -> banco "INSERT INTO habits (...)"
            modelos -> banco "INSERT INTO habitinstance (...) para cada data"
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista dinâmica — Ciclo do timer
        // ---------------------------------------------------------------
        dynamic atomvs "FluxoTimerCompleto" {
            title "Fluxo: Ciclo completo do timer (iniciar, pausar, retomar, parar)"
            usuario -> tui "Pressiona 's' para iniciar timer na instância"
            tui -> servicos "TimerService.start_timer(habit_instance_id)"
            servicos -> modelos "Cria TimeLog com status=RUNNING"
            modelos -> banco "INSERT INTO time_log (...)"
            usuario -> tui "Pressiona 'p' para pausar"
            tui -> servicos "TimerService.pause_timer(timelog_id)"
            servicos -> modelos "Atualiza status=PAUSED, registra pause_start"
            usuario -> tui "Pressiona 'p' para retomar"
            tui -> servicos "TimerService.resume_timer(timelog_id)"
            servicos -> modelos "Atualiza status=RUNNING, acumula paused_duration"
            usuario -> tui "Pressiona Enter para parar"
            tui -> servicos "TimerService.stop_timer(timelog_id)"
            servicos -> modelos "Calcula duração, determina substatus, atualiza HabitInstance"
            modelos -> banco "UPDATE time_log e habitinstance"
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista dinâmica — Carregar dashboard
        // ---------------------------------------------------------------
        dynamic atomvs "FluxoCarregarDashboard" {
            title "Fluxo: Renderizar o dashboard (carregamento de dados)"
            usuario -> tui "Inicia aplicação (atomvs sem argumentos)"
            tui -> servicos "Loader.ensure_today_instances() gera instâncias do dia"
            servicos -> modelos "Consulta hábitos da rotina ativa"
            modelos -> banco "SELECT hábitos e instâncias existentes"
            servicos -> modelos "Gera instâncias faltantes"
            modelos -> banco "INSERT INTO habitinstance (...)"
            tui -> servicos "Loader carrega rotina, instâncias, tarefas, timer e métricas"
            servicos -> modelos "Consulta todas as entidades necessárias"
            modelos -> banco "SELECT rotinas, instâncias, tarefas, timelogs"
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista dinâmica — Persistir estado (backup)
        // ---------------------------------------------------------------
        dynamic atomvs "FluxoPersistirEstado" {
            title "Fluxo: Persistir estado (commit e backup)"
            tui -> servicos "service_action() envolve chamada em sessão"
            servicos -> modelos "Executa operação na entidade"
            modelos -> banco "Transação SQLAlchemy: INSERT/UPDATE/DELETE"
            banco -> sistemaArquivos "SQLite persiste em atomvs.db"
            tui -> servicos "BackupService.create_backup() no encerramento"
            servicos -> sistemaArquivos "Copia atomvs.db com timestamp para backups/"
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Vista de deployment
        // ---------------------------------------------------------------
        deployment atomvs "Local" "DeploymentLocal" {
            title "ATOMVS — Deployment Local"
            include *
            autolayout lr
        }

        // ---------------------------------------------------------------
        // Estilos
        // ---------------------------------------------------------------
        styles {
            element "Person" {
                shape Person
                background #4a90d9
                color #ffffff
                fontSize 22
            }
            element "Software System" {
                background #2d8cf0
                color #ffffff
                shape RoundedBox
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Externa" {
                background #999999
                color #ffffff
            }
            element "Banco" {
                shape Cylinder
            }
        }

    }

}
