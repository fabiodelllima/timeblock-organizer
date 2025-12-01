# Business Rules: Streak

- **Domínio:** Streak
- **Área:** Cálculo e Feedback de Consistência
- **Última atualização:** 14 de Novembro de 2025

---

## Índice

- [BR-STREAK-001: Calculation Algorithm](#br-streak-001)
- [BR-STREAK-002: Break Conditions](#br-streak-002)
- [BR-STREAK-003: Maintain Conditions](#br-streak-003)
- [BR-STREAK-004: Psychological Feedback by Substatus](#br-streak-004)

---

## BR-STREAK-001: Calculation Algorithm

**Status:** Definida
**Prioridade:** Alta
**Decisão relacionada:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)

### Descrição

Streak é calculado contando dias consecutivos com `status = DONE`, do mais recente para trás, parando no primeiro `NOT_DONE`.

### Algoritmo

```python
def calculate_streak(habit_id: int) -> int:
    """
    Calcula dias consecutivos com DONE.
    Retorna número de dias do streak atual.
    """
    instances = get_instances_chronological(habit_id)
    streak = 0

    for instance in reversed(instances):  # Do mais recente para trás
        if instance.status == InstanceStatus.DONE:
            streak += 1
        elif instance.status == InstanceStatus.NOT_DONE:
            break  # Primeira quebra encontrada, para contagem
        # PENDING não conta nem quebra (ainda não passou)

    return streak
```

### Regras do Algoritmo

1. **Direção:** Do presente para o passado
2. **Conta:** Apenas instances com `status = DONE`
3. **Para:** No primeiro `status = NOT_DONE`
4. **Ignora:** Instances `PENDING` (ainda não aconteceram)

### Critérios de Aceitação

- [ ] Contagem do mais recente para o mais antigo
- [ ] Inclui qualquer DONE (todos substatus)
- [ ] Para no primeiro NOT_DONE (qualquer substatus)
- [ ] PENDING não afeta contagem (skip temporariamente)
- [ ] Retorna 0 se último instance é NOT_DONE
- [ ] Retorna 0 se não há instances DONE

### Testes Relacionados

- `test_br_streak_001_counts_consecutive_done`
- `test_br_streak_001_stops_at_first_not_done`
- `test_br_streak_001_ignores_pending`
- `test_br_streak_001_zero_if_last_not_done`

### Exemplos

#### Exemplo 1: Streak Ativo (3 dias)

```python
# Histórico Academia (do mais recente para antigo)
instances = [
    HabitInstance(date=date(2025, 11, 14), status=DONE),      # Hoje
    HabitInstance(date=date(2025, 11, 13), status=DONE),      # Ontem
    HabitInstance(date=date(2025, 11, 12), status=DONE),      # Anteontem
    HabitInstance(date=date(2025, 11, 11), status=NOT_DONE),  # QUEBRA
    HabitInstance(date=date(2025, 11, 10), status=DONE),      # Streak anterior
]

streak = calculate_streak(habit_id=42)
# Resultado: 3 dias
```

#### Exemplo 2: Streak Quebrado (0 dias)

```python
# Último instance é NOT_DONE
instances = [
    HabitInstance(date=date(2025, 11, 14), status=NOT_DONE),  # Hoje (quebrou)
    HabitInstance(date=date(2025, 11, 13), status=DONE),      # Ontem
    HabitInstance(date=date(2025, 11, 12), status=DONE),      # Anteontem
]

streak = calculate_streak(habit_id=42)
# Resultado: 0 dias (quebrou hoje)
```

#### Exemplo 3: Com PENDING (ignora)

```python
# PENDING não afeta contagem
instances = [
    HabitInstance(date=date(2025, 11, 16), status=PENDING),   # Futuro (ignora)
    HabitInstance(date=date(2025, 11, 15), status=PENDING),   # Amanhã (ignora)
    HabitInstance(date=date(2025, 11, 14), status=DONE),      # Hoje
    HabitInstance(date=date(2025, 11, 13), status=DONE),      # Ontem
    HabitInstance(date=date(2025, 11, 12), status=NOT_DONE),  # QUEBRA
]

streak = calculate_streak(habit_id=42)
# Resultado: 2 dias (14/11 + 13/11)
# PENDING não conta, mas também não quebra
```

---

## BR-STREAK-002: Break Conditions

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)

### Descrição

Streak SEMPRE quebra quando `status = NOT_DONE`, independente do substatus.

### Regra Fundamental

```python
if instance.status == InstanceStatus.NOT_DONE:
    # SEMPRE quebra streak
    # Não importa o substatus (SKIPPED_JUSTIFIED, UNJUSTIFIED, IGNORED)
    break_streak()
```

### Substatuses que Quebram

Todos os `not_done_substatus` quebram streak:

1. **SKIPPED_JUSTIFIED:** Quebra ✗ (mas impacto psicológico BAIXO)
2. **SKIPPED_UNJUSTIFIED:** Quebra ✗ (impacto psicológico MÉDIO)
3. **IGNORED:** Quebra ✗ (impacto psicológico ALTO)

**Filosofia:** Baseada em "Atomic Habits" (James Clear)

- Consistência > Perfeição
- "Nunca pule dois dias seguidos"
- Skip consciente ainda é quebra de hábito
- Diferenciamos impacto psicológico, não o fato da quebra

### Critérios de Aceitação

- [ ] Qualquer NOT_DONE quebra streak
- [ ] SKIPPED_JUSTIFIED quebra (com feedback compreensivo)
- [ ] SKIPPED_UNJUSTIFIED quebra (com warning moderado)
- [ ] IGNORED quebra (com warning forte)
- [ ] Streak resetado para 0 após quebra

### Testes Relacionados

- `test_br_streak_002_skipped_justified_breaks`
- `test_br_streak_002_skipped_unjustified_breaks`
- `test_br_streak_002_ignored_breaks`
- `test_br_streak_002_all_not_done_reset_to_zero`

### Exemplos

#### Exemplo 1: SKIPPED_JUSTIFIED Quebra

```python
# Antes
streak = 14 dias

# Skip justificado (consulta médica)
instance = HabitInstance(
    date=date(2025, 11, 14),
    status=InstanceStatus.NOT_DONE,
    not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
    skip_reason=SkipReason.HEALTH
)

# Depois
streak = 0 dias  # QUEBROU

# CLI feedback (tom compreensivo)
"""
✗ Academia pulada (justificado: Saúde)
  Streak quebrado: 14 → 0 dias
  Motivo registrado: Consulta médica

Continue amanhã para recomeçar streak!
"""
```

#### Exemplo 2: IGNORED Quebra (warning forte)

```python
# Antes
streak = 7 dias

# Ignorado (48h sem ação)
instance = HabitInstance(
    date=date(2025, 11, 14),
    status=InstanceStatus.NOT_DONE,
    not_done_substatus=NotDoneSubstatus.IGNORED
)

# Depois
streak = 0 dias  # QUEBROU

# CLI feedback (tom de alerta)
"""
[WARN] Academia ignorada (sem ação consciente)
       Streak quebrado: 7 → 0 dias

       3 ignores este mês. Hábito está consolidado?
       Considere ajustar horário ou meta.
"""
```

---

## BR-STREAK-003: Maintain Conditions

- **Status:** Definida
- **Prioridade:** Alta
- **Decisão relacionada:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)

### Descrição

Streak SEMPRE mantém quando `status = DONE`, independente do substatus.

### Regra Fundamental

```python
if instance.status == InstanceStatus.DONE:
    # SEMPRE mantém streak
    # Não importa o substatus (EXCESSIVE, OVERDONE, FULL, PARTIAL)
    maintain_streak()
```

### Substatuses que Mantêm

Todos os `done_substatus` mantêm streak:

1. **EXCESSIVE:** Mantém ✓ MAS alerta sobre impacto na rotina
2. **OVERDONE:** Mantém ✓ MAS monitora recorrência
3. **FULL:** Mantém ✓ [OK] Ideal!
4. **PARTIAL:** Mantém ✓ (warning se recorrente)

**Filosofia:** "Melhor feito que perfeito"

- Qualquer execução conta
- Incentiva ação ao invés de perfeição
- Sistema ajusta comportamento via feedback (não penalizando streak)

### Critérios de Aceitação

- [ ] Qualquer DONE mantém streak
- [ ] EXCESSIVE mantém com warning de impacto
- [ ] OVERDONE mantém com info de monitoramento
- [ ] FULL mantém com feedback positivo
- [ ] PARTIAL mantém sem penalidade

### Testes Relacionados

- `test_br_streak_003_excessive_maintains`
- `test_br_streak_003_overdone_maintains`
- `test_br_streak_003_full_maintains`
- `test_br_streak_003_partial_maintains`

### Exemplos

#### Exemplo 1: PARTIAL Mantém Streak

```python
# Antes
streak = 5 dias

# Timer stop com 60min (67% da meta de 90min)
instance = HabitInstance(
    status=InstanceStatus.DONE,
    done_substatus=DoneSubstatus.PARTIAL,
    actual_duration=60,
    expected_duration=90
)

# Depois
streak = 6 dias  # MANTÉM ✓

# CLI feedback
"""
✓ Sessão completa!
  Tempo: 60min (67% da meta)
  Status: DONE (PARTIAL)
  Streak: 6 dias ✓

[INFO] Abaixo da meta, mas streak mantido!
"""
```

#### Exemplo 2: EXCESSIVE Mantém com Warning

```python
# Antes
streak = 12 dias

# Timer stop com 180min (200% da meta)
instance = HabitInstance(
    status=InstanceStatus.DONE,
    done_substatus=DoneSubstatus.EXCESSIVE,
    actual_duration=180,
    expected_duration=90
)

# Depois
streak = 13 dias  # MANTÉM ✓

# CLI feedback (mantém MAS alerta)
"""
✓ Sessão completa!
  Tempo: 180min (200% da meta)
  Status: DONE (EXCESSIVE)
  Streak: 13 dias ✓

[WARN] Academia ultrapassou meta em 90min

Impacto na rotina:
  - Trabalho: PERDIDO
  - Inglês: ATRASADO 1h

Sugestão: Ajustar meta para 2h?
"""
```

---

## BR-STREAK-004: Psychological Feedback by Substatus

- **Status:** Definida
- **Prioridade:** Média
- **Decisão relacionada:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)

