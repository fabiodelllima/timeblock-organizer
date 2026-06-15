# TUI

A TUI (Terminal User Interface) é a segunda interface do TimeBlock Planner, projetada para o uso interativo diário que a CLI, por sua natureza sequencial, não consegue atender com a mesma fluidez. Consultar a agenda, marcar hábitos como concluídos, iniciar um timer e verificar métricas são operações que no CLI exigem múltiplos comandos separados; na TUI, estão a um ou dois keybindings de distância, visíveis simultaneamente na mesma tela.

A TUI foi implementada com o framework Textual (ADR-031), que utiliza Rich internamente — uma dependência que o projeto já possui para a formatação do output da CLI. A decisão arquitetural mais importante é que a TUI compartilha 100% da camada de services com a CLI: nenhuma lógica de negócio é duplicada. A TUI é exclusivamente interface — captura input do usuário, chama o service apropriado com uma session de banco de dados efêmera (session-per-action), e exibe o resultado com widgets estilizados. Se um service funciona na CLI, funciona na TUI; se uma regra de negócio muda, muda em um único lugar.

O design visual segue um sistema Material-like com paleta de cores definida em TCSS (arquivo único, single source of truth), cards com bordas arredondadas, spacing consistente e hierarquia visual clara entre texto primário, secundário e metadados. A TUI opera em cinco screens navegáveis por sidebar (Dashboard, Routines, Habits, Tasks, Timer), cada uma com keybindings específicos documentados nas BRs a seguir. O Dashboard concentra a visão do dia com alta densidade informacional; a tela de Rotinas exibe a semana completa em grade temporal; as demais screens oferecem CRUD completo com formulários inline.

**Referências:** ADR-006 (decisão original), ADR-031 (implementação), ADR-007 (service layer)

**Convenção de marcadores no heading das BRs:**

- **(NOVA dd/mm/aaaa):** primeira publicação da BR. Data de criação.
- **(EMENDADA dd/mm/aaaa):** cláusulas pontuais alteradas, estrutura geral preservada. Data da última emenda.
- **(REVISADA dd/mm/aaaa):** reescrita substancial (>30% das cláusulas ou mudança de premissa). Data da última revisão.

A data entre parênteses é sempre a da última alteração. Data de criação original rastreável via `git log`.


---

### BR-TUI-001: Entry Point Detection

**Descrição:** O binário `timeblock` sem argumentos abre a TUI. Com argumentos, executa CLI normalmente. Se Textual não está instalado, exibe mensagem de orientação.

**Regras:**

1. `timeblock` (sem args) → Abre TUI
2. `timeblock <qualquer-arg>` → Executa CLI (Typer)
3. `timeblock --help` → Help da CLI (tem argumento)
4. Se Textual não instalado e sem args → Mensagem orientando instalação
5. CLI NUNCA depende de Textual (import condicional)

**Implementação:**

```python
import sys

def main():
    if len(sys.argv) <= 1:
        try:
            from timeblock.tui.app import TimeBlockApp
            TimeBlockApp().run()
        except ImportError:
            print("[WARN] TUI requer 'textual'.")
            print("       Instale: pip install timeblock-organizer[tui]")
            print("       Uso CLI: timeblock --help")
    else:
        app()  # Typer
```

**Testes:**

- `test_br_tui_001_no_args_launches_tui`
- `test_br_tui_001_with_args_launches_cli`
- `test_br_tui_001_help_uses_cli`
- `test_br_tui_001_fallback_without_textual`

---

### BR-TUI-002: Screen Navigation

**Descrição:** A TUI possui 5 screens navegáveis por sidebar. Navegação por keybindings numéricos ou mnemônicos. Apenas uma screen ativa por vez.

**Regras:**

1. Screens disponíveis: Dashboard, Routines, Habits, Tasks, Timer
2. Screen inicial ao abrir: Dashboard
3. Keybindings numéricos: `1`=Dashboard, `2`=Routines, `3`=Habits, `4`=Tasks, `5`=Timer
4. Keybindings mnemônicos: `d`=Dashboard, `r`=Routines, `h`=Habits, `t`=Tasks, `m`=Timer (de "medidor")
5. Sidebar exibe todas as screens com indicador da screen ativa
6. Navegação preserva estado da screen anterior (não reseta dados em edição)

**Testes:**

- `test_br_tui_002_initial_screen_is_dashboard`
- `test_br_tui_002_numeric_keybinding_navigation`
- `test_br_tui_002_mnemonic_keybinding_navigation`
- `test_br_tui_002_sidebar_shows_active_screen`

---

### BR-TUI-003: Dashboard Screen

**Descrição:** O Dashboard exibe visão completa e interativa do dia corrente com alta densidade informacional. Layout híbrido composto por: header bar com contexto resumido, agenda vertical estilo Google Calendar com blocos de tempo proporcionais, e grid de cards (hábitos, tarefas, timer, métricas). Serve como ponto de entrada principal e painel de controle diário.

**Referências:** ADR-031 seção 4, BR-TUI-008 (visual), BR-TUI-009 (services)

**Regras:**

1. **Header Bar:** barra compacta (3 linhas) exibe rotina ativa, progresso do dia (X/Y hábitos + barra visual + percentual), contagem de tarefas pendentes, timer ativo (se houver) e data atual. Se não há rotina ativa, exibe "[Sem rotina]" com orientação para criar/ativar
2. **Agenda do Dia (timeline vertical):** coluna esquerda do conteúdo. Régua de tempo com granularidade de 30 minutos (06:00, 06:30, 07:00, ..., 22:00) e blocos proporcionais à duração — um bloco de 30min ocupa 1 slot visual, um de 1h ocupa 2 slots, etc. Cada bloco exibe: nome do evento, status com cor, duração formatada (Xmin para < 60, Xh ou XhYY para >= 60). Marcador `▸` indica slot atual. Blocos concluídos usam `░` ($success), ativo usa `▓` ($primary-light), pendentes usam `┄` ($muted), skipados usam `╌` ($warning). Horários livres entre blocos exibem `┈ livre ┈` centralizado. Conflitos (overlaps) renderizam blocos lado a lado divididos por `│`
3. **Card Hábitos:** lista instâncias do dia com indicador de status (✓ done, ▶ running, ✗ skipped, ! missed, · pending), nome, horário início–fim, duração real/planejada e sparkline de esforço relativo (◼◼◼). Título inclui contador X/Y. Quick actions: `enter`=done (solicita duração), `s`=skip (solicita categoria), `g`=navegar para screen Habits
4. **Card Tarefas:** lista tarefas pendentes com indicador de prioridade (!! overdue+alta, ! alta, ▪ média, · baixa), nome, prioridade, deadline abreviado. Tarefas vencidas destacadas em $error com marcador `venc.`. Quick actions: `enter`=detalhes, `c`=concluir, `g`=navegar para screen Tasks
5. **Card Timer:** display centralizado com tempo decorrido, evento associado e status (▶ RUNNING, ⏸ PAUSED, ⏹ IDLE). Resumo do dia: sessões concluídas, tempo total acumulado, média por sessão. Keybindings contextuais (exibe apenas ações válidas para o estado atual). Se idle, exibe último timer concluído com horário
6. **Card Métricas:** streak atual e melhor streak, barras de completude 7d e 30d com percentual. Histórico semanal com barra de progresso + dot matrix por hábito (✓/·) por dia. Dia atual destacado com `← hoje`. Cores das barras: verde (≥ 80%), amarelo (50–79%), vermelho (< 50%). Filtro de período alternável com `f` (7d → 14d → 30d)
7. **Layout:** três colunas — sidebar fixa (22 chars), agenda do dia (coluna central, scroll vertical), cards em grid (coluna direita, 2 cards empilhados por subcoluna)
8. **Navegação entre zonas:** `Tab`/`Shift+Tab` navegam entre zonas focáveis (Agenda → Hábitos → Tarefas → Timer → Métricas → cicla). Cada zona tem keybindings próprios. `g` em qualquer zona navega para a screen completa correspondente
9. **Refresh:** dados atualizados ao entrar na screen (on_focus) e após qualquer quick action. Timer atualiza header e card Timer a cada segundo quando ativo
10. **Responsividade:** 3 breakpoints — ≥120 cols (completo: 3 colunas, agenda + cards), 80–119 cols (compacto: agenda reduzida, cards com conteúdo truncado), <80 cols (minimal: layout 1 coluna, agenda oculta, cards empilhados verticalmente)

**Mockup de referência:** `docs/tui/dashboard-mockup-v3.md`

**Composição de widgets:**

```python
class DashboardScreen(Screen):
    """Dashboard principal com layout híbrido."""

    def compose(self) -> ComposeResult:
        yield HeaderBar(id="header-bar")
        with Horizontal(id="content"):
            yield AgendaWidget(id="agenda")
            with Vertical(id="cards"):
                yield HabitListWidget(id="habits-today")
                yield TaskListWidget(id="tasks-pending")
            with Vertical(id="cards-right"):
                yield TimerDisplayWidget(id="timer-display")
                yield MetricsPanelWidget(id="metrics-panel")
```

**Testes:**

- `test_br_tui_003_header_shows_routine_and_progress`
- `test_br_tui_003_header_shows_no_routine_message`
- `test_br_tui_003_header_shows_timer_active`
- `test_br_tui_003_header_shows_task_count`
- `test_br_tui_003_agenda_renders_day_blocks`
- `test_br_tui_003_agenda_shows_current_time_marker`
- `test_br_tui_003_agenda_block_colors_by_status`
- `test_br_tui_003_agenda_shows_free_slots`
- `test_br_tui_003_agenda_renders_conflict_side_by_side`
- `test_br_tui_003_agenda_running_block_with_projection`
- `test_br_tui_003_habits_list_with_status_and_time`
- `test_br_tui_003_habits_shows_effort_sparkline`
- `test_br_tui_003_habits_quick_done_action`
- `test_br_tui_003_habits_quick_skip_action`
- `test_br_tui_003_habits_go_to_screen`
- `test_br_tui_003_tasks_sorted_by_priority`
- `test_br_tui_003_tasks_overdue_highlighted`
- `test_br_tui_003_tasks_quick_complete_action`
- `test_br_tui_003_timer_shows_active_session`
- `test_br_tui_003_timer_shows_idle_with_last_session`
- `test_br_tui_003_timer_shows_session_summary`
- `test_br_tui_003_timer_contextual_keybindings`
- `test_br_tui_003_metrics_shows_streak`
- `test_br_tui_003_metrics_shows_weekly_history`
- `test_br_tui_003_metrics_dot_matrix_per_habit`
- `test_br_tui_003_metrics_period_filter`
- `test_br_tui_003_metrics_bar_colors_by_threshold`
- `test_br_tui_003_responsive_compact_layout`
- `test_br_tui_003_responsive_minimal_layout`
- `test_br_tui_003_tab_navigates_zones`
- `test_br_tui_003_refreshes_on_focus`
- `test_br_tui_003_refreshes_after_quick_action`
- `test_br_tui_003_timer_updates_every_second`

---

## BR-TUI-004: Global Keybindings (REVISADA 15/03/2026, EMENDADA 28/05/2026)

**Descrição:** Keybindings padronizados em toda a aplicação conforme ADR-037. Teclas simples sem modificador. CRUD contextual (n/e/x). Quick actions por panel (v/s/u/c/t). Uma ação = um binding.

**Mapa de keybindings:**

```plaintext
GLOBAIS (app.py):
  1..5 ................. trocar screen (1=Dash, 2=Rotin, 3=Habit, 4=Tasks, 5=Timer)
  Ctrl+Q ............... sair da TUI [MODAL de confirmação]
  ? .................... help overlay (toggle)
  Escape ............... fechar modal / fechar help / voltar ao Dashboard

NAVEGAÇÃO (intra-screen):
  Tab .................. avançar entre panels
  j / seta baixo ....... próximo item no panel focado
  i / seta cima ........ item anterior no panel focado
  Enter ................ ativar placeholder / selecionar item

CRUD (contextual ao panel focado):
  n .................... novo (abre FormModal contextual)
  e .................... editar item sob cursor (abre FormModal)
  x .................... deletar item sob cursor [MODAL]
  r .................... trocar rotina ativa [MODAL] (DT-047)

HABITS PANEL (quick actions):
  v .................... marcar done [MODAL de substatus - BR-TUI-022]
  s .................... skip [MODAL de SkipReason - BR-TUI-024]
  t .................... iniciar timer para hábito selecionado
  u .................... undo (reverter para pending)

TASKS PANEL (quick actions):
  v .................... completar task
  s .................... adiar task (abre FormModal de edit - ADR-038 D5)
  c .................... cancelar task (soft delete)
  u .................... reabrir task cancelada

TIMER PANEL (quick actions):
  space ................ pausar / retomar timer
  s .................... parar timer (stop - marca hábito como done)
  c .................... cancelar timer [MODAL]

PROIBIDOS (reservados pelo OS - ADR-035):
  Ctrl+C ............... SIGINT (nunca capturar)
  Ctrl+Z ............... SIGTSTP (nunca capturar)
  Ctrl+D ............... EOF (nunca capturar)
```

