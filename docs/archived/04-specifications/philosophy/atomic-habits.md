# Filosofia: Hábitos Atômicos

**Influência Principal:** James Clear - "Atomic Habits" (2018)

## Conceito Central

TimeBlock é um sistema para construir identidade através de pequenos hábitos consistentes.

> "Você não se eleva ao nível das suas metas. Você cai ao nível dos seus sistemas." — James Clear

## Os Quatro Pilares

### 1. Cue (Gatilho) - Torne Óbvio

**No TimeBlock:**

- `scheduled_start_time` = Implementation Int ention
- Notificações (futuro v2.0)
- Agenda visual mostra próximo hábito

**Princípio:** "Eu vou [COMPORTAMENTO] às [HORÁRIO] em [LOCAL]"

### 2. Craving (Desejo) - Torne Atrativo

**No TimeBlock:**

- Habit Stacking via `Routine`
- Visualização de progresso
- Streaks (sequências ininterruptas)

**Princípio:** Encadear hábito novo com existente

### 3. Response (Resposta) - Torne Fácil

**No TimeBlock:**

- 2-Minute Rule: Hábitos começam pequenos
- Timer integrado para execução imediata
- CLI rápida (< 1 segundo resposta)

**Princípio:** Reduzir fricção ao máximo

### 4. Reward (Recompensa) - Torne Satisfatório

**No TimeBlock:**

- Marcar como completo = dopamina
- `TimeLog` rastreia progresso real
- Relatórios mostram evolução (v1.2)

**Princípio:** Recompensa imediata aumenta repetição

## Implementação no Sistema

### HabitAtom (não HabitInstance)

Nome reflete filosofia: cada ocorrência é "átomo" de mudança.

```python
# Habit = Template do hábito atômico
habit = Habit(
    title="Meditar",
    scheduled_start_time=time(7, 0),
    scheduled_duration_minutes=10  # Começa pequeno (2-Minute Rule)
)

# HabitAtom = Ocorrência atômica específica
atom = HabitAtom(
    habit_id=habit.id,
    date=date.today(),
    status="planned"
)
```

### Routine = Habit Stack

```python
morning_routine = Routine(name="Morning Routine")
# Stack: Acordar → Meditar → Exercitar → Café
```

### Identity-Based System

Não focamos em metas ("perder 10kg"), mas em identidade ("sou pessoa que se exercita diariamente").

TimeBlock rastreia execução consistente = reforça identidade.

## Métricas que Importam

### 1. Consistency > Intensity

Melhor: 15min de leitura todos dias
Pior: 4h de leitura uma vez semana

### 2. Streak Count

Dias consecutivos sem pular = métrica principal

### 3. Completion Rate

% dias executados dos planejados

### 4. Time Variance

Quanto horário real desvia do planejado (analisa padrões)

## Anti-Patterns Evitados

### **Goals Without Systems**

Sistema evita definir meta sem processo diário. TimeBlock força criação de sistema através de agendamento recorrente.

### **All-or-Nothing Thinking**

Sistema evita mentalidade de "tudo ou nada" onde pular hábito por não poder fazer completo leva ao abandono. TimeBlock permite ajustar duração mantendo consistência.

### **Lack of Tracking**

Sistema evita ausência de medição de progresso. TimeBlock garante `TimeLog` automático via timer.

## Pesquisa Científica

### Formação de Hábitos

**Lally et al. (2010)** - European Journal of Social Psychology

**Resultado:** Média 66 dias para automatizar hábito (variação: 18-254 dias)

**Influência no TimeBlock:** Horizonte 8 semanas (56 dias) alinha com ciência. Período suficiente para iniciar automatização sem ser intimidador.

**Link:** <https://doi.org/10.1002/ejsp.674>

### Implementation Intentions

**Gollwitzer (1999)** - American Psychologist

**Resultado:** Especificar quando/onde aumenta 2-3x taxa execução

**Influência no TimeBlock:** Campo `scheduled_start_time` obrigatório força commitment concreto.

**Link:** <https://doi.org/10.1037/0003-066X.54.7.493>

### Habit Stacking

**Fogg (2020)** - Stanford Behavior Lab

**Resultado:** Encadear comportamento novo com existente aumenta aderência

**Influência no TimeBlock:** `Routine` agrupa hábitos sequenciais reforçando stack.

**Link:** <https://tinyhabits.com>

## Referências

### Livros

CLEAR, J. **Atomic Habits**: an easy & proven way to build good habits & break bad ones. New York: Avery, 2018. ISBN 978-0735211292. Disponível em: <https://jamesclear.com/atomic-habits>. Acesso em: 31 out. 2025.

DUHIGG, C. **The Power of Habit**: why we do what we do in life and business. New York: Random House, 2012. ISBN 978-0812981605.

FOGG, B. J. **Tiny Habits**: the small changes that change everything. Boston: Houghton Mifflin Harcourt, 2020. ISBN 978-0358003328. Disponível em: <https://tinyhabits.com/book/>. Acesso em: 31 out. 2025.

### Artigos

GOLLWITZER, P. M. Implementation intentions: strong effects of simple plans. **American Psychologist**, v. 54, n. 7, p. 493-503, 1999. DOI: 10.1037/0003-066X.54.7.493. Disponível em: <https://doi.org/10.1037/0003-066X.54.7.493>. Acesso em: 31 out. 2025.

LALLY, P. et al. How are habits formed: modelling habit formation in the real world. **European Journal of Social Psychology**, v. 40, n. 6, p. 998-1009, 2010. DOI: 10.1002/ejsp.674. Disponível em: <https://doi.org/10.1002/ejsp.674>. Acesso em: 31 out. 2025.

WOOD, W.; NEAL, D. T. A new look at habits and the habit-goal interface. **Psychological Review**, v. 114, n. 4, p. 843-863, 2007. DOI: 10.1037/0033-295X.114.4.843. Disponível em: <https://doi.org/10.1037/0033-295X.114.4.843>. Acesso em: 31 out. 2025.

### Outros Recursos

- James Clear Blog: <https://jamesclear.com/articles>
- 3-2-1 Newsletter (James Clear): <https://jamesclear.com/3-2-1>
- Stanford Behavior Lab: <https://tinyhabits.com>
