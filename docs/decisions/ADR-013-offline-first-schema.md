# ADR-013: Offline-First Schema Migration

**Status**: Accepted

**Data**: 2025-11-05

**Depende de**: ADR-012 (Sync Strategy)

## Contexto

O ADR-012 definiu Queue-Based Sync como estrategia de sincronizacao. Para implementa-la, precisamos modificar o schema SQLite para suportar:

1. **Identificadores Unicos Globais**: IDs que nao colidem entre dispositivos
2. **Metadata de Sync**: Tracking de quando/onde/como foi modificado
3. **Conflict Detection**: Dados para detectar e resolver conflitos
4. **Soft Deletes**: Propagar delecoes entre dispositivos

**Schema Atual (v1.2.0):**

```python
class Habit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # AUTO-INCREMENT
    routine_id: int = Field(foreign_key="routines.id")
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence
```

**Problemas para Sync:**

1. Auto-increment ID: colisoes garantidas
2. Sem device tracking
3. Sem timestamps
4. Sem version control
5. Hard deletes
6. Sem sync status

## Decisao

Adotamos **6 novos campos** no schema + **migracao int para UUID**.

### Novo Schema (v2.0)

```python
from uuid import UUID, uuid4
from datetime import datetime

class Habit(SQLModel, table=True):
    # Primary Key: int → UUID
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign Keys migram para UUID
    routine_id: UUID = Field(foreign_key="routines.id")
    tag_id: UUID | None = Field(default=None, foreign_key="tags.id")

    # Business Fields (mantidos)
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence
    color: str | None = Field(default=None, max_length=7)

    # 6 Campos Sync Metadata
    device_id: UUID = Field(default_factory=get_device_id)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    synced_at: datetime | None = None
    version: int = Field(default=1)
    deleted_at: datetime | None = None
```

### Proposito dos Campos

- **device_id**: Identifica dispositivo criador/modificador
- **created_at**: Timestamp criacao (imutavel)
- **updated_at**: Timestamp ultima modificacao (last-write-wins)
- **synced_at**: Timestamp ultima sincronizacao (otimizacao)
- **version**: Contador modificacoes (deteccao conflito)
- **deleted_at**: Soft delete (propaga deletes)

## Alternativas Consideradas

- **Composite Key**: Rejeitada (complexidade de composite PKs)
- **Timestamps Only**: Rejeitada (clock skew, resolution limit)
- **Event Sourcing**: Rejeitada (complexidade excessiva)
- **CRDTs**: Rejeitada v2.0 (possivel v3.0 com Rust)

## Consequencias

### Positivas

1. IDs unicos globalmente (zero colisoes)
2. Conflict detection robusto
3. Sync otimizado (incremental)
4. Auditoria completa
5. Soft deletes propagam
6. Padrao industria

### Negativas

1. Breaking change (migration necessaria)
2. Storage overhead (+30% DB size)
3. Performance marginal (UUID slower que int)
4. Migration complexity (FKs recriacao)

**Mitigacoes**: Backup automatico, testing extensivo, rollback procedure.

## Migration Strategy

```python
# alembic/versions/002_offline_first.py
def upgrade():
    # 1. Adiciona UUID temporaria
    # 2. Gera UUIDs para registros existentes
    # 3. Atualiza FKs
    # 4. Drop constraints antigas
    # 5. Drop colunas int
    # 6. Renomeia UUID para id
    # 7. Adiciona 6 campos sync
    # 8. Recria constraints
    # 9. Cria indices
```

## Validacao

1. Migration success: 100% em 1000 DBs teste
2. Zero data loss
3. Query performance delta <10%
4. Sync reliability >98%

## Referencias

- CouchDB Replication: <https://docs.couchdb.org/>
- PouchDB Sync: <https://pouchdb.com/guides/replication.html>
- UUID Performance: <https://antonz.org/sqlite-guid/>

---

**Upstream**: ADR-012 (Sync Strategy)

**Downstream**: ADR-014 (Sync UX Flow)