**Modal de confirmação exigido em:**

- x (deletar item - ConfirmDialog)
- c no timer panel (cancelar timer, descarta sessão - ConfirmDialog)
- v no habits panel (done manual - modal de substatus, BR-TUI-022)
- v com timer ativo (notificação com opções - BR-TUI-023)
- s no habits panel (skip - modal de SkipReason, BR-TUI-024)
- Ctrl+Q (sair da TUI - ConfirmDialog, regra 16)

**Regras:**

1. 1..5 sem modificador troca screen (ADR-037)
2. Tab cicla entre panels; j/k ou setas movem cursor dentro do panel
3. n/e/x sem modificador para CRUD - x sempre abre ConfirmDialog
4. v e o binding de "concluir/done" - abre modal no habits, executa direto no tasks
5. s e contextual: skip (habits), postpone/edit (tasks), stop (timer)
6. t inicia timer para hábito selecionado
7. u e undo/reopen - reverte status em ambos os panels
8. space e toggle de pause/resume exclusivo do timer panel
9. c e cancelar - soft delete (tasks), cancel com ConfirmDialog (timer)
10. Enter ativa placeholders (BR-TUI-013) ou seleciona item
11. Ações que alteram estado devem usar modal (ADR-038 D12)
12. Ctrl+C, Ctrl+Z, Ctrl+D nunca são capturados pela TUI
13. Help overlay (?) lista todos os keybindings - toggle
14. Footer contextual (BR-TUI-007) exibe bindings conforme panel focado
15. Modals respondem a Enter (confirmar) e Escape (cancelar)
16. Ctrl+Q abre ConfirmDialog antes de encerrar; Enter confirma e encerra, Escape cancela e mantém a TUI aberta. O backup de shutdown roda ao acionar Ctrl+Q, independentemente da confirmação. Havendo timer ativo, a mensagem do modal o menciona.

**Supersede:** Versão 08/03/2026. Removidos todos os Ctrl+/Shift+ (ADR-037).

**Referência:** ADR-037, ADR-038

**Testes:**

- `test_br_tui_004_1_to_5_switches_screen`
- `test_br_tui_004_ctrl_q_opens_confirm`
- `test_br_tui_004_quit_confirm_exits`
- `test_br_tui_004_quit_cancel_stays`
- `test_br_tui_004_quit_message_mentions_active_timer`
- `test_br_tui_004_escape_closes_modal`
- `test_br_tui_004_help_overlay_toggle`
- `test_br_tui_004_tab_advances_panels`
- `test_br_tui_004_ji_navigates_items`
- `test_br_tui_004_n_opens_contextual_modal`
- `test_br_tui_004_v_marks_done_with_modal`
- `test_br_tui_004_s_skips_with_reason`
- `test_br_tui_004_t_starts_timer`
- `test_br_tui_004_u_undoes_action`
- `test_br_tui_004_space_toggles_pause`
- `test_br_tui_004_c_cancels_with_confirm`
- `test_br_tui_004_x_deletes_with_confirm`

---

### BR-TUI-005: CRUD Operations Pattern

**Descrição:** Todas as screens com CRUD seguem padrão consistente de interação. Create e Update usam formulários inline. Delete requer confirmação.

**Regras:**

1. `n` ou `a` → Novo item (abre formulário inline)
2. `e` → Editar item selecionado
3. `x` → Deletar item selecionado (abre confirmação)
4. `enter` → Ver detalhes do item selecionado
5. Confirmação de delete exibe nome do item e requer `y` explícito
6. Operações de escrita usam session-per-action (ADR-031)
7. Após operação bem-sucedida, lista atualizada automaticamente
8. Erros de validação exibidos inline (não modal)

**Testes:**

- `test_br_tui_005_create_opens_form`
- `test_br_tui_005_edit_opens_prefilled_form`
- `test_br_tui_005_delete_requires_confirmation`
- `test_br_tui_005_delete_confirmation_shows_name`
- `test_br_tui_005_successful_operation_refreshes_list`
- `test_br_tui_005_validation_error_shown_inline`

---

### BR-TUI-006: Timer Screen Live Display

**Descrição:** O Timer screen exibe contagem em tempo real com atualização a cada segundo. Suporta start, pause, resume, stop e cancel. Integra com TimerService existente.

**Regras:**

1. Display atualiza a cada 1 segundo (set_interval)
2. Keybindings de timer: `s`=start, `p`=pause/resume, `enter`=stop, `c`=cancel
3. Display mostra: tempo decorrido, evento associado, status (running/paused)
4. Pause congela display; resume retoma contagem
5. Stop salva sessão e exibe resumo
6. Cancel descarta sessão com confirmação
7. Timer ativo visível na status bar de qualquer screen

**Testes:**

- `test_br_tui_006_timer_display_updates`
- `test_br_tui_006_start_keybinding`
- `test_br_tui_006_pause_resume_toggle`
- `test_br_tui_006_stop_saves_session`
- `test_br_tui_006_cancel_requires_confirmation`
- `test_br_tui_006_active_timer_in_status_bar`

---

### BR-TUI-007: Footer Contextual (REVISADA 25/02/2026)

**Descrição:** Barra de rodapé persistente com três seções: rotina ativa (esquerda, persistente), keybindings da zona focada (centro, contextual) e timer + hora (direita, persistente). O header exibe informação (o quê), o footer exibe ações (o que fazer).

**Layout:**

```plaintext
┌────────────────────────────────────────────────────────────────────────────┐
│ Rotina Matinal     │  Ctrl+Enter done  Ctrl+S skip    │ ▶ 47:23      14:32 │
└────────────────────────────────────────────────────────────────────────────┘
  c_left (1fr)         c_center (1fr)                     c_right (auto)
```

**Keybindings por zona focada:**

| Zona    | Footer center                                 |
| ------- | --------------------------------------------- |
| Agenda  | `Ctrl+Enter done  Ctrl+S skip`                |
| Hábitos | `Ctrl+Enter done  Ctrl+S skip`                |
| Tarefas | `Ctrl+K complete  Ctrl+Enter detalhe`         |
| Timer   | `Ctrl+S start  Ctrl+P pause  Ctrl+Enter stop` |
| Nenhum  | `Tab navegar  ? ajuda  Ctrl+Q sair`           |

**Regras:**

