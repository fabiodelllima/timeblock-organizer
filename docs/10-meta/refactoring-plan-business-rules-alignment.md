# Plano de Refatoração: Business Rules Alignment

- **Branch:** `refactor/business-rules-alignment`
- **Data:** 06 de Novembro de 2025
- **Objetivo:** Alinhar código com regras de negócio documentadas

---

## Resumo Executivo

O EventReorderingService atual implementa lógica de priorização automática e sugestões de reordenamento que contradizem as regras de negócio reais do TimeBlock. Este plano detalha as mudanças necessárias para transformar o service em um serviço puro de detecção de conflitos.

---

## Análise do Estado Atual

Baseado na documentação do projeto (SESSAO-EVENT-REORDERING-COMPLETA.md, ANALISE-PROJETO-TIMEBLOCK.md), o código atual implementa:

### Funcionalidades Implementadas (a serem removidas)

1. **`calculate_priorities()`** - Calcula prioridades automáticas (CRITICAL, HIGH, NORMAL, LOW)
2. **`propose_reordering()`** - Gera proposta de reordenamento automático
3. **`apply_reordering()`** - Aplica mudanças (se existir)
4. **EventPriority enum** - Define prioridades automáticas
5. **ProposedChange dataclass** - Sugestões de novos horários
6. **ReorderingProposal dataclass** - Proposta completa de reordenamento

### Funcionalidades a Manter

1. **`detect_conflicts()`** - Detecção de sobreposições temporais
2. **Conflict dataclass** - Representação de conflito
3. **ConflictType enum** - OVERLAP, SEQUENTIAL
4. **Helpers de detecção** - `_get_event_times()`, `_has_overlap()`, etc.

---

## Mudanças Necessárias

### Fase 1: Remover Lógica de Priorização e Reordenamento

#### Arquivo: `src/timeblock/services/event_reordering_models.py`

**Remover completamente:**

```python
class EventPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class ProposedChange:
    event_id: int
    event_type: str
    event_title: str
    current_start: datetime
    current_end: datetime
    proposed_start: datetime
    proposed_end: datetime
    reason: str

@dataclass
class ReorderingProposal:
    conflicts: list[Conflict]
    proposed_changes: list[ProposedChange]
    estimated_duration_shift: int
```

**Manter apenas:**

```python
class ConflictType(str, Enum):
    OVERLAP = "overlap"
    SEQUENTIAL = "sequential"

@dataclass
class Conflict:
    triggered_event_id: int
    triggered_event_type: str
    conflicting_event_id: int
    conflicting_event_type: str
    conflict_type: ConflictType
    triggered_start: datetime
    triggered_end: datetime
    conflicting_start: datetime
    conflicting_end: datetime
```

#### Arquivo: `src/timeblock/services/event_reordering_service.py`

**Remover métodos:**

```python
@staticmethod
def calculate_priorities(events: list, current_time: datetime) -> dict[int, EventPriority]:
    # REMOVER COMPLETAMENTE
    pass

@staticmethod
def propose_reordering(conflicts: list[Conflict]) -> ReorderingProposal:
    # REMOVER COMPLETAMENTE
    pass

@staticmethod
def apply_reordering(proposal: ReorderingProposal, user_approved: bool) -> list:
    # REMOVER COMPLETAMENTE
    pass

@staticmethod
def _calculate_event_priority(event, current_time: datetime) -> EventPriority:
    # REMOVER COMPLETAMENTE
    pass
```

**Manter e refinar:**

