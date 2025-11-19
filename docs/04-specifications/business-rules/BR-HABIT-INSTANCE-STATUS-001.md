# BR-HABIT-INSTANCE-STATUS-001: Refatoração Status + Substatus

- **ID:** BR-HABIT-INSTANCE-STATUS-001
- **Domínio:** HabitInstance
- **Tipo:** Breaking Change
- **Prioridade:** CRÍTICA
- **Versão:** MVP v1.4.0

---

## 1. DESCRIÇÃO

Refatorar modelo HabitInstance de status único (string) para sistema Status + Substatus (enums), permitindo rastreamento detalhado de completion e skip.

---

## 2. MOTIVAÇÃO

**Problema atual:**

- Status é string livre (`status: str = "planned"`)
- Não há distinção entre DONE com 50% vs 150% completion
- Não há diferenciação entre skip justificado vs injustificado
- Sistema não rastreia razões de skip
- Dificulta análise de padrões comportamentais

**Benefícios da refatoração:**

- Rastreamento preciso de completion (FULL/PARTIAL/OVERDONE/EXCESSIVE)
- Distinção clara entre skip categorias (JUSTIFIED/UNJUSTIFIED/IGNORED)
- Histórico rastreável de motivos de skip
- Análise de impacto de overdone em rotina
- Fundação para Streak tracking

---

## 3. REGRAS DE NEGÓCIO

### 3.1 Status Principal (3 valores)

```python
class Status(str, Enum):
    PENDING = "pending"    # Ainda não iniciado
    DONE = "done"          # Completado (qualquer %)
    NOT_DONE = "not_done"  # Não completado
```

**Transição de estados:**

```
PENDING -> DONE (timer stop com completion > 0%)
PENDING -> NOT_DONE (skip ou dia termina sem execução)
DONE -> imutável (não volta para PENDING)
NOT_DONE -> imutável (não volta para PENDING)
```

### 3.2 DoneSubstatus (4 valores)

Aplica-se apenas quando `status = DONE`.

```python
class DoneSubstatus(str, Enum):
    FULL = "full"              # 90-110% da meta
    PARTIAL = "partial"        # <90% da meta
    OVERDONE = "overdone"      # 110-150% da meta
    EXCESSIVE = "excessive"    # >150% da meta
```

**Cálculo:**

```python
completion_percentage = (actual_duration / target_duration) * 100

if completion >= 90 and completion <= 110:
    substatus = FULL
elif completion < 90:
    substatus = PARTIAL
elif completion > 110 and completion <= 150:
    substatus = OVERDONE
else:  # >150%
    substatus = EXCESSIVE
```

**Validação:**

- `done_substatus` deve ser `None` se `status != DONE`
- `done_substatus` deve ser preenchido se `status == DONE`

### 3.3 NotDoneSubstatus (3 valores)

Aplica-se apenas quando `status = NOT_DONE`.

```python
class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"        # Skip com categoria
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"    # Skip sem categoria (após 24h)
    IGNORED = "ignored"                             # Não marcado, dia terminou
```

**Regras:**

- `SKIPPED_JUSTIFIED`: Requer `skip_reason` preenchido
- `SKIPPED_UNJUSTIFIED`: `skip_reason = None` e skip explícito
- `IGNORED`: Nunca teve interação do usuário

**Validação:**

- `not_done_substatus` deve ser `None` se `status != NOT_DONE`
- `not_done_substatus` deve ser preenchido se `status == NOT_DONE`

### 3.4 SkipReason (8 categorias)

Aplica-se apenas quando `not_done_substatus = SKIPPED_JUSTIFIED`.

```python
class SkipReason(str, Enum):
    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    TRAVEL = "viagem"
    WEATHER = "clima"
    LACK_RESOURCES = "falta_recursos"
    EMERGENCY = "emergencia"
    OTHER = "outro"
```

**Regras:**

- Obrigatório quando usuário executa `habit skip`
- Opcional campo adicional `skip_note` (texto livre)
- Categorias são mutuamente exclusivas

---

## 4. MODELO DE DADOS

### 4.1 Campos NOVOS

```python
class HabitInstance(SQLModel, table=True):
    # Campos existentes mantidos
    id: int | None
    habit_id: int
    date: date
    scheduled_start: time
    scheduled_end: time
    actual_start: datetime | None
    actual_end: datetime | None
    manually_adjusted: bool

    # NOVOS campos (Status+Substatus)
    status: Status = Field(default=Status.PENDING)
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None
    skip_reason: SkipReason | None = None
    skip_note: str | None = None
    completion_percentage: int | None = None  # Calculado, persistido
```

### 4.2 Migração de Dados

**Mapeamento de status antigo -> novo:**

```sql
-- Status atual (string) -> Status novo (enum)
UPDATE habit_instances SET
    status = CASE
        WHEN status = 'planned' THEN 'pending'
        WHEN status = 'in_progress' THEN 'pending'
        WHEN status = 'completed' THEN 'done'
        WHEN status = 'skipped' THEN 'not_done'
        ELSE 'pending'
    END;

-- Preencher substatus para eventos DONE (assumir FULL se não tiver info)
UPDATE habit_instances SET
    done_substatus = 'full'
WHERE status = 'done' AND done_substatus IS NULL;

-- Preencher substatus para eventos NOT_DONE (assumir UNJUSTIFIED)
UPDATE habit_instances SET
    not_done_substatus = 'skipped_unjustified'
WHERE status = 'not_done' AND not_done_substatus IS NULL;
```

