# BR-CLI-HABIT-SKIP-001: Comando CLI para Skip de Habit

- **ID:** BR-CLI-HABIT-SKIP-001
- **Domínio:** CLI / Habit
- **Tipo:** Feature
- **Prioridade:** ALTA
- **Versão:** MVP v1.4.0
- **Depende de:** BR-HABIT-SKIP-001

---

## 1. DESCRIÇÃO

Implementar comando CLI `timeblock habit skip <instance_id>` para marcar HabitInstance como skipped com categorização interativa ou via flags.

---

## 2. SINTAXE

```bash
# Modo interativo (prompt categorias)
timeblock habit skip <instance_id>

# Modo direto (com flags)
timeblock habit skip <instance_id> --category <CATEGORY> [--note "texto"]
```

---

## 3. REGRAS DE NEGÓCIO

### RN-CLI-001: Parâmetro instance_id Obrigatório

- `<instance_id>` deve ser inteiro positivo
- Se ausente: erro "Usage: timeblock habit skip <instance_id>"
- Se inválido: erro "Invalid instance_id"

### RN-CLI-002: Modo Interativo (sem flags)

Se `--category` não fornecido:

1. Exibir prompt com 8 categorias:

```
   Por que pulou o hábito?
   [1] Saúde (doença, consulta)
   [2] Trabalho (reunião, deadline)
   [3] Família (evento, emergência)
   [4] Viagem
   [5] Clima (chuva, frio extremo)
   [6] Falta de recursos
   [7] Emergência
   [8] Outro motivo

   Escolha [1-8]: _
```

2. Aguardar input usuário (1-8)
3. Perguntar nota opcional: `Adicionar nota? (Enter para pular): _`
4. Executar skip com categoria + nota

### RN-CLI-003: Modo Direto (com --category)

```bash
timeblock habit skip 42 --category HEALTH --note "Gripe"
```

- Validar categoria existe (HEALTH|WORK|FAMILY|TRAVEL|WEATHER|LACK_RESOURCES|EMERGENCY|OTHER)
- Se categoria inválida: listar opções válidas
- --note opcional

### RN-CLI-004: Feedback Sucesso

```
✓ Hábito marcado como skipped
  Categoria: Saúde
  Nota: Gripe, febre 38°C
```

### RN-CLI-005: Feedback Erro

- Instance não existe: `✗ HabitInstance 42 não encontrada`
- Timer ativo: `✗ Pare o timer antes de marcar skip`
- Já completada: `✗ Não é possível skip de instância completada`
- Nota muito longa: `✗ Nota deve ter no máximo 500 caracteres`

### RN-CLI-006: Exit Codes

- 0: Sucesso
- 1: Erro de validação
- 2: Instance não encontrada

---

## 4. EXEMPLOS

### Exemplo 1: Modo interativo

```bash
$ timeblock habit skip 42
Por que pulou o hábito?
[1] Saúde
...
Escolha [1-8]: 1
Adicionar nota? Gripe
✓ Hábito marcado como skipped
  Categoria: Saúde
  Nota: Gripe
```

### Exemplo 2: Modo direto

```bash
$ timeblock habit skip 42 --category WORK
✓ Hábito marcado como skipped
  Categoria: Trabalho
```

### Exemplo 3: Erro

```bash
$ timeblock habit skip 999
✗ HabitInstance 999 não encontrada
```

---

## 5. INTEGRAÇÃO

- **Service:** `HabitInstanceService.skip_habit_instance()`
- **Validação:** Typer argument validation
- **Output:** Rich console formatting

---

## 6. TESTES

- BDD: `cli/tests/bdd/features/habit_skip_cli.feature`
- Unit: `cli/tests/unit/test_commands/test_habit_skip_cli.py`
- Integration: `cli/tests/integration/commands/test_habit_skip_integration.py`

---

**Criado em:** 19 de novembro de 2025

**Status:** [DRAFT - Aguardando implementação]