```python
@staticmethod
def detect_conflicts(
    triggered_event_id: int,
    event_type: str,
) -> list[Conflict]:
    """
    Detecta conflitos temporais com outros eventos.

    Retorna lista de conflitos baseado em sobreposição temporal.
    NÃO modifica nenhum dado, apenas consulta e retorna informações.

    Args:
        triggered_event_id: ID do evento que desencadeou a verificação
        event_type: Tipo do evento ("task", "habit_instance", "event")

    Returns:
        Lista de conflitos detectados. Lista vazia se não houver conflitos.
    """
    pass

@staticmethod
def get_conflicts_for_day(date: date) -> list[Conflict]:
    """
    Retorna todos os conflitos detectados em um dia específico.

    Útil para visualização geral da agenda do dia.

    Args:
        date: Data para buscar conflitos

    Returns:
        Lista de todos os conflitos do dia
    """
    pass

# Helpers privados (manter)
@staticmethod
def _get_event_by_type(session, event_id: int, event_type: str):
    pass

@staticmethod
def _get_event_times(event) -> tuple[datetime, datetime]:
    pass

@staticmethod
def _get_events_in_range(session, start: datetime, end: datetime) -> list:
    pass

@staticmethod
def _has_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    pass

@staticmethod
def _is_same_event(event, event_id: int, event_type: str) -> bool:
    pass

@staticmethod
def _get_event_type(event) -> str:
    pass
```

---

### Fase 2: Atualizar Services que Integram com EventReordering

#### Arquivo: `src/timeblock/services/habit_instance_service.py`

**ANTES (implementação incorreta):**

```python
def adjust_instance_time(
    instance_id: int,
    new_start: time | None = None,
    new_end: time | None = None,
) -> tuple[Optional[HabitInstance], Optional[ReorderingProposal]]:
    # ... ajusta instância ...
    instance.user_override = True  # REMOVER
    instance.manually_adjusted = True  # REMOVER

    conflicts = EventReorderingService.detect_conflicts(instance_id, "habit_instance")
    if conflicts:
        proposal = EventReorderingService.propose_reordering(conflicts)  # REMOVER
        return instance, proposal

    return instance, None
```

**DEPOIS (implementação correta):**

```python
def adjust_instance_time(
    instance_id: int,
    new_start: time | None = None,
    new_end: time | None = None,
) -> tuple[Optional[HabitInstance], Optional[list[Conflict]]]:
    """
    Ajusta horário de instância específica.

    Returns:
        Tupla (instância atualizada, lista de conflitos detectados)
    """
    # ... validações ...

    with get_engine_context() as engine, Session(engine) as session:
        instance = session.get(HabitInstance, instance_id)
        if not instance:
            return None, None

        instance.scheduled_start = new_start
        instance.scheduled_end = new_end

        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Detecta conflitos mas NÃO gera proposta de reordenamento
        conflicts = EventReorderingService.detect_conflicts(
            instance_id,
            "habit_instance"
        )

        return instance, conflicts
```

#### Arquivo: `src/timeblock/services/task_service.py`

**Mudança Similar:**

```python
def update_task(
    task_id: int,
    title: str | None = None,
    scheduled_datetime: datetime | None = None,
    description: str | None = None,
    tag_id: int | None = None,
) -> tuple[Optional[Task], Optional[list[Conflict]]]:
    """
    Atualiza task existente.

    Returns:
        Tupla (task atualizada, lista de conflitos se horário mudou)
    """
    # ... atualização ...

    conflicts = None
    if scheduled_datetime is not None:
        conflicts = EventReorderingService.detect_conflicts(task_id, "task")

    return task, conflicts
```

#### Arquivo: `src/timeblock/services/timer_service.py`

**Mudança Similar:**

```python
def start_timer(
    event_id: int | None = None,
    task_id: int | None = None,
    habit_instance_id: int | None = None,
) -> tuple[TimeLog, Optional[list[Conflict]]]:
    """
    Inicia timer para evento.

    Returns:
        Tupla (timelog criado, lista de conflitos detectados)
    """
    # ... criação do timelog ...

    # Detecta conflitos no horário atual
    if habit_instance_id:
        conflicts = EventReorderingService.detect_conflicts(
            habit_instance_id,
            "habit_instance"
        )
    elif task_id:
        conflicts = EventReorderingService.detect_conflicts(task_id, "task")
    else:
        conflicts = None

    return timelog, conflicts
```

---

### Fase 3: Atualizar CLI Commands

#### Arquivo: `src/timeblock/commands/reschedule.py`

**ANTES:**

