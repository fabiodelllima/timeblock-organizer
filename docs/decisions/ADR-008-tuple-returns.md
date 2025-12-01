# ADR-008: Tuple Returns em Services

- **Status:** Deprecated
- **Data:** 2025-10-20
- **Superseded by:** Return direto ou exceções

## Contextoo

Services retornando tuplas `(success: bool, data, error)` para indicar resultado.

## Decisão (Original)

Pattern: `return (True, result, None)` ou `(False, None, error_msg)`

## Problemaa Identificado

- Força checagem manual de `success`
- Fácil esquecer validação
- Menos pythônico

## Nova Abordagem

**Sucesso:** Return direto
**Erro:** Raise exception

```python
# Antes
success, habit, error = service.create_habit(name)
if not success:
    print(error)
    return

# Depois
try:
    habit = service.create_habit(name)
except ValueError as e:
    print(e)
    return
```

## Consequências

**Positivas:**

- Pythônico (EAFP)
- Impossível esquecer validação
- Stack trace automático

**Negativas:**

- Breaking change em código existente

## Migração

Sprint 1.5: Remover tuplas de TaskService como piloto
