# BR-HABIT-002: Geração de Instâncias de Hábitos

- **ID:** BR-HABIT-002
- **Domínio:** Habit
- **Status:** [ATIVO]
- **Criado em:** 13 de novembro de 2025

---

## Descrição

O sistema deve gerar instâncias (eventos agendados) de um hábito para um período específico de tempo, respeitando o padrão de recorrência definido no hábito.

---

## Regras

### R1: Período de Geração Obrigatório

1. **Condição:** Ao gerar instâncias de um hábito
2. **Então:** Usuário DEVE especificar período de tempo (início e fim)

### R2: Formatos de Data Aceitos

**O sistema DEVE aceitar múltiplos formatos:**

1. **ISO 8601 (YYYY-MM-DD):**

   - `--from 2025-11-13 --to 2025-11-20`

2. **Shortcuts textuais:**

   - `--from today --to tomorrow`
   - `--from this-week --to next-week`

3. **Offsets relativos:**

   - `--from +0days --to +7days` (hoje até 7 dias)
   - `--from +1week --to +2week` (próximas 2 semanas)

4. **Combinações:**
   - `--from today --to +7days`
   - `--from 2025-11-13 --to +1week`

### R3: Geração Baseada em Recorrência

**Condição:** Hábito tem padrão de recorrência definido
**Então:** Sistema gera apenas instâncias nos dias que correspondem ao padrão

**Exemplos:**

- `EVERYDAY`: Todos os dias do período
- `WEEKDAYS`: Segunda a sexta do período
- `WEEKENDS`: Sábado e domingo do período
- `MONDAY,WEDNESDAY,FRIDAY`: Apenas esses dias da semana

### R4: Validação de Período

**Condição:** Data inicial posterior à data final
**Então:** Sistema rejeita com erro "Data inicial deve ser anterior à data final"

**Condição:** Período muito extenso (> 365 dias)
**Então:** Sistema avisa usuário sobre alto número de instâncias

### R5: Feedback ao Usuário

**Após geração bem-sucedida:**

- Número de instâncias geradas
- Nome do hábito
- Período coberto (data início → data fim)

---

## Exemplos de Uso

### Exemplo 1: Gerar para próxima semana (ISO)

```bash
schedule generate 1 --from 2025-11-13 --to 2025-11-20
# Output: 7 instâncias geradas para "Meditação"
#         Período: 13/11/2025 a 20/11/2025
```

### Exemplo 2: Gerar para hoje usando shortcut

```bash
schedule generate 1 --from today --to today
# Output: 1 instância gerada para "Meditação"
#         Período: 13/11/2025 a 13/11/2025
```

### Exemplo 3: Gerar para próximos 7 dias

```bash
schedule generate 1 --from today --to +7days
# Output: 7 instâncias geradas para "Meditação"
#         Período: 13/11/2025 a 20/11/2025
```

### Exemplo 4: Gerar para esta semana

```bash
schedule generate 1 --from this-week --to this-week
# Output: 7 instâncias geradas para "Meditação"
#         Período: 11/11/2025 (seg) a 17/11/2025 (dom)
```

---

## Validações

### V1: Hábito Existe

- Sistema verifica se `habit_id` existe antes de gerar
- Se não existe: erro "Hábito não encontrado"

### V2: Formato de Data Válido

- Sistema tenta parsear data em ordem:
  1. Shortcuts textuais (`today`, `tomorrow`)
  2. Offsets relativos (`+7days`, `+1week`)
  3. ISO 8601 (`YYYY-MM-DD`)
- Se nenhum formato reconhecido: erro "Formato de data inválido"

### V3: Não Duplicar Instâncias

- Sistema verifica se já existe instância para aquele dia/horário
- Se existe: pula geração (não sobrescreve)

---

## Implementação

### Comando CLI

```bash
schedule generate HABIT_ID --from DATE --to DATE
```

**Parâmetros:**

- `HABIT_ID`: ID do hábito (int, obrigatório)
- `--from DATE`: Data início (string, obrigatório)
- `--to DATE`: Data fim (string, obrigatório)

### Parser de Datas (Prioridade)

```python
def parse_flexible_date(date_str: str) -> date:
    """
    Ordem de tentativa:
    1. parse_date_shortcut() - shortcuts textuais
    2. parse_relative_offset() - +7days, +1week
    3. date.fromisoformat() - YYYY-MM-DD
    """
```

---

## Testes

### Casos de Teste Obrigatórios

1. **test_br_habit_002_generate_with_iso_dates**
   - Gerar com datas ISO explícitas
2. **test_br_habit_002_generate_with_shortcuts**
   - Gerar com `today`, `tomorrow`, `this-week`
3. **test_br_habit_002_generate_with_offsets**
   - Gerar com `+7days`, `+1week`
4. **test_br_habit_002_mixed_formats**
   - Gerar com `--from today --to +7days`
5. **test_br_habit_002_respects_recurrence**
   - WEEKDAYS gera apenas seg-sex
6. **test_br_habit_002_invalid_period_rejected**
   - Data início > data fim deve falhar

---

## Referências

- **Helpers:** `src/timeblock/utils/date_helpers.py`
- **Parser:** `src/timeblock/utils/date_parser.py`
- **Service:** `src/timeblock/services/habit_instance_service.py`
- **ADR-XXX:** Date Parsing Strategy (a criar)

---

**Última atualização:** 2025-11-13