### Descrição

Feedback CLI diferenciado por substatus para minimizar impacto psicológico negativo e incentivar continuidade.

### Matriz de Feedback

| Substatus           | Quebra?  | Tom                | Impacto Psicológico |
| ------------------- | -------- | ------------------ | ------------------- |
| FULL                | ✗ Mantém | Positivo           | Reforço             |
| PARTIAL             | ✗ Mantém | Neutro/Encorajador | Baixo               |
| OVERDONE            | ✗ Mantém | Info/Monitoramento | Baixo               |
| EXCESSIVE           | ✗ Mantém | Warning/Corretivo  | Médio               |
| SKIPPED_JUSTIFIED   | ✓ Quebra | Compreensivo       | Baixo               |
| SKIPPED_UNJUSTIFIED | ✓ Quebra | Moderado           | Médio               |
| IGNORED             | ✓ Quebra | Alerta Forte       | Alto                |

### Templates de Feedback

#### SKIPPED_JUSTIFIED (impacto BAIXO)

```terminal
Mensagem: Neutra/Compreensiva
Tom: "Tudo bem, acontece. Continue amanhã!"
Símbolos: ✗ (não emojis)
```

Exemplo:

```terminal
✗ Hábito pulado (justificado: Saúde)
  Streak quebrado: 14 → 0 dias
  Motivo: Consulta médica

Continue amanhã para recomeçar streak!
```