```python
@app.command("preview")
def preview(event_id: int, event_type: str = "task"):
    """Visualiza proposta de reordenamento."""
    conflicts = EventReorderingService.detect_conflicts(event_id, event_type)
    if not conflicts:
        console.print("Nenhum conflito detectado")
        return

    proposal = EventReorderingService.propose_reordering(conflicts)
    display_proposal(proposal, console)
```

**DEPOIS:**

```python
@app.command("conflicts")
def conflicts(
    event_id: int = typer.Option(None, help="ID do evento específico"),
    event_type: str = typer.Option(None, help="Tipo do evento"),
    date: str = typer.Option(None, help="Data específica (YYYY-MM-DD)"),
):
    """Visualiza conflitos detectados."""

    if event_id and event_type:
        # Conflitos de um evento específico
        conflicts = EventReorderingService.detect_conflicts(event_id, event_type)
    elif date:
        # Conflitos de um dia específico
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        conflicts = EventReorderingService.get_conflicts_for_day(parsed_date)
    else:
        console.print("[red]Especifique --event-id e --event-type ou --date[/red]")
        raise typer.Exit(1)

    if not conflicts:
        console.print("[green]Nenhum conflito detectado[/green]")
        return

    # Exibe conflitos de forma clara
    display_conflicts(conflicts, console)
```

**Remover completamente:**

- Subcomando `apply` (não faz sentido sem proposta de reordenamento)
- Função `display_proposal()` em `proposal_display.py`
- Função `confirm_apply_proposal()` em `proposal_display.py`

**Criar nova função:**

```python
# src/timeblock/utils/conflict_display.py
def display_conflicts(conflicts: list[Conflict], console: Console):
    """Exibe conflitos de forma estruturada."""

    console.print(f"\n[yellow]⚠ {len(conflicts)} conflito(s) detectado(s)[/yellow]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Evento 1", style="cyan")
    table.add_column("Horário", style="cyan")
    table.add_column("Evento 2", style="yellow")
    table.add_column("Horário", style="yellow")
    table.add_column("Sobreposição", style="red")

    for conflict in conflicts:
        # Calcula sobreposição
        overlap_start = max(conflict.triggered_start, conflict.conflicting_start)
        overlap_end = min(conflict.triggered_end, conflict.conflicting_end)
        overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)

        table.add_row(
            f"{conflict.triggered_event_type} #{conflict.triggered_event_id}",
            f"{conflict.triggered_start.strftime('%H:%M')}-{conflict.triggered_end.strftime('%H:%M')}",
            f"{conflict.conflicting_event_type} #{conflict.conflicting_event_id}",
            f"{conflict.conflicting_start.strftime('%H:%M')}-{conflict.conflicting_end.strftime('%H:%M')}",
            f"{overlap_minutes} min"
        )

    console.print(table)
    console.print("\n[dim]Use comandos específicos para ajustar eventos conforme necessário[/dim]")
```

#### Atualizar comandos que iniciam timer

**Arquivo: `src/timeblock/commands/timer.py`**

```python
@app.command("start")
def start(
    task_id: int = typer.Option(None, help="ID da task"),
    habit_instance_id: int = typer.Option(None, help="ID da instância de hábito"),
):
    """Inicia timer para evento."""

    timelog, conflicts = TimerService.start_timer(
        task_id=task_id,
        habit_instance_id=habit_instance_id
    )

    console.print(f"[green]✓[/green] Timer iniciado para {timelog.entity_type} #{timelog.entity_id}")

    # Se há conflitos, apresenta mas NÃO bloqueia
    if conflicts:
        console.print(f"\n[yellow]⚠ Atenção: {len(conflicts)} conflito(s) detectado(s)[/yellow]")
        display_conflicts(conflicts, console)
        console.print("\n[dim]Timer foi iniciado. Você pode ajustar eventos conflitantes depois.[/dim]")
```

---

### Fase 4: Atualizar Modelos

#### Arquivo: `src/timeblock/models/habit_instance.py`

**Remover campos:**

```python
# REMOVER estas linhas
user_override: bool = Field(default=False)
manually_adjusted: bool = Field(default=False)
```

**Modelo final:**