1. Posição: rodapé, largura total, 1 linha de altura
2. Seção esquerda: nome da rotina ativa. "[Sem rotina]" se nenhuma
3. Seção central: keybindings da zona/card focado. Atualiza em on_focus
4. Seção direita: timer elapsed (atualiza 1s) + hora HH:MM (atualiza 1min)
5. Tecla em Overlay0 #6C7086, label da ação em Subtext0 #A6ADC8
6. Timer exibe ícone de estado: ▶ (running, Mauve #CBA6F7), ⏸ (paused, Yellow #F9E2AF)
7. Se nenhum timer ativo, seção direita exibe apenas hora
8. Footer visível em todas as screens, não apenas no Dashboard

**Testes:**

- `test_br_tui_007_footer_shows_active_routine`
- `test_br_tui_007_footer_shows_no_routine`
- `test_br_tui_007_footer_shows_current_time`
- `test_br_tui_007_footer_keybindings_change_on_focus`
- `test_br_tui_007_footer_agenda_zone_keybindings`
- `test_br_tui_007_footer_habits_zone_keybindings`
- `test_br_tui_007_footer_tasks_zone_keybindings`
- `test_br_tui_007_footer_timer_zone_keybindings`
- `test_br_tui_007_footer_default_keybindings`
- `test_br_tui_007_footer_timer_updates_every_second`

---

### BR-TUI-003-R12: Viewport-Aware Truncation

**Descrição:** Cards não definem limite fixo de itens. A quantidade exibida é determinada pela altura disponível do viewport. Itens que excedem o viewport são indicados por overflow indicator.

**Regras:**

1. Máximo de itens visíveis = viewport_height do card - 2 (bordas)
2. Se total > visíveis, exibe `+N ▼` no rodapé interno, alinhado à direita
3. Cor do indicador: Overlay0 #6C7086
4. Scroll interno com j/k quando card está focado (Tab)
5. Item selecionado (cursor) indicado por fundo Surface0 #313244
6. Scroll mantém item selecionado visível (auto-scroll)

**Testes:**

- `test_br_tui_003_r12_no_fixed_item_limit`
- `test_br_tui_003_r12_overflow_indicator_shown`
- `test_br_tui_003_r12_overflow_count_correct`
- `test_br_tui_003_r12_scroll_with_jk`
- `test_br_tui_003_r12_selected_item_always_visible`

---

### BR-TUI-003-R13: Régua de Horário Adaptativa (EMENDADA 14/03/2026)

**Descrição:** A agenda exibe range de horários adaptativo ao conteúdo do dia, cobrindo de 00:00 a 23:30 conforme necessidade. Default compacto quando não há eventos fora do horário comercial.

**Algoritmo:**

```python
if not instances:
    range_start, range_end = 10, 47   # 05:00–23:30 (default)
else:
    first_slot = min(i["start_minutes"] // 30 for i in instances)
    last_slot  = max(-(-i["end_minutes"] // 30) for i in instances)  # ceil
    range_start = max(0, first_slot - 2)     # 1h padding antes
    range_end   = min(47, last_slot + 2)     # 1h padding depois
    range_start = min(range_start, 10)       # nunca acima de 05:00
    range_end   = max(range_end, 47)         # nunca abaixo de 23:30
```

**Regras:**

1. Range adaptativo: expande para cobrir todos os eventos com 1h de padding
2. Piso absoluto: 00:00 (slot 0) — hábitos de madrugada são visíveis
3. Teto absoluto: 23:30 (slot 47) — cobre até meia-noite
4. Range mínimo garantido: 05:00–23:30 (slots 10–47) — nunca menor que isso
5. Granularidade: 30 minutos = 2 linhas (header + fill)
6. Se nenhum evento no dia, exibe 05:00–23:30

**Emenda:** Removido piso fixo de 06:00 e teto de 22:00 da versão anterior. Range mínimo agora é 05:00–23:30, cobrindo o dia completo. Hábitos de madrugada (antes das 05:00) expandem o range para baixo.

**Testes:**

- `test_br_tui_003_r13_range_adapts_to_events`
- `test_br_tui_003_r13_default_range_no_events`
- `test_br_tui_003_r13_early_event_extends_range`
- `test_br_tui_003_r13_late_event_extends_range`
- `test_br_tui_003_r13_madrugada_event_visible`
- `test_br_tui_003_r13_minimum_range_05_2330`
- `test_br_tui_003_r13_granularity_30min`
- `test_br_tui_003_r13_padding_one_hour`

---

### BR-TUI-003-R14: Subtítulo do Card Hábitos

**Descrição:** O border_title do card Hábitos exibe dot matrix com contagem e percentual de completude do dia.

**Formato:** `●●●○○○ X/Y Z%` onde ● = done/running, ○ = pending/not_done

**Regras:**

1. X = instâncias com status done (qualquer substatus) + running
2. Y = total de instâncias agendadas para hoje
3. Z = percentual (X / Y \* 100), arredondado
4. Dot matrix: 1 dot por instância, ● preenchido, ○ vazio
5. Máximo de dots exibidos: min(Y, 10). Se Y > 10, exibe apenas X/Y Z%
6. Cor dos ● e do Z%: Green #A6E3A1 (>= 80%), Yellow #F9E2AF (50-79%), Red #F38BA8 (< 50%)
7. Cor dos ○: Overlay0 #6C7086

**Testes:**

- `test_br_tui_003_r14_dot_matrix_count`
- `test_br_tui_003_r14_percentage_calculation`
- `test_br_tui_003_r14_color_green_above_80`
- `test_br_tui_003_r14_color_yellow_50_to_79`
- `test_br_tui_003_r14_color_red_below_50`
- `test_br_tui_003_r14_max_10_dots`
- `test_br_tui_003_r14_running_counts_as_done`

---

### BR-TUI-003-R15: Auto-scroll na Agenda

**Descrição:** Ao abrir o dashboard, a agenda faz scroll automático para posicionar a hora atual no terço superior do viewport.

**Regras:**

1. Ao montar a screen (on_mount), agenda faz scroll para hora atual
2. Posição: hora atual no terço superior do viewport visível
3. Se hora atual está antes do primeiro evento, scroll para o topo
4. Se hora atual está após o último evento, scroll para o final
5. Scroll automático ocorre apenas no mount, não a cada refresh

**Testes:**

- `test_br_tui_003_r15_autoscroll_on_mount`
- `test_br_tui_003_r15_current_time_upper_third`
- `test_br_tui_003_r15_no_scroll_if_fits_viewport`

---

### BR-TUI-003-R16: Marcador de Hora Atual

**Descrição:** O slot correspondente à hora atual recebe marcador visual ▸ no início da linha, cor Mauve #CBA6F7.

**Regras:**

1. Marcador `▸` posicionado antes do horário no slot atual
2. Cor do marcador: Mauve #CBA6F7
3. Slot atual = slot de 30min que contém a hora corrente
4. Apenas 1 marcador visível por vez
5. Marcador atualiza a cada 30 minutos (quando slot muda)

**Testes:**

- `test_br_tui_003_r16_marker_on_current_slot`
- `test_br_tui_003_r16_marker_color_mauve`
- `test_br_tui_003_r16_only_one_marker`

---

### BR-TUI-003-R17: Indicador de Tempo Livre

**Descrição:** Gaps de 30 minutos ou mais entre blocos exibem indicador `┈ livre ┈` centralizado em Overlay0 #6C7086.

**Regras:**

1. Gap = tempo entre end de um bloco e start do próximo
2. Gaps >= 30 minutos exibem `┈ livre ┈` centralizado
3. Gaps < 30 minutos não exibem indicador (só espaço vazio)
4. Cor do indicador: Overlay0 #6C7086
5. Proporcionalidade mantida: gap de 1h = 2 linhas (indicador na primeira)

**Testes:**

- `test_br_tui_003_r17_gap_30min_shows_indicator`
- `test_br_tui_003_r17_gap_under_30min_no_indicator`
- `test_br_tui_003_r17_indicator_centered`
- `test_br_tui_003_r17_indicator_color_overlay0`

---

### BR-TUI-003-R18: Effort Bar nos Hábitos

**Descrição:** Cada hábito exibe barra de esforço proporcional ao tempo real dedicado versus planejado. Fórmula: `filled = round((actual / planned) * 5)`, clamp [0, 7].

**Regras:**

1. Base: 5 dots. Overflow: até 7 dots (+40% max)
2. Dot cheio: `●`, cor do status
3. Dot vazio: `·`, Overlay0 #6C7086
4. Not_done (qualquer substatus): `─────`, cor do status
5. Pending (sem registro): `·····`, Overlay0
6. Largura fixa: 5 chars (base) + até 2 chars (overflow)

**Testes:**

- `test_br_tui_003_r18_100_percent_5_dots`
- `test_br_tui_003_r18_80_percent_4_dots`
- `test_br_tui_003_r18_overflow_120_percent_6_dots`
- `test_br_tui_003_r18_max_overflow_7_dots`
- `test_br_tui_003_r18_not_done_dashes`
- `test_br_tui_003_r18_pending_empty_dots`

---

### BR-TUI-003-R19: Ordenação dos Hábitos

**Descrição:** Hábitos no card são ordenados cronologicamente pelo horário de início planejado.

**Regras:**

1. Ordenação: ascendente por `start_time` do hábito
2. Hábitos sem horário definido ficam no final
3. Hábito com status running é sempre visível (auto-scroll se necessário)
4. Empate em horário: ordem alfabética por nome

**Testes:**

- `test_br_tui_003_r19_sorted_by_start_time`
- `test_br_tui_003_r19_no_time_at_end`
- `test_br_tui_003_r19_running_always_visible`

---

### BR-TUI-003-R20: Ordenação das Tarefas

**Descrição:** Tarefas no card são ordenadas por urgência, com concluídas e canceladas agrupadas no final.

**Regras:**

1. Grupo 1 (topo): overdue, ordenado por data ascendente (mais atrasada primeiro)
2. Grupo 2: pendentes, ordenado por proximidade ascendente (mais próxima primeiro)
3. Grupo 3 (final): done, ordenado por data de conclusão descendente
4. Grupo 4 (final): cancelled, ordenado por data descendente

**Testes:**

- `test_br_tui_003_r20_overdue_first`
- `test_br_tui_003_r20_pending_by_proximity`
- `test_br_tui_003_r20_done_after_pending`
- `test_br_tui_003_r20_cancelled_last`

### BR-TUI-003-R21: Overflow nos Cards

**Descrição:** Quando itens excedem o viewport do card, um indicador `+N ▼` é exibido no rodapé interno. Alias de BR-TUI-003-R12 para rastreabilidade com o spec original.

**Regras:** Ver BR-TUI-003-R12 (Viewport-Aware Truncation).

**Testes:** Mesmos de BR-TUI-003-R12.

---

### BR-TUI-003-R22: Strikethrough em Done/Cancelled

**Descrição:** Tarefas concluídas e canceladas exibem nome com strikethrough via Rich markup `[strike]nome[/strike]`.

**Regras:**

1. Strikethrough aplicado apenas ao campo nome (c1)
2. Aplica-se a: status done (qualquer substatus) e cancelled
3. Cor do nome mantém a cor do status (Green para done, Overlay0 para cancelled)
4. Demais colunas sem strikethrough

**Testes:**

- `test_br_tui_003_r22_done_task_strikethrough`
- `test_br_tui_003_r22_cancelled_task_strikethrough`
- `test_br_tui_003_r22_pending_no_strikethrough`
- `test_br_tui_003_r22_only_name_column`

---

### BR-TUI-003-R23: Subtítulo do Card Tarefas

**Descrição:** O border_title do card Tarefas exibe contadores por status com cores semânticas. Contadores com valor 0 são omitidos.

**Formato:** `N pend. N done N canc. N over.`

**Cores:** pend.=Text #CDD6F4, done=Green #A6E3A1, canc.=Overlay0 #6C7086, over.=Red #F38BA8

**Regras:**

1. Contadores com valor 0 são omitidos
2. Overdue = tarefa pendente com data no passado
3. Atualiza após cada quick action e on_focus

**Testes:**

- `test_br_tui_003_r23_shows_pending_count`
- `test_br_tui_003_r23_shows_overdue_count`
- `test_br_tui_003_r23_omits_zero_counters`
- `test_br_tui_003_r23_correct_colors`

---

### BR-TUI-003-R24: Períodos da Agenda

**Descrição:** A agenda agrupa blocos em 3 períodos fixos com separadores visuais: Manhã (06:00-12:00), Tarde (12:00-18:00), Noite (18:00-23:00). Cada período exibe header com nome, rotina associada e progresso X/Y.

**Separador:** `── Manhã ─── Rotina Matinal ──── 3/4 ──────`

**Regras:**

1. Períodos fixos: Manhã (06:00-12:00), Tarde (12:00-18:00), Noite (18:00-23:00)
2. Períodos sem eventos são ocultos (não renderizam separador)
3. Separador exibe: nome do período + rotina associada + progresso X/Y
4. X = eventos done + running no período. Y = total de eventos no período
5. Cor do progresso: Green (>= 80%), Yellow (50-79%), Red (< 50%)
6. Cor do nome do período e traços: Subtext0 #A6ADC8
7. Cor do nome da rotina: Text #CDD6F4
8. Se nenhuma rotina associada ao período: "[Sem rotina]" em Overlay0
9. Na v1.7, períodos são fixos. Customização em v1.8+ (SettingsScreen)

**Testes:**

- `test_br_tui_003_r24_three_periods`
- `test_br_tui_003_r24_empty_period_hidden`
- `test_br_tui_003_r24_separator_shows_routine_name`
- `test_br_tui_003_r24_separator_shows_progress`
- `test_br_tui_003_r24_progress_color_by_threshold`
- `test_br_tui_003_r24_no_routine_shows_placeholder`

---

### BR-TUI-003-R25: Timer Card Compacto

**Descrição:** O card Timer no dashboard ocupa 2 linhas de conteúdo (sem ASCII art). ASCII art fica exclusivamente na TimerScreen dedicada.

**Regras:**

1. Card ocupa 4 linhas totais (borda + 2 conteúdo + borda)
2. Sem ASCII art no dashboard
3. Estado running: ícone ▶ + nome + sessão X/Y + elapsed (Mauve #CBA6F7, 1s update)
4. Estado paused: ícone ⏸ + nome + sessão X/Y + elapsed piscando (Yellow #F9E2AF)
5. Estado idle: última sessão (nome + duração + hora) + resumo do dia
6. Border_title direita: `▶ ativo` (Mauve) / `⏸ paused` (Yellow) / `⏹ idle` (Overlay0)
7. Linha 2 sempre: resumo do dia `Hoje: N sessões · XhYYm total`

**Testes:**

- `test_br_tui_003_r25_running_shows_elapsed`
- `test_br_tui_003_r25_running_session_count`
- `test_br_tui_003_r25_paused_shows_yellow`
- `test_br_tui_003_r25_idle_shows_last_session`
- `test_br_tui_003_r25_idle_shows_day_summary`
- `test_br_tui_003_r25_no_ascii_art`
- `test_br_tui_003_r25_border_title_reflects_state`

---

### BR-TUI-003-R26: Cores Temporais na Régua

**Descrição:** Os horários na régua da agenda usam cores que indicam contexto temporal.

**Regras:**

1. Horários passados: Subtext0 #A6ADC8 (dim)
2. Horário atual: Mauve #CBA6F7, bold
3. Horários futuros: Text #CDD6F4 (normal)
4. "Atual" = slot de 30min que contém datetime.now()
5. Atualização: a cada 30 minutos (quando slot muda)

**Testes:**

- `test_br_tui_003_r26_past_hours_subtext0`
- `test_br_tui_003_r26_current_hour_mauve_bold`
- `test_br_tui_003_r26_future_hours_text`

---

### BR-TUI-003-R27: Herança de Cor por Status

**Descrição:** Em todos os cards, o campo nome herda a cor do status do item. Mapeamento definido em `color-system.md` (SSOT para cores).

**Mapeamento:** done/full=Green #A6E3A1, done/partial=Rosewater #F5E0DC, done/overdone=Flamingo #F2CDCD, done/excessive=Peach #FAB387, not_done/justified=Yellow #F9E2AF, not_done/unjustified=Red #F38BA8, not_done/ignored=Maroon #EBA0AC, running=Mauve #CBA6F7, paused=Yellow #F9E2AF, pending=Blue #89B4FA, cancelled=Overlay0 #6C7086

**Regras:**

1. Campo nome em todos os cards herda cor do status/substatus
2. Nome bold se running ou paused
3. Nome strikethrough se done ou cancelled (apenas tarefas, ver R22)
4. Aplicável a: card Agenda, card Hábitos, card Tarefas

**Testes:**

- `test_br_tui_003_r27_done_name_green`
- `test_br_tui_003_r27_running_name_mauve_bold`
- `test_br_tui_003_r27_pending_name_overlay0`
- `test_br_tui_003_r27_not_done_unjustified_name_red`

---

### BR-TUI-003-R28: Mock Data como Fixture

**Descrição:** Dados de demonstração não são fallback do dashboard. Mock data existe apenas em fixtures de teste e no comando `atomvs demo`. Dashboard com banco vazio exibe estado vazio com orientação ao usuário.

**Regras:**

1. Dashboard com banco vazio exibe mensagem de orientação por card
2. Mock data hardcoded removido do `dashboard.py`
3. Mock data migrado para `tests/unit/test_tui/conftest.py` como fixtures
4. Comando `atomvs demo` cria rotina demo no banco (feature separada)
5. Mensagem de orientação indica ação concreta (keybinding ou comando CLI)
6. Cor da mensagem: Subtext0 #A6ADC8
7. Texto centralizado verticalmente no card

**Testes:**

- `test_br_tui_003_r28_empty_db_shows_orientation`
- `test_br_tui_003_r28_habits_empty_message`
- `test_br_tui_003_r28_tasks_empty_message`
- `test_br_tui_003_r28_timer_empty_message`
- `test_br_tui_003_r28_no_hardcoded_mock_data`

---

### BR-TUI-003-R29: Tasks Recentes no Dashboard (NOVA 14/03/2026)

**Descrição:** O `load_tasks()` do dashboard inclui tasks concluídas e canceladas das últimas 24 horas, além das pendentes e overdue. Tasks recentes aparecem após as ativas na ordenação.

**Decisão arquitetural:** ADR-036

**Dependências:** BR-TASK-007 (derivação de status), BR-TASK-009 (soft delete)

**Dados carregados:**

```python
# Pendentes + Overdue (sem filtro temporal)
pending_tasks = Task.where(completed_datetime=None, cancelled_datetime=None)

# Concluídas recentes (últimas 24h)
recent_completed = Task.where(
    completed_datetime >= now() - 24h,
    cancelled_datetime=None
)

# Canceladas recentes (últimas 24h)
recent_cancelled = Task.where(
    cancelled_datetime >= now() - 24h
)
```

**Ordenação no painel (BR-TUI-003-R20 estendida):**

```plaintext
overdue > pending > completed (recentes) > cancelled (recentes)
```

**Regras:**

1. O loader combina as três queries em uma lista unificada
2. Cada dict inclui `status` derivado conforme BR-TASK-007
3. O campo `proximity` para tasks completed exibe "Concluída" (ou delta como "Há 2h")
4. O campo `proximity` para tasks cancelled exibe "Cancelada"
5. Tasks completed/cancelled contam para o subtítulo (BR-TUI-003-R23) — os contadores já existem no `TasksPanel`
6. Limite de 9 tasks no painel permanece (BR-TUI-003 original)
7. Dentro do limite, pendentes/overdue têm prioridade sobre recentes

**Testes:**

- `test_br_tui_003_r29_loads_pending_tasks`
- `test_br_tui_003_r29_loads_recently_completed`
- `test_br_tui_003_r29_loads_recently_cancelled`
- `test_br_tui_003_r29_excludes_old_completed`
- `test_br_tui_003_r29_pending_priority_over_recent`
- `test_br_tui_003_r29_respects_nine_task_limit`

---

### BR-TUI-008: Visual Consistency (Material-like)

**Descrição:** A TUI segue design system Material-like com paleta de cores definida, cards com bordas, spacing consistente, hierarquia visual clara e layout responsivo com três breakpoints.

**Regras:**

1. Paleta definida em theme.tcss (single source of truth para cores)
2. Cards: borda arredondada, padding 1x2, margin 1
3. Status colors: verde/`$success` (done), amarelo/`$warning` (pending/skipped), vermelho/`$error` (missed/overdue), purple/`$primary-light` (running)
4. Texto primário: alto contraste sobre superfície (`$on-surface` sobre `$surface`)
5. Texto secundário: cor `$muted` para labels e metadados
6. Sidebar: largura fixa 22 caracteres, fundo `$surface-alt`
7. Tipografia: bold para títulos, normal para conteúdo, dim para metadados
8. Breakpoint completo (≥ 120 colunas): layout 3 colunas (sidebar + agenda + cards), timeline vertical completa, todos os cards visíveis, métricas com histórico semanal + dot matrix
9. Breakpoint compacto (80–119 colunas): agenda com menos horas visíveis, cards com conteúdo truncado (nomes até 10 chars), métricas reduzidas (3 dias de histórico)
10. Breakpoint minimal (< 80 colunas): layout 1 coluna (cards empilhados verticalmente), agenda oculta (substituída por barra de progresso simples no header), métricas apenas streak + completude 7d
11. Barras de progresso seguem esquema de cores por faixa: verde (`$success`) para ≥ 80%, amarelo (`$warning`) para 50–79%, vermelho (`$error`) para < 50%
12. Indicadores ASCII consistentes em toda a TUI: ✓ (done), ✗ (skip), ! (alta/missed), ▪ (média), · (baixa/pending), ▶ (running), ◼ (sparkline esforço)

**Paleta de referência:**

| Variável TCSS    | Cor     | Uso                         |
| ---------------- | ------- | --------------------------- |
| `$primary`       | #7C4DFF | Bordas, elementos de ênfase |
| `$primary-light` | #B388FF | Timer running, destaques    |
| `$surface`       | #1E1E2E | Fundo principal             |
| `$surface-alt`   | #2A2A3E | Cards, sidebar, elevação    |
| `$on-surface`    | #CDD6F4 | Texto principal             |
| `$success`       | #A6E3A1 | Done, concluído             |
| `$warning`       | #F9E2AF | Pending, skipped            |
| `$error`         | #F38BA8 | Missed, overdue, alta       |
| `$muted`         | #6C7086 | Labels, metadados, vazio    |

**Testes:**

- `test_br_tui_008_theme_file_exists`
- `test_br_tui_008_cards_have_consistent_style`
- `test_br_tui_008_status_colors_applied`
- `test_br_tui_008_progress_bar_color_thresholds`
- `test_br_tui_008_responsive_breakpoint_compact`
- `test_br_tui_008_responsive_breakpoint_minimal`
- `test_br_tui_008_ascii_indicators_consistent`

---

### BR-TUI-009: Service Layer Sharing

**Descrição:** A TUI consome os mesmos services que a CLI. Nenhuma lógica de negócio é duplicada na camada TUI. A TUI é exclusivamente UI: captura input, chama service, exibe resultado.

**Regras:**

1. TUI importa de `timeblock.services` (mesmo pacote que CLI)
2. TUI NUNCA acessa models/ORM diretamente (sempre via service)
3. Session criada por operação (session-per-action pattern)
4. Erros de service propagados e exibidos como notificação
5. Validações de negócio permanecem nos services (não na TUI)

**Testes:**

- `test_br_tui_009_uses_routine_service`
- `test_br_tui_009_uses_habit_service`
- `test_br_tui_009_uses_task_service`
- `test_br_tui_009_uses_timer_service`
- `test_br_tui_009_no_direct_model_access`

---

### BR-TUI-010: Habit Instance Actions

**Descrição:** A tela de Hábitos permite marcar instâncias como done ou skip com substatus, integrando com BR-HABITINSTANCE-001 e BR-SKIP-001.

**Regras:**

1. Lista instâncias do dia agrupadas por hábito
2. `enter` em instância pendente → Menu de ação (Done/Skip)
3. Done solicita duração real (minutos) para cálculo de substatus
4. Skip solicita categoria (SkipReason) e justificativa opcional
5. Instâncias já finalizadas (done/not_done) exibem status com cor
6. Substatus calculado automaticamente pelo HabitInstanceService (BR-HABITINSTANCE-002/003)

**Testes:**

- `test_br_tui_010_lists_today_instances`
- `test_br_tui_010_mark_done_asks_duration`
- `test_br_tui_010_mark_skip_asks_reason`
- `test_br_tui_010_shows_substatus_color`
- `test_br_tui_010_completed_instances_readonly`

### BR-TUI-011: Routines Screen

**Descrição:** A tela de Rotinas exibe a semana completa em formato de grade temporal (estilo Google Calendar weekly view), representando o plano ideal do usuário. Enquanto o Dashboard mostra o dia real com status de execução, a tela de Rotinas mostra a intenção: os templates de hábitos distribuídos na semana conforme sua recorrência. A grade permite visualizar, criar, editar e deletar hábitos diretamente no contexto temporal, além de gerenciar múltiplas rotinas.

**Referências:** ADR-031 seção 4, BR-TUI-005 (CRUD pattern), BR-TUI-008 (visual), BR-ROUTINE-001 (single active), BR-HABIT-001/002 (estrutura e recorrência)

**Regras:**

1. **Header Bar:** barra compacta exibe lista horizontal de rotinas com contagem de hábitos por rotina, indicador `▸` e `(ativa)` na rotina ativa, ação `+ Nova rotina` à direita e período da semana exibida (`Sem DD─DD Mês AAAA`). `Tab`/`Shift+Tab` navega entre rotinas no header; a grade atualiza para exibir os hábitos da rotina focada
2. **Grade Semanal:** ocupa toda a largura após a sidebar. 7 colunas (Seg─Dom) distribuídas horizontalmente com largura igual. Régua de horas (06:00─22:00) à esquerda, vertical. Cada hábito posicionado como bloco no dia e horário correspondentes à sua recorrência (BR-HABIT-002)
3. **Rendering de blocos:** cada hora = 2 linhas na grade. Blocos com duração ≤ 30min = 1 linha. Blocos com duração > 30min = múltiplas linhas, label na primeira. Nome truncado conforme largura da coluna. Cada hábito usa preenchimento distinto (████, ▒▒▒▒, ░░░░, ▓▓▓▓) como canal redundante de acessibilidade, combinado com a cor do hábito (`color`) em terminais que suportam
4. **Navegação na grade:** `←`/`→` navega entre dias (colunas), `↑`/`↓` ou `j`/`k` navega entre blocos no mesmo dia (pula para próximo hábito). `[`/`]` alterna semana anterior/próxima. `T` retorna à semana atual
5. **Painel de detalhes:** quando o cursor está sobre um bloco, ele ganha borda `$primary` e um painel lateral fixo exibe: nome, horário início─fim, duração, recorrência, cor, contagem de instâncias (pendentes/concluídas), streak atual e keybindings contextuais (`[e]` editar, `[x]` deletar, `[g]` ver instâncias). Painel atualiza em tempo real conforme o cursor se move
6. **CRUD contextual:** keybindings `n`/`e`/`x` operam sobre rotinas quando o foco está no header, e sobre hábitos quando o foco está na grade. Novo hábito abre formulário modal (título, horário, recorrência, cor). Após criar, o hábito aparece imediatamente na grade nos dias correspondentes. Segue padrões de BR-TUI-005 (confirmação em delete, refresh após operação, erros inline)
7. **Ativação de rotina:** `a` com foco em rotina no header ativa a rotina selecionada (BR-ROUTINE-001: desativa todas as outras). Mudança refletida no header (indicador `▸` move), na status bar e no dashboard
8. **Conflitos:** dois hábitos no mesmo horário/dia renderizam lado a lado na mesma célula, separados por `│`, com borda `$error`. Conflitos são exibidos mas nunca bloqueados (consistente com BR-REORDER-001)
9. **Rotina sem hábitos:** grade vazia com mensagem centralizada "Nenhum hábito nesta rotina. Pressione [n] para criar o primeiro."
10. **Responsividade:** ≥ 120 colunas: 7 dias visíveis simultaneamente, labels completos. 80─119 colunas: 5 dias visíveis (Seg─Sex), Sáb/Dom com scroll horizontal, nomes truncados em 6 chars. < 80 colunas: 3 dias visíveis, scroll horizontal, blocos sem label (apenas preenchimento + cor), painel de detalhes como overlay (ativado com `enter`, fechado com `escape`)
11. **Refresh:** dados atualizados ao entrar na screen (on_focus) e após qualquer operação CRUD. Troca de rotina no header recarrega a grade com os hábitos da rotina focada
12. **Navegação cross-screen:** `g` com bloco selecionado navega para a screen Habits com filtro no hábito selecionado (visão de instâncias). Keybinding de navegação global (`3`/`h`) vai para Habits sem filtro

**Mockup de referência:** `docs/tui/routines-weekly-mockup.md`

**Testes:**

- `test_br_tui_011_header_shows_routines_list`
- `test_br_tui_011_header_shows_active_indicator`
- `test_br_tui_011_header_shows_habit_count`
- `test_br_tui_011_header_shows_week_period`
- `test_br_tui_011_tab_switches_routine_in_header`
- `test_br_tui_011_grade_renders_seven_columns`
- `test_br_tui_011_grade_renders_hour_ruler`
- `test_br_tui_011_grade_places_habit_by_recurrence`
- `test_br_tui_011_grade_block_duration_proportional`
- `test_br_tui_011_grade_block_fill_patterns`
- `test_br_tui_011_grade_block_uses_habit_color`
- `test_br_tui_011_grade_truncates_long_names`
- `test_br_tui_011_navigate_days_left_right`
- `test_br_tui_011_navigate_blocks_up_down`
- `test_br_tui_011_navigate_week_prev_next`
- `test_br_tui_011_navigate_week_today`
- `test_br_tui_011_detail_panel_shows_on_focus`
- `test_br_tui_011_detail_panel_shows_habit_info`
- `test_br_tui_011_detail_panel_shows_instance_stats`
- `test_br_tui_011_detail_panel_shows_streak`
- `test_br_tui_011_detail_panel_updates_on_cursor_move`
- `test_br_tui_011_crud_context_header_operates_routine`
- `test_br_tui_011_crud_context_grade_operates_habit`
- `test_br_tui_011_create_habit_modal`
- `test_br_tui_011_create_habit_appears_in_grade`
- `test_br_tui_011_edit_habit_prefilled`
- `test_br_tui_011_delete_habit_confirmation`
- `test_br_tui_011_activate_routine_updates_indicator`
- `test_br_tui_011_conflict_renders_side_by_side`
- `test_br_tui_011_conflict_uses_error_color`
- `test_br_tui_011_empty_routine_message`
- `test_br_tui_011_responsive_compact_five_days`
- `test_br_tui_011_responsive_minimal_three_days`
- `test_br_tui_011_responsive_minimal_overlay_panel`
- `test_br_tui_011_refreshes_on_focus`
- `test_br_tui_011_refreshes_after_crud`
- `test_br_tui_011_go_to_habits_screen`

---

### BR-TUI-012: Panel Navigation (NOVA 02/03/2026)

**Descrição:** Navegação entre panels (cards) dentro de uma screen. Cada panel é uma zona focável independente com cursor interno para seus itens. O panel focado recebe destaque visual e o footer atualiza seus keybindings.

**Regras:**

1. Tab avança para o próximo panel (ciclo: Agenda → Hábitos → Tarefas → Timer → Agenda)
2. Ctrl+Tab volta para o panel anterior (ciclo reverso)
3. Números 1-4 focam panel diretamente (1=Agenda, 2=Hábitos, 3=Tarefas, 4=Timer)
4. Panel focado recebe borda `$primary` (#CBA6F7 Mauve)
5. Panels não focados mantêm borda `$surface` (#313244)
6. Setas ↑/↓ ou j/k navegam itens dentro do panel focado
7. Item selecionado (cursor) indicado por fundo Surface0 #313244
8. Se panel tem overflow, scroll interno acompanha cursor (auto-scroll)
9. Ao trocar de panel, cursor do panel anterior é preservado (retorna na mesma posição)
10. Footer central atualiza keybindings conforme panel focado (BR-TUI-007)

**Testes:**

- `test_br_tui_012_tab_advances_panel`
- `test_br_tui_012_ctrl_tab_reverses_panel`
- `test_br_tui_012_number_focuses_panel_directly`
- `test_br_tui_012_focused_panel_has_primary_border`
- `test_br_tui_012_unfocused_panel_has_surface_border`
- `test_br_tui_012_arrows_navigate_items_in_panel`
- `test_br_tui_012_cursor_preserved_on_panel_switch`
- `test_br_tui_012_overflow_scrolls_with_cursor`
- `test_br_tui_012_footer_updates_on_panel_focus`

---

### BR-TUI-013: Placeholders Editáveis (NOVA 02/03/2026)

**Descrição:** Quando o banco está vazio ou um card tem menos itens que o viewport, placeholders (linhas com `---`) são exibidos. Estes placeholders são navegáveis e editáveis: o usuário pode selecionar um placeholder e transformá-lo em item real via Enter (edição inline) ou N (modal com campos).

**Regras:**

1. Placeholders exibidos quando card tem menos itens que slots visuais disponíveis
2. Placeholders são navegáveis com setas/j/k como itens normais
3. Enter em placeholder abre edição inline: cursor transforma `---` em input de texto
4. Tipo do item criado é determinado pelo panel (Hábitos → habit, Tarefas → task)
5. Após confirmar (Enter no input), item é criado via service e placeholder substituído
6. Escape cancela edição inline, restaura placeholder
7. N em placeholder abre modal com campos completo (nome, duração, recorrência, etc.)
8. : abre barra de comando independente do que está selecionado (power user)
9. Barra de comando aceita sintaxe CLI: `habit add "Leitura" --duration 30 --recurrence daily`
10. Após criação, lista atualiza e cursor posiciona no novo item

**Testes:**

- `test_br_tui_013_placeholder_shown_when_empty`
- `test_br_tui_013_placeholder_is_navigable`
- `test_br_tui_013_enter_on_placeholder_opens_inline_edit`
- `test_br_tui_013_inline_edit_creates_item`
- `test_br_tui_013_escape_cancels_inline_edit`
- `test_br_tui_013_n_opens_modal_on_placeholder`
- `test_br_tui_013_colon_opens_command_bar`
- `test_br_tui_013_command_bar_accepts_cli_syntax`
- `test_br_tui_013_list_refreshes_after_creation`

---

### BR-TUI-014: TCSS Modularização (NOVA 02/03/2026)

**Descrição:** O arquivo theme.tcss (479+ linhas) deve ser decomposto em módulos por responsabilidade. O Textual suporta múltiplos arquivos TCSS via `CSS_PATH` como lista. A decomposição melhora manutenibilidade e reduz conflitos em merges.

**Estrutura alvo:**

```plaintext
src/timeblock/tui/styles/
├── base.tcss          # Reset, variáveis, tipografia
├── layout.tcss        # Grid, sidebar, content area
├── panels.tcss        # Panel widget, bordas, padding
├── dashboard.tcss     # Agenda, header bar, panels específicos
├── forms.tcss         # Inputs, modais, confirmação
└── theme.tcss         # Import agregador (ou app.CSS_PATH lista todos)
```

**Regras:**

1. Nenhum arquivo TCSS deve exceder 150 linhas
2. Variáveis de cor definidas exclusivamente em base.tcss
3. Cada screen pode ter TCSS próprio se necessário
4. Ordem de carregamento: base → layout → panels → screen-specific → forms
5. Refatoração não pode alterar comportamento visual (zero regressão)

**Testes:**

- `test_br_tui_014_app_loads_all_tcss_files`
- `test_br_tui_014_no_tcss_file_exceeds_150_lines`
- `test_br_tui_014_visual_regression_after_split` (manual/screenshot)

---

### BR-TUI-015: Revisão de Código e Qualidade (NOVA 02/03/2026)

**Descrição:** Revisão completa do codebase usando frameworks industriais de qualidade de software como referência. Objetivo: identificar oportunidades de refatoração, eliminar code smells, e alinhar com princípios SOLID, Clean Code e padrões de manutenibilidade.

**Escopo da revisão:**

1. **SOLID:** Verificar SRP em services e widgets, DIP na integração TUI→services
2. **Clean Code:** Nomes expressivos, funções curtas (≤50 linhas), sem magic numbers
3. **Complexidade ciclomática:** Identificar métodos com CC > 10 para decomposição
4. **Duplicação:** Detectar padrões repetidos entre screens/widgets para extração
5. **Coesão:** Cada módulo faz uma coisa bem; módulos com múltiplas responsabilidades são candidatos a split
6. **Acoplamento:** Services não devem conhecer detalhes de TUI/CLI; widgets não devem acessar banco diretamente
7. **Testabilidade:** Todo código novo deve ser testável em isolamento (DI, session injection)

**Critérios de avaliação por arquivo:**

| Critério          | Severidade | Limiar                   |
| ----------------- | ---------- | ------------------------ |
| Arquivo > 300 LOC | WARNING    | Avaliar decomposição     |
| Arquivo > 500 LOC | CRITICAL   | Decomposição obrigatória |
| Função > 50 LOC   | WARNING    | Avaliar extração         |
| Função > 100 LOC  | CRITICAL   | Extração obrigatória     |
| CC > 10           | WARNING    | Simplificar lógica       |
| CC > 15           | CRITICAL   | Decomposição obrigatória |
| Duplicação > 10L  | WARNING    | Extrair helper/mixin     |

**Referências:**

- Martin, R. C. (2008). _Clean Code_. Prentice Hall.
- Martin, R. C. (2017). _Clean Architecture_. Prentice Hall.
- Fowler, M. (2018). _Refactoring_. Addison-Wesley, 2nd ed.
- IEEE 730-2014 (Software Quality Assurance)

**Entregável:** Relatório com findings por severidade (CRITICAL/WARNING/INFO), arquivo, linha e sugestão de correção.

### BR-TUI-016: Dashboard CRUD — Rotinas (NOVA 05/03/2026)

**Descrição:** O dashboard permite criar, editar e deletar rotinas diretamente via modais contextuais, sem navegar para a RoutinesScreen. A operação é acionada quando o header bar está focado.

**Regras:**

1. `n` com header focado abre FormModal para criar rotina (campo: nome)
2. `e` com header focado edita rotina ativa (nome)
3. `x` com header focado abre ConfirmDialog para deletar rotina ativa
4. Enter ou seleção ativa/desativa rotina (se múltiplas existirem)
5. Sem rotina ativa → header exibe hint: `[Sem rotina] n criar`
6. Criação de rotina a torna automaticamente ativa
7. Deletar rotina ativa desativa e limpa todos os panels
8. Operação usa `service_action()` (session-per-action)
9. Após operação, `refresh_data()` atualiza todos os panels

**Dependências:** BR-TUI-019 (ConfirmDialog), BR-TUI-020 (FormModal), BR-TUI-005 (CRUD Pattern)

**Testes esperados:** 8

- `test_br_tui_016_n_on_header_opens_routine_form`
- `test_br_tui_016_created_routine_becomes_active`
- `test_br_tui_016_e_on_header_edits_active_routine`
- `test_br_tui_016_x_on_header_opens_confirm_dialog`
- `test_br_tui_016_delete_clears_all_panels`
- `test_br_tui_016_no_routine_shows_hint`
- `test_br_tui_016_refresh_after_crud_operation`
- `test_br_tui_016_switch_active_routine_updates_panels`

---

### BR-TUI-017: Dashboard CRUD — Hábitos (NOVA 05/03/2026)

**Descrição:** O dashboard permite criar, editar e deletar hábitos diretamente via modais contextuais quando o panel de hábitos está focado. Requer rotina ativa.

**Regras:**

1. `n` com panel hábitos focado abre FormModal (campos: título, horário início, duração em minutos, recorrência)
2. `e` edita hábito sob cursor (FormModal preenchido)
3. `x` deleta hábito sob cursor com ConfirmDialog
4. Requer rotina ativa — sem rotina, `n` redireciona para criação de rotina (DT-040, ADR-038 D9)
5. Hábito criado gera HabitInstance para o dia atual automaticamente (via HabitInstanceService)
6. Hábito criado aparece imediatamente no panel (refresh local + banco)
7. Quick actions existentes coexistem: v done [MODAL], s skip [MODAL] (BR-TUI-004, ADR-037)
8. Campos obrigatórios: título, horário início, duração. Recorrência default: EVERYDAY
9. Validação inline: título não vazio, duração > 0, horário no formato HH:MM

**Dependências:** BR-TUI-019, BR-TUI-020, BR-TUI-016 (rotina ativa), BR-HABIT-001

**Testes esperados:** 10

- `test_br_tui_017_n_on_habits_opens_form`
- `test_br_tui_017_n_without_routine_shows_error`
- `test_br_tui_017_created_habit_appears_in_panel`
- `test_br_tui_017_e_opens_prefilled_form`
- `test_br_tui_017_x_opens_confirm_dialog`
- `test_br_tui_017_delete_removes_from_panel`
- `test_br_tui_017_validation_title_required`
- `test_br_tui_017_validation_duration_positive`
- `test_br_tui_017_default_recurrence_everyday`
- `test_br_tui_017_coexists_with_quick_actions`

---

### BR-TUI-018: Dashboard CRUD — Tarefas (NOVA 05/03/2026)

**Descrição:** O dashboard permite criar, editar e deletar tarefas diretamente via modais contextuais quando o panel de tarefas está focado.

**Regras:**

1. `n` com panel tarefas focado abre FormModal (campos: título, data, horário, prioridade)
2. `e` edita task sob cursor (FormModal preenchido)
3. `x` deleta task sob cursor com ConfirmDialog
4. Task criada aparece na posição correta (ordenação por proximidade temporal)
5. Quick actions coexistem (BR-TUI-004, ADR-037): v complete, s postpone [MODAL edit], c cancel, u reopen
6. Campos obrigatórios: título. Data, horário e prioridade são opcionais
7. Prioridade: low, medium, high (default: medium)
8. Data default: hoje. Horário default: vazio (sem horário)
9. Validação inline: título não vazio

**Dependências:** BR-TUI-019, BR-TUI-020, BR-TASK-001

**Testes esperados:** 8

- `test_br_tui_018_n_on_tasks_opens_form`
- `test_br_tui_018_created_task_appears_in_panel`
- `test_br_tui_018_task_ordered_by_proximity`
- `test_br_tui_018_e_opens_prefilled_form`
- `test_br_tui_018_x_opens_confirm_dialog`
- `test_br_tui_018_delete_removes_from_panel`
- `test_br_tui_018_validation_title_required`
- `test_br_tui_018_coexists_with_ctrl_k`

---

### BR-TUI-019: ConfirmDialog (NOVA 05/03/2026)

**Descrição:** Widget modal genérico de confirmação reutilizável por qualquer operação destrutiva no sistema. Overlay sobre o conteúdo atual com foco exclusivo (modal trap).

**Regras:**

1. Exibe título, mensagem descritiva e botões Confirm/Cancel
2. Enter confirma a operação
3. Esc cancela e fecha o modal
4. Foco exclusivo: nenhum widget atrás do modal recebe input (modal trap)
5. Callback `on_confirm` e `on_cancel` configuráveis pelo chamador
6. Mensagem inclui nome do item sendo deletado (contextual)
7. Visual: borda Red (#F38BA8), fundo Mantle (#181825), texto em Text (#CDD6F4)
8. Ao fechar, foco retorna ao widget que abriu o modal

**Dependências:** Nenhuma (widget primitivo)

**Testes esperados:** 6

- `test_br_tui_019_enter_triggers_confirm`
- `test_br_tui_019_esc_triggers_cancel`
- `test_br_tui_019_displays_item_name`
- `test_br_tui_019_modal_traps_focus`
- `test_br_tui_019_focus_returns_on_close`
- `test_br_tui_019_custom_callbacks`

---

### BR-TUI-020: FormModal (NOVA 05/03/2026)

**Descrição:** Widget modal genérico de formulário reutilizável para operações de criação e edição. Suporta campos tipados com validação inline.

**Regras:**

1. Exibe título, lista de campos com labels e input, botões Save/Cancel
2. Tab navega entre campos sequencialmente
3. Shift+Tab navega para campo anterior
4. Enter no último campo ou no botão Save submete o formulário
5. Esc cancela e fecha o modal sem salvar
6. Validação inline: campo obrigatório vazio exibe mensagem de erro abaixo do campo
7. Campos suportados: text (string), time (HH:MM), number (int), select (enum com opções)
8. Modo edit: campos preenchidos com valores atuais do item
9. Modo create: campos vazios com placeholder indicando formato esperado
10. Visual: borda Blue (#89B4FA), fundo Mantle (#181825), campos com borda Surface2 (#585B70)
11. Foco exclusivo (modal trap) enquanto aberto
12. Callback `on_submit(data: dict)` e `on_cancel()` configuráveis

**Dependências:** Nenhuma (widget primitivo)

**Testes esperados:** 10

- `test_br_tui_020_tab_navigates_fields`
- `test_br_tui_020_shift_tab_reverse_navigation`
- `test_br_tui_020_enter_submits_form`
- `test_br_tui_020_esc_cancels_form`
- `test_br_tui_020_required_field_validation`
- `test_br_tui_020_time_field_format_validation`
- `test_br_tui_020_number_field_positive_validation`
- `test_br_tui_020_edit_mode_prefilled`
- `test_br_tui_020_create_mode_empty_with_placeholder`
- `test_br_tui_020_modal_traps_focus`

### BR-TUI-021: Timer no Dashboard (NOVA 08/03/2026)

**Descrição:** O dashboard permite iniciar, pausar, retomar, parar e cancelar sessões de timer diretamente, sem navegar para a Timer Screen. O TimerPanel exibe elapsed em tempo real com atualização a cada segundo. O timer opera sobre o hábito selecionado no panel de hábitos.

**Regras:**

1. `t` no panel de hábitos com hábito selecionado inicia timer via TimerService.start_timer (ADR-037)
2. `space` no panel de timer com timer ativo alterna entre pause e resume (ADR-037)
3. `s` no panel de timer para o timer e salva a sessão via TimerService.stop_timer (ADR-037)
4. `c` no panel de timer abre ConfirmDialog e, se confirmado, cancela via TimerService.cancel_timer (ADR-037)
5. TimerPanel atualiza elapsed a cada segundo via set_interval do Textual
6. TimerPanel exibe nome do hábito associado ao timer ativo
7. Elapsed é formatado como MM:SS e renderizado em ASCII art
8. Cores por estado: Mauve (#CBA6F7) para running, Yellow (#F9E2AF) para paused, Overlay0 (#6C7086) para idle
9. Se não há timer ativo, TimerPanel exibe "idle" com hint de keybinding
10. Iniciar timer requer hábito selecionado no panel de hábitos — sem seleção, nenhuma ação
11. Se já existe timer ativo e usuário tenta iniciar outro, exibir erro (um timer por vez)
12. refresh_data() atualiza TimerPanel após start/stop/pause/resume/cancel
13. Footer contextual exibe keybindings de timer quando panel de timer está focado

**Dependências:** BR-TUI-004 (keybindings), BR-TUI-009 (Service Layer), BR-TUI-012 (navegação), BR-TIMER-001 a BR-TIMER-004 (regras de timer)

**Testes:**

- `test_br_tui_021_t_starts_timer_on_selected_habit`
- `test_br_tui_021_t_without_selection_does_nothing`
- `test_br_tui_021_space_pauses_active_timer`
- `test_br_tui_021_space_resumes_paused_timer`
- `test_br_tui_021_s_stops_timer`
- `test_br_tui_021_c_opens_cancel_confirm`
- `test_br_tui_021_timer_panel_updates_every_second`
- `test_br_tui_021_timer_panel_shows_habit_name`
- `test_br_tui_021_one_timer_at_a_time`
- `test_br_tui_021_idle_shows_hint`

---

### BR-TUI-022: Done Manual via Modal (NOVA 15/03/2026)

**Descrição:** Ao marcar hábito como done sem timer ativo, o sistema abre modal para o usuário selecionar substatus, aderindo a BR-HABITINSTANCE-002.

**Decisão arquitetural:** ADR-038 D3

**Regras:**

1. `v` em hábito PENDING sem timer ativo e sem TimeLog DONE existente abre modal
2. Modal exibe Select com DoneSubstatus: FULL, PARTIAL, OVERDONE, EXCESSIVE
3. Default pre-selecionado: FULL
4. Enter confirma, Esc cancela sem alterar status
5. Após confirmação: `status=DONE`, `done_substatus=<selecionado>`
6. `v` em hábito PENDING com TimeLog DONE existente abre modal de restauração (BR-HABITINSTANCE-007 regra 5)

**Testes:**

- `test_br_tui_022_v_without_timer_opens_modal`
- `test_br_tui_022_modal_shows_substatus_options`
- `test_br_tui_022_esc_cancels_without_change`
- `test_br_tui_022_enter_confirms_done_with_substatus`
- `test_br_tui_022_detects_existing_timelog`

---

### BR-TUI-023: Notificação de Timer Ativo no Done (NOVA 15/03/2026)

**Descrição:** Ao pressionar `v` em hábito com timer ativo, o sistema abre modal informativo com opções.

**Decisão arquitetural:** ADR-038 D4

**Regras:**

1. `v` em hábito com status `running` abre modal
2. Modal: "Timer ativo para este hábito"
3. Opções: [Parar timer e marcar done] / [Cancelar]
4. "Parar timer e marcar done": executa `TimerService.stop_timer`
5. "Cancelar": fecha modal, nenhuma ação

**Testes:**

- `test_br_tui_023_v_on_running_opens_modal`
- `test_br_tui_023_stop_and_done_marks_habit`
- `test_br_tui_023_cancel_does_nothing`

---

### BR-TUI-024: Skip com Modal de SkipReason (NOVA 15/03/2026)

**Descrição:** Ao pular hábito via `s`, o sistema sempre abre modal para categorização do skip, aderindo a BR-SKIP-001.

**Decisão arquitetural:** ADR-038 D6

**Regras:**

1. `s` em hábito PENDING abre modal com Select de SkipReason
2. Opções: as 8 categorias (HEALTH, WORK, FAMILY, TRAVEL, WEATHER, LACK_RESOURCES, EMERGENCY, OTHER) e a opção "Sem justificativa"
3. Campo opcional de nota (texto livre, max 500 chars)
4. Enter confirma skip com razão selecionada
5. Esc cancela sem alterar status
6. Após confirmação com categoria: `status=NOT_DONE`, `not_done_substatus=SKIPPED_JUSTIFIED`, `skip_reason=<selecionado>`
7. Após confirmação com "Sem justificativa": `status=NOT_DONE`, `not_done_substatus=SKIPPED_UNJUSTIFIED`, `skip_reason=None`

**Testes:**

- `test_br_tui_024_s_opens_skip_reason_modal`
- `test_br_tui_024_modal_shows_all_reasons`
- `test_br_tui_024_note_optional`
- `test_br_tui_024_esc_cancels`
- `test_br_tui_024_confirm_sets_skip_reason`
- `test_br_tui_024_unjustified_sets_no_reason`

---

### BR-TUI-025: Fluxo Routine-first (NOVA 15/03/2026)

**Descrição:** Quando o usuário tenta criar hábito sem rotina ativa, o sistema redireciona para criação de rotina com mensagem explicativa.

**Decisão arquitetural:** ADR-038 D9

**Regras:**

1. `n` com habits panel focado e sem rotina ativa abre FormModal de criação de rotina
2. FormModal exibe mensagem: "Crie uma rotina primeiro para adicionar hábitos"
3. Após criar rotina, retorna ao dashboard
4. `n` sem panel focado e sem rotina ativa: mesmo comportamento
5. `n` com tasks panel focado não depende de rotina (tasks são independentes)

**Testes:**

- `test_br_tui_025_n_habits_no_routine_opens_routine_modal`
- `test_br_tui_025_returns_to_dashboard_after_routine`
- `test_br_tui_025_n_tasks_independent_of_routine`

---

### BR-TUI-026: Limites de Exibição nos Panels (NOVA 15/03/2026)

**Descrição:** Panels do dashboard exibem número limitado de items para manter legibilidade.

**Decisão arquitetural:** ADR-038 D10

**Regras:**

1. HabitsPanel exibe no máximo 12 hábitos
2. TasksPanel exibe no máximo 9 tasks
3. Limites são fixos (constantes no código)
4. Items excedentes são acessíveis via screens dedicadas (Habits Screen, Tasks Screen)
5. Limites serão configuráveis em screen de configurações futura

**Testes:**

- `test_br_tui_026_habits_panel_max_12`
- `test_br_tui_026_tasks_panel_max_9`

---

### BR-TUI-027: Renderização Multi-Coluna para Sobreposição na Agenda (NOVA 21/03/2026)

**Descrição:** Quando dois ou mais hábitos possuem horários sobrepostos, a Agenda do Dia deve renderizar os blocos lado a lado em colunas proporcionais, similar ao Google Calendar.

**Decisão arquitetural:** DT-045

**Regras:**

1. Eventos sobrepostos são agrupados em clusters de overlap (Union-Find)
2. Cada evento recebe uma coluna via algoritmo greedy (primeira coluna livre)
3. Largura de cada coluna é proporcional: `(fw - separadores) / n_colunas`
4. Separador visual entre colunas é `┆` (tracejado leve)
5. Nome do hábito é truncado para caber na largura da coluna
6. Conectores usam `─┼─` (start) e `│` (fill)
7. Apenas ícone de status é exibido (sem label textual nem duração)
8. Suporte a 2+ colunas simultâneas

**Testes:**

- `test_br_tui_027_overlap_two_events_side_by_side`
- `test_br_tui_027_overlap_three_events_columns`
- `test_br_tui_027_no_overlap_single_column`

### BR-TUI-028: Inicialização de Banco no Startup da TUI (NOVA 21/03/2026)

**Descrição:** A TUI deve garantir que o banco de dados existe e possui todas as tabelas necessárias antes de qualquer operação. Se o banco não existir ou estiver vazio, a TUI deve criá-lo automaticamente.

**Decisão arquitetural:** DT-056

**Regras:**

1. No `on_mount` do DashboardScreen, antes de `ensure_today_instances`, verificar se as tabelas existem
2. Se tabelas não existirem, chamar `create_db_and_tables()` automaticamente
3. Se `get_db_path()` resolver para path inexistente, usar XDG path canônico (`~/.local/share/atomvs/atomvs.db`) como fallback
4. Exibir notificação ao usuário quando banco é inicializado pela primeira vez
5. Erros de banco em `service_action` devem gerar `app.notify()` em vez de falha silenciosa

**Testes:**

- `test_br_tui_028_startup_creates_tables_if_missing`
- `test_br_tui_028_service_action_notifies_db_errors`

### BR-TUI-029: Feedback de Erro em Operações Destrutivas (NOVA 21/03/2026)

**Descrição:** Operações destrutivas na TUI (delete de rotina, delete de hábito) devem exibir feedback visual ao usuário quando falham, em vez de fechar o modal silenciosamente.

**Decisão arquitetural:** DT-057

**Regras:**

1. Callbacks de `ConfirmDialog` devem verificar o retorno de `service_action`
2. Se `service_action` retornar erro, exibir `app.notify(error, severity="error")`
3. Delete de rotina com hábitos vinculados deve informar: "Rotina possui N hábitos. Delete os hábitos primeiro ou use a CLI para cascade delete."
4. O modal não deve fechar quando a operação falha — manter aberto com mensagem de erro
5. Padrão aplicável a todas as operações destrutivas futuras

**Testes:**

- `test_br_tui_029_delete_routine_with_habits_shows_error`
- `test_br_tui_029_confirm_dialog_stays_open_on_failure`

---

### BR-TUI-030: Paginação Temporal da Agenda (NOVA 22/03/2026)

**Descrição:** Agenda exibe um dia por vez com navegação temporal de -3 a +3 dias.

**Decisão arquitetural:** ADR-041

**Regras:**

1. Agenda exibe um dia por vez. Padrão: dia atual (hoje)
2. Navegação via `←` ou `h` (dia anterior) e `→` ou `l` (dia seguinte)
3. Range permitido: hoje -3 até hoje +3 (7 dias total)
4. Tecla `0` ou `Home` retorna para hoje
5. Header exibe data do dia selecionado
6. Indicador visual quando dia != hoje (`◀` para passados, `▶` para futuros no BorderTitle do header)
7. Dias passados: hábitos com status final (done/skipped). Ações de edição permitidas, timer desabilitado
8. Dias futuros: instances geradas sob demanda via `loader.ensure_instances(date)`. Status pending. Timer desabilitado
9. Mudar de dia recarrega agenda + instances + panels do dia selecionado
10. Footer inclui `←→ dia` nos keybindings visíveis

**Cenários BDD planejados:**

```gherkin
Scenario: Navigate to previous day
  Given the dashboard is showing today's agenda
  When I press the left arrow key
  Then the agenda should display yesterday's habits
  And the header should show yesterday's date

Scenario: Navigate beyond range limit
  Given the dashboard is showing today -3
  When I press the left arrow key
  Then the agenda should remain on today -3
  And no navigation should occur

Scenario: Return to today
  Given the dashboard is showing a past day
  When I press the 0 key
  Then the agenda should display today's habits
  And the header should show today's date
```

**Testes:**

- `test_br_tui_030_navigate_previous_day`
- `test_br_tui_030_navigate_next_day`
- `test_br_tui_030_range_limit_minus3`
- `test_br_tui_030_range_limit_plus3`
- `test_br_tui_030_return_to_today`
- `test_br_tui_030_timer_disabled_past_day`

---

### BR-TUI-031: Scroll Horizontal da Agenda (NOVA 22/03/2026)

**Descrição:** Scroll horizontal interno no painel da agenda quando conteúdo de blocos excede a viewport.

**Decisão arquitetural:** ADR-041

**Regras:**

1. Scroll horizontal ativa quando conteúdo interno (colunas de blocos) excede a largura visível do painel
2. Input primário: Shift + scroll wheel do mouse
3. Input alternativo teclado: Shift+h (esquerda) e Shift+l (direita)
4. Margem de horas (coluna esquerda com `HH:MM │`) permanece fixa — não scrolla horizontalmente
5. Indicador de overflow à direita: `→` no BorderTitle do painel quando há conteúdo oculto à direita
6. Indicador de overflow à esquerda: `←` no BorderTitle quando scrollou para a direita e há conteúdo oculto à esquerda
7. `← →` sem Shift sempre muda dia (BR-TUI-030). Nunca faz scroll horizontal. Sem ambiguidade

**Nota:** BR-TUI-030-R2 define `← →` para navegação de dia. BR-TUI-031-R3 define `Shift+h/l` para scroll horizontal. Modifier key (Shift) diferencia as ações.

**Testes:**

- `test_br_tui_031_scroll_h_activates_on_overflow`
- `test_br_tui_031_hours_margin_fixed_on_scroll`
- `test_br_tui_031_overflow_indicator_right`
- `test_br_tui_031_overflow_indicator_left`
- `test_br_tui_031_arrow_keys_navigate_day_not_scroll`

---

### BR-TUI-032: Renderização de Blocos de Tempo na Agenda (EMENDADA 16/04/2026)

**Descrição:** Blocos de tempo são retângulos contínuos com granularidade de 15min, sem interrupção por linhas horizontais.

**Decisão arquitetural:** ADR-041

**Regras — Granularidade:**

1. Cada linha da agenda corresponde a 15 minutos
2. Labels de hora exibidos a cada 2 linhas (30min). Linha 1 do slot: `HH:MM`. Linha 2: vazio na coluna de hora
3. Blocos de tempo iniciam e terminam em qualquer múltiplo de 15min (:00, :15, :30, :45)

**Regras — Renderização de bloco:**

4. Primeira linha do bloco (horário de início): `{ícone} {título}`. Ícone na cor semântica do status (paleta Catppuccin), título em C_TEXT (`#CDD6F4`). Separados por um único espaço. Não há accent bar nem prefixo — a distinção visual vem da cor do ícone. Para status bold (`running`, `paused`), tanto o ícone quanto o título recebem `[bold]`.
5. Linhas seguintes do bloco (corpo): `· {fill}`. Prefixo `·` (U+00B7) em `[dim]`. Após o espaço, o caractere de preenchimento (`fill_char`) é repetido `col_w - 2` vezes na cor suave do status (`fill_color`). Caracteres de fill por status: `░` (pending, done), `▓` (running), `▒` (paused), `┄` (not_done).
6. Cor do fill provém de `fill_color(status, substatus)` em `colors.py`. Running usa Mauve escuro (`#8B6EAC`), paused usa Yellow escuro (`#B8A050`), demais usam `status_color(status, substatus)`.
7. Ícones de status preservam padrão existente: `○` pending, `▶` running, `✓` done, `⏸` paused. Substatus done: `✓~` partial, `✓+` overdone, `✓!` excessive. Substatus not_done: `!` justified, `✗!` unjustified, `✗?` ignored.
8. Nenhuma linha horizontal (`───`) atravessa um bloco de tempo

**Regras — Término de bloco:**

9. A linha correspondente ao horário de término do bloco AINDA exibe fill. A linha seguinte é livre. Nota: accent visual de término (borda direita `▌` e sublinhado na última linha de fill) pendente de implementação — ver issue #57.
10. Se nenhum bloco inicia na linha seguinte ao término: área vazia (sem pontilhado)
11. Se outro bloco inicia exatamente no horário de término: o título do novo bloco substitui diretamente — sem gap, sem cor residual do bloco anterior

**Regras — Multi-coluna (sobreposição):**

12. Largura mínima por coluna: 18 caracteres. Colunas não encolhem abaixo disso
13. Gap entre colunas: 1 caractere vazio
14. Título truncado com reticências se exceder largura da coluna
15. Lógica de overlap: union-find + greedy column assignment (preserva implementação existente de DT-045)

**Regras — Áreas vazias:**

16. Linhas sem bloco em nenhuma coluna: área vazia (string vazia)
17. Linhas sem bloco em uma coluna mas com bloco em outra: espaço vazio na coluna sem bloco

**Exemplos de referência:** ver `docs/reference/agenda-panel-mockup-reference.md`

**Testes:**

- `test_br_tui_032_block_first_line_title_icon`
- `test_br_tui_032_block_body_accent_bar_color`
- `test_br_tui_032_no_horizontal_lines_through_blocks`
- `test_br_tui_032_end_time_line_has_color`
- `test_br_tui_032_consecutive_blocks_no_gap`
- `test_br_tui_032_minimum_column_width_18`
- `test_br_tui_032_empty_area_dotted`
- `test_br_tui_032_granularity_15min`

**Histórico:** versão original 22/03/2026 usava accent bar `▌` na borda esquerda de todas as linhas e formato `▌{título} · {ícone}`. Emendada 16/04/2026: accent bar removida; corpo usa prefixo `·` dim; primeira linha invertida para `{ícone} {título}` (v1.7.2, issues #34, #40).

---
### BR-TUI-033: MetricsPanel — Exibição de Métricas de Hábitos (NOVA 03/04/2026)

**Descrição:** Painel de métricas agrega dados de completude da rotina ativa com streak, completude percentual e heatmap semanal.

**Decisão arquitetural:** ADR-047

**Regras — Dados exibidos:**

1. O MetricsPanel exibe: streak atual, best streak, completude 7d (%), completude 30d (%), e heatmap semanal com contagem done/total por dia
2. Escopo: métricas agregadas de todos os hábitos da rotina ativa. Métricas por hábito individual deferidas para v2.0

**Regras — Streak:**

3. Streak conta dias consecutivos (do mais recente para o mais antigo) em que pelo menos 1 hábito da rotina foi marcado como DONE
4. Skip e ausência de registro têm o mesmo efeito para o streak: o hábito não foi praticado naquele dia
5. Streak conta dias consecutivos com todos os hábitos DONE (100%). Qualquer dia sem conclusão total — skip, pending ou ausência — quebra o streak. A regra "nunca quebre duas vezes" (CLEAR, 2018) é diretriz comportamental, não lógica de cálculo
6. Best streak: maior streak já alcançado para a rotina ativa. Persistido no banco para sobreviver a limites de query temporal

**Regras — Heatmap semanal:**

7. Exibe os últimos 7 dias (padrão) com formato `DIA done/total`
8. Total corresponde ao número de hábitos ativos na rotina naquele dia. Dias sem instâncias exibem `0/N`, não `0/0`
9. Geração retroativa: ao abrir o dashboard, dias sem instâncias para hábitos que já existiam naquela data recebem instâncias PENDING para que o denominador reflita o real

**Regras — Completude percentual:**

10. `pct_7d = média(done/total * 100)` dos últimos 7 dias. `pct_30d` idem para 30 dias
11. Dias sem instâncias contam como 0% para o cálculo (penaliza inatividade)

**Regras — Interação:**

12. Marcar um hábito como DONE, SKIP ou UNDO recalcula e atualiza o MetricsPanel imediatamente
13. Keybinding `f` no MetricsPanel alterna entre 7d, 14d e 30d. Informação do atalho exibida no footer contextual (status_bar) quando o panel está focado
14. Texto mock `[f] 7d/14d/30d` removido do corpo do painel

**Testes:**

- `test_br_tui_033_streak_consecutive_done_days`
- `test_br_tui_033_streak_skip_breaks_like_miss`
- `test_br_tui_033_streak_two_misses_breaks`
- `test_br_tui_033_heatmap_shows_total_habits`
- `test_br_tui_033_heatmap_retroactive_pending`
- `test_br_tui_033_completude_7d_calculation`
- `test_br_tui_033_reactive_update_on_done`
- `test_br_tui_033_keybinding_f_cycles_period`

---

### BR-TUI-034: Hints Contextuais no Footer Global (EMENDADA 16/04/2026)

**Descrição:** Hints de teclado (atalhos contextuais) vivem exclusivamente no footer global (`#status-bar`). Nenhum panel exibe hints inline no corpo do widget. O footer atualiza dinamicamente conforme o panel em foco, garantindo single source of truth para as teclas disponíveis ao usuário.

**Decisão arquitetural:** ADR-035

**Regras — Localização única:**

1. Apenas o `StatusBar` (`#status-bar`) renderiza hints. Panels (`HabitsPanel`, `TasksPanel`, `TimerPanel`, `AgendaPanel`, `MetricsPanel`) não emitem strings de hint nos métodos `_build_*_lines`.
2. Docstrings de métodos de build de conteúdo que historicamente continham hints e foram removidas devem mencionar este princípio para evitar reintrodução acidental.

**Regras — Formato canônico:**

3. Cada hint segue o padrão `(<tecla>) <descrição>`, com parênteses. Exemplos: `(q) sair`, `(j/k) navegar`, `(Ctrl+Q) sair`, `(↑↓) navegar`.
4. Múltiplos hints na mesma string são separados por ` · ` (espaço + U+00B7 ponto medial + espaço): `(v) concluir · (s) skip · (t) timer`.
5. Convenção da tecla: uma letra como `(v)`, combinações como `(Ctrl+Q)`, setas como `(↑↓)`, múltiplas teclas equivalentes como `(j/k)` ou `(h/l)`.
6. Este formato é usado tanto no mapa `PANEL_KEYBINDINGS` quanto na saída renderizada. Não há conversão de delimitadores — o `_format_hint` apenas aplica cores e retorna.

**Regras — Cores:**

7. Parênteses e tecla recebem `C_INFO` (`#89B4FA`, azul Catppuccin). A cor é aplicada via markup Rich pelo helper `_format_hint`, não via TCSS global do `#status-center`.
8. Descrição (texto após `)`) recebe `C_SUBTEXT1` (`#BAC2DE`, cinza claro Catppuccin).
9. O uso de `[dim]` envolvendo o hint inteiro está proibido. A hierarquia visual vem das duas cores Catppuccin distintas, não de opacidade global.

**Regras — Contextualidade:**

10. O `StatusBar` mantém um mapa `PANEL_KEYBINDINGS: dict[panel_id, hint_string]` no módulo `status_bar.py`. Cada entrada do mapa é uma string no formato definido pelas regras 3-5.
11. Quando `focused_panel` muda (via `update_focused_panel`), o `_build_center_section` consulta `PANEL_KEYBINDINGS.get(panel_id, DEFAULT_KEYBINDINGS)` e aplica `_format_hint` ao resultado.
12. `DEFAULT_KEYBINDINGS` é o fallback usado quando nenhum panel está em foco ou quando o panel_id não existe no mapa. Deve cobrir as ações globais (Tab, ajuda, sair).
13. Todos os IDs de panel registrados no dashboard têm entrada correspondente em `PANEL_KEYBINDINGS`. Adicionar um panel novo sem registrar seu hint é violação desta BR.

**Testes:**

- `test_br_tui_034_format_single_key`
- `test_br_tui_034_format_multiple_keys`
- `test_br_tui_034_format_multichar_key`
- `test_br_tui_034_format_arrow_key`
- `test_br_tui_034_format_empty_returns_empty`
- `test_br_tui_034_panel_keybindings_all_panels_covered`
- `test_br_tui_034_default_keybindings_when_unknown_panel`

**Referências:**

- ADR-035 (Keybindings Standardization)
- BR-TUI-007 (StatusBar — definição original do footer contextual)
- BR-TUI-008 (Visual Consistency Material-like — paleta Catppuccin)
- Issue #29 (TimerPanel hint removal — primeiro caso prático do princípio)
- Issue #44 (motivação documental desta BR)
- Issue #32 (implementação do formato `(tecla) descrição` com cores)

**Histórico:** versão original 10/04/2026 usava formato `[tecla]` com colchetes no mapa e conversão para `(tecla)` no render. Emendada 16/04/2026: formato unificado para `(tecla)` em fonte e render por incompatibilidade do escape `\[\]` na pipeline Rich→Textual (v1.7.2, issues #32, #44).

---

### BR-TUI-035: Conteúdo Interno do HeaderBar (NOVA 16/04/2026)

**Descrição:** O conteúdo interno do HeaderBar exibe métricas agregadas do dia/semana em três seções: progresso semanal de hábitos, progresso de tarefas do dia e próximo item pendente. Informação de contexto (rotina ativa, data) vive nos atributos `border_title` e `border_subtitle` do widget, não no conteúdo interno.

**Decisão arquitetural:** ADR-052

**Regras — Seção 1: Progresso semanal de hábitos:**

1. Formato: `Hábitos X/Y ▪▪▪▪▪▪░░░░ ZZ%`. X = instâncias DONE na semana corrente (segunda a domingo). Y = total esperado (hábitos ativos × dias transcorridos na semana).
2. Barra visual com 10 caracteres (`▪` para preenchido, `░` para restante), proporcional ao percentual arredondado.
3. Percentual exibido como inteiro seguido de `%`: `60%`, `100%`.
4. Quando sem rotina ativa: `[dim]Hábitos --/--[/dim]` sem barra e sem percentual.
5. Cor da barra: C_SUCCESS (`#A6E3A1`) quando percentual >= 90%, C_INFO (`#89B4FA`) quando < 90%.

**Regras — Seção 2: Progresso de tarefas do dia:**

6. Formato: `Tarefas X/Y ▪▪▪░░ ZZ%`. X = tarefas concluídas hoje. Y = tarefas com deadline hoje ou pendentes sem deadline.
7. Barra visual com 5 caracteres, mesma convenção de `▪`/`░`.
8. Quando Y = 0: `[dim]Sem tarefas[/dim]` sem barra.
9. Quando X = Y e Y > 0: barra inteira em C_SUCCESS.
10. Cor padrão da barra: C_INFO quando percentual < 90%.

**Regras — Seção 3: Próximo item:**

11. Formato: `Próximo: {nome} em {countdown}`. Nome do próximo hábito ou tarefa pendente, o que vier primeiro cronologicamente.
12. Countdown em formato relativo: `em Xmin` (< 60min), `em XhYY` (>= 60min). Exemplos: `em 25min`, `em 1h15`.
13. Hábitos considerados: instâncias com status `pending` e `scheduled_start` futuro no dia corrente.
14. Tarefas consideradas: tarefas pendentes com horário definido hoje e `scheduled_start` futuro.
15. Quando empate de horário: hábito tem prioridade (rotina é o eixo principal do ATOMVS).
16. Nome truncado com `…` se exceder espaço disponível na seção.
17. Quando sem itens pendentes restantes hoje: `[dim]Sem próximos hoje[/dim]`.

**Regras — Layout e responsividade:**

18. Seções separadas por `  [dim]│[/dim]  ` (2 espaços + pipe dim + 2 espaços).
19. Distribuição: seções alinhadas à esquerda com gap proporcional preenchendo a largura disponível.
20. Viewport < 80 colunas: seção 3 (Próximo) colapsa — não é exibida.
21. Viewport < 60 colunas: seção 2 (Tarefas) também colapsa — apenas seção 1 visível.

**Regras — Eliminação de redundância:**

22. O nome da rotina ativa NÃO aparece no conteúdo interno — vive exclusivamente no `border_title`.
23. Timer NÃO aparece no conteúdo interno — vive exclusivamente no TimerPanel.
24. Uma única chamada ao `RoutineService.get_active_routine()` por refresh alimenta tanto o `border_title` quanto a seção 1.

**Testes:**

- `test_br_tui_035_habits_progress_format`
- `test_br_tui_035_habits_progress_no_routine`
- `test_br_tui_035_tasks_progress_format`
- `test_br_tui_035_tasks_progress_no_tasks`
- `test_br_tui_035_next_item_habit`
- `test_br_tui_035_next_item_task`
- `test_br_tui_035_next_item_none`
- `test_br_tui_035_responsive_collapse_80`
- `test_br_tui_035_responsive_collapse_60`
- `test_br_tui_035_no_routine_name_in_content`
- `test_br_tui_035_no_timer_in_content`

**Referências:**

- ADR-052 (Redesign do conteúdo interno do HeaderBar)
- BR-TUI-003 (Dashboard Screen — regras gerais)
- BR-TUI-034 (Hints no footer — sem call-to-action no header)
- Issue #52 (motivação desta BR)

---

### BR-TUI-036: Deleção Contextual no DashboardScreen via `x` (NOVA 10/06/2026)

**Descrição:** No DashboardScreen, a tecla `x` aciona a deleção do item sob o cursor do panel focado, sem exigir navegação até a CRUD screen dedicada. O despacho é contextual ao panel em foco: HabitsPanel deleta o hábito selecionado, TasksPanel deleta a tarefa selecionada. AgendaPanel e TimerPanel não possuem item deletável e tratam `x` como no-op. A operação é destrutiva e exige confirmação modal (`ConfirmDialog`) antes de executar, reaproveitando o mesmo widget e padrão das CRUD screens. Após a operação, o feedback é dado por notificação (`app.notify`) e pelo refresh dos panels.

**Decisão arquitetural:** ADR-037 (TUI Keybindings Standard — `x` como CRUD contextual "Deletar item sob cursor")

**Regras — Despacho contextual:**

1. No DashboardScreen, `x` é interceptado pelo `on_key` e despachado conforme o panel focado (`_focused_panel`), seguindo o mesmo mecanismo de `n` (criar) e `e` (editar).
2. HabitsPanel (`panel-habits`) focado com item sob cursor: aciona a deleção do hábito selecionado via `HabitService.delete_habit` (que é soft delete / archive — BR-HABIT-005/006).
3. TasksPanel (`panel-tasks`) focado com item sob cursor: aciona a deleção da tarefa selecionada via `TaskService.delete_task`.
4. AgendaPanel focado: `x` é no-op no MVP. Deleção de `HabitInstance` individual do dia (skip permanente) fica reservada para spike futuro.
5. TimerPanel focado: `x` é no-op (não há item deletável).
6. Quando o panel focado não possui item sob cursor (lista vazia ou seleção nula), `x` é no-op silencioso — nenhum dialog é aberto.

**Regras — Confirmação obrigatória:**

7. Antes de executar qualquer deleção, o DashboardScreen exibe um `ConfirmDialog` modal com título `Deletar <Tipo>` e mensagem `Deletar '<title>'?`, idêntico ao padrão das CRUD screens dedicadas.
8. Cancelar o `ConfirmDialog` (Esc ou ação de cancelar) não executa a deleção, não emite notificação e não dispara refresh — o estado permanece inalterado.
9. Apenas a confirmação explícita do dialog invoca o service de deleção.

**Regras — Feedback pós-operação:**

10. Em deleção bem-sucedida: emitir `app.notify(f"Deletado: {title}")` e, em seguida, `refresh_data()` no DashboardScreen para atualizar todos os panels.
11. Em erro retornado pelo `service_action` (tupla `(_, error)` com `error` não nulo): emitir `app.notify(error, severity="error")` e retornar sem disparar `refresh_data()` desnecessário.
12. A captura do resultado segue o contrato de `service_action`, que nunca propaga exceção à TUI e retorna `(resultado, None)` em sucesso ou `(None, mensagem_erro)` em falha.

**Regras — Affordance na StatusBar:**

13. Quando HabitsPanel ou TasksPanel está focado, o hint contextual da StatusBar (`PANEL_KEYBINDINGS`, BR-TUI-034) inclui `(x) deletar`.
14. Quando AgendaPanel, TimerPanel ou nenhum panel deletável está focado, o hint NÃO inclui `(x) deletar` (coerência com o no-op das regras 4 e 5).
15. O help overlay (`?`) lista `x` como "Deletar item" no contexto do DashboardScreen.

**Nota de consistência:** As regras 10 e 11 estabelecem notificação de sucesso E erro para a deleção contextual de hábito e tarefa. Isso diverge intencionalmente do `open_delete_routine` existente (BR-TUI-016), que notifica apenas em erro e delega o feedback de sucesso ao refresh (o item desaparece da lista). A divergência é uma decisão consciente: a deleção contextual corre direto do dashboard sem troca de contexto, e a notificação de sucesso reforça o feedback da ação destrutiva. A uniformização retroativa do padrão de notify de rotina fica fora do escopo desta BR.

**Testes:**

- `test_dashboard_delete_habit_via_x_focused_panel`
- `test_dashboard_delete_task_via_x_focused_panel`
- `test_dashboard_delete_habit_notifies_on_success`
- `test_dashboard_delete_task_notifies_on_success`
- `test_dashboard_delete_cancel_does_not_delete`
- `test_dashboard_delete_cancel_does_not_notify`
- `test_dashboard_statusbar_hint_includes_delete_when_habits_focused`
- `test_dashboard_statusbar_hint_includes_delete_when_tasks_focused`
- `test_dashboard_statusbar_hint_excludes_delete_when_timer_focused`

**Referências:**

- ADR-037 (TUI Keybindings Standard — `x` como CRUD contextual)
- BR-TUI-016 (CRUD de rotinas — padrão `service_action` + notify; divergência de notify documentada na Nota de consistência)
- BR-TUI-017 / BR-TUI-018 (delete de hábito e tarefa via CRUD screens dedicadas)
- BR-TUI-034 (hints contextuais no footer global)
- BR-HABIT-005 / BR-HABIT-006 (delete de hábito é soft delete / archive — pré-requisito resolvido pela issue #61)
- Issue #62 (motivação desta BR)
