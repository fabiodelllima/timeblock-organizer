# BR-HABIT-SKIP-001: Skip de Habit com Categorização

- **ID:** BR-HABIT-SKIP-001
- **Domínio:** Habit
- **Tipo:** Feature Enhancement
- **Prioridade:** ALTA
- **Versão:** MVP v1.4.0
- **Depende de:** BR-HABIT-INSTANCE-STATUS-001

---

## 1. DESCRIÇÃO

Permitir que usuário marque HabitInstance como skipped (pulado) com:

- Categoria obrigatória (SkipReason: saude, trabalho, familia, etc)
- Nota opcional (texto livre até 500 chars)
- Atualização automática de Status+Substatus

---

## 2. MOTIVAÇÃO

**Problema:**

- Usuário não consegue registrar quando pula um hábito
- Sem rastreamento de razões de skip
- Impossível identificar padrões (ex: sempre skip por trabalho às segundas)

**Benefício:**

- Rastreamento detalhado de skips
- Análise de padrões de interrupção
- Fundação para alertas e insights

---

## 3. REGRAS DE NEGÓCIO

### 3.1 Assinatura do Método

```python
def skip_habit_instance(
    habit_instance_id: int,
    skip_reason: SkipReason,
    skip_note: str | None = None,
    session: Session | None = None
) -> HabitInstance:
    """Marca HabitInstance como skipped com categoria."""
```

### 3.2 Campos Atualizados

Ao executar skip:

1. **status** → `Status.NOT_DONE`
2. **not_done_substatus** → `NotDoneSubstatus.SKIPPED_JUSTIFIED`
3. **skip_reason** → `SkipReason` fornecido pelo usuário
4. **skip_note** → texto opcional (max 500 chars)
5. **done_substatus** → `None`
6. **completion_percentage** → `None`

### 3.3 Categorias de Skip (SkipReason)

```python
class SkipReason(str, Enum):
    HEALTH = "saude"                   # Doença, lesão, indisposição
    WORK = "trabalho"                  # Demanda de trabalho, reunião
    FAMILY = "familia"                 # Compromisso familiar
    TRAVEL = "viagem"                  # Viagem, deslocamento
    WEATHER = "clima"                  # Chuva, clima inadequado
    LACK_RESOURCES = "falta_recursos"  # Falta de material, local
    EMERGENCY = "emergencia"           # Emergência imprevista
    OTHER = "outro"                    # Outro motivo
```

### 3.4 Validações

**PRÉ-CONDIÇÕES:**

- HabitInstance deve existir
- skip_reason deve ser válido (enum)
- skip_note <= 500 caracteres (se fornecida)

**PÓS-CONDIÇÕES:**

- Status = NOT_DONE
- not_done_substatus = SKIPPED_JUSTIFIED
- skip_reason preenchido
- Validação de consistência passa

### 3.5 Restrições

**NÃO permitir skip se:**

- HabitInstance já tem status=DONE (completado)
- Timer ativo (deve parar timer primeiro)

**Permitir skip de:**

- HabitInstance com status=PENDING
- HabitInstance já skipped (re-skip com nova categoria)

---

## 4. CASOS DE USO

### Caso 1: Skip com categoria HEALTH

```
Usuário:
- Acorda doente
- Marca "Ginásio" como skip
- Categoria: SAÚDE
- Nota: "Gripe, febre 38°C"

Sistema:
- status → NOT_DONE
- not_done_substatus → SKIPPED_JUSTIFIED
- skip_reason → HEALTH
- skip_note → "Gripe, febre 38°C"
```

### Caso 2: Skip com categoria WORK

```
Usuário:
- Reunião urgente às 7h
- Marca "Meditação" como skip
- Categoria: TRABALHO
- Nota: "Reunião com cliente"

Sistema:
- status → NOT_DONE
- not_done_substatus → SKIPPED_JUSTIFIED
- skip_reason → WORK
- skip_note → "Reunião com cliente"
```

### Caso 3: Skip sem nota

```
Usuário:
- Marca "Leitura" como skip
- Categoria: FAMILY
- Nota: (vazio)

Sistema:
- status → NOT_DONE
- not_done_substatus → SKIPPED_JUSTIFIED
- skip_reason → FAMILY
- skip_note → None
```

---

## 5. INTERFACE CLI

