# ADR-005: Resource-first CLI

- **Status:** Accepted
- **Data:** 2025-09-22

## Contextoo

Definir ordem dos comandos CLI: `<resource> <action>` vs `<action> <resource>`.

Requisitos:

- Descoberta intuitiva
- Agrupamento lógico
- Autocompleção eficaz

## Decisão

Formato: `timeblock <resource> <action> [args]`

Exemplos:

- `timeblock habit add "Meditar"`
- `timeblock habit list`
- `timeblock task complete 42`

## Alternativas

### Action-first (tradicional)

**Prós:** Padrão comum (git, docker)
**Contras:** Comandos dispersos, dificulta descoberta

### Flat (sem agrupamento)

**Prós:** Curto
**Contras:** Explosão de comandos, conflitos de nome

## Consequências

### Positivas

- Tab completion por recurso
- Help agrupado: `timeblock habit --help`
- Escalável (novos recursos sem conflito)
- Semântica clara: objeto primeiro, ação depois

### Negativas

- Mais verboso que flat
- Padrão menos comum que git-style

### Neutras

- Typer suporta nativamente via `app.add_typer()`

## Validação

- Usuários novos encontram comandos via tab < 30s
- Zero conflitos de nomes ao adicionar recursos

## Implementação

```python
# main.py
app = typer.Typer()

habit_app = typer.Typer()
task_app = typer.Typer()

app.add_typer(habit_app, name="habit")
app.add_typer(task_app, name="task")

@habit_app.command("add")
def habit_add(name: str): ...
```
