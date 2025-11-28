# BR-HABIT-002: Geração de Instâncias de Hábitos

- **ID:** BR-HABIT-002
- **Domínio:** Habit
- **Status:** [ATIVO]
- **Criado em:** 13 de novembro de 2025
- **Atualizado em:** 27 de novembro de 2025

---

## Descrição

O sistema deve gerar instâncias (eventos agendados) de um hábito para um período específico de tempo, respeitando o padrão de recorrência definido no hábito.

---

## Regras

### R1: Geração Integrada na Criação

1. **Condição:** Ao criar um hábito com flag `--generate N`
2. **Então:** Sistema gera automaticamente instâncias para os próximos N meses

### R2: Período de Geração

**O sistema calcula o período automaticamente:**

- Data início: hoje (`date.today()`)
- Data fim: hoje + N meses (usando `relativedelta`)

**Exemplo:** `--generate 1` gera instâncias para os próximos 30-31 dias.

### R3: Geração Baseada em Recorrência

**Condição:** Hábito tem padrão de recorrência definido
**Então:** Sistema gera apenas instâncias nos dias que correspondem ao padrão

**Exemplos:**

- `EVERYDAY`: Todos os dias do período
- `WEEKDAYS`: Segunda a sexta do período
- `WEEKENDS`: Sábado e domingo do período
- `MONDAY,WEDNESDAY,FRIDAY`: Apenas esses dias da semana

### R4: Feedback ao Usuário

**Após geração bem-sucedida:**

- Número de instâncias geradas
- Nome do hábito
- Confirmação visual com Rich

---

## Exemplos de Uso

### Exemplo 1: Criar hábito e gerar instâncias para 1 mês

```bash
habit create --title "Meditação" --start 06:00 --end 06:30 --repeat EVERYDAY --generate 1
# Output: Hábito criado: "Meditação" (ID: 1)
#         ✓ 31 instâncias geradas
```

### Exemplo 2: Criar hábito para dias úteis com geração

```bash
habit create --title "Standup" --start 09:00 --end 09:15 --repeat WEEKDAYS --generate 2
# Output: Hábito criado: "Standup" (ID: 2)
#         ✓ 44 instâncias geradas
```

### Exemplo 3: Criar hábito sem geração automática

```bash
habit create --title "Review Semanal" --start 17:00 --end 18:00 --repeat FRIDAY
# Output: Hábito criado: "Review Semanal" (ID: 3)
#         (sem instâncias geradas - use habit renew para gerar depois)
```

### Exemplo 4: Gerar instâncias para hábito existente

```bash
schedule generate 1 --from 2025-12-01 --to 2025-12-31
# Output: 31 instâncias geradas para "Meditação"
#         Período: 01/12/2025 a 31/12/2025
```

> **Nota:** O comando `schedule generate` está **depreciado** e será removido na v2.0.0.
> Prefira usar `--generate N` durante a criação do hábito.

---

## Validações

### V1: Hábito Existe (para schedule generate)

- Sistema verifica se `habit_id` existe antes de gerar
- Se não existe: erro "Hábito não encontrado"

### V2: Valor de --generate Válido

- Deve ser inteiro positivo (1-12 meses recomendado)
- Sistema avisa se período muito extenso (> 12 meses)

### V3: Não Duplicar Instâncias

- Sistema verifica se já existe instância para aquele dia/horário
- Se existe: pula geração (não sobrescreve)

---

## Implementação

### API Principal (Recomendada)

```bash
habit create --title TITLE --start TIME --end TIME --repeat PATTERN --generate N
```

**Parâmetros:**

- `--title`: Nome do hábito (string, obrigatório)
- `--start`: Horário início (string, obrigatório)
- `--end`: Horário fim (string, obrigatório)
- `--repeat`: Padrão de recorrência (string, obrigatório)
- `--generate N`: Gerar instâncias para N meses (int, opcional)

### API Legada (Depreciada)

```bash
schedule generate HABIT_ID --from DATE --to DATE
```

> **Depreciado:** Será removido na v2.0.0. Ver `docs/10-meta/deprecation-notices.md`.

---

## Testes

### Casos de Teste Obrigatórios

1. **test_br_habit_002_generate_on_create**
   - Criar hábito com `--generate 1` gera instâncias
2. **test_br_habit_002_generate_respects_recurrence**
   - WEEKDAYS gera apenas seg-sex
3. **test_br_habit_002_generate_counts_instances**
   - Feedback mostra número correto de instâncias
4. **test_br_habit_002_no_duplicate_instances**
   - Geração não duplica instâncias existentes
5. **test_br_habit_002_create_without_generate**
   - Criar sem `--generate` não gera instâncias

---

## Referências

- **Service:** `src/timeblock/services/habit_instance_service.py`
- **Command:** `src/timeblock/commands/habit.py` (linhas 32, 98-107)
- **Depreciação:** `docs/10-meta/deprecation-notices.md`

---

**Última atualização:** 27-11-2025
