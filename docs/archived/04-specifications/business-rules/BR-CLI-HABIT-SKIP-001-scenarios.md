# BR-CLI-HABIT-SKIP-001: Cenários BDD

- **Referência:** BR-CLI-HABIT-SKIP-001
- **Formato:** Gherkin (DADO/QUANDO/ENTÃO)
- **Total de Cenários:** 8

---

## FUNCIONALIDADE: Comando CLI Habit Skip

Como usuário do TimeBlock

Quero usar `timeblock habit skip` no terminal

Para marcar hábitos como skipped rapidamente

---

## CENÁRIO 1: Skip modo interativo - categoria 1 (HEALTH)

```gherkin
DADO que existe HabitInstance com ID 42 e status PENDING
E não existe timer ativo para essa instance
QUANDO usuário executa "timeblock habit skip 42"
E sistema exibe prompt com 8 categorias
E usuário digita "1" (Saúde)
E sistema pergunta nota opcional
E usuário digita "Gripe"
ENTÃO sistema exibe "✓ Hábito marcado como skipped"
E exibe "Categoria: Saúde"
E exibe "Nota: Gripe"
E instance tem status NOT_DONE
E instance tem skip_reason HEALTH
E instance tem skip_note "Gripe"
E comando retorna exit code 0
```

---

## CENÁRIO 2: Skip modo direto com --category

```gherkin
DADO que existe HabitInstance com ID 42 e status PENDING
QUANDO usuário executa "timeblock habit skip 42 --category WORK --note 'Reunião urgente'"
ENTÃO sistema exibe "✓ Hábito marcado como skipped"
E exibe "Categoria: Trabalho"
E exibe "Nota: Reunião urgente"
E instance tem skip_reason WORK
E comando retorna exit code 0
```

---

## CENÁRIO 3: Skip modo direto sem nota

```gherkin
DADO que existe HabitInstance com ID 42 e status PENDING
QUANDO usuário executa "timeblock habit skip 42 --category FAMILY"
ENTÃO sistema exibe "✓ Hábito marcado como skipped"
E exibe "Categoria: Família"
E skip_note deve ser NULL
E comando retorna exit code 0
```

---

## CENÁRIO 4: Erro - instance_id ausente

```gherkin
QUANDO usuário executa "timeblock habit skip"
ENTÃO sistema exibe "Usage: timeblock habit skip <instance_id>"
E comando retorna exit code 1
```

---

## CENÁRIO 5: Erro - instance não existe

```gherkin
QUANDO usuário executa "timeblock habit skip 999"
ENTÃO sistema exibe "✗ HabitInstance 999 não encontrada"
E comando retorna exit code 2
```

---

## CENÁRIO 6: Erro - timer ativo

```gherkin
DADO que existe HabitInstance com ID 42
E existe timer ativo para essa instance
QUANDO usuário executa "timeblock habit skip 42 --category HEALTH"
ENTÃO sistema exibe "✗ Pare o timer antes de marcar skip"
E comando retorna exit code 1
```

---

## CENÁRIO 7: Erro - categoria inválida

```gherkin
DADO que existe HabitInstance com ID 42
QUANDO usuário executa "timeblock habit skip 42 --category INVALID"
ENTÃO sistema exibe "✗ Categoria inválida"
E exibe lista de categorias válidas
E comando retorna exit code 1
```

---

## CENÁRIO 8: Modo interativo - usuário cancela (Ctrl+C)

```gherkin
DADO que existe HabitInstance com ID 42
QUANDO usuário executa "timeblock habit skip 42"
E sistema exibe prompt
E usuário pressiona Ctrl+C
ENTÃO sistema cancela operação
E nenhuma mudança é feita na instance
E comando retorna exit code 130 (SIGINT)
```

---

## MAPEAMENTO SCENARIOS → TESTES

| Cenário | Teste Unit                       | Teste Integration               |
| ------- | -------------------------------- | ------------------------------- |
| 1       | test_cli_skip_interactive_health | test_habit_skip_cli_e2e         |
| 2       | test_cli_skip_direct_with_note   | test_habit_skip_cli_e2e         |
| 3       | test_cli_skip_direct_no_note     | test_habit_skip_cli_basic       |
| 4       | test_cli_skip_missing_id         | test_habit_skip_cli_errors      |
| 5       | test_cli_skip_not_found          | test_habit_skip_cli_errors      |
| 6       | test_cli_skip_timer_active       | test_habit_skip_cli_errors      |
| 7       | test_cli_skip_invalid_category   | test_habit_skip_cli_errors      |
| 8       | test_cli_skip_user_cancel        | test_habit_skip_cli_interactive |

---

**Criado em:** 19 de novembro de 2025

**Status:** [APROVADO - Pronto para TDD]