```python
class HabitInstance(SQLModel, table=True):
    """Representa ocorrência específica de um hábito em uma data."""

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id")
    date: date
    scheduled_start: time
    scheduled_end: time
    status: str = Field(default="planned")

    # Relacionamentos
    habit: Habit = Relationship(back_populates="instances")
    timelogs: list[TimeLog] = Relationship(back_populates="habit_instance")
```

**Criar migration:**

```bash
# Será necessária migration para remover colunas
alembic revision -m "remove_redundant_fields_from_habit_instance"
```

---

### Fase 5: Atualizar Todos os Testes

#### Testes de EventReorderingService

**Remover completamente:**

- `tests/unit/test_services/test_event_reordering_priorities.py`
- `tests/unit/test_services/test_event_reordering_propose.py`
- `tests/unit/test_services/test_event_reordering_apply.py`

**Manter e atualizar:**

- `tests/unit/test_services/test_event_reordering_service.py`

**Exemplo de teste correto:**

```python
class TestEventReorderingDetection:
    """Testa detecção de conflitos sem modificar dados."""

    def test_detect_simple_overlap(self, session, test_habit_instance, test_task):
        """Detecta sobreposição simples entre dois eventos."""
        # Arrange
        habit = test_habit_instance  # 07:00-08:00
        task = test_task  # 07:30-08:30

        # Act
        conflicts = EventReorderingService.detect_conflicts(
            habit.id,
            "habit_instance"
        )

        # Assert
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.OVERLAP
        assert conflicts[0].conflicting_event_id == task.id

    def test_detect_no_conflicts(self, session, test_habit_instance, test_task):
        """Retorna lista vazia quando não há conflitos."""
        # Arrange
        habit = test_habit_instance  # 07:00-08:00
        task = test_task  # 09:00-10:00 (sem sobreposição)

        # Act
        conflicts = EventReorderingService.detect_conflicts(
            habit.id,
            "habit_instance"
        )

        # Assert
        assert len(conflicts) == 0

    def test_detection_does_not_modify_data(self, session, test_habit_instance):
        """Verifica que detecção não modifica nenhum dado."""
        # Arrange
        original_start = test_habit_instance.scheduled_start
        original_end = test_habit_instance.scheduled_end

        # Act
        EventReorderingService.detect_conflicts(
            test_habit_instance.id,
            "habit_instance"
        )

        # Assert
        session.refresh(test_habit_instance)
        assert test_habit_instance.scheduled_start == original_start
        assert test_habit_instance.scheduled_end == original_end
```

#### Testes de Integração

**Atualizar para validar retorno correto:**

```python
class TestHabitInstanceServiceIntegration:
    """Testa integração de HabitInstanceService com detecção de conflitos."""

    def test_adjust_time_returns_conflicts(self, session, test_instance, test_task):
        """Ajuste de horário retorna conflitos detectados."""
        # Arrange: task às 09:00-10:00

        # Act: ajusta instância para 09:30
        instance, conflicts = HabitInstanceService.adjust_instance_time(
            test_instance.id,
            new_start=time(9, 30),
            new_end=time(10, 30)
        )

        # Assert
        assert instance.scheduled_start == time(9, 30)
        assert len(conflicts) == 1
        assert conflicts[0].conflicting_event_id == test_task.id

    def test_adjust_time_without_conflicts(self, session, test_instance):
        """Ajuste sem conflitos retorna lista vazia."""
        # Act
        instance, conflicts = HabitInstanceService.adjust_instance_time(
            test_instance.id,
            new_start=time(18, 0),
            new_end=time(19, 0)
        )

        # Assert
        assert instance.scheduled_start == time(18, 0)
        assert conflicts == []
```

#### Testes E2E

**Criar novos testes validando comportamento correto:**

