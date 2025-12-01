# ADR-021: Refatoração Status+Substatus para HabitInstance

- **Status:** ACEITO
- **Data:** 2025-11-19
- **Decisores:** TimeBlock Development Team
- **Referência:** BR-HABIT-INSTANCE-STATUS-001

---

## Contexto

O modelo HabitInstance (v1.3.0) usa um único campo `status` (enum) com 5 valores:

- PLANNED
- IN_PROGRESS
- PAUSED
- COMPLETED
- SKIPPED

**Problemas identificados:**

1. **Granularidade insuficiente:** Não distingue completion parcial (50%) vs completa (100%) vs excessive (200%)
2. **Skip sem contexto:** Não rastreia razão do skip (doença, trabalho, clima)
3. **Análise limitada:** Impossível identificar padrões de overdone ou skip recorrente
4. **Streak tracking:** Fundação inadequada para implementação futura de streaks

---

## Decisão

Refatorar para sistema **Status + Substatus**:

### Status Principal (3 valores)

```python
class Status(str, Enum):
    PENDING = "pending"    # Ainda não iniciado
    DONE = "done"          # Completado (qualquer %)
    NOT_DONE = "not_done"  # Não completado
```

### DoneSubstatus (4 valores)

```python
class DoneSubstatus(str, Enum):
    FULL = "full"              # 90-110% da meta
    PARTIAL = "partial"        # <90% da meta
    OVERDONE = "overdone"      # 110-150% da meta
    EXCESSIVE = "excessive"    # >150% da meta
```

### NotDoneSubstatus (3 valores)

```python
class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"        # Com categoria
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"    # Sem categoria
    IGNORED = "ignored"                             # Não marcado
```

### SkipReason (8 categorias)

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

---

## Consequências

### Positivas

1. **Rastreamento detalhado:** Completion percentage persistido permite análise precisa
2. **Skip categorizado:** Histórico de razões permite identificar padrões (ex: sempre skip por trabalho às segundas)
3. **Fundação para features futuras:**
   - Streak tracking com regras personalizadas (ex: PARTIAL conta como streak?)
   - Análise de impacto de overdone na rotina
   - Alertas para skip recorrente por mesma categoria
4. **Validações robustas:** Consistência garantida entre status e substatus

### Negativas

1. **Breaking change:** Requer migração de dados
2. **Complexidade aumentada:** Services precisam lidar com mais campos
3. **Schema maior:** 5 colunas adicionais no banco
4. **Código legado quebrado:** Testes antigos precisam atualização

---

## Alternativas Consideradas

### Alternativa 1: Manter status único, adicionar campos auxiliares

**Prós:** Sem breaking change

**Contras:** Status continua ambíguo, validações fracas

**Rejeitada:** Não resolve problema fundamental

### Alternativa 2: Status único com mais valores (15+ valores)

**Exemplo:** COMPLETED_FULL, COMPLETED_PARTIAL, COMPLETED_OVERDONE, SKIPPED_HEALTH, etc.

**Prós:** Sem substatus separados

**Contras:** Explosão combinatória (3 x 4 x 8 = 96 valores possíveis), impossível manter

**Rejeitada:** Inviável escalar

### Alternativa 3: OVERDUE como status persistido

**Decisão:** OVERDUE é property calculada, não estado persistido

**Razão:** OVERDUE é função de (status=PENDING AND now > scheduled_start), não um estado independente

---

## Migração

### Dados Existentes

Mapeamento automático:

```
PLANNED → PENDING (nenhum substatus)
IN_PROGRESS → PENDING (nenhum substatus)
PAUSED → PENDING (nenhum substatus)
COMPLETED → DONE + FULL (assumido)
SKIPPED → NOT_DONE + SKIPPED_UNJUSTIFIED (assumido)
```

### Rollback

Script `downgrade()` permite reverter:

- Remove novas colunas
- Restaura status antigo
- Perda de dados: substatus, skip_reason, completion_percentage

**Tempo estimado:** 5 minutos

---

## Validação

### Testes

- 14 testes unitários (100% passando)
- 18 cenários BDD documentados
- Cobertura: 84% (habit_instance.py)

### Regras Validadas

1. DONE requer done_substatus
2. NOT_DONE requer not_done_substatus
3. PENDING não pode ter substatus
4. Substatus mutuamente exclusivos
5. SKIPPED_JUSTIFIED requer skip_reason
6. skip_reason só com SKIPPED_JUSTIFIED

---

## Impacto

### Arquivos Afetados

**Models:**

- `habit_instance.py` (refatorado)
- `enums.py` (4 enums novos)
- `__init__.py` (exports atualizados)

**Database:**

- `migration_001_status_substatus.py` (novo)

**Tests:**

- `test_habit_instance_status.py` (novo - 14 testes)
- Testes antigos (quebrados - atualização pendente)

**Services (pendente v1.4.1):**

- `timer_service.py` (calcular substatus)
- `habit_instance_service.py` (skip command)
- Novo: `skip_service.py`

**CLI (pendente v1.4.1):**

- `habit skip` (novo comando)
- `timer stop` (calcular completion)
- `report` (usar novos campos)

---

## Referências

- BR-HABIT-INSTANCE-STATUS-001: Especificação completa
- Commit: afea231
- James Clear - Atomic Habits (filosofia do projeto)

---

## Histórico

- **2025-11-19:** Decisão aceita, implementação completa (modelo + testes)
- **Próximo:** Migração SQL + atualização services (v1.4.1)

---

## Notas

**HabitInstanceStatus mantido temporariamente** para compatibilidade com código legado. Marcado como DEPRECATED. Remover em v2.0.0.
