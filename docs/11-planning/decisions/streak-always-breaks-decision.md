# Decisão: Streak Sempre Quebra com NOT_DONE

- **Status:** Decidido
- **Data:** 14 de Novembro de 2025
- **Contexto:** Discussão sobre skip justificado e streak
- **Impacto:** Cálculo de streak, relatórios, motivação do usuário

---

## Problema

Definir regras claras sobre quando um streak é quebrado, especialmente considerando:

1. Skip justificado vs não justificado
2. Partial vs Full completion
3. Ignored (falha passiva) vs Skipped (decisão ativa)

---

## Decisão: NOT_DONE Sempre Quebra Streak

### Regra Fundamental

```python
if instance.status == InstanceStatus.DONE:
    # Qualquer DONE mantém streak (EXCESSIVE, OVERDONE, FULL, PARTIAL)
    maintain_streak()
elif instance.status == InstanceStatus.NOT_DONE:
    # Qualquer NOT_DONE quebra streak (SKIPPED_*, IGNORED)
    break_streak()
```

### Justificativa

**Baseado em "Atomic Habits" (James Clear):**

- Consistência > Perfeição
- "Nunca pule dois dias seguidos"
- Skip consciente ainda é quebra de hábito
- Diferenciamos **impacto psicológico**, não o **fato da quebra**

---

## Detalhamento por Substatus

### DONE (Mantém Streak)

#### EXCESSIVE (> 150% meta)

```bash
Status: DONE (EXCESSIVE)
Streak: MANTÉM ✓
Feedback: [WARN] Desbalanceou rotina, ajustar meta?
```

**Lógica:** Fez o hábito (mantém), mas precisa ajustar planejamento.

#### OVERDONE (110-150% meta)

```bash
Status: DONE (OVERDONE)
Streak: MANTÉM ✓
Feedback: [INFO] Acima do planejado
```

**Lógica:** Fez mais que esperado, ótimo! Mas atenção para não virar EXCESSIVE.

#### FULL (90-110% meta)

```bash
Status: DONE (FULL)
Streak: MANTÉM ✓
Feedback: [OK] Perfeito!
```

**Lógica:** Ideal absoluto.

#### PARTIAL (< 90% meta)

```bash
Status: DONE (PARTIAL)
Streak: MANTÉM ✓
Feedback: Abaixo da meta, mas completo
```

**Lógica:** Fez o hábito (mantém), mesmo que parcialmente. Melhor partial que nada.

---

### NOT_DONE (Quebra Streak)

#### SKIPPED_JUSTIFIED (com reason)

```bash
Status: NOT_DONE (SKIPPED_JUSTIFIED)
Streak: QUEBRA ✗
Feedback: Skip justificado (aceitável)
Impacto psicológico: BAIXO
```

**Lógica:**

- Decisão consciente e justificada
- Sistema entende o motivo
- Mas ainda quebra streak (não executou)
- Usuário não se sente mal (tinha motivo válido)

**Exemplo:**

```terminal
Reason: HEALTH (Consulta médica)
Feedback: "Streak quebrado, mas por motivo de saúde.
           Continue amanhã!"
```

#### SKIPPED_UNJUSTIFIED (sem reason)

```bash
Status: NOT_DONE (SKIPPED_UNJUSTIFIED)
Streak: QUEBRA ✗
Feedback: Skip sem justificativa [WARN]
Impacto psicológico: MÉDIO
```

**Lógica:**

- Decisão consciente mas sem justificativa
- Sistema não entende o motivo
- Quebra streak com alerta
- Usuário tem 24h para justificar

**Exemplo:**

```terminal
Feedback: "Streak quebrado. Quer adicionar justificativa?
           [Y] Sim, justificar agora
           [N] Não"
```

#### IGNORED

```bash
Status: NOT_DONE (IGNORED)
Streak: QUEBRA ✗
Feedback: Hábito ignorado [WARN FORTE]
Impacto psicológico: ALTO
```

**Lógica:**

- Sem ação consciente (esqueceu ou ignorou)
- Sistema marca automaticamente após 48h
- Quebra streak com alerta forte
- Sinal de que hábito não está consolidado

**Exemplo:**

```terminal
Feedback: "Streak quebrado (hábito ignorado).
           3 ignores este mês.
           Considere ajustar horário ou meta?"
```