---

## 5. VALIDAÇÕES

### 5.1 Validações de Integridade

**Regra 1:** Status e substatus devem ser consistentes

```python
# INVÁLIDO
status = DONE, not_done_substatus = SKIPPED_JUSTIFIED  # [X]

# VÁLIDO
status = DONE, done_substatus = FULL  # [OK]
status = NOT_DONE, not_done_substatus = SKIPPED_JUSTIFIED  # [OK]
```

**Regra 2:** Skip reason só com substatus correto

```python
# INVÁLIDO
not_done_substatus = IGNORED, skip_reason = HEALTH  # [X]

# VÁLIDO
not_done_substatus = SKIPPED_JUSTIFIED, skip_reason = HEALTH  # [OK]
```

**Regra 3:** Substatus mutuamente exclusivos

```python
# INVÁLIDO
done_substatus = FULL, not_done_substatus = IGNORED  # [X]

# VÁLIDO
done_substatus = FULL, not_done_substatus = None  # [OK]
```

### 5.2 Método de Validação

```python
def validate_status_consistency(self) -> None:
    """Valida consistência entre status e substatus."""
    if self.status == Status.DONE:
        if self.done_substatus is None:
            raise ValueError("done_substatus obrigatório quando status=DONE")
        if self.not_done_substatus is not None:
            raise ValueError("not_done_substatus deve ser None quando status=DONE")

    elif self.status == Status.NOT_DONE:
        if self.not_done_substatus is None:
            raise ValueError("not_done_substatus obrigatório quando status=NOT_DONE")
        if self.done_substatus is not None:
            raise ValueError("done_substatus deve ser None quando status=NOT_DONE")

    elif self.status == Status.PENDING:
        if self.done_substatus is not None or self.not_done_substatus is not None:
            raise ValueError("Substatus deve ser None quando status=PENDING")

    # Validar skip_reason
    if self.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED:
        if self.skip_reason is None:
            raise ValueError("skip_reason obrigatório para SKIPPED_JUSTIFIED")
    else:
        if self.skip_reason is not None:
            raise ValueError("skip_reason só permitido com SKIPPED_JUSTIFIED")
```

---

## 6. IMPACTO

### 6.1 Breaking Changes

**Modelos afetados:**

- `HabitInstance` (mudança de schema)

**Services afetados:**

- `HabitInstanceService` (lógica de status)
- `TimerService` (cálculo de completion)
- `SkipService` (novo - a criar)

**CLI afetados:**

- `habit skip` (novo comando)
- `timer stop` (calcular substatus)
- `report` (usar novos campos)

### 6.2 Compatibilidade

**[X] NÃO compatível com v1.3.0**

- Requer migração de banco
- Requer atualização de todos services
- Requer atualização de CLI commands

**Migração obrigatória:**

- Script SQL de migração
- Testes de migração
- Rollback plan documentado

---

## 7. TESTES

### 7.1 Cenários de Teste (BDD)

Ver arquivo: `docs/04-specifications/business-rules/BR-HABIT-INSTANCE-STATUS-001-scenarios.md`

### 7.2 Testes Unitários

**Arquivo:** `tests/unit/test_models/test_habit_instance_status.py`

Cobertura mínima:

- [ ] Transições de status válidas
- [ ] Validação substatus obrigatório
- [ ] Validação skip_reason com JUSTIFIED
- [ ] Validação substatus mutuamente exclusivos
- [ ] Cálculo de completion_percentage
- [ ] Property `is_overdue` (se PENDING)

### 7.3 Testes de Integração

**Arquivo:** `tests/integration/test_habit_instance_status_integration.py`

Cobertura mínima:

- [ ] Timer stop define status=DONE + substatus correto
- [ ] Skip define status=NOT_DONE + substatus JUSTIFIED
- [ ] Migração de dados de v1.3.0 funciona
- [ ] Queries com novos campos funcionam

---

## 8. DOCUMENTAÇÃO ATUALIZAR

- [ ] `CHANGELOG.md` (breaking change)
- [ ] `docs/01-architecture/ARCHITECTURE.md` (modelo atualizado)
- [ ] `docs/08-user-guides/cli-reference.md` (comandos novos)
- [ ] ADR-021: Status+Substatus Refactoring

---

## 9. ROLLBACK PLAN

Em caso de problemas críticos após deploy:

1. **Parar aplicação**
2. **Restaurar backup do banco** (pré-migração)
3. **Reverter para branch `v1.3.0`**
4. **Reiniciar aplicação**

**Tempo estimado de rollback:** 5 minutos

---

## 10. CHECKLIST DE IMPLEMENTAÇÃO

**Docs:**

- [ ] BR-HABIT-INSTANCE-STATUS-001.md (este arquivo)
- [ ] BDD scenarios (próximo arquivo)

**Testes:**

- [ ] Testes unitários (RED)
- [ ] Testes integração (RED)
- [ ] Testes E2E (RED)

**Código:**

- [ ] Enums (Status, DoneSubstatus, NotDoneSubstatus, SkipReason)
- [ ] HabitInstance model refatorado
- [ ] Migração SQL
- [ ] Services atualizados
- [ ] CLI commands atualizados

**Validação:**

- [ ] Todos testes passando (GREEN)
- [ ] Cobertura 99%+
- [ ] Migração testada com dados reais

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - PRONTO PARA BDD]
