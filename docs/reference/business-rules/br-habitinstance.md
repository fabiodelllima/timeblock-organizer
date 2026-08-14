# HabitInstance

A HabitInstance é o átomo do TimeBlock Planner — a menor unidade acionável do sistema. Cada instância representa uma oportunidade concreta e específica de executar um hábito: "Leitura, dia 20 de fevereiro, das 21:00 às 22:00". Enquanto o Habit expressa a intenção recorrente, a HabitInstance captura a realidade de um único dia. É nela que o ciclo de feedback se completa: o usuário planeja (Habit), executa (HabitInstance), mede (Timer/TimeLog) e avalia (substatus).

O ciclo de vida de uma instância segue três estados principais: PENDING (aguardando execução), DONE (concluída) e NOT*DONE (não realizada). Mas a riqueza do modelo está nos substatus que qualificam \_como* cada transição aconteceu. Uma instância DONE pode ser FULL (tempo completo), PARTIAL (tempo reduzido), OVERDONE (ligeiramente acima) ou EXCESSIVE (muito acima do planejado). Uma instância NOT_DONE pode ser SKIPPED (pulada conscientemente, com justificativa) ou IGNORED (expirou sem ação). Essa granularidade transforma um simples checkbox em um registro nuanceado que permite ao usuário identificar padrões e ajustar sua rotina com dados reais.

O cálculo de substatus é automático e baseado no percentual de completude: a razão entre o tempo real de execução e o tempo planejado. Se a meditação planejada para 30 minutos durou 25 minutos, o percentual é 83% e o substatus é PARTIAL. Essa automação libera o usuário de avaliações subjetivas — o sistema calcula, o usuário decide o que fazer com a informação. Cada HabitInstance mantém referência ao seu Habit pai, data específica e horários (que podem diferir do template se o usuário fez ajustes pontuais naquele dia), preservando a separação entre plano e execução.

### BR-HABITINSTANCE-001: Status Principal

**Descrição:** HabitInstance possui 3 status principais.

**Enum Status:**

```python
class Status(str, Enum):
    PENDING = "pending"      # Agendado, não iniciado
    DONE = "done"            # Realizado
    NOT_DONE = "not_done"    # Não realizado
```

**Transições:**

```plaintext
PENDING
  ├─> DONE (via timer stop ou log manual)
  └─> NOT_DONE (via skip ou timeout)

DONE -> PENDING (via undo - ADR-038 D1)
NOT_DONE -> PENDING (via undo - ADR-038 D1)
```

**Testes:**

- `test_br_habitinstance_001_valid_status`
- `test_br_habitinstance_001_transitions`

---

### BR-HABITINSTANCE-002: Substatus Obrigatório

**Descrição:** Status finais requerem substatus correspondente.

**DoneSubstatus (quando DONE):**

```python
class DoneSubstatus(str, Enum):
    FULL = "full"            # 90-110% da meta
    PARTIAL = "partial"      # <90% da meta
    OVERDONE = "overdone"    # 110-150% da meta
    EXCESSIVE = "excessive"  # >150% da meta
```

**NotDoneSubstatus (quando NOT_DONE):**

```python
class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"      # Timeout sem ação
```

**Regras de Consistência:**

1. DONE requer done_substatus preenchido
2. NOT_DONE requer not_done_substatus preenchido
3. PENDING não pode ter substatus
4. Substatus são mutuamente exclusivos

**Validação:**

```python
def validate_status_consistency(self) -> None:
    if self.status == Status.DONE:
        if self.done_substatus is None:
            raise ValueError("done_substatus obrigatório quando status=DONE")
        if self.not_done_substatus is not None:
            raise ValueError("not_done_substatus deve ser None quando status=DONE")
    # ... similar para NOT_DONE e PENDING
```

**Testes:**

- `test_br_habitinstance_002_done_requires_substatus`
- `test_br_habitinstance_002_not_done_requires_substatus`
- `test_br_habitinstance_002_pending_no_substatus`
- `test_br_habitinstance_002_mutually_exclusive`

---

### BR-HABITINSTANCE-003: Completion Thresholds

**Descrição:** DoneSubstatus é calculado baseado em completion percentage.

**Thresholds:**

| Completion | Substatus | Feedback                |
| ---------- | --------- | ----------------------- |
| > 150%     | EXCESSIVE | [WARN] Ultrapassou meta |
| 110-150%   | OVERDONE  | [INFO] Acima da meta    |
| 90-110%    | FULL      | [OK] Perfeito           |
| < 90%      | PARTIAL   | Abaixo da meta          |

**Formula:**

```python
completion = (actual_duration / expected_duration) * 100
```

**Testes:**

- `test_br_habitinstance_003_threshold_full`
- `test_br_habitinstance_003_threshold_partial`
- `test_br_habitinstance_003_threshold_overdone`
- `test_br_habitinstance_003_threshold_excessive`

---

### BR-HABITINSTANCE-004: Timeout Automático

**Descrição:** Instancia PENDING sem ação após prazo é marcada como IGNORED.

**Regra:**

- Instancia PENDING > 48h após scheduled_start
- Automaticamente: NOT_DONE + IGNORED

**Property:**

```python
@property
def is_overdue(self) -> bool:
    if self.status != Status.PENDING:
        return False
    now = datetime.now()
    scheduled = datetime.combine(self.date, self.scheduled_start)
    return now > scheduled
```