### 5.1 Comando Básico

```bash
timeblock habit skip <instance_id> --category <categoria>
```

**Exemplos:**

```bash
# Skip por saúde
timeblock habit skip 123 --category saude

# Skip por trabalho com nota
timeblock habit skip 123 --category trabalho --note "Reunião urgente"

# Skip por clima
timeblock habit skip 123 --category clima --note "Chuva forte"
```

### 5.2 Aliases de Categoria

Aceitar português e inglês:

- `saude` ou `health`
- `trabalho` ou `work`
- `familia` ou `family`
- `viagem` ou `travel`
- `clima` ou `weather`
- `falta_recursos` ou `lack_resources`
- `emergencia` ou `emergency`
- `outro` ou `other`

### 5.3 Output CLI

```
✓ Hábito marcado como skipped

Hábito: Ginásio (08:00-09:00)
Razão: Saúde
Nota: Gripe, febre 38°C
Status: NOT_DONE (SKIPPED_JUSTIFIED)
```

---

## 6. VALIDAÇÕES DE ERRO

### 6.1 HabitInstance não existe

```python
if not instance:
    raise ValueError(f"HabitInstance {habit_instance_id} not found")
```

### 6.2 Skip reason inválido

```python
if skip_reason not in SkipReason:
    raise ValueError(f"Invalid skip reason. Valid: {list(SkipReason)}")
```

### 6.3 Nota muito longa

```python
if skip_note and len(skip_note) > 500:
    raise ValueError("Skip note must be <= 500 characters")
```

### 6.4 Timer ativo

```python
active_timer = get_active_timer(habit_instance_id)
if active_timer:
    raise ValueError("Cannot skip with active timer. Stop timer first.")
```

### 6.5 Já completado

```python
if instance.status == Status.DONE:
    raise ValueError("Cannot skip completed instance")
```

---

## 7. INTERAÇÃO COM OUTRAS BRs

### 7.1 Validação de Consistência (BR-HABIT-INSTANCE-STATUS-001)

Após skip, invocar:

```python
instance.validate_status_consistency()
```

Deve passar:

- status = NOT_DONE
- not_done_substatus = SKIPPED_JUSTIFIED
- skip_reason preenchido
- done_substatus = None

### 7.2 Timer Service (BR-TIMER-006)

Skip NÃO afeta timer diretamente, mas:

- Se timer ativo → erro (usuário deve parar timer primeiro)
- Skip pode ser feito em instance sem timer

---

## 8. IMPACTO

### Services Afetados

- **NOVO:** `HabitInstanceService.skip_habit_instance()` (novo método)
- Nenhum service existente modificado

### CLI Afetado

- **NOVO:** `habit skip <id> --category <cat> [--note <text>]`

### Testes

Mínimo 8 cenários:

1. Skip com categoria válida
2. Skip com nota
3. Skip sem nota
4. Re-skip (mudar categoria)
5. Erro: instance não existe
6. Erro: categoria inválida
7. Erro: nota muito longa
8. Erro: timer ativo

---

## 9. ANÁLISE E INSIGHTS FUTUROS

Com skip categorizado, possibilitar:

**Relatórios:**

- "Você skipou 5x por TRABALHO nas últimas 2 semanas"
- "SAÚDE é sua razão #1 de skip (40%)"

**Alertas:**

- "Você skipa LEITURA toda segunda por TRABALHO - considere mudar horário"

**Padrões:**

- Identificar dias/horários problemáticos
- Sugerir ajustes de rotina baseados em skips recorrentes

---

## 10. TESTES

### 10.1 Cenários BDD

Ver: `BR-HABIT-SKIP-001-scenarios.md`

### 10.2 Testes Unitários

**Arquivo:** `tests/unit/test_services/test_habit_instance_skip.py`

Cobertura mínima:

- [ ] test_br_habit_skip_001_skip_with_category
- [ ] test_br_habit_skip_001_skip_with_note
- [ ] test_br_habit_skip_001_skip_without_note
- [ ] test_br_habit_skip_001_reskip_changes_category
- [ ] test_br_habit_skip_001_error_instance_not_found
- [ ] test_br_habit_skip_001_error_invalid_category
- [ ] test_br_habit_skip_001_error_note_too_long
- [ ] test_br_habit_skip_001_error_timer_active

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - PRONTO PARA BDD]