```python
# tests/e2e/test_conflict_detection_workflow.py
class TestConflictDetectionWorkflow:
    """Testa fluxo completo de detecção e visualização de conflitos."""

    def test_adjust_habit_shows_conflicts_but_allows_adjustment(self, cli_runner):
        """Sistema apresenta conflitos mas não bloqueia ajuste."""
        # Arrange: criar hábito e task conflitantes

        # Act: ajustar hábito
        result = cli_runner.invoke(app, [
            "habit", "adjust", "42",
            "--start", "09:00"
        ])

        # Assert
        assert result.exit_code == 0
        assert "Instância ajustada" in result.output
        # Conflito é mencionado mas não impede ajuste

    def test_start_timer_with_conflicts_requires_confirmation(self, cli_runner):
        """Timer com conflitos pede confirmação mas permite prosseguir."""
        # Arrange: eventos conflitantes

        # Act: iniciar timer
        result = cli_runner.invoke(
            app,
            ["timer", "start", "--habit-instance", "42"],
            input="y\n"  # Confirma mesmo com conflitos
        )

        # Assert
        assert result.exit_code == 0
        assert "Timer iniciado" in result.output
        assert "conflito" in result.output.lower()
```

---

## Checklist de Implementação

### Sprint 1: Limpeza do EventReorderingService (2-3 dias)

- [ ] Remover EventPriority, ProposedChange, ReorderingProposal de `event_reordering_models.py`
- [ ] Remover métodos calculate_priorities, propose_reordering, apply_reordering
- [ ] Adicionar método get_conflicts_for_day
- [ ] Atualizar docstrings de métodos mantidos
- [ ] Garantir que detect_conflicts não modifica dados
- [ ] Commit: "refactor(services): Simplifica EventReorderingService para detecção apenas"

### Sprint 2: Atualizar Services Integradores (2 dias)

- [ ] Atualizar HabitInstanceService.adjust_instance_time
- [ ] Remover campos user_override e manually_adjusted do modelo
- [ ] Atualizar TaskService.update_task
- [ ] Atualizar TimerService.start_timer
- [ ] Todas as tuplas agora retornam list[Conflict], não ReorderingProposal
- [ ] Commit: "refactor(services): Atualiza serviços para retornar conflitos sem propostas"

### Sprint 3: Atualizar CLI Commands (2 dias)

- [ ] Refatorar comando reschedule para mostrar apenas conflitos
- [ ] Remover subcomando apply
- [ ] Criar função display_conflicts
- [ ] Atualizar comando timer start para mostrar conflitos
- [ ] Adicionar confirmação quando há conflitos
- [ ] Commit: "refactor(cli): Atualiza comandos para apresentar conflitos sem automação"

### Sprint 4: Migration e Modelo (1 dia)

- [ ] Criar migration para remover user_override e manually_adjusted
- [ ] Testar migration up e down
- [ ] Atualizar fixtures de teste
- [ ] Commit: "refactor(models): Remove campos redundantes de HabitInstance"

### Sprint 5: Atualizar Testes (3-4 dias)

- [ ] Remover testes de priorização e proposta
- [ ] Atualizar testes de detecção
- [ ] Atualizar testes de integração dos services
- [ ] Criar novos testes E2E validando fluxo correto
- [ ] Garantir 100% dos testes passando
- [ ] Commit: "test: Atualiza testes para validar comportamento correto"

### Sprint 6: Documentação Final (1 dia)

- [ ] Atualizar README se necessário
- [ ] Atualizar CHANGELOG
- [ ] Verificar consistência com docs/04-specifications/business-rules/
- [ ] Code review completo
- [ ] Commit: "docs: Atualiza documentação pós-refatoração"

---

## Riscos e Mitigações

### **Risco 1: Breaking Changes**

- Mitigação: Versão será 2.0 (major bump), breaking changes são esperados

### **Risco 2: Testes Falhando**

- Mitigação: Fazer mudanças incrementais, garantir testes passando a cada commit

### **Risco 3: Perda de Funcionalidade Útil**

- Mitigação: Documentar que priorização e sugestões virão em v2.5+ quando validadas

---

## Critérios de Sucesso

1. EventReorderingService apenas detecta conflitos, não resolve
2. Nenhum service modifica dados automaticamente sem confirmação do usuário
3. CLI apresenta conflitos claramente mas não bloqueia ações
4. Todos os testes passando (100%)
5. Código alinhado com documentação em docs/04-specifications/business-rules/
6. Zero automação de decisões sobre agenda do usuário

---

**Próximo Passo:** Executar Sprint 1 - Limpeza do EventReorderingService
