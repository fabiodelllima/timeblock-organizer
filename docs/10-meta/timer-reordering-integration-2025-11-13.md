# Integração Timer + Event Reordering

- **Data:** 13 de novembro de 2025
- **Tipo:** Gap Analysis & Integration Spec
- **Status:** [DESIGN]
- **Relacionado:** BR003, ADR-003, event-reordering.md

---

## GAP IDENTIFICADO

**O que JÁ existe:**

- Event Reordering Service (detecta conflitos, propõe mudanças)
- BR003: Lógica de reordering completa
- ADR-003: Decisão arquitetural baseada em prioridades

**O que FALTA:**

- Integração `habit timer` com Event Reordering
- Cálculo de atraso (tempo real vs ideal da Routine)
- Interface CLI para aceitar/rejeitar propostas após timer

---

## FLUXO COMPLETO: Timer -> Reordering

### 1. Usuário Inicia Timer (NO horário)

```bash
# Routine define: Almoço 12:00-13:00
$ habit timer start Almoço

[TIMER] 12:00 | Almoço
   00:00 / 01:00
   [HORÁRIO IDEAL - OK]
```

**Backend:**

```python
def timer_start(habit_id: int) -> TimerSession:
    habit = HabitService.get_habit(habit_id)
    instance = get_today_instance(habit)

    session = TimerSession(
        instance_id=instance.id,
        started_at=datetime.now(),
        ideal_start=datetime.combine(date.today(), instance.scheduled_start),
        ideal_end=datetime.combine(date.today(), instance.scheduled_end)
    )

    # Calcular atraso
    delay_minutes = (session.started_at - session.ideal_start).total_seconds() / 60

    if abs(delay_minutes) < 5:
        # Tolerância: ±5 min
        session.on_time = True
    else:
        session.on_time = False
        session.delay_minutes = delay_minutes

    return session
```

---

### 2. Usuário Para Timer (COM atraso)

```bash
# 13:30 - 1h30 após ideal
$ habit timer stop Almoço

[OK] Completo! 1h00 (100% meta)
     Concluído: 13:30 (1h30 após ideal)

[ANALISANDO IMPACTO NOS PRÓXIMOS HABITS...]
```

#### **Backend: Integração com Event Reordering**

```python
def timer_stop(session: TimerSession) -> TimerResult:
    """
    Para timer e dispara Event Reordering se necessário.

    Integra com EventReorderingService existente.
    """
    session.stopped_at = datetime.now()
    session.time_spent = (session.stopped_at - session.started_at).total_seconds()

    # Marca instância como completa
    instance = session.instance
    instance.status = "completed"
    instance.actual_start = session.started_at
    instance.actual_end = session.stopped_at
    save(instance)

    # Calcular atraso total
    delay = (session.stopped_at - session.ideal_end).total_seconds() / 60

    if abs(delay) < 5:
        # Tolerância: não precisa reorganizar
        return TimerResult(
            session=session,
            needs_reordering=False
        )

    # DISPARA EVENT REORDERING
    proposal = trigger_reordering_analysis(instance, delay)

    if not proposal:
        # Nenhum conflito detectado
        return TimerResult(
            session=session,
            needs_reordering=False
        )

    # Tem conflitos: apresentar proposta ao usuário
    return TimerResult(
        session=session,
        needs_reordering=True,
        reordering_proposal=proposal
    )


def trigger_reordering_analysis(
    completed_instance: HabitInstance,
    delay_minutes: float
) -> ReorderingProposal | None:
    """
    Integra Timer com Event Reordering Service.

    Usa código existente de EventReorderingService.
    """
    # 1. Buscar habits seguintes do dia (mesma Routine)
    following_habits = get_following_habits_in_routine(
        routine=completed_instance.habit.routine,
        after_time=completed_instance.actual_end
    )

    if not following_habits:
        # Último habit do dia
        return None

    # 2. Usar Event Reordering Service existente
    conflicts = []
    for habit_inst in following_habits:
        # Simular conflito (habit terminou atrasado)
        conflict_detected = EventReorderingService.detect_conflicts(
            triggered_event_id=completed_instance.id,
            event_type="habit_instance"
        )
        conflicts.extend(conflict_detected)

    if not conflicts:
        return None

    # 3. Gerar propostas usando algoritmo existente
    proposed_changes = generate_reordering_proposals(
        conflicts=conflicts,
        delay_minutes=delay_minutes,
        following_habits=following_habits
    )

    return ReorderingProposal(
        conflicts=conflicts,
        proposed_changes=proposed_changes,
        estimated_duration_shift=int(delay_minutes),
        affected_events_count=len(following_habits)
    )
```

---

### 3. Interface CLI: Aceitar/Rejeitar Proposta

```bash
+------------------------------------------------+
| REORGANIZAÇÃO NECESSÁRIA                       |
+------------------------------------------------+
| "Almoço" terminou 13:30 (1h30 após ideal).   |
|                                                |
| Habits afetados:                              |
|   - Leitura (ideal: 13:00-14:00)             |
|   - Reunião (ideal: 14:00-15:00) [CRÍTICA]   |
|   - Emails (ideal: 15:00-16:00)              |
|                                                |
| Opções:                                       |
|                                                |
| [1] Empurrar tudo +1h30                       |
|     14:30-15:30 Leitura                       |
|     15:30-16:30 Reunião (+1h30) [!]          |
|     16:30-17:30 Emails (+1h30)               |
|                                                |
| [2] Pular Leitura (priorizar Reunião)        |
|     [SKIP] Leitura                            |
|     14:30-15:30 Reunião (+30min)             |
|     15:30-16:30 Emails (+30min)              |
|                                                |
| [3] Encurtar Leitura (30min)                  |
|     14:30-15:00 Leitura (50%)                |
|     15:00-16:00 Reunião (ideal mantido!)     |
|     16:00-17:00 Emails                        |
|                                                |
| [4] Ajustar manualmente                       |
| [5] Ignorar (manter como está)                |
|                                                |
| Escolha [1-5]: _                              |
+------------------------------------------------+
```