**Nota:** Timeout automático está documentado mas ainda não implementado no MVP. Property `is_overdue` apenas verifica atraso.

**Testes:**

- `test_br_habitinstance_004_is_overdue_pending`
- `test_br_habitinstance_004_not_overdue_done`

---

### BR-HABITINSTANCE-005: Edição de Instancia

**Descrição:** Usuário pode editar horário de uma HabitInstance específica.

**Comando:**

```bash
habit adjust INSTANCE_ID --start 08:00 --end 09:30
```

**Comportamento:**

- Novo horário aplicado apenas àquela instância
- Outras instâncias mantêm horário do template
- Não afeta Habit (template)
- Horário planejado preservado em `original_scheduled_*` (BR-HABITINSTANCE-008)

**Testes:**

- `test_br_habitinstance_005_edit_single`
- `test_br_habitinstance_005_preserves_template`

---

### BR-HABITINSTANCE-006: Listagem de Instâncias

**Descrição:** Sistema permite listar instâncias com filtros opcionais.

**Filtros Disponíveis:**

- `habit_id`: Filtra por hábito específico
- `date_start`: Data inicial do período
- `date_end`: Data final do período

**Comportamento:**

- Sem filtros: retorna todas as instâncias
- Com filtros: aplica AND entre filtros fornecidos
- Nenhum resultado: retorna lista vazia (nunca None)
- Ordenação: por data ascendente

**Testes:**

- `test_br_habitinstance_006_list_all`
- `test_br_habitinstance_006_filter_by_habit`
- `test_br_habitinstance_006_filter_by_date_range`
- `test_br_habitinstance_006_returns_empty_list`

---

### BR-HABITINSTANCE-007: Undo com Preservacao de TimeLog (NOVA 15/03/2026)

**Descricao:** O undo reverte HabitInstance para PENDING preservando TimeLogs como registros factuais. Re-done detecta TimeLogs existentes e oferece restauracao.

**Decisao arquitetural:** ADR-038 D1, D2

**Regras:**

1. `u` em habito DONE ou NOT_DONE reverte status para PENDING
2. Undo limpa: `done_substatus`, `not_done_substatus`, `skip_reason`, `skip_note`, `completion_percentage`
3. TimeLogs com status DONE vinculados a instancia permanecem inalterados
4. `v` em habito PENDING que possui TimeLog DONE vinculado abre modal de restauracao
5. Modal de restauracao: "Sessao anterior encontrada (Xmin, Y%). Restaurar? [Sim/Nao]"
6. "Sim" restaura `done_substatus` e `completion_percentage` originais do TimeLog
7. "Nao" abre modal de done manual (BR-TUI-022)

**Testes:**

- `test_br_habitinstance_007_undo_done_to_pending`
- `test_br_habitinstance_007_undo_not_done_to_pending`
- `test_br_habitinstance_007_undo_clears_all_substatus`
- `test_br_habitinstance_007_undo_preserves_timelog`
- `test_br_habitinstance_007_redone_detects_timelog`
- `test_br_habitinstance_007_redone_restores_substatus`

---

### BR-HABITINSTANCE-008: Preservação do Horário Planejado (NOVA 14/08/2026)

**Descrição:** A HabitInstance distingue horário planejado de horário efetivo. O ajuste altera apenas o efetivo, e a divergência entre plano e execução passa a ser consultável em vez de destruída no momento do registro.

**Decisão arquitetural:** ADR-036 (precedente de BR-TASK-008, aplicado a outro agregado sem alterar a decisão)

**Regras:**

1. `scheduled_start` e `scheduled_end` significam horário efetivo
2. `original_scheduled_start` e `original_scheduled_end` guardam o horário planejado
3. `generate_instances` fixa o planejado a partir do template do Habit
4. `adjust_instance_time` captura o valor corrente em `original_*` quando encontra `None`, antes de sobrescrever — o primeiro ajuste é o último instante em que o horário pré-ajuste ainda é conhecido
5. Uma vez preenchido, `original_*` nunca é reescrito
6. `adjustment_count` incrementa apenas quando o horário muda de fato; ajuste para os valores já vigentes não incrementa
7. A migração 005 faz backfill igualando `original_*` ao horário corrente das linhas existentes

**Nulabilidade:** os campos `original_*` são nuláveis no modelo, ao contrário do precedente `Task.original_scheduled_datetime`. O motivo é a existência de cerca de 90 construções diretas de `HabitInstance` na suíte, que campos obrigatórios quebrariam. Como `table=True` desativa a validação do Pydantic, a invariante da regra 5 vive na camada de service.

**Assimetria conhecida:** `adjustment_count` é declarado `int` não-nulável no modelo, mas o `ALTER TABLE ADD COLUMN ... INTEGER DEFAULT 0` deixa a coluna nulável no schema SQLite. O backfill da migração e o default do modelo cobrem os dois caminhos de escrita, de modo que `None` não é alcançável no fluxo real. É a mesma divergência que `Task` carrega desde a migração 002.

**Testes:**

- `test_br_habitinstance_008_adjust_preserves_original`
- `test_br_habitinstance_008_original_is_immutable`
- `test_br_habitinstance_008_count_increments`
- `test_br_habitinstance_008_noop_does_not_increment`
- `test_br_habitinstance_008_generate_populates_original`
