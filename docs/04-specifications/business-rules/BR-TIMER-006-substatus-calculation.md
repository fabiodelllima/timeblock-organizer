# BR-TIMER-006: Cálculo Automático de Substatus ao Parar Timer

- **ID:** BR-TIMER-006
- **Domínio:** Timer
- **Tipo:** Feature Enhancement
- **Prioridade:** ALTA
- **Versão:** MVP v1.4.0
- **Depende de:** BR-HABIT-INSTANCE-STATUS-001

---

## 1. DESCRIÇÃO

Ao parar um timer de HabitInstance, o sistema deve calcular automaticamente:

- Status: DONE
- Substatus: FULL/PARTIAL/OVERDONE/EXCESSIVE
- Completion percentage: baseado em duração real vs meta

---

## 2. MOTIVAÇÃO

**Problema:**

- Timer stop atualmente apenas registra duração
- Não preenche campos Status+Substatus do BR-HABIT-INSTANCE-STATUS-001
- Usuário não tem feedback automático de completion

**Benefício:**

- Preenchimento automático de substatus
- Feedback imediato de performance
- Fundação para análise de padrões

---

## 3. REGRAS DE NEGÓCIO

### 3.1 Cálculo de Completion Percentage

```python
target_duration = habit_instance.scheduled_end - habit_instance.scheduled_start
actual_duration = stop_time - start_time
completion_percentage = (actual_duration / target_duration) * 100
```

**Exemplo:**

- Meta: 60 minutos (08:00 - 09:00)
- Real: 55 minutos
- Completion: 92%

### 3.2 Mapeamento para Substatus

| Completion % | Substatus |
| ------------ | --------- |
| < 90%        | PARTIAL   |
| 90% - 110%   | FULL      |
| 110% - 150%  | OVERDONE  |
| > 150%       | EXCESSIVE |

**Limites:**

- PARTIAL: 0% - 89%
- FULL: 90% - 110%
- OVERDONE: 111% - 150%
- EXCESSIVE: 151% - ∞

### 3.3 Atualização de Campos

Ao chamar `timer_service.stop_timer()`:

1. Calcular `completion_percentage`
2. Determinar `done_substatus` baseado em completion
3. Setar `status = Status.DONE`
4. Setar `not_done_substatus = None`
5. Persistir alterações

**Validação:**

- Invocar `habit_instance.validate_status_consistency()`
- Garantir consistência Status+Substatus

---

## 4. INTERFACE DO SERVICE

### 4.1 Assinatura do Método

```python
def stop_timer(
    self,
    habit_instance_id: int,
    session: Session | None = None
) -> tuple[TimeLog, HabitInstance]:
    """Para timer e calcula substatus.

    Args:
        habit_instance_id: ID da instância
        session: Sessão opcional (DI)

    Returns:
        tuple[TimeLog, HabitInstance]: TimeLog criado + HabitInstance atualizado

    Raises:
        ValueError: Se timer não estiver ativo
    """
```

### 4.2 Lógica Interna

```python
# 1. Buscar TimeLog ativo
timelog = get_active_timelog(habit_instance_id)

# 2. Parar timer
timelog.end_time = datetime.now()
timelog.duration_seconds = (timelog.end_time - timelog.start_time).total_seconds()

# 3. Buscar HabitInstance
instance = get_habit_instance(habit_instance_id)

# 4. Calcular completion
target_seconds = (
    datetime.combine(instance.date, instance.scheduled_end) -
    datetime.combine(instance.date, instance.scheduled_start)
).total_seconds()

completion_percentage = int((timelog.duration_seconds / target_seconds) * 100)

# 5. Determinar substatus
if completion_percentage < 90:
    done_substatus = DoneSubstatus.PARTIAL
elif completion_percentage <= 110:
    done_substatus = DoneSubstatus.FULL
elif completion_percentage <= 150:
    done_substatus = DoneSubstatus.OVERDONE
else:
    done_substatus = DoneSubstatus.EXCESSIVE

# 6. Atualizar HabitInstance
instance.status = Status.DONE
instance.done_substatus = done_substatus
instance.completion_percentage = completion_percentage
instance.not_done_substatus = None

# 7. Validar consistência
instance.validate_status_consistency()

# 8. Persistir
session.add(timelog)
session.add(instance)
session.commit()

return (timelog, instance)
```

---

## 5. CASOS DE USO

### Caso 1: Timer stop com completion FULL

```
Usuário:
1. Inicia timer para "Ginásio" (meta: 60 min)
2. Treina por 58 minutos
3. Para timer

Sistema:
- Calcula: 58/60 = 97%
- Substatus: FULL (90-110%)
- Status: DONE
- Persiste automaticamente
```

### Caso 2: Timer stop com completion PARTIAL

```
Usuário:
1. Inicia timer para "Estudar" (meta: 120 min)
2. Estuda por 90 minutos (interrupção)
3. Para timer

Sistema:
- Calcula: 90/120 = 75%
- Substatus: PARTIAL (<90%)
- Status: DONE
- Persiste automaticamente
```

### Caso 3: Timer stop com completion EXCESSIVE

```
Usuário:
1. Inicia timer para "Leitura" (meta: 30 min)
2. Lê por 60 minutos (engajado demais)
3. Para timer

Sistema:
- Calcula: 60/30 = 200%
- Substatus: EXCESSIVE (>150%)
- Status: DONE
- Persiste automaticamente
```

---

## 6. VALIDAÇÕES

### 6.1 Pré-condições

- Timer deve estar ativo (`timelog.end_time is None`)
- HabitInstance deve existir
- HabitInstance deve ter scheduled_start/end válidos

### 6.2 Pós-condições

- TimeLog tem end_time preenchido
- HabitInstance tem status=DONE
- HabitInstance tem done_substatus válido
- HabitInstance tem completion_percentage calculado
- Validação de consistência passou

---

## 7. EXCEÇÕES

### TimeLog não encontrado

```python
if not timelog:
    raise ValueError(f"Timer não está ativo para HabitInstance {habit_instance_id}")
```

### HabitInstance não encontrado

```python
if not instance:
    raise ValueError(f"HabitInstance {habit_instance_id} não encontrado")
```

### Duração target inválida

```python
if target_seconds <= 0:
    raise ValueError("Duração target deve ser positiva")
```

---

## 8. IMPACTO

### Services Afetados

- `timer_service.py` (modificado)
- Nenhum service novo necessário

### CLI Afetado

- `timer stop` (modificado - mostrar feedback de substatus)

### Testes

- `test_timer_service.py` (novos testes)
- Mínimo 4 cenários: PARTIAL, FULL, OVERDONE, EXCESSIVE

---

## 9. TESTES

### 9.1 Cenários BDD

Ver: `BR-TIMER-006-scenarios.md`

### 9.2 Testes Unitários

**Arquivo:** `tests/unit/test_services/test_timer_service_substatus.py`

Cobertura mínima:

- [ ] test_br_timer_006_stop_calculates_partial
- [ ] test_br_timer_006_stop_calculates_full
- [ ] test_br_timer_006_stop_calculates_overdone
- [ ] test_br_timer_006_stop_calculates_excessive
- [ ] test_br_timer_006_validates_consistency

---

## 10. DOCUMENTAÇÃO ATUALIZAR

- [ ] CHANGELOG.md (feature)
- [ ] CLI reference (timer stop output)
- [ ] Service documentation

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - PRONTO PARA BDD]