#### SKIPPED_UNJUSTIFIED (impacto MÉDIO)

```terminal
Mensagem: Alerta moderado
Tom: "Streak quebrado. Quer justificar?"
Símbolos: [WARN]
```

Exemplo:

```terminal
✗ Hábito pulado (sem justificativa)
  Streak quebrado: 14 → 0 dias

[WARN] Skip sem justificativa.
       Adicionar motivo? [Y/n]: _
```

#### IGNORED (impacto ALTO)

```terminal
Mensagem: Alerta forte
Tom: "Hábito ignorado. Isso é recorrente?"
Símbolos: [WARN] em vermelho
```

Exemplo:

```terminal
[WARN] Hábito ignorado (sem ação consciente)
       Streak quebrado: 7 → 0 dias

       3 ignores este mês.
       Considere ajustar horário ou meta?
```

### Critérios de Aceitação

- [ ] Tom diferenciado por substatus
- [ ] SKIPPED_JUSTIFIED usa linguagem compreensiva
- [ ] SKIPPED_UNJUSTIFIED oferece adicionar justificativa
- [ ] IGNORED usa warning forte
- [ ] PARTIAL encoraja continuidade
- [ ] EXCESSIVE alerta sobre impacto

### Testes Relacionados

- `test_br_streak_004_justified_feedback_tone`
- `test_br_streak_004_unjustified_prompt_reason`
- `test_br_streak_004_ignored_strong_warning`
- `test_br_streak_004_partial_encouraging`

### Exemplos

#### Exemplo 1: Report com Análise de Quebras

```bash
$ report habit Academia --period 30

Academia - Últimos 30 dias
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Streak atual: 12 dias
Melhor streak: 18 dias

Quebras este mês: 3x
  ├─ Skipped (justified): 2x  (Trabalho, Saúde)
  ├─ Skipped (unjust.): 0x
  └─ Ignored: 1x              [WARN]

[INFO] Quebras justificadas são normais (67% deste mês)
[WARN] 1 ignore detectado - atenção ao engajamento
```

#### Exemplo 2: Celebração de Milestones

```bash
$ timer stop

✓ Sessão completa!
  Tempo: 90min (100% da meta)
  Status: DONE (FULL)

╔════════════════════════════════════════╗
║  MILESTONE: 30 DIAS CONSECUTIVOS!      ║
╠════════════════════════════════════════╣
║  Parabéns! Hábito consolidado.         ║
║  Continue assim!                       ║
╚════════════════════════════════════════╝
```

---

## Referências

- **Decisão:** [streak-always-breaks-decision.md](../../11-planning/decisions/streak-always-breaks-decision.md)
- **Livro:** "Atomic Habits" - James Clear
- **Service:** `src/timeblock/services/streak_service.py`
- **CLI:** `src/timeblock/commands/report.py`

---

**Última revisão:** 14 de Novembro de 2025

**Status:** Documentação completa, ready para implementação