---

## Cálculo de Streak

### Algoritmo

```python
def calculate_streak(habit_id: int) -> int:
    """Calcula dias consecutivos com DONE."""
    instances = get_instances_chronological(habit_id)
    streak = 0

    for instance in reversed(instances):  # Do mais recente para trás
        if instance.status == InstanceStatus.DONE:
            streak += 1
        elif instance.status == InstanceStatus.NOT_DONE:
            break  # Quebrou streak
        # PENDING não conta nem quebra (ainda não passou)

    return streak
```

### Exemplo Prático

```terminal
Histórico Academia (últimos 10 dias):
14/11 - DONE (FULL)          ✓ Dia 3
13/11 - DONE (PARTIAL)       ✓ Dia 2
12/11 - DONE (OVERDONE)      ✓ Dia 1
11/11 - NOT_DONE (SKIPPED_J) ✗ QUEBROU (justificado: Viagem)
10/11 - DONE (FULL)          ✓ Dia 7 (streak anterior)
09/11 - DONE (FULL)          ✓ Dia 6
08/11 - DONE (EXCESSIVE)     ✓ Dia 5
07/11 - DONE (PARTIAL)       ✓ Dia 4
06/11 - DONE (FULL)          ✓ Dia 3
05/11 - NOT_DONE (IGNORED)   ✗ QUEBROU

Streak atual: 3 dias
Streak anterior: 7 dias (quebrado por skip justificado)
```

---

## CLI Outputs

### Após Timer Stop (DONE)

```bash
$ timer stop

✓ Sessão completa!
  Tempo: 85min (94% da meta)
  Status: DONE (PARTIAL)
  Streak: 14 dias ✓

[INFO] Abaixo da meta, mas streak mantido!
```

### Após Skip Justificado

```bash
$ habit skip Academia --reason WORK

✗ Hábito pulado (justificado: Trabalho)
  Streak quebrado: 14 → 0 dias
  Motivo registrado: Reunião urgente

Continue amanhã para recomeçar streak!
```

### Após Skip Não Justificado

```bash
$ habit skip Academia

✗ Hábito pulado (sem justificativa)
  Streak quebrado: 14 → 0 dias

[WARN] Skip sem justificativa.
       Adicionar motivo? [Y/n]: y

Motivo:
1. Saúde
2. Trabalho
...
Escolha [1-8]: 2

✓ Justificativa adicionada (Trabalho)
```

### Report com Análise de Quebras

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

---

## Impacto Psicológico (UX)

### Diferenciação de Feedback

**SKIPPED_JUSTIFIED:**

```terminal
Mensagem: Neutra/Compreensiva
Tom: "Tudo bem, acontece. Continue amanhã!"
Cor: Amarelo (warning leve)
```

**SKIPPED_UNJUSTIFIED:**

```terminal
Mensagem: Alerta moderado
Tom: "Streak quebrado. Quer justificar?"
Cor: Laranja (warning médio)
```

**IGNORED:**

```terminal
Mensagem: Alerta forte
Tom: "Hábito ignorado. Isso é recorrente?"
Cor: Vermelho (warning alto)
```

---

## Implementação MVP

### Fase 1 (Imediato)

- [x] Regra: DONE mantém, NOT_DONE quebra
- [x] Cálculo de streak simples
- [x] Feedback diferenciado por substatus

### Fase 2 (Pós-MVP)

- [ ] Análise de padrões (quebras recorrentes)
- [ ] Sugestão de ajustes (horário, meta)
- [ ] Celebração de milestones (10, 30, 100 dias)
- [ ] Comparação com média de outros usuários

---

## Business Rules Relacionadas

**A criar:**

- BR-STREAK-001: Calculation Algorithm
- BR-STREAK-002: Break Conditions (NOT_DONE sempre quebra)
- BR-STREAK-003: Maintain Conditions (DONE sempre mantém)
- BR-STREAK-004: Psychological Feedback by Substatus

---

## Referências

- Livro: "Atomic Habits" - James Clear
- Decisão relacionada: `habit-states-final.md`
- Decisão relacionada: `skip-categorization-final.md`

---

**Próxima Revisão:** Após 30 dias de uso real

**Status:** DECIDIDO
