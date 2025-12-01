# Protocolo de Tratamento de Erros

## Hierarquia de Exceções

```terminal
TimeBlockError (base)
├── ValidationError
├── ConflictError
├── StateError
└── NotFoundError
```

## Mensagens para Usuário

**Princípios:**

- Claras e acionáveis
- Sem stack traces
- Sugerir soluções

**Exemplo:**

```python
# [X] Ruim
raise Exception("Invalid time")

# [OK] Bom
raise ValidationError(
    "Horário final deve ser após horário inicial.\n"
    "Início: 10:00\n"
    "Fim: 09:00\n"
    "Sugestão: Use -e 11:00 ou posterior"
)
```

## Categorias de Erro

### ValidationError

Dados inválidos fornecidos pelo usuário.

**Quando usar:** Input não passa validação Pydantic.

**Exemplo:** Duração negativa, horário inválido.

### ConflictError

Operação resultaria em conflito de agenda.

**Quando usar:** Detecção de sobreposição temporal.

**Exemplo:** Evento sobrepõe outro existente.

### StateError

Operação inválida para estado atual.

**Quando usar:** Transição de estado ilegal.

**Exemplo:** Tentar pausar timer não iniciado.

### NotFoundError

Entidade referenciada não existe.

**Quando usar:** Query por ID retorna None.

**Exemplo:** Habit ID não encontrado no banco.

## Tratamento na CLI

```python
try:
    service.operation()
except ValidationError as e:
    console.print(f"[red][X] Erro de Validação:[/red] {e}")
    sys.exit(1)
except ConflictError as e:
    console.print(f"[yellow][AVISO] Conflito:[/yellow] {e}")
    # Não exit - conflito pode ser warning
except StateError as e:
    console.print(f"[red][X] Estado Inválido:[/red] {e}")
    sys.exit(1)
except NotFoundError as e:
    console.print(f"[red][X] Não Encontrado:[/red] {e}")
    sys.exit(1)
```

## Logs vs Mensagens Usuário

**Logs (para debug):**

- Stack trace completo
- Contexto técnico detalhado
- Valores variáveis

**Mensagens (para usuário):**

- Descrição problema
- Sugestão solução
- Sem jargão técnico
