# Business Rules: Habit Skip

- **Domínio:** HabitInstance
- **Área:** Skip e Justificativas
- **Última atualização:** 14 de Novembro de 2025

---

## Índice

- [BR-HABIT-SKIP-001: Categorização de Skip com Enum](#br-habit-skip-001)
- [BR-HABIT-SKIP-002: Campos de Skip](#br-habit-skip-002)
- [BR-HABIT-SKIP-003: Prazo para Justificar Skip](#br-habit-skip-003)
- [BR-HABIT-SKIP-004: CLI Prompt Interativo](#br-habit-skip-004)

---

## BR-HABIT-SKIP-001: Categorização de Skip com Enum

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [skip-categorization-final.md](../../11-planning/decisions/skip-categorization-final.md)

### Descrição

Skip de habit deve ser categorizado usando enum `SkipReason` com 8 categorias pré-definidas, evitando texto livre que dificulta análise.

### Enum SkipReason

```python
class SkipReason(str, Enum):
    """Categorias de motivo para skip."""
    HEALTH = "health"           # Saúde (doença, consulta)
    WORK = "work"               # Trabalho (reunião, deadline)
    FAMILY = "family"           # Família (evento, emergência)
    TRAVEL = "travel"           # Viagem
    WEATHER = "weather"         # Clima (chuva, frio extremo)
    TIRED = "tired"             # Cansaço/Fadiga
    PERSONAL = "personal"       # Pessoal (outro motivo)
    NO_REASON = "no_reason"     # Sem motivo específico
```

### Critérios de Aceitação

- [ ] Enum `SkipReason` com exatamente 8 valores
- [ ] Valores em lowercase (health, work, etc)
- [ ] Campo obrigatório quando `status = NOT_DONE` e `substatus = SKIPPED_JUSTIFIED`
- [ ] Campo opcional quando `substatus = SKIPPED_UNJUSTIFIED`
- [ ] Campo NULL quando `status != NOT_DONE`

### Testes Relacionados

- `test_br_habit_skip_001_enum_has_8_categories`
- `test_br_habit_skip_001_justified_requires_reason`
- `test_br_habit_skip_001_null_when_not_skipped`

### Exemplos

#### Exemplo 1: Skip Justificado

```python
instance = HabitInstance(
    status=InstanceStatus.NOT_DONE,
    not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
    skip_reason=SkipReason.HEALTH,  # Obrigatório
    skip_note="Consulta médica marcada há 2 meses"
)
```

#### Exemplo 2: Skip Não Justificado

```python
instance = HabitInstance(
    status=InstanceStatus.NOT_DONE,
    not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
    skip_reason=None,  # Opcional (pode adicionar depois)
    skip_note=None
)
```

#### Exemplo 3: DONE (não skipped)

```python
instance = HabitInstance(
    status=InstanceStatus.DONE,
    done_substatus=DoneSubstatus.FULL,
    skip_reason=None,  # DEVE ser NULL
    skip_note=None     # DEVE ser NULL
)
```

---

## BR-HABIT-SKIP-002: Campos de Skip

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [skip-categorization-final.md](../../11-planning/decisions/skip-categorization-final.md)

### Descrição

HabitInstance deve ter dois campos para skip: `skip_reason` (categoria) e `skip_note` (opcional, texto livre curto).

### Modelo de Dados

```python
class HabitInstance(SQLModel, table=True):
    # ... campos existentes

    # Skip fields
    skip_reason: SkipReason | None = Field(default=None)
    skip_note: str | None = Field(default=None, max_length=200)
```

### Critérios de Aceitação

- [ ] Campo `skip_reason` aceita `SkipReason | None`
- [ ] Campo `skip_note` aceita `str | None`
- [ ] `skip_note` limitado a 200 caracteres
- [ ] Ambos NULL quando instance não é skipped
- [ ] `skip_reason` obrigatório para SKIPPED_JUSTIFIED
- [ ] `skip_note` sempre opcional

### Validações

```python
def validate_skip_fields(instance: HabitInstance) -> None:
    """Valida campos de skip."""

    # Se skipped justified, reason é obrigatória
    if (instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        and instance.skip_reason is None):
        raise ValueError("skip_reason obrigatório para SKIPPED_JUSTIFIED")

    # Se não skipped, campos devem ser NULL
    if instance.status != InstanceStatus.NOT_DONE:
        if instance.skip_reason is not None or instance.skip_note is not None:
            raise ValueError("skip_reason/skip_note devem ser NULL quando não skipped")

    # skip_note limitado a 200 chars
    if instance.skip_note and len(instance.skip_note) > 200:
        raise ValueError("skip_note deve ter no máximo 200 caracteres")
```

### Testes Relacionados

- `test_br_habit_skip_002_skip_note_max_length`
- `test_br_habit_skip_002_reason_required_for_justified`
- `test_br_habit_skip_002_null_when_not_skipped`

### Exemplos

#### Exemplo 1: Skip com Nota Detalhada

```python
instance = HabitInstance(
    status=InstanceStatus.NOT_DONE,
    not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
    skip_reason=SkipReason.WORK,
    skip_note="Reunião urgente com cliente marcada pela manhã"  # 52 chars
)
```

#### Exemplo 2: Skip sem Nota

```python
instance = HabitInstance(
    status=InstanceStatus.NOT_DONE,
    not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
    skip_reason=SkipReason.HEALTH,
    skip_note=None  # Opcional, não precisa explicar
)
```

#### Exemplo 3: Validação de Tamanho

```python
# ✗ Falha: skip_note > 200 chars
instance = HabitInstance(
    skip_note="A" * 201  # ValueError
)

# ✓ OK: exatamente 200 chars
instance = HabitInstance(
    skip_note="A" * 200  # OK
)
```

---

## BR-HABIT-SKIP-003: Prazo para Justificar Skip

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [skip-categorization-final.md](../../11-planning/decisions/skip-categorization-final.md)

### Descrição

Usuário tem 24 horas após skip para adicionar justificativa. Após prazo, skip permanece como SKIPPED_UNJUSTIFIED.

### Regra Temporal

```python
# Quando usuário faz skip sem reason
created_at = datetime.now()  # 14/11/2025 08:00

# Prazo para justificar
deadline = created_at + timedelta(hours=24)  # 15/11/2025 08:00

# Se usuário adicionar reason antes do deadline
if datetime.now() < deadline:
    # Permitir mudança: UNJUSTIFIED → JUSTIFIED
    substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
else:
    # Deadline expirado, permanece UNJUSTIFIED
    raise ValueError("Prazo de 24h expirado")
```

### Critérios de Aceitação

- [ ] Prazo de 24h após criação do skip
- [ ] Permitir mudança UNJUSTIFIED → JUSTIFIED dentro do prazo
- [ ] Bloquear mudança após prazo expirado
- [ ] CLI avisa prazo ao fazer skip sem justificativa
- [ ] Reports mostram skips com prazo expirado

### Testes Relacionados

- `test_br_habit_skip_003_can_justify_within_24h`
- `test_br_habit_skip_003_cannot_justify_after_24h`
- `test_br_habit_skip_003_deadline_calculation`

### Exemplos

#### Exemplo 1: Justificar Dentro do Prazo

```python
# Skip sem justificativa (08:00)
instance = skip_habit(habit_id=42)
# status: NOT_DONE
# substatus: SKIPPED_UNJUSTIFIED
# skip_reason: None
# created_at: 14/11/2025 08:00

# 10 horas depois (18:00), usuário adiciona justificativa
add_skip_justification(
    instance_id=instance.id,
    reason=SkipReason.WORK,
    note="Reunião urgente"
)
# ✓ OK: dentro das 24h
# substatus: SKIPPED_JUSTIFIED
```

#### Exemplo 2: Prazo Expirado

```python
# Skip sem justificativa (08:00 dia 14)
instance = skip_habit(habit_id=42)
# created_at: 14/11/2025 08:00

# 25 horas depois (09:00 dia 15)
add_skip_justification(
    instance_id=instance.id,
    reason=SkipReason.WORK
)
# ✗ ValueError: "Prazo de 24h expirado"
# substatus: permanece SKIPPED_UNJUSTIFIED
```

#### Exemplo 3: CLI Warning

```bash
$ habit skip Academia

[WARN] Skip sem justificativa
       Você tem 24h para adicionar motivo:

       habit skip Academia --add-reason

       Sem justificativa, contará como skip não justificado.

Confirmar skip? [y/N]: y

✓ Academia pulada (sem justificativa)
  Prazo para justificar: até 15/11/2025 08:00
```

---

## BR-HABIT-SKIP-004: CLI Prompt Interativo

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [skip-categorization-final.md](../../11-planning/decisions/skip-categorization-final.md)

### Descrição

Comando `habit skip` deve ter prompt interativo para selecionar categoria e opcionalmente adicionar nota.

### Fluxo CLI

```bash
# Comando básico
$ habit skip Academia

Motivo do skip:
[1] Saúde (consulta, doença)
[2] Trabalho (reunião, deadline)
[3] Família (evento, emergência)
[4] Viagem
[5] Clima (chuva, frio extremo)
[6] Cansaço/Fadiga
[7] Pessoal (outro motivo)
[8] Sem motivo específico
[9] Pular agora, justificar depois

Escolha [1-9]: 2

Adicionar nota? (opcional, max 200 chars)
[Enter para pular]: Reunião urgente marcada pela manhã

✓ Academia pulada
  Motivo: Trabalho
  Nota: Reunião urgente marcada pela manhã
  Streak quebrado: 14 → 0 dias
```

### Critérios de Aceitação

- [ ] Prompt com 9 opções (8 categorias + "justificar depois")
- [ ] Opção 9 cria SKIPPED_UNJUSTIFIED
- [ ] Opções 1-8 criam SKIPPED_JUSTIFIED
- [ ] Prompt para nota opcional após escolher categoria
- [ ] Validar tamanho da nota (max 200 chars)
- [ ] Flag `--reason` permite pular prompt

### Flags do Comando

```bash
# Com reason predefinida
habit skip Academia --reason WORK

# Com reason e nota
habit skip Academia --reason HEALTH --note "Consulta médica"

# Sem prompt (justificar depois)
habit skip Academia --no-reason
```

### Testes Relacionados

- `test_br_habit_skip_004_interactive_prompt`
- `test_br_habit_skip_004_reason_flag`
- `test_br_habit_skip_004_note_validation`

### Exemplos

#### Exemplo 1: Prompt Interativo Completo

```bash
$ habit skip Meditação

Motivo do skip:
[1] Saúde
[2] Trabalho
[3] Família
[4] Viagem
[5] Clima
[6] Cansaço
[7] Pessoal
[8] Sem motivo
[9] Justificar depois

Escolha [1-9]: 6

Adicionar nota? (opcional)
[Enter para pular]: Dormi tarde ontem

✓ Meditação pulada (justificado)
  Motivo: Cansaço
  Nota: Dormi tarde ontem
  Streak quebrado: 7 → 0 dias
```

#### Exemplo 2: Skip Rápido com Flag

```bash
$ habit skip Academia --reason WEATHER --note "Chuva forte"

✓ Academia pulada (justificado)
  Motivo: Clima
  Nota: Chuva forte
  Streak quebrado: 12 → 0 dias
```

#### Exemplo 3: Skip sem Justificativa

```bash
$ habit skip Leitura --no-reason

[WARN] Skip sem justificativa
       Prazo para justificar: 24h

✓ Leitura pulada (não justificado)
  Streak quebrado: 5 → 0 dias

Para justificar depois:
  habit skip Leitura --add-reason
```

---

## Referências

- **Decisão:** [skip-categorization-final.md](../../11-planning/decisions/skip-categorization-final.md)
- **Modelo:** `src/timeblock/models/habit_instance.py`
- **Service:** `src/timeblock/services/habit_instance_service.py`
- **CLI:** `src/timeblock/commands/habit.py`

---

**Última revisão:** 14 de Novembro de 2025

**Status:** Documentação completa, ready para implementação
