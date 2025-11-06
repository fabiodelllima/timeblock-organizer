# ADR-008: Estratégia de Ambientes (dev/test/prod)

**Status:** ACEITO

**Data:** 03 de Novembro de 2025

**Contexto:** v1.2.0 - Infraestrutura

## Contexão

Projeto visa ser showcase profissional. Necessidade de formalizar ambientes.

## Decisão

**Implementar 3 ambientes em v1.3.0:**

### 1. DEVELOPMENT (dev)

```python
ENV = 'dev'
DATABASE = 'data/dev/timeblock.db'
LOG_LEVEL = DEBUG
LOG_TO_CONSOLE = True
FEATURES = ['experimental', 'debug_mode']
```

### 2. TEST (test)

```python
ENV = 'test'
DATABASE = ':memory:' ou 'data/test/timeblock.db'
LOG_LEVEL = WARNING
LOG_TO_CONSOLE = False
PYTEST_ONLY = True
```

### 3. PRODUCTION (prod)

```python
ENV = 'prod'
DATABASE = '~/.timeblock/timeblock.db'
LOG_LEVEL = INFO
LOG_TO_CONSOLE = False
LOG_ROTATION = {'max_bytes': 10_000_000, 'backup_count': 5}
```

## Admin vs User

**ESCLARECIMENTO:** "Admin" não é ambiente, é ROLE/PERMISSÃO.

```python
# Mesma pessoa, diferentes chapéus:
if comando in ['migrate', 'backup', 'restore']:
    # Operação administrativa
    require_confirmation()
    log_admin_action()
else:
    # Uso normal
    execute_user_command()
```

## Sync Linux/Termux

**CONSIDERAÇÃO FUTURA (v2.0):**

```python
# Ambientes por dispositivo:
Linux Desktop: PRODUCTION (banco principal)
Android Termux: PRODUCTION (sync com Linux)

# Estratégias de sync:
1. Shared DB via Dropbox/Drive
2. API REST (servidor local)
3. Git-like sync (pull/push)
```

**Documentação separada:** `docs/04-specifications/sync-strategy.md` (v2.0)

## Timeline

- v1.2.0: Ambientes não formalizados (tudo roda como dev/prod misturado)
- v1.3.0: Ambientes formalizados (ENV var)
- v2.0: Sync entre dispositivos

---

**Relacionado:** ADR-007 (Alembic), v2.0 sync feature