**Implementação CLI:**

```python
def display_reordering_proposal(proposal: ReorderingProposal) -> str:
    """
    Apresenta proposta ao usuário e captura escolha.

    Returns:
        "accept_option_1" | "accept_option_2" | ... | "reject"
    """
    # Renderizar UI (usando Rich ou ASCII art)
    render_proposal_ui(proposal)

    # Capturar input
    choice = click.prompt("Escolha [1-5]", type=int)

    if choice == 5:
        return "reject"
    elif choice == 4:
        # Modo manual (futuro)
        return "manual_edit"
    else:
        return f"accept_option_{choice}"


def apply_user_choice(
    choice: str,
    proposal: ReorderingProposal
) -> None:
    """
    Aplica escolha do usuário.

    Usa código existente de BR003 (apply_reordering).
    """
    if choice == "reject":
        click.echo("Reorganização ignorada.")
        return

    if choice.startswith("accept_option_"):
        option_num = int(choice.split("_")[-1])
        selected_changes = proposal.options[option_num - 1]

        # Aplicar usando código existente (BR003)
        result = apply_reordering(
            events=get_affected_instances(proposal),
            proposals=selected_changes
        )

        if result.failed:
            click.echo(f"[ERRO] {len(result.failed)} mudanças falharam")
            for fail in result.failed:
                click.echo(f"  - {fail}")
        else:
            click.echo(f"[OK] {len(result.moved)} habits reorganizados")
            for moved in result.moved:
                click.echo(f"  - {moved.habit.title}: {moved.scheduled_start}")
```

---

## MODELO DE DADOS ADICIONAL

```python
class TimerSession(SQLModel, table=True):
    """Sessão de timer ativa ou concluída."""
    id: int | None = Field(default=None, primary_key=True)
    instance_id: int = Field(foreign_key="habitinstances.id")

    # Horários ideais (da Routine)
    ideal_start: datetime
    ideal_end: datetime

    # Horários reais (do timer)
    started_at: datetime
    stopped_at: datetime | None

    # Métricas
    time_spent_seconds: int = Field(default=0)
    delay_minutes: float = Field(default=0.0)
    on_time: bool = Field(default=True)

    # Reordering disparado?
    triggered_reordering: bool = Field(default=False)
    reordering_accepted: bool | None  # None = proposta rejeitada

    instance: HabitInstance = Relationship(back_populates="timer_sessions")
```

---

## COMANDOS CLI FINAIS

```bash
# Iniciar timer
habit timer start HABIT

# Parar timer (pode disparar reordering)
habit timer stop HABIT

# Ver timer ativo
habit timer status

# Histórico de timers
habit timer history HABIT [--days N]
```

---

## INTEGRAÇÃO COM CÓDIGO EXISTENTE

**Arquivos a modificar:**

1. `src/timeblock/commands/habit.py`

   - Adicionar `timer start/stop` subcommands

2. `src/timeblock/services/timer_service.py` (NOVO)

   - Gestão de TimerSession
   - Integração com Event Reordering

3. `src/timeblock/services/event_reordering_service.py` (EXISTENTE)

   - Sem mudanças! Já funciona
   - Apenas chamado pelo timer_service

4. `src/timeblock/models/timer.py` (NOVO)
   - Model TimerSession

---

## TESTES NECESSÁRIOS

```python
# tests/integration/test_timer_reordering.py

def test_timer_triggers_reordering_on_delay():
    """Timer atrasado dispara reordering."""
    # Setup: Routine com 3 habits
    # Habit 1: 12:00-13:00
    # Habit 2: 13:00-14:00
    # Habit 3: 14:00-15:00

    # Timer começa 13:30 (1h30 atrasado)
    session = timer_start(habit1, start_time=datetime(2025,11,13,13,30))

    # Timer para 14:30
    result = timer_stop(session, stop_time=datetime(2025,11,13,14,30))

    # Assert: Reordering proposto
    assert result.needs_reordering
    assert len(result.reordering_proposal.conflicts) == 2
    assert result.reordering_proposal.estimated_duration_shift == 90


def test_timer_no_reordering_on_time():
    """Timer no horário não dispara reordering."""
    session = timer_start(habit1, start_time=datetime(2025,11,13,12,0))
    result = timer_stop(session, stop_time=datetime(2025,11,13,13,0))

    assert not result.needs_reordering
```

---

## PRÓXIMOS PASSOS

1. **Sprint 1:** Implementar TimerSession model
2. **Sprint 2:** Implementar timer_service (start/stop)
3. **Sprint 3:** Integrar com Event Reordering Service
4. **Sprint 4:** Interface CLI de proposta
5. **Sprint 5:** Testes de integração

---

**Referências:**

- BR003: docs/04-specifications/business-rules/BR003-reordering-logic.md
- ADR-003: docs/03-decisions/003-event-reordering.md
- Algoritmo: docs/04-specifications/algorithms/event-reordering.md
- Service existente: src/timeblock/services/event_reordering_service.py

**Status:** Aguardando aprovação para implementação
